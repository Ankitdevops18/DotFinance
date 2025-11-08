from fastapi import APIRouter
from app.tally_bridge.client import send_tally_request

router = APIRouter(prefix="/companies/{company_id}/reports", tags=["reports"])

@router.get("/payables")
def get_payables(company_id: int):
    return {"company_id": company_id, "report": "payables"}

@router.get("/receivables")
async def get_receivables(company_id: int):
    payload = {
        "Request": {
            "Type": "Receivables",
            "Params": {"FromDate": "2025-01-01", "ToDate": "2025-01-31"}
        }
    }
    result = await send_tally_request(payload)
    return result

@router.get("/{report_id}/download")
def download_report(company_id: int, report_id: int):
    return {"company_id": company_id, "report_id": report_id, "download": True}
