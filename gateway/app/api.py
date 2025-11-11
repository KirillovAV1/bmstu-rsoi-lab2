from fastapi import APIRouter, Header, HTTPException, Query, Response, status
from fastapi.responses import JSONResponse
from datetime import date
from . import clients
from .models import (
    PaginationResponse,
    UserInfoResponse,
    ReservationResponse,
    CreateReservationRequest,
    CreateReservationResponse,
    ValidationErrorResponse,
    ErrorResponse,
    PaymentInfo,
    ReservationStatus,
)

router = APIRouter()


@router.get("/manage/health")
def health():
    return {"gateway": "ok"}


@router.get("/api/v1/hotels", response_model=PaginationResponse)
def list_hotels(page: int = Query(0, ge=0), size: int = Query(10, ge=1, le=100)):
    return clients.get_hotels(page=page, size=size)


@router.get("/api/v1/loyalty")
def get_loyalty(x_user_name: str = Header(..., alias="X-User-Name")):
    return clients.get_loyalty(username=x_user_name)


@router.get("/api/v1/me", response_model=UserInfoResponse)
def get_me(x_user_name: str = Header(..., alias="X-User-Name")):
    reservations = clients.list_reservations(username=x_user_name)
    for r in reservations:
        pay_uid = r.get("payment", {}).get("paymentUid")
        if pay_uid:
            p = clients.get_payment(pay_uid)
            if p:
                r["payment"] = {"status": p["status"], "price": p["price"]}
    loyalty = clients.get_loyalty(username=x_user_name)
    return {"reservations": reservations, "loyalty": loyalty}


@router.get("/api/v1/reservations", response_model=list[ReservationResponse])
def list_my_reservations(x_user_name: str = Header(..., alias="X-User-Name")):
    items = clients.list_reservations(username=x_user_name)
    for r in items:
        pay_uid = r.get("payment", {}).get("paymentUid")
        if pay_uid:
            p = clients.get_payment(pay_uid)
            if p:
                r["payment"] = {"status": p["status"], "price": p["price"]}
    return items


@router.post(
    "/api/v1/reservations",
    response_model=CreateReservationResponse,
    responses={400: {"model": ValidationErrorResponse}},
)
def create_reservation(payload: CreateReservationRequest,
                       x_user_name: str = Header(..., alias="X-User-Name")):
    try:
        start = date.fromisoformat(payload.startDate)
        end = date.fromisoformat(payload.endDate)
    except ValueError:
        return JSONResponse(
            status_code=400,
            content={
                "message": "Invalid date format",
                "errors": [{"field": "startDate/endDate", "error": "Use YYYY-MM-DD"}],
            },
        )
    if end <= start:
        return JSONResponse(
            status_code=400,
            content={
                "message": "Validation error",
                "errors": [{"field": "endDate", "error": "endDate must be after startDate"}],
            },
        )
    nights = (end - start).days

    hotel = clients.get_hotel_by_uid(payload.hotelUid)
    if not hotel:
        return JSONResponse(
            status_code=400,
            content={
                "message": "Validation error",
                "errors": [{"field": "hotelUid", "error": "Hotel not found"}],
            },
        )
    base_price = int(hotel["price"]) * nights

    loyalty = clients.get_loyalty(username=x_user_name)
    discount = int(loyalty.get("discount", 0))
    final_price = base_price * (100 - discount) // 100

    payment = clients.create_payment(price=final_price)

    created = clients.create_reservation(
        username=x_user_name,
        hotel_uid=str(payload.hotelUid),
        start_date=payload.startDate,
        end_date=payload.endDate,
        payment_uid=payment["paymentUid"],
        status="PAID",
    )

    return {
        "reservationUid": created["reservationUid"],
        "hotelUid": str(payload.hotelUid),
        "startDate": payload.startDate,
        "endDate": payload.endDate,
        "discount": discount,
        "status": ReservationStatus.PAID,
        "payment": PaymentInfo(status=payment["status"], price=payment["price"]),
    }


@router.get(
    "/api/v1/reservations/{reservationUid}",
    response_model=ReservationResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_reservation(reservationUid: str,
                    x_user_name: str = Header(..., alias="X-User-Name")):
    data = clients.get_reservation_by_uid(reservationUid)
    if not data or data.get("username") != x_user_name:
        raise HTTPException(status_code=404, detail="Not found")
    pay_uid = data.get("payment", {}).get("paymentUid")
    if pay_uid:
        p = clients.get_payment(pay_uid)
        if p:
            data["payment"] = {"status": p["status"], "price": p["price"]}
    return data


@router.delete(
    "/api/v1/reservations/{reservationUid}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
def cancel_reservation(reservationUid: str,
                       x_user_name: str = Header(..., alias="X-User-Name")):
    data = clients.get_reservation_by_uid(reservationUid)
    if not data or data.get("username") != x_user_name:
        raise HTTPException(status_code=404, detail="Not found")

    pay_uid = data["payment"]["paymentUid"]
    clients.cancel_payment(pay_uid)
    clients.cancel_reservation(reservationUid)
    clients.loyalty_mutate(username=x_user_name, delta=-1)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
