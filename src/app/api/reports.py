from fastapi import APIRouter
from src.app.tally_bridge.client import send_tally_request

router = APIRouter(prefix="/companies/{company_id}/reports", tags=["reports"])

@router.get("/payables")
def get_payables(company_id: int):
    return {"company_id": company_id, "report": "payables"}

@router.get("/receivables")
async def get_receivables(company_id: int):
    # XML payload for Bills Receivable
    xml_payload = """
    <ENVELOPE>
        <HEADER>
            <TALLYREQUEST>Export Data</TALLYREQUEST>
        </HEADER>
        <BODY>
            <EXPORTDATA>
                <REQUESTDESC>
                    <REPORTNAME>Bills Receivable</REPORTNAME>
                    <STATICVARIABLES>
                        <SVFROMDATE>20250401</SVFROMDATE>
                        <SVTODATE>20250430</SVTODATE>
                    </STATICVARIABLES>
                </REQUESTDESC>
            </EXPORTDATA>
        </BODY>
    </ENVELOPE>
    """
    result = await send_tally_request(xml_payload)
    return result

@router.get("/ledgers")
async def get_ledgers(company_id: int):
    # XML payload for List of Ledgers (matches curl --data-binary payload)
    xml_payload = """
            <ENVELOPE>
                <HEADER>
                        <VERSION>1</VERSION>
                        <TALLYREQUEST>EXPORT</TALLYREQUEST>
                        <TYPE>COLLECTION</TYPE>
                        <ID>List of Ledgers</ID>
                </HEADER>
                <BODY>
                <DESC>
                        <STATICVARIABLES>
                                <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                        </STATICVARIABLES>
                </DESC>
                </BODY>
            </ENVELOPE>
            """
    result = await send_tally_request(xml_payload)
    return result

@router.get("/company-balance")
async def get_company_balance(company_id: int):
    # Use company name and id for FinanceBox
    company_name = "FinanceBox"
    company_id_str = "100000"
    # XML payload for Balance Sheet report for FinanceBox with export format
    xml_payload = f"""
    <ENVELOPE>
        <HEADER>
            <TALLYREQUEST>Export Data</TALLYREQUEST>
        </HEADER>
        <BODY>
            <EXPORTDATA>
                <REQUESTDESC>
                    <REPORTNAME>Balance Sheet</REPORTNAME>
                    <EXPORTFORMAT>XML</EXPORTFORMAT>
                    <STATICVARIABLES>
                        <SVFROMDATE>20250401</SVFROMDATE>
                        <SVTODATE>20250430</SVTODATE>
                        <SVCURRENTCOMPANY>{company_name}</SVCURRENTCOMPANY>
                    </STATICVARIABLES>
                </REQUESTDESC>
            </EXPORTDATA>
        </BODY>
    </ENVELOPE>
    """
    result = await send_tally_request(xml_payload)
    return result

@router.get("/{report_id}/download")
def download_report(company_id: int, report_id: int):
    return {"company_id": company_id, "report_id": report_id, "download": True}
