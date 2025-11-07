from fastapi import APIRouter

router = APIRouter(prefix="/companies/{id}/reports", tags=["reports"])

@router.get("/payables")
def get_payables(id: int):
    return {"company_id": id, "report": "payables"}

@router.get("/receivables")
def get_receivables(id: int):
    return {"company_id": id, "report": "receivables"}

@router.get("/{report_id}/download")
def download_report(id: int, report_id: int):
    return {"company_id": id, "report_id": report_id, "download": True}
