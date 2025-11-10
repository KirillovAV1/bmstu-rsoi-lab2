from fastapi import APIRouter

router = APIRouter()

@router.get("/manage/health")
async def health():
    return {"status": "ok"}

