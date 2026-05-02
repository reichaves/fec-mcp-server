
import json
from typing import Optional
from ..server import mcp
from ..context import fec
from ..i18n import get_text

@mcp.tool()
async def search_candidates(
    name: Optional[str] = None,
    state: Optional[str] = None,
    office: Optional[str] = None,
    party: Optional[str] = None,
    cycle: Optional[int] = None
) -> str:
    """
    Search for political candidates in the FEC database.
    
    Args:
        name: Candidate name or part of name (e.g., "Biden", "Trump", "Ocasio")
        state: Two-letter state code (e.g., "CA", "NY", "TX")
        office: P=President, S=Senate, H=House
        party: DEM=Democrat, REP=Republican, LIB=Libertarian, GRE=Green
        cycle: Two-year election cycle (e.g., 2020, 2022, 2024)
    
    Returns:
        List of matching candidates with their IDs
    """
    try:
        result = await fec.search_candidates(
            name=name,
            state=state,
            office=office,
            party=party,
            cycle=cycle
        )
        
        candidates = []
        for c in result.get("results", [])[:15]:
            candidates.append({
                "candidate_id": c.get("candidate_id"),
                "name": c.get("name"),
                "party": c.get("party_full"),
                "state": c.get("state"),
                "office": c.get("office_full"),
                "district": c.get("district"),
                "election_years": c.get("election_years", [])[-3:],  # últimos 3 ciclos
                "has_raised_funds": c.get("has_raised_funds"),
                "principal_committees": [
                    {"id": pc.get("committee_id"), "name": pc.get("name")}
                    for pc in c.get("principal_committees", [])[:2]
                ]
            })
        
        return json.dumps({
            "total_results": result.get("pagination", {}).get("count", 0),
            "showing": len(candidates),
            "candidates": candidates,
            "tip": get_text("tip_search_candidates")
        }, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
async def get_candidate_finances(
    candidate_id: str,
    cycle: Optional[int] = None
) -> str:
    """
    Get comprehensive financial information for a candidate.
    
    Args:
        candidate_id: FEC candidate ID (e.g., "P80001571" for Biden, "P80000722" for Trump)
        cycle: Specific two-year election cycle (e.g., 2024, 2020)
    
    Returns:
        Financial totals including money raised, spent, and cash on hand. 
        Note: Financial values are returned as raw floats in USD. Format them according to the user's locale when displaying.
    """
    try:
        # Busca totais financeiros
        result = await fec.get_candidate_totals(candidate_id, cycle)
        totals = result.get("results", [{}])[0] if result.get("results") else {}
        
        # Busca info básica do candidato
        candidate_info = await fec.get_candidate(candidate_id)
        candidate = candidate_info.get("results", [{}])[0] if candidate_info.get("results") else {}
        
        return json.dumps({
            "candidate": {
                "id": candidate_id,
                "name": candidate.get("name"),
                "party": candidate.get("party_full"),
                "office": candidate.get("office_full"),
                "state": candidate.get("state")
            },
            "finances": {
                "cycle": totals.get("cycle"),
                "total_raised": totals.get("receipts"),
                "total_spent": totals.get("disbursements"),
                "cash_on_hand": totals.get("cash_on_hand_end_period"),
                "debt": totals.get("debts_owed_by_committee"),
                "individual_contributions": totals.get("individual_contributions"),
                "pac_contributions": totals.get("other_political_committee_contributions"),
                "self_funding": totals.get("candidate_contribution")
            },
            "coverage_dates": {
                "start": totals.get("coverage_start_date"),
                "end": totals.get("coverage_end_date")
            },
            "committee_id": totals.get("committee_id"),
            "tip": get_text("tip_candidate_finances_past_cycle", cycle_returned=totals.get("cycle"), cycle_requested=cycle) if cycle and totals.get("cycle") != cycle else get_text("tip_candidate_finances_normal")
        }, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
