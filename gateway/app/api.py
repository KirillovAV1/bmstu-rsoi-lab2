from fastapi import APIRouter, Depends, Header, Body, HTTPException
from .utils import *

router = APIRouter()


@router.get("/manage/health")
def health():
    return {"gateway": "ok"}


@router.get("/api/v1/hotels",
            response_model=PaginationResponse,
            summary="Получить список отелей")
def get_hotels(params: GetHotelsQuery = Depends()):
    data = fetch_hotels(params.page, params.size)
    items = [HotelResponse(**h) for h in data["items"]]
    return PaginationResponse(
        page=params.page,
        pageSize=params.size,
        totalElements=data["total"],
        items=items,
    )


@router.get(
    "/api/v1/me",
    response_model=UserInfoResponse,
    summary="Информация о пользователе",
)
def get_user_info(x_user_name: str = Header(..., alias="X-User-Name")):
    reservations_data = fetch_user_reservations(x_user_name)
    loyalty_data = fetch_user_loyalty(x_user_name)
    reservations = concat_reservation_payments(reservations_data.get("reservations", []))

    return UserInfoResponse(
        reservations=reservations,
        loyalty=LoyaltyInfoResponse(
            status=loyalty_data.get("status"),
            discount=loyalty_data.get("discount"),
            reservationCount=loyalty_data.get("reservationCount")
        )
    )


@router.get(
    "/api/v1/reservations",
    response_model=List[ReservationResponse],
    summary="Информация по всем бронированиям пользователя",
)
def get_user_reservations(x_user_name: str = Header(..., alias="X-User-Name")):
    reservations_data = fetch_user_reservations(x_user_name)
    reservations = concat_reservation_payments(reservations_data.get("reservations", []))
    return reservations


@router.get("/api/v1/loyalty",
            response_model=LoyaltyInfoResponse,
            summary="Получить информацию о статусе в программе лояльности")
def get_loyalty_status(x_user_name: str = Header(..., alias="X-User-Name")):
    loyalty_data = fetch_user_loyalty(x_user_name)
    return LoyaltyInfoResponse(
        status=loyalty_data.get("status"),
        discount=loyalty_data.get("discount"),
        reservationCount=loyalty_data.get("reservationCount")
    )


@router.post("/api/v1/reservations",
             response_model=CreateReservationResponse,
             summary="Забронировать отель")
def create_reservation(x_user_name: str = Header(..., alias="X-User-Name"),
                       body: CreateReservationRequest = Body(...)):
    hotel_data = fetch_hotel(body.hotelUid)
    try:
        hotel_data = HotelResponse(**hotel_data)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=f"Отель с UID {body.hotelUid} не найден"
        )

    loyalty_data = LoyaltyInfoResponse(**fetch_user_loyalty(x_user_name))
    payment_data = create_payment(
        calculate_price(body.startDate, body.endDate, hotel_data.price, loyalty_data.discount))
    update_loyalty(x_user_name, delta=1)

    reservation_data = create_reservation_in_service({
        "hotelUid": str(body.hotelUid),
        "paymentUid": str(payment_data["paymentUid"]),
        "startDate": body.startDate.isoformat(),
        "endDate": body.endDate.isoformat(),
        "status": payment_data["status"],
    }, x_user_name)

    return CreateReservationResponse(
        reservationUid=reservation_data["reservationUid"],
        hotelUid=body.hotelUid,
        startDate=body.startDate,
        endDate=body.endDate,
        discount=loyalty_data.discount,
        status=payment_data["status"],
        payment=PaymentInfo(
            status=payment_data["status"],
            price=payment_data["price"]
        )
    )


@router.get("/api/v1/reservations/{reservationUid}",
            response_model=ReservationResponse,
            summary="Информация по конкретному бронированию")
def get_reservation(
        reservationUid: UUID,
        x_user_name: str = Header(..., alias="X-User-Name")
):
    reservation = fetch_reservation_by_uid(reservationUid, x_user_name)
    if reservation is None:
        raise HTTPException(status_code=404, detail="Билет не найден")

    payment_data = fetch_payment(reservation["paymentUid"])

    return ReservationResponse(
        reservationUid=reservation["reservationUid"],
        hotel=HotelInfo(**reservation["hotel"]),
        startDate=reservation["startDate"],
        endDate=reservation["endDate"],
        status=reservation["status"],
        payment=PaymentInfo(
            status=payment_data["status"],
            price=payment_data["price"]
        )
    )

@router.delete("/api/v1/reservations/{reservationUid}")
def delete_reservation(
        reservationUid: UUID,
        x_user_name: str = Header(..., alias="X-User-Name")
):
    update_loyalty(x_user_name, delta=-1)


    # * Статус бронирования помечается как `CANCELED`.
# * В Payment Service запись об оплате помечается отмененной (статус `CANCELED`).
# * Loyalty Service уменьшается счетчик бронирований. Так же возможно понижение статуса лояльности, если счетчик стал ниже
#   границы уровня.


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
