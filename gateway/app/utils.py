from .clients import *
from .models import *


def concat_reservation_payments(reservations: list[dict]) -> list[ReservationResponse]:
    result = []
    for r in reservations:
        payment_data = fetch_payment(r["paymentUid"])
        result.append(
            ReservationResponse(
                reservationUid=r["reservationUid"],
                hotel=HotelInfo(**r["hotel"]),
                startDate=r["startDate"],
                endDate=r["endDate"],
                status=r["status"],
                payment=PaymentInfo(
                    status=PaymentStatus(payment_data["status"]),
                    price=payment_data["price"]
                )
            )
        )
    return result


def calculate_price(start_date: date, end_date: date, price_per_night: int, discount_percent: int) -> int:
    nights: int = (end_date - start_date).days
    return price_per_night * nights * (100 - discount_percent) // 100
