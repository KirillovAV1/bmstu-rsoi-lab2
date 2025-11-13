from typing import Dict, Any
from uuid import UUID


def build_hotel_from_row(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "hotelUid": row["hotel_uid"],
        "name": row["name"],
        "country": row["country"],
        "city": row["city"],
        "address": row["address"],
        "stars": row["stars"],
        "price": row["price"],
    }


def build_reservation_from_row(row: Dict[str, Any]) -> Dict[str, Any]:
    full_address = f"{row['country']}, {row['city']}, {row['address']}"
    return {
        "reservationUid": row["reservation_uid"],
        "hotel": {
            "hotelUid": row["hotel_uid"],
            "name": row["name"],
            "fullAddress": full_address,
            "stars": row["stars"],
        },
        "startDate": row["start_date"].isoformat() if row["start_date"] else None,
        "endDate": row["end_date"].isoformat() if row["end_date"] else None,
        "status": row["status"],
        "paymentUid": row["payment_uid"],
    }


def build_created_reservation_response(
        row: Dict[str, Any],
        hotel_uid: UUID,
        payment_uid: UUID,
) -> Dict[str, Any]:
    return {
        "reservationUid": str(row["reservation_uid"]),
        "hotelUid": str(hotel_uid),
        "startDate": row["start_date"].isoformat() if row["start_date"] else None,
        "endDate": row["end_date"].isoformat() if row["end_date"] else None,
        "status": row["status"],
        "paymentUid": str(payment_uid),
    }
