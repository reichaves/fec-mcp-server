
import json
from typing import Optional
from ..server import mcp
from ..context import fec

@mcp.tool()
async def get_campaign_expenditures(
    committee_id: str,
    recipient_name: Optional[str] = None,
    purpose: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    election_cycle: Optional[int] = None
) -> str:
    """
    Get campaign expenditures/disbursements (Schedule B) - how campaigns spend money.
    
    Args:
        committee_id: FEC committee ID
        recipient_name: Name of vendor/recipient (e.g., "Facebook", "GMMB")
        purpose: Expense category (ADVERTISING, POLLING, TRAVEL, FUNDRAISING, SALARIES, CONSULTING)
        min_amount: Minimum amount in dollars
        max_amount: Maximum amount in dollars
        election_cycle: Two-year election cycle (e.g., 2024)
    
    Returns:
        List of expenditures with recipient and purpose details
    """
    try:
        result = await fec.get_disbursements(
            committee_id=committee_id,
            recipient_name=recipient_name,
            disbursement_purpose=purpose,
            min_amount=min_amount,
            max_amount=max_amount,
            two_year_transaction_period=election_cycle,
            per_page=50
        )
        
        expenditures = []
        by_recipient = {}
        by_purpose = {}
        
        for e in result.get("results", []):
            exp = {
                "recipient": e.get("recipient_name"),
                "amount": e.get("disbursement_amount"),
                "date": e.get("disbursement_date"),
                "purpose": e.get("disbursement_description"),
                "category": e.get("disbursement_purpose_category")
            }
            expenditures.append(exp)
            
            # Agrega por destinatário
            rec = exp["recipient"] or "Unknown"
            if rec not in by_recipient:
                by_recipient[rec] = 0
            by_recipient[rec] += exp["amount"] or 0
            
            # Agrega por propósito
            cat = exp["category"] or "OTHER"
            if cat not in by_purpose:
                by_purpose[cat] = 0
            by_purpose[cat] += exp["amount"] or 0
        
        # Top destinatários
        top_recipients = sorted(by_recipient.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return json.dumps({
            "committee_id": committee_id,
            "expenditures": expenditures[:30],
            "summary": {
                "total_shown": sum(e["amount"] or 0 for e in expenditures),
                "by_purpose": by_purpose,
                "top_recipients": [{"name": r[0], "total": r[1]} for r in top_recipients]
            }
        }, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
async def get_independent_expenditures(
    candidate_id: Optional[str] = None,
    committee_id: Optional[str] = None,
    support_oppose: Optional[str] = None,
    min_amount: Optional[float] = None,
    cycle: Optional[int] = None
) -> str:
    """
    Get independent expenditures (Schedule E) - spending by Super PACs and other groups
    to support or oppose candidates (not coordinated with campaigns).
    
    Args:
        candidate_id: FEC candidate ID (to see spending for/against this candidate)
        committee_id: FEC committee ID (to see spending BY this committee)
        support_oppose: S=Support, O=Oppose (filter by intent)
        min_amount: Minimum expenditure amount
        cycle: Two-year election cycle (e.g., 2024)
    
    Returns:
        List of independent expenditures with spender and target details
    """
    try:
        result = await fec.get_independent_expenditures(
            candidate_id=candidate_id,
            committee_id=committee_id,
            support_oppose=support_oppose,
            min_amount=min_amount,
            cycle=cycle,
            per_page=50
        )
        
        expenditures = []
        support_total = 0
        oppose_total = 0
        by_committee = {}
        
        for e in result.get("results", []):
            amount = e.get("expenditure_amount", 0)
            is_support = e.get("support_oppose_indicator") == "S"
            
            exp = {
                "spender": {
                    "committee_id": e.get("committee_id"),
                    "committee_name": e.get("committee", {}).get("name") if e.get("committee") else None
                },
                "target": {
                    "candidate_id": e.get("candidate_id"),
                    "candidate_name": e.get("candidate_name")
                },
                "amount": amount,
                "support_oppose": "SUPPORT" if is_support else "OPPOSE",
                "purpose": e.get("expenditure_description"),
                "date": e.get("expenditure_date"),
                "payee": e.get("payee_name")
            }
            expenditures.append(exp)
            
            # Totais
            if is_support:
                support_total += amount
            else:
                oppose_total += amount
            
            # Por comitê
            cid = exp["spender"]["committee_id"] or "Unknown"
            if cid not in by_committee:
                by_committee[cid] = {
                    "name": exp["spender"]["committee_name"],
                    "support": 0,
                    "oppose": 0
                }
            if is_support:
                by_committee[cid]["support"] += amount
            else:
                by_committee[cid]["oppose"] += amount
        
        # Top spenders
        top_spenders = sorted(
            by_committee.items(),
            key=lambda x: x[1]["support"] + x[1]["oppose"],
            reverse=True
        )[:10]
        
        return json.dumps({
            "filters": {
                "candidate_id": candidate_id,
                "committee_id": committee_id,
                "support_oppose": support_oppose
            },
            "expenditures": expenditures[:30],
            "summary": {
                "total_support": support_total,
                "total_oppose": oppose_total,
                "ratio": f"{support_total/(support_total+oppose_total)*100:.1f}% support" if support_total + oppose_total > 0 else "N/A"
            },
            "top_spenders": [
                {
                    "committee_id": cid,
                    "name": data["name"],
                    "total_support": data["support"],
                    "total_oppose": data["oppose"]
                }
                for cid, data in top_spenders
            ]
        }, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
