import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class ContactBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = None
    job_title: str | None = None
    tags: list[str] = Field(default_factory=list)
    lead_source: str | None = None
    custom_fields: dict = Field(default_factory=dict)


class ContactCreate(ContactBase):
    company_id: uuid.UUID | None = None
    owner_id: uuid.UUID | None = None


class ContactUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    job_title: str | None = None
    company_id: uuid.UUID | None = None
    owner_id: uuid.UUID | None = None
    tags: list[str] | None = None
    custom_fields: dict | None = None


class ContactRead(ContactBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID | None
    owner_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
