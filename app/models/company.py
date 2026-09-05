import uuid
from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin, TenantMixin


class Company(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin, TenantMixin):
    """شرکت/سازمان مشتری (Account) — نه سازمان صاحب CRM"""
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(255), index=True)
    domain: Mapped[str | None] = mapped_column(String(255), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    size: Mapped[str | None] = mapped_column(String(50), nullable=True)  # 1-10, 11-50, ...
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    custom_fields: Mapped[dict] = mapped_column(JSONB, default=dict)

    contacts: Mapped[list["Contact"]] = relationship(back_populates="company")
    deals: Mapped[list["Deal"]] = relationship(back_populates="company")
