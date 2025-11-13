from typing import List
from uuid import UUID
from enum import Enum
from datetime import date
from pydantic import BaseModel, Field


class ReservationStatus(str, Enum):
    PAID = "PAID"
    RESERVED = "RESERVED"
    CANCELED = "CANCELED"


class PaymentStatus(str, Enum):
    PAID = "PAID"
    RESERVED = "RESERVED"
    CANCELED = "CANCELED"


class LoyaltyLevel(str, Enum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"


class HotelResponse(BaseModel):
    hotelUid: UUID
    name: str
    country: str
    city: str
    address: str
    stars: int
    price: int


class PaginationResponse(BaseModel):
    page: int
    pageSize: int
    totalElements: int
    items: List[HotelResponse]


class HotelInfo(BaseModel):
    hotelUid: UUID
    name: str
    fullAddress: str
    stars: int


class PaymentInfo(BaseModel):
    status: PaymentStatus
    price: int


class ReservationResponse(BaseModel):
    reservationUid: UUID
    hotel: HotelInfo
    startDate: date
    endDate: date
    status: ReservationStatus
    payment: PaymentInfo


class LoyaltyInfoResponse(BaseModel):
    status: LoyaltyLevel
    discount: int
    reservationCount: int | None = None


class UserInfoResponse(BaseModel):
    reservations: List[ReservationResponse]
    loyalty: LoyaltyInfoResponse


class CreateReservationRequest(BaseModel):
    hotelUid: UUID
    startDate: date
    endDate: date


class CreateReservationResponse(BaseModel):
    reservationUid: UUID
    hotelUid: UUID
    startDate: date
    endDate: date
    discount: int
    status: ReservationStatus
    payment: PaymentInfo


class ErrorDescription(BaseModel):
    field: str | None = None
    error: str


class ErrorResponse(BaseModel):
    message: str


class ValidationErrorResponse(BaseModel):
    message: str
    errors: List[ErrorDescription]


class GetHotelsQuery(BaseModel):
    page: int = Field(0, ge=0)
    size: int = Field(1, ge=1, le=100)
