from uuid import uuid4
from fastapi import APIRouter, Header, Query, HTTPException
from .db import get_conn

router = APIRouter()


@router.get("/manage/health")
def health():
    return {"status": "ok"}


@router.get("/api/v1/hotels")
def list_hotels(page: int = Query(0, ge=0), size: int = Query(10, ge=1, le=100)):
    offset = page * size
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM hotels")
        total = cur.fetchone()[0]
        cur.execute(
            """SELECT hotel_uid, name, country, city, address, COALESCE(stars,0), price
               FROM hotels
               ORDER BY id
               LIMIT %s OFFSET %s""",
            (size, offset),
        )
        items = [
            {
                "hotelUid": str(r[0]),
                "name": r[1],
                "country": r[2],
                "city": r[3],
                "address": r[4],
                "stars": int(r[5]),
                "price": int(r[6]),
            }
            for r in cur.fetchall()
        ]
    return {"page": page, "pageSize": size, "totalElements": total, "items": items}


# ---------- RESERVATIONS (внутренние ручки)

@router.get("/api/v1/reservations")
def list_reservations(x_user_name: str = Header(..., alias="X-User-Name")):
    with get_conn() as c, c.cursor() as cur:
        cur.execute("""
            SELECT r.reservation_uid,
                   h.hotel_uid, h.name, h.country, h.city, h.address, COALESCE(h.stars,0),
                   r.start_date::date, r.end_date::date,
                   r.status, r.payment_uid
            FROM reservation r
            JOIN hotels h ON h.id = r.hotel_id
            WHERE r.username = %s
            ORDER BY r.id DESC
        """, (x_user_name,))
        rows = cur.fetchall()

    out = []
    for r in rows:
        out.append({
            "reservationUid": str(r[0]),
            "hotel": {
                "hotelUid": str(r[1]),
                "name": r[2],
                "fullAddress": f"{r[3]}, {r[4]}, {r[5]}",
                "stars": int(r[6]),
            },
            "startDate": str(r[7]),
            "endDate": str(r[8]),
            "status": r[9],
            "payment": {"paymentUid": str(r[10])},
            "username": x_user_name,  # для gateway
        })
    return out


@router.get("/api/v1/reservations/{reservation_uid}")
def get_reservation(reservation_uid: str):
    with get_conn() as c, c.cursor() as cur:
        cur.execute("""
            SELECT r.username,
                   r.reservation_uid,
                   h.hotel_uid, h.name, h.country, h.city, h.address, COALESCE(h.stars,0),
                   r.start_date::date, r.end_date::date,
                   r.status, r.payment_uid
            FROM reservation r
            JOIN hotels h ON h.id = r.hotel_id
            WHERE r.reservation_uid = %s
        """, (reservation_uid,))
        r = cur.fetchone()

    if not r:
        raise HTTPException(status_code=404, detail="Not found")

    return {
        "username": r[0],
        "reservationUid": str(r[1]),
        "hotel": {
            "hotelUid": str(r[2]),
            "name": r[3],
            "fullAddress": f"{r[4]}, {r[5]}, {r[6]}",
            "stars": int(r[7]),
        },
        "startDate": str(r[8]),
        "endDate": str(r[9]),
        "status": r[10],
        "payment": {"paymentUid": str(r[11])},
    }


@router.post("/api/v1/reservations")
def create_reservation(payload: dict):
    username = payload["username"]
    hotel_uid = payload["hotelUid"]
    start_date = payload["startDate"]
    end_date = payload["endDate"]
    payment_uid = payload["paymentUid"]
    status = payload.get("status", "PAID")

    with get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT id FROM hotels WHERE hotel_uid = %s", (hotel_uid,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=400, detail="Hotel not found")

        hotel_id = int(row[0])
        res_uid = str(uuid4())
        cur.execute("""
            INSERT INTO reservation (reservation_uid, username, payment_uid, hotel_id, status, start_date, end_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (res_uid, username, payment_uid, hotel_id, status, start_date, end_date))
        c.commit()

    return {"reservationUid": res_uid}


@router.delete("/api/v1/reservations/{reservation_uid}")
def cancel_reservation(reservation_uid: str):
    with get_conn() as c, c.cursor() as cur:
        cur.execute("UPDATE reservation SET status='CANCELED' WHERE reservation_uid=%s", (reservation_uid,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Not found")
        c.commit()
    return {"status": "CANCELED"}
