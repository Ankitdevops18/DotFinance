from fastapi import APIRouter

router = APIRouter(prefix="/tenants", tags=["tenants"])

@router.get("")
def list_tenants():
    return {"tenants": []}
