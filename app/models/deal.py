import uuid
from datetime import date, datetime
from sqlalchemy import String, ForeignKey, Numeric, Date, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin, TenantMixin


class Deal(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin, TenantMixin):
    """معامله/فرصت فروش — قلب تپنده‌ی CRM"""
    __tablename__ = "deals"

    title: Mapped[str] = mapped_column(String(255))
    amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    currency: Mapped[str] = mapped_column(String(10), default="USD")

    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pipelines.id"), index=True
    )
    stage_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stages.id"), index=True
    )
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True
    )
    primary_contact_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=True
    )
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    expected_close_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    closed_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    lost_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    custom_fields: Mapped[dict] = mapped_column(JSONB, default=dict)

    company: Mapped["Company"] = relationship(back_populates="deals")
    primary_contact: Mapped["Contact"] = relationship(back_populates="deals")
    stage: Mapped["Stage"] = relationship()
    activities: Mapped[list["Activity"]] = relationship(back_populates="deal")

    # این جدول به‌صورت append-only نگه داشته می‌شه تا تاریخچه‌ی حرکت روی
    # پایپ‌لاین برای گزارش‌گیری (مثلاً میانگین زمان توقف در هر مرحله) حفظ بشه
    stage_history: Mapped[list["DealStageHistory"]] = relationship(
        back_populates="deal", order_by="DealStageHistory.changed_at"
    )


class DealStageHistory(Base, UUIDMixin):
    __tablename__ = "deal_stage_history"

    deal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("deals.id"), index=True
    )
    from_stage_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stages.id"), nullable=True
    )
    to_stage_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stages.id")
    )
    changed_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    changed_at: Mapped["datetime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    deal: Mapped["Deal"] = relationship(back_populates="stage_history")
