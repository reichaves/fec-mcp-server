
import json
from typing import Optional
from ..server import mcp
from ..context import fec

@mcp.tool()
async def search_contributions(
    contributor_name: Optional[str] = None,
    contributor_employer: Optional[str] = None,
    contributor_state: Optional[str] = None,
    committee_id: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    election_cycle: Optional[int] = None
) -> str:
    """
    Search for individual campaign contributions (Schedule A).
    
    Args:
        contributor_name: Name of the donor (e.g., "John Smith")
        contributor_employer: Employer of the donor (e.g., "Google", "Goldman Sachs")
        contributor_state: State of the donor (e.g., "CA", "NY")
        committee_id: FEC committee ID that received the contribution
        min_amount: Minimum contribution amount in dollars
        max_amount: Maximum contribution amount in dollars
        election_cycle: Two-year election cycle (e.g., 2024, 2022)
    
    Returns:
        List of matching contributions with donor and recipient details
    """
    try:
        result = await fec.get_contributions(
            committee_id=committee_id,
            contributor_name=contributor_name,
            contributor_employer=contributor_employer,
            contributor_state=contributor_state,
            min_amount=min_amount,
            max_amount=max_amount,
            two_year_transaction_period=election_cycle,
            per_page=30
        )
        
        contributions = []
        for c in result.get("results", []):
            contributions.append({
                "contributor": {
                    "name": c.get("contributor_name"),
                    "employer": c.get("contributor_employer"),
                    "occupation": c.get("contributor_occupation"),
                    "city": c.get("contributor_city"),
                    "state": c.get("contributor_state"),
                    "zip": c.get("contributor_zip")
                },
                "recipient": {
                    "committee_id": c.get("committee_id"),
                    "committee_name": c.get("committee", {}).get("name") if c.get("committee") else None
                },
                "amount": c.get("contribution_receipt_amount"),
                "date": c.get("contribution_receipt_date"),
                "memo": c.get("memo_text")
            })
        
        # Agrupa por empregador se buscou por empregador
        employer_summary = {}
        if contributor_employer:
            for c in contributions:
                emp = c["contributor"]["employer"] or "Unknown"
                if emp not in employer_summary:
                    employer_summary[emp] = {"count": 0, "total": 0}
                employer_summary[emp]["count"] += 1
                employer_summary[emp]["total"] += c["amount"] or 0
        
        response = {
            "total_results": result.get("pagination", {}).get("count", 0),
            "showing": len(contributions),
            "contributions": contributions
        }
        
        if employer_summary:
            response["employer_summary"] = employer_summary
        
        return json.dumps(response, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
async def get_top_donors(
    committee_id: str,
    min_amount: float = 1000,
    election_cycle: Optional[int] = None
) -> str:
    """
    Get the top donors to a campaign committee.
    
    Args:
        committee_id: FEC committee ID (e.g., "C00703975" for Biden for President)
        min_amount: Minimum contribution amount to include (default: $1,000)
        election_cycle: Two-year election cycle (e.g., 2024)
    
    Returns:
        Aggregated list of top donors with total contributions
    """
    try:
        result = await fec.get_contributions(
            committee_id=committee_id,
            min_amount=min_amount,
            two_year_transaction_period=election_cycle,
            per_page=100
        )
        
        # Agrega por doador
        donors = {}
        for c in result.get("results", []):
            name = c.get("contributor_name", "Unknown")
            if name not in donors:
                donors[name] = {
                    "name": name,
                    "employer": c.get("contributor_employer"),
                    "occupation": c.get("contributor_occupation"),
                    "state": c.get("contributor_state"),
                    "total_amount": 0,
                    "contribution_count": 0
                }
            donors[name]["total_amount"] += c.get("contribution_receipt_amount", 0)
            donors[name]["contribution_count"] += 1
        
        # Ordena por total
        sorted_donors = sorted(donors.values(), key=lambda x: x["total_amount"], reverse=True)[:20]
        
        # Estatísticas por empregador
        by_employer = {}
        for d in donors.values():
            emp = d["employer"] or "Unknown/Self-employed"
            if emp not in by_employer:
                by_employer[emp] = {"total": 0, "count": 0}
            by_employer[emp]["total"] += d["total_amount"]
            by_employer[emp]["count"] += 1
        
        top_employers = sorted(by_employer.items(), key=lambda x: x[1]["total"], reverse=True)[:10]
        
        return json.dumps({
            "committee_id": committee_id,
            "top_donors": sorted_donors,
            "top_employers": [
                {"employer": emp, "total": data["total"], "donor_count": data["count"]}
                for emp, data in top_employers
            ],
            "summary": {
                "unique_donors": len(donors),
                "total_from_top_20": sum(d["total_amount"] for d in sorted_donors)
            }
        }, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
async def get_contributions_by_state(
    committee_id: str,
    election_cycle: Optional[int] = None
) -> str:
    """
    Get contribution totals aggregated by state - useful for geographic analysis.
    
    Args:
        committee_id: FEC committee ID
        election_cycle: Two-year election cycle (e.g., 2024)
    
    Returns:
        Contributions broken down by state with totals
    """
    try:
        result = await fec.get_contributions_by_state(committee_id, election_cycle)
        
        states = []
        for s in result.get("results", []):
            states.append({
                "state": s.get("state"),
                "state_full": s.get("state_full"),
                "total": s.get("total"),
                "count": s.get("count")
            })
        
        # Ordena por total
        states_sorted = sorted(states, key=lambda x: x["total"] or 0, reverse=True)
        
        total_all = sum(s["total"] or 0 for s in states)
        
        return json.dumps({
            "committee_id": committee_id,
            "cycle": election_cycle,
            "by_state": states_sorted,
            "summary": {
                "total_amount": total_all,
                "states_with_contributions": len([s for s in states if s["total"]]),
                "top_5_states": [s["state"] for s in states_sorted[:5]]
            }
        }, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
