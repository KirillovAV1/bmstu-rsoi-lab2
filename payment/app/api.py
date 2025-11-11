from fastapi import APIRouter, HTTPException
from uuid import uuid4
from .db import get_conn

router = APIRouter()


@router.get("/manage/health")
def health():
    return {"status": "ok"}


@router.post("/api/v1/payments")
def create_payment(payload: dict):
    price = int(payload["price"])
    payment_uid = str(uuid4())
    with get_conn() as c, c.cursor() as cur:
        cur.execute("""
            INSERT INTO payment (payment_uid, status, price)
            VALUES (%s, 'PAID', %s)
        """, (payment_uid, price))
        c.commit()
    return {"paymentUid": payment_uid, "status": "PAID", "price": price}


@router.post("/api/v1/payments/{payment_uid}/cancel")
def cancel_payment(payment_uid: str):
    with get_conn() as c, c.cursor() as cur:
        cur.execute("UPDATE payment SET status='CANCELED' WHERE payment_uid=%s", (payment_uid,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Payment not found")
        c.commit()
    return {"paymentUid": payment_uid, "status": "CANCELED"}


@router.get("/api/v1/payments/{payment_uid}")
def get_payment(payment_uid: str):
    with get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT status, price FROM payment WHERE payment_uid=%s", (payment_uid,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Payment not found")
    return {"paymentUid": payment_uid, "status": row[0], "price": int(row[1])}
