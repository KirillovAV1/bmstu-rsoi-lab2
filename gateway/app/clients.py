import httpx
from uuid import UUID

services = {
    "LOYALTY_URL": "http://loyalty:8050",
    "PAYMENT_URL": "http://payment:8060",
    "RESERVATION_URL": "http://reservation:8070",
}

client = httpx.Client(timeout=5.0)


def fetch_hotels(page: int, size: int):
    r = client.get(
        f"{services["RESERVATION_URL"]}/api/v1/hotels",
        params={"page": page, "size": size})
    r.raise_for_status()
    return r.json()


def fetch_user_reservations(username: str):
    r = client.get(
        f"{services["RESERVATION_URL"]}/api/v1/me",
        headers={"X-User-Name": username},
    )
    r.raise_for_status()
    return r.json()


def fetch_user_loyalty(username: str):
    r = client.get(
        f"{services["LOYALTY_URL"]}/api/v1/me",
        headers={"X-User-Name": username})
    r.raise_for_status()
    return r.json()


def fetch_payment(payment_uid: UUID):
    r = client.get(f"{services["PAYMENT_URL"]}/api/v1/payments/{payment_uid}")
    r.raise_for_status()
    return r.json()


def fetch_hotel(hotel_uid: UUID):
    r = client.get(f"{services["RESERVATION_URL"]}/api/v1/hotel/{hotel_uid}")
    r.raise_for_status()
    return r.json()


def create_payment(price: int):
    r = client.post(
        f"{services['PAYMENT_URL']}/api/v1/payments",
        json={"price": price})
    r.raise_for_status()
    return r.json()


def increase_loyalty(username: str):
    r = client.patch(
        f"{services["LOYALTY_URL"]}/api/v1/increase",
        headers={"X-User-Name": username})
    r.raise_for_status()
    return r.json()


def new_reservation(reservation_data: dict, x_user_name: str):
    r = client.post(
        f"{services['RESERVATION_URL']}/api/v1/reservations",
        headers={"X-User-Name": x_user_name},
        json=reservation_data)
    r.raise_for_status()
    return r.json()


def fetch_reservation_by_uid(reservation_uid: UUID, x_user_name: str):
    r = client.get(
        f"{services['RESERVATION_URL']}/api/v1/reservations/{reservation_uid}",
        headers={"X-User-Name": x_user_name})
    r.raise_for_status()
    return r.json()
