from fastapi import APIRouter, Header, Body, Depends, HTTPException
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
        cur.execute("SELECT COUNT(*) AS total FROM hotels;")
        total = cur.fetchone()["total"]

        cur.execute(
            """
            SELECT *
            FROM hotels
            ORDER BY id
            LIMIT %s OFFSET %s;
            """,
            (params.size, offset),
        )
        rows = cur.fetchall()

    items = [build_hotel_from_row(r) for r in rows]
    return {"total": total, "items": items}


@router.get("/api/v1/me")
def user_reservations(x_user_name: str = Header(..., alias="X-User-Name")):
    with get_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """
            SELECT reservation.*, hotels.*
            FROM reservation
            JOIN hotels ON reservation.hotel_id = hotels.id
            WHERE reservation.username = %s;
            """,
            (x_user_name,),
        )
        rows = cur.fetchall()

    if not rows:
        return {"reservations": []}

    reservations = [build_reservation_from_row(r) for r in rows]
    return {"reservations": reservations}


@router.get("/api/v1/hotel/{hotelUid}")
def get_hotel(hotelUid: UUID):
    with get_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """
            SELECT *
            FROM hotels
            WHERE hotel_uid = %s;
            """,
            (hotelUid,),
        )
        row = cur.fetchone()

    if not row:
        return {}

    return build_hotel_from_row(row)


@router.post("/api/v1/reservations")
def create_reservation(
    x_user_name: str = Header(..., alias="X-User-Name"),
    body: dict = Body(...),
):
    reservation_uid = uuid4()

    try:
        hotel_uid = UUID(body["hotelUid"])
        payment_uid = UUID(body["paymentUid"])
    except Exception:
        raise HTTPException(status_code=400, detail="Неверный формат UUID")

    start_date = body.get("startDate")
    end_date = body.get("endDate")
    status_value = body.get("status")

    if not (hotel_uid and payment_uid and start_date and end_date and status_value):
        raise HTTPException(
            status_code=400,
            detail="Не хватает обязательных полей для создания бронирования",
        )

    with get_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT id FROM hotels WHERE hotel_uid = %s;", (hotel_uid,))
        hotel_row = cur.fetchone()
        if not hotel_row:
            raise HTTPException(status_code=400, detail="Отель не найден")

        cur.execute(
            """
            INSERT INTO reservation
                (reservation_uid, username, payment_uid, hotel_id, status, start_date, end_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING reservation_uid, status, start_date, end_date;
            """,
            (
                reservation_uid,
                x_user_name,
                payment_uid,
                hotel_row["id"],
                status_value,
                start_date,
                end_date,
            ),
        )
        row = cur.fetchone()
        conn.commit()

    return build_created_reservation_response(row, hotel_uid, payment_uid)


@router.get("/api/v1/reservations/{reservationUid}")
def get_reservation(
    reservationUid: UUID,
    x_user_name: str = Header(..., alias="X-User-Name"),
):
    with get_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """
            SELECT reservation.*, hotels.*
            FROM reservation
            JOIN hotels ON reservation.hotel_id = hotels.id
            WHERE reservation.reservation_uid = %s;
            """,
            (reservationUid,),
        )
        row = cur.fetchone()

    if not row or row["username"] != x_user_name:
        raise HTTPException(status_code=404, detail="Билет не найден")

    return build_reservation_from_row(row)

@router.delete("/api/v1/reservations/{reservationUid}")


    # delete:
    #   summary: Отменить бронирование
    #   tags:
    #     - Gateway API
    #   parameters:
    #     - name: reservationUid
    #       in: path
    #       description: UUID бронирования
    #       required: true
    #       schema:
    #         type: string
    #         format: uuid
    #     - name: X-User-Name
    #       in: header
    #       description: Имя пользователя
    #       required: true
    #       schema:
    #         type: string
    #   responses:
    #     "204":
    #       description: Бронь успешно отменена
    #     "404":
    #       description: Бронь не найдена
    #       content:
    #         application/json:
    #           schema:
    #             $ref: "#/components/schemas/ErrorResponse"
