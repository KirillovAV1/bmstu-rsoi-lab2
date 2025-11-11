from fastapi import APIRouter, Header
from .db import get_conn

router = APIRouter()

@router.get("/manage/health")
def health():
    return {"status": "ok"}

@router.get("/api/v1/loyalty")
def get_loyalty(x_user_name: str = Header(..., alias="X-User-Name")):
    with get_conn() as c, c.cursor() as cur:
        cur.execute(
            "SELECT reservation_count, status, discount FROM loyalty WHERE username=%s",
            (x_user_name,),
        )
        row = cur.fetchone()
    return {"status": row[1], "discount": int(row[2]), "reservationCount": int(row[0])}
