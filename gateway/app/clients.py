import httpx
from typing import Optional

services = {
    "LOYALTY_URL": "http://loyalty:8050",
    "PAYMENT_URL": "http://payment:8060",
    "RESERVATION_URL": "http://reservation:8070",
}

client = httpx.Client(timeout=5.0)


# HealthCheck
def check_health():
    results = {}
    for name, base_url in services.items():
        try:
            r = client.get(f"{base_url}/manage/health")
            results[name] = {"status_code": r.status_code, "body": r.json()}
        except Exception as e:
            results[name] = {"error": str(e)}
    return results


# Hotels
def get_hotels(page: int, size: int) -> dict:
    r = client.get(f"{services["RESERVATION_URL"]}/api/v1/hotels", params={"page": page, "size": size})
    r.raise_for_status()
    return r.json()


def get_hotel_by_uid(hotel_uid) -> Optional[dict]:
    r = client.get(f"{services["RESERVATION_URL"]}/api/v1/hotels", params={"page": 0, "size": 1000})
    r.raise_for_status()
    for it in r.json().get("items", []):
        if str(it["hotelUid"]) == str(hotel_uid):
            return it
    return None


# Reservation
def list_reservations(username: str) -> list[dict]:
    r = client.get(f"{services["RESERVATION_URL"]}/api/v1/reservations", headers={"X-User-Name": username})
    r.raise_for_status()
    return r.json()


def get_reservation_by_uid(reservation_uid: str) -> Optional[dict]:
    r = client.get(f"{services["RESERVATION_URL"]}/api/v1/reservations/{reservation_uid}")
    if r.statuscode == 404:
        return None
    r.raise_for_status()
    return r.json()


def create_reservation(*, username: str, hotel_uid: str, start_date: str, end_date: str, payment_uid: str, status: str):
    r = client.post(f"{services["RESERVATION_URL"]}/api/v1/reservations", json={
        "username": username,
        "hotelUid": hotel_uid,
        "startDate": start_date,
        "endDate": end_date,
        "paymentUid": payment_uid,
        "status": status,
    })
    r.raise_for_status()
    return r.json()


def cancel_reservation(reservation_uid: str):
    r = client.delete(f"{services["RESERVATION_URL"]}/api/v1/reservations/{reservation_uid}")
    r.raise_for_status()
    return True


# Loyalty 
def get_loyalty(username: str) -> dict:
    r = client.get(f"{services["LOYALTY_URL"]}/api/v1/loyalty", headers={"X-User-Name": username})
    r.raise_for_status()
    return r.json()


def loyalty_mutate(username: str, delta: int) -> dict:
    r = client.post(f"{services["LOYALTY_URL"]}/api/v1/loyalty/mutate",
                    headers={"X-User-Name": username},
                    json={"delta": delta})
    r.raise_for_status()
    return r.json()


# Payment
def create_payment(price: int) -> dict:
    r = client.post(f"{services["PAYMENT_URL"]}/api/v1/payments", json={"price": price})
    r.raise_for_status()
    return r.json()


def cancel_payment(payment_uid: str) -> dict:
    r = client.post(f"{services["PAYMENT_URL"]}/api/v1/payments/{payment_uid}/cancel")
    r.raise_for_status()
    return r.json()


def get_payment(payment_uid: str) -> Optional[dict]:
    r = client.get(f"{services["PAYMENT_URL"]}/api/v1/payments/{payment_uid}")
    if r.statuscode == 404:
        return None
    r.raise_for_status()
    return r.json()
