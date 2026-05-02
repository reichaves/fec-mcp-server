
import json
from typing import Optional
from ..server import mcp
from ..context import fec
from ..i18n import get_text

@mcp.tool()
async def get_campaign_filings(
    candidate_id: Optional[str] = None,
    committee_id: Optional[str] = None,
    form_type: Optional[str] = None,
    min_receipt_date: Optional[str] = None
) -> str:
    """
    Get FEC filings/reports submitted by campaigns and committees.
    
    Args:
        candidate_id: FEC candidate ID
        committee_id: FEC committee ID
        form_type: Form type (F3=House/Senate report, F3P=Presidential, F3X=PAC, F5=Independent expenditure 24h)
        min_receipt_date: Minimum filing date (YYYY-MM-DD)
    
    Returns:
        List of filings with dates, types, and financial summaries
    """
    try:
        result = await fec.get_filings(
            candidate_id=candidate_id,
            committee_id=committee_id,
            form_type=form_type,
            min_receipt_date=min_receipt_date,
            per_page=30
        )
        
        filings = []
        for f in result.get("results", []):
            filings.append({
                "filing_id": f.get("file_number"),
                "form_type": f.get("form_type"),
                "committee_id": f.get("committee_id"),
                "committee_name": f.get("committee_name"),
                "receipt_date": f.get("receipt_date"),
                "coverage_start": f.get("coverage_start_date"),
                "coverage_end": f.get("coverage_end_date"),
                "total_receipts": f.get("total_receipts"),
                "total_disbursements": f.get("total_disbursements"),
                "cash_on_hand": f.get("cash_on_hand_end_period"),
                "document_url": f.get("pdf_url"),
                "is_amended": f.get("is_amended")
            })
        
        # Agrupa por tipo
        by_form = {}
        for f in filings:
            ft = f["form_type"] or "Unknown"
            if ft not in by_form:
                by_form[ft] = 0
            by_form[ft] += 1
        
        return json.dumps({
            "total_results": result.get("pagination", {}).get("count", 0),
            "showing": len(filings),
            "filings": filings,
            "by_form_type": by_form,
            "tip": get_text("tip_filings")
        }, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
