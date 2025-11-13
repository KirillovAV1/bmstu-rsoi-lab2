def build_reservation_from_row(r: dict) -> dict:
    full_address = f"{r['country']}, {r['city']}, {r['address']}"
    return {
        "reservationUid": r["reservation_uid"],
        "hotel": {
            "hotelUid": r["hotel_uid"],
            "name": r["name"],
            "fullAddress": full_address,
            "stars": r["stars"],
        },
        "startDate": r["start_date"].isoformat() if r["start_date"] else None,
        "endDate": r["end_date"].isoformat() if r["end_date"] else None,
        "status": r["status"],
        "paymentUid": r["payment_uid"],
    }
