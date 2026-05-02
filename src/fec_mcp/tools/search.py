
import json
from typing import Optional
from ..server import mcp
from ..context import fec
from ..i18n import get_text

@mcp.tool()
async def search_pacs(
    name: Optional[str] = None,
    super_pac_only: bool = False,
    state: Optional[str] = None,
    party: Optional[str] = None,
    cycle: Optional[int] = None
) -> str:
    """
    Search for PACs (Political Action Committees) and Super PACs.
    
    Args:
        name: Committee name to search (e.g., "America", "Freedom", "Progress")
        super_pac_only: If True, only return Super PACs (Independent Expenditure-Only)
        state: Two-letter state code
        party: Party affiliation (DEM, REP)
        cycle: Two-year election cycle (e.g., 2020, 2022, 2024)
    
    Returns:
        List of matching committees with their IDs and types
    """
    try:
        committee_type = "O" if super_pac_only else None  # O = Super PAC
        
        result = await fec.search_committees(
            name=name,
            committee_type=committee_type,
            state=state,
            party=party,
            cycle=cycle,
            per_page=30
        )
        
        committees = []
        for c in result.get("results", []):
            committees.append({
                "committee_id": c.get("committee_id"),
                "name": c.get("name"),
                "type": c.get("committee_type_full"),
                "type_code": c.get("committee_type"),
                "designation": c.get("designation_full"),
                "party": c.get("party_full"),
                "state": c.get("state"),
                "treasurer": c.get("treasurer_name"),
                "first_filing_date": c.get("first_file_date"),
                "is_active": c.get("cycles") and max(c.get("cycles", [0])) >= 2022
            })
        
        # Agrupa por tipo
        by_type = {}
        for c in committees:
            t = c["type"] or "Unknown"
            if t not in by_type:
                by_type[t] = 0
            by_type[t] += 1
        
        return json.dumps({
            "total_results": result.get("pagination", {}).get("count", 0),
            "showing": len(committees),
            "committees": committees,
            "by_type": by_type,
            "tip": get_text("tip_search_committees")
        }, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
