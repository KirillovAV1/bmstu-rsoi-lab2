from fastapi import APIRouter, Header, Body, Depends, HTTPException, status
from uuid import uuid4
from .models import *
import psycopg2.extras
from .db import get_conn
from .utils import *

router = APIRouter()
psycopg2.extras.register_uuid()


@router.get("/manage/health")
def health():
    return {"status": "ok"}


@router.get("/api/v1/hotels")
def list_hotels(params: GetHotelsQuery = Depends()):
    offset = params.page * params.size
    with get_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT COUNT(*) FROM hotels;")
        total = cur.fetchone()["count"]

        cur.execute("""
            SELECT *
            FROM hotels
            ORDER BY id
            LIMIT %s OFFSET %s;
                    """, (params.size, offset))
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

    reservations = [build_reservation_from_row(r) for r in rows]
    return {"reservations": reservations}



@router.get("/api/v1/hotel/{hotelUid}")
def get_hotel(hotelUid: UUID):
    with get_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("""
                SELECT *
                FROM hotels
                WHERE hotel_uid = %s;
            """, (hotelUid,))
        row = cur.fetchone()

    if not row:
        return {}

    hotel = {
        "hotelUid": row["hotel_uid"],
        "name": row["name"],
        "country": row["country"],
        "city": row["city"],
        "address": row["address"],
        "stars": row["stars"],
        "price": row["price"],
    }

    return hotel


@router.post("/api/v1/reservations")
def create_reservation(
        x_user_name: str = Header(..., alias="X-User-Name"),
        body: dict = Body(...),
):
    reservation_uid = uuid4()

    try:
        hotel_uid = UUID(body["hotelUid"])
        payment_uid = UUID(body["paymentUid"])
    except:
        raise HTTPException(400, "Неверный формат UUID")

    start_date = body.get("startDate")
    end_date = body.get("endDate")
    status_value = body.get("status")

    if not (hotel_uid and payment_uid and start_date and end_date and status_value):
        raise HTTPException(400, "Не хватает обязательных полей")

    with get_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:

        cur.execute("SELECT id FROM hotels WHERE hotel_uid=%s", (hotel_uid,))
        hotel_row = cur.fetchone()
        if not hotel_row:
            raise HTTPException(400, "Отель не найден")

        cur.execute(
            """
            INSERT INTO reservation
                (reservation_uid, username, payment_uid, hotel_id, status, start_date, end_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING reservation_uid, status, start_date, end_date;
            """,
            (reservation_uid, x_user_name, payment_uid, hotel_row["id"],
             status_value, start_date, end_date)
        )
        row = cur.fetchone()
        conn.commit()

    return {
        "reservationUid": str(row["reservation_uid"]),
        "hotelUid": str(hotel_uid),
        "startDate": row["start_date"].isoformat(),
        "endDate": row["end_date"].isoformat(),
        "status": row["status"],
        "paymentUid": str(payment_uid)
    }


@router.get("/api/v1/reservations/{reservationUid}")
def get_reservation(
    reservationUid: UUID,
    x_user_name: str = Header(..., alias="X-User-Name"),
):
    with get_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("""
            SELECT reservation.*, hotels.*
            FROM reservation
            JOIN hotels ON reservation.hotel_id = hotels.id
            WHERE reservation.reservation_uid = %s;
        """, (reservationUid,))
        row = cur.fetchone()

    if not row or row["username"] != x_user_name:
        raise HTTPException(status_code=404, detail="Билет не найден")

    return build_reservation_from_row(row)

