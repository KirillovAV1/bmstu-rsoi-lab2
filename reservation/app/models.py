from uuid import UUID
from pydantic import BaseModel, Field


class CreateReservationRequest(BaseModel):
    hotelUid: UUID
    startDate: str
    endDate: str


class GetHotelsQuery(BaseModel):
    page: int = Field(0, ge=0)
    size: int = Field(1, ge=1, le=100)
