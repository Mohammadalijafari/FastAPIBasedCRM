import uuid
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class DealBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    amount: Decimal = Field(default=0, ge=0)
    currency: str = Field(default="USD", max_length=10)
    expected_close_date: date | None = None
    custom_fields: dict = Field(default_factory=dict)


class DealCreate(DealBase):
    pipeline_id: uuid.UUID
    stage_id: uuid.UUID
    company_id: uuid.UUID | None = None
    primary_contact_id: uuid.UUID | None = None
    owner_id: uuid.UUID | None = None


class DealUpdate(BaseModel):
    title: str | None = None
    amount: Decimal | None = Field(default=None, ge=0)
    expected_close_date: date | None = None
    owner_id: uuid.UUID | None = None
    custom_fields: dict | None = None


class DealStageMove(BaseModel):
    stage_id: uuid.UUID


class DealRead(DealBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    pipeline_id: uuid.UUID
    stage_id: uuid.UUID
    company_id: uuid.UUID | None
    primary_contact_id: uuid.UUID | None
    owner_id: uuid.UUID | None
    closed_at: date | None
    lost_reason: str | None
    created_at: datetime
    updated_at: datetime


class PipelineStageSummary(BaseModel):
    id: uuid.UUID
    name: str
    order: int
    deal_count: int
    total_amount: Decimal


class PaginatedResponse(BaseModel):
    items: list[DealRead]
    total: int
    page: int
    page_size: int
