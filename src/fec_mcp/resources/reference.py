
import json
from ..server import mcp

@mcp.resource("fec://reference/codes")
def get_reference_codes() -> str:
    """Complete reference codes for FEC data"""
    return json.dumps({
        "parties": {
            "DEM": "Democratic Party",
            "REP": "Republican Party",
            "LIB": "Libertarian Party",
            "GRE": "Green Party",
            "IND": "Independent",
            "CON": "Constitution Party",
            "REF": "Reform Party",
            "NNE": "None (No Party)"
        },
        "offices": {
            "P": "President",
            "S": "Senate",
            "H": "House of Representatives"
        },
        "committee_types": {
            "C": "Communication Cost",
            "D": "Delegate Committee",
            "E": "Electioneering Communication",
            "H": "House Campaign",
            "I": "Independent Expenditure (Person)",
            "N": "PAC - Nonqualified",
            "O": "Super PAC (Independent Expenditure-Only)",
            "P": "Presidential Campaign",
            "Q": "PAC - Qualified",
            "S": "Senate Campaign",
            "U": "Single Candidate Independent Expenditure",
            "V": "PAC with Non-Contribution Account",
            "W": "PAC with Non-Contribution Account - Nonqualified",
            "X": "Party - Nonqualified",
            "Y": "Party - Qualified",
            "Z": "National Party Nonfederal Account"
        },
        "disbursement_categories": {
            "ADVERTISING": "Advertising expenses",
            "POLLING": "Polling and surveys",
            "TRAVEL": "Travel expenses",
            "FUNDRAISING": "Fundraising costs",
            "SALARIES": "Staff salaries",
            "CONSULTING": "Consulting fees",
            "EVENTS": "Event expenses",
            "MATERIALS": "Campaign materials",
            "ADMINISTRATIVE": "Administrative costs"
        },
        "form_types": {
            "F1": "Statement of Organization",
            "F2": "Statement of Candidacy",
            "F3": "Report of Receipts and Disbursements (House/Senate)",
            "F3P": "Report of Receipts and Disbursements (Presidential)",
            "F3X": "Report of Receipts and Disbursements (PAC/Party)",
            "F5": "Report of Independent Expenditures (24-hour)",
            "F6": "48-Hour Notice of Contributions",
            "F7": "Report of Communication Costs",
            "F9": "24-Hour Notice of Electioneering Communications",
            "F99": "Miscellaneous Text"
        },
        "support_oppose": {
            "S": "Support",
            "O": "Oppose"
        },
        "contribution_limits_2024": {
            "individual_to_candidate": "$3,300 per election",
            "individual_to_pac": "$5,000 per year",
            "individual_to_national_party": "$41,300 per year",
            "pac_to_candidate": "$5,000 per election",
            "note": "Super PACs have no contribution limits but cannot coordinate with campaigns"
        }
    }, indent=2, ensure_ascii=False)


@mcp.resource("fec://reference/notable_ids")
def get_notable_ids() -> str:
    """Notable candidate and committee IDs for reference"""
    return json.dumps({
        "presidential_2024": {
            "Joe Biden": {"candidate_id": "P80000722", "committee_id": "C00703975"},
            "Donald Trump": {"candidate_id": "P80001571", "committee_id": "C00580100"},
            "Robert Kennedy Jr": {"candidate_id": "P00016451", "committee_id": "C00831735"}
        },
        "national_committees": {
            "Democratic National Committee": "C00010603",
            "Republican National Committee": "C00003418",
            "Democratic Senatorial Campaign Committee": "C00042366",
            "National Republican Senatorial Committee": "C00027466",
            "Democratic Congressional Campaign Committee": "C00000935",
            "National Republican Congressional Committee": "C00075820"
        },
        "notable_super_pacs": {
            "Priorities USA Action": "C00495861",
            "Senate Leadership Fund": "C00571703",
            "Senate Majority PAC": "C00484642",
            "Congressional Leadership Fund": "C00504530",
            "House Majority PAC": "C00485102"
        },
        "note": "IDs are stable across election cycles. Use search_candidates() or search_pacs() to find specific IDs."
    }, indent=2, ensure_ascii=False)


@mcp.resource("fec://reference/api_info")
def get_api_info() -> str:
    """Information about the FEC API and data"""
    return json.dumps({
        "api": {
            "name": "OpenFEC API",
            "documentation": "https://api.open.fec.gov/developers/",
            "data_source": "Federal Election Commission",
            "update_frequency": "Daily (filings), varies by report type"
        },
        "data_coverage": {
            "federal_only": True,
            "includes": ["President", "Senate", "House"],
            "excludes": ["State elections", "Local elections", "Ballot measures"],
            "historical_data": "1979-present (varies by data type)"
        },
        "limitations": {
            "rate_limits": "1,000 requests/hour with API key",
            "pagination": "Max 100 results per request",
            "dark_money": "501(c)(4) donors not disclosed to FEC",
            "timing": "Data may be 24-48 hours behind filings"
        },
        "tips": {
            "1": "Always start with search_candidates() to get correct IDs",
            "2": "Committee IDs (Cxxxxxxxx) are needed for financial details",
            "3": "Use fec_help() for guidance on specific topics",
            "4": "Cross-reference with OpenSecrets.org for additional context"
        }
    }, indent=2, ensure_ascii=False)


from pathlib import Path

@mcp.resource("fec://reference/glossary")
def get_glossary() -> str:
    """Glossary of FEC terminology"""
    try:
        glossary_path = Path(__file__).parent.parent / "data" / "glossary.json"
        with open(glossary_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return json.dumps({"error": f"Failed to load glossary: {str(e)}"})
