import uuid
from sqlalchemy import String, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin, TenantMixin


class Contact(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin, TenantMixin):
    __tablename__ = "contacts"
    __table_args__ = (
        Index("ix_contacts_org_email", "organization_id", "email"),
    )

    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    job_title: Mapped[str | None] = mapped_column(String(150), nullable=True)
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True, index=True
    )
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    lead_source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    custom_fields: Mapped[dict] = mapped_column(JSONB, default=dict)

    company: Mapped["Company"] = relationship(back_populates="contacts")
    deals: Mapped[list["Deal"]] = relationship(back_populates="primary_contact")
    activities: Mapped[list["Activity"]] = relationship(back_populates="contact")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
