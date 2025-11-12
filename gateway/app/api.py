from fastapi import APIRouter, Depends, Header, Body
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
    response_model=List(ReservationResponse),
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
             response_model=CreateReservationRequest,
             summary="Забронировать отель")
def create_reservation(x_user_name: str = Header(..., alias="X-User-Name"),
                       body: CreateReservationRequest = Body(...)):
    pass


#     post:
#       summary: Забронировать отель
#       tags:
#         - Gateway API
#       parameters:
#         - name: X-User-Name
#           in: header
#           description: Имя пользователя
#           required: true
#           schema:
#             type: string
#       requestBody:
#         content:
#           application/json:
#             schema:
#               $ref: "#/components/schemas/CreateReservationRequest"
#       responses:
#         "200":
#           description: Информация о бронировании
#           content:
#             application/json:
#               schema:
#                 $ref: "#/components/schemas/CreateReservationResponse"
#         "400":
#           description: Ошибка валидации данных
#           content:
#             application/json:
#               schema:
#                 $ref: "#/components/schemas/ValidationErrorResponse"
