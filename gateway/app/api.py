from fastapi import APIRouter
from .clients import check_health

router = APIRouter()


@router.get("/manage/health")
def health():
    return {"gateway": "ok", "services": check_health()}
