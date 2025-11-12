from fastapi import APIRouter, Header
from .db import get_conn
import psycopg2.extras

router = APIRouter()


@router.get("/manage/health")
def health():
    return {"status": "ok"}


@router.get("/api/v1/me")
def user_loyalty(x_user_name: str = Header(..., alias="X-User-Name")):
    with get_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("""
            SELECT *
            FROM loyalty
            WHERE username = %s;
        """, (x_user_name,))
        row = cur.fetchone()

    if not row:
        return {}

    loyalty = {
        "status": row["status"],
        "discount": row["discount"],
        "reservationCount": row["reservation_count"]
    }

    return loyalty



