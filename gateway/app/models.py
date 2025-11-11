from typing import List
from uuid import UUID
from enum import Enum
from pydantic import BaseModel


class ReservationStatus(str, Enum):
    PAID = "PAID"
    RESERVED = "RESERVED"
    CANCELED = "CANCELED"


class PaymentStatus(str, Enum):
    PAID = "PAID"
    REVERSED = "REVERSED"
    CANCELED = "CANCELED"


class LoyaltyLevel(str, Enum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"


class PaginationResponse(BaseModel):
    page: int
    pageSize: int
    totalElements: int
    items: List[HotelResponse]


class HotelResponse(BaseModel):
    hotelUid: UUID
    name: str
    country: str
    city: str
    address: str
    stars: int
    price: int


class HotelInfo(BaseModel):
    hotelUid: UUID
    name: str
    fullAddress: str
    stars: int


class UserInfoResponse(BaseModel):
    reservations: List[ReservationResponse]
    loyalty: LoyaltyInfoResponse


class ReservationResponse(BaseModel):
    reservationUid: UUID
    hotel: HotelInfo
    startDate: str
    endDate: str
    status: ReservationStatus
    payment: PaymentInfo


class CreateReservationRequest(BaseModel):
    hotelUid: UUID
    startDate: str
    endDate: str


class CreateReservationResponse(BaseModel):
    reservationUid: UUID
    hotelUid: UUID
    startDate: str
    endDate: str
    discount: int
    status: ReservationStatus
    payment: PaymentInfo


class PaymentInfo(BaseModel):
    status: PaymentStatus
    price: int


class LoyaltyInfoResponse(BaseModel):
    status: LoyaltyLevel
    discount: int
    reservationCount: int | None = None


class ErrorDescription(BaseModel):
    field: str
    error: str


class ErrorResponse(BaseModel):
    message: str


class ValidationErrorResponse(BaseModel):
    message: str
    errors: List[ErrorDescription]
