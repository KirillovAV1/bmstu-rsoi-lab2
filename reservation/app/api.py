from fastapi import APIRouter, Query, Header
from fastapi.responses import JSONResponse
from uuid import UUID
import psycopg2.extras
from .db import get_conn

router = APIRouter()
psycopg2.extras.register_uuid()


@router.get("/manage/health")
def health():
    return {"status": "ok"}


@router.get("/api/v1/hotels")
def list_hotels(page: int = Query(0, ge=0), size: int = Query(1, ge=1, le=100)):
    offset = page * size
    with get_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT COUNT(*) FROM hotels;")
        total = cur.fetchone()["count"]

        cur.execute("""
            SELECT *
            FROM hotels
            ORDER BY id
            LIMIT %s OFFSET %s;
                    """, (size, offset))
        rows = cur.fetchall()

    items = [
        {
            "hotelUid": r["hotelUid"],
            "name": r["name"],
            "country": r["country"],
            "city": r["city"],
            "address": r["address"],
            "stars": r["stars"],
            "price": r["price"],
        }
        for r in rows
    ]

    return {"total": total, "items": items}


@router.get("/api/v1/me")
def user_reservations(x_user_name: str = Header(..., alias="X-User-Name")):
    with get_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("""
            SELECT reservation.*, hotels.*
            FROM reservation
            JOIN hotels ON reservation.hotel_id = hotels.id
            WHERE reservation.username = %s;
        """, (x_user_name,))
        rows = cur.fetchall()

    if not rows:
        return {"reservations": []}

    reservations = []
    for r in rows:
        full_address = f"{r['country']}, {r['city']}, {r['address']}"
        reservations.append({
            "reservationUid": r["reservation_uid"],
            "hotel": {
                "hotelUid": r["hotel_uid"],
                "name": r["name"],
                "fullAddress": full_address,
                "stars": r["stars"]
            },
            "startDate": r["start_date"].isoformat() if r["start_date"] else None,
            "endDate": r["end_date"].isoformat() if r["end_date"] else None,
            "status": r["status"],
            "paymentUid": r["payment_uid"]
        })

    return {"reservations": reservations}
