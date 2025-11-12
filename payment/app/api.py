from fastapi import APIRouter
from .db import get_conn
import psycopg2.extras
from uuid import UUID

router = APIRouter()


@router.get("/manage/health")
def health():
    return {"status": "ok"}


@router.get("/api/v1/payments/{paymentUid}")
def payment_by_id(paymentUid: UUID):
    with get_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("""
            SELECT *
            FROM payment
            WHERE payment_uid = %s;
        """, (paymentUid,))
        row = cur.fetchone()

    if not row:
        return {}

    payment = {
        "status": row["status"],
        "price": row["price"]
    }

    return payment
