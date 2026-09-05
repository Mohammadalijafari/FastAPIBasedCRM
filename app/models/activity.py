import uuid
import enum
from datetime import datetime
from sqlalchemy import String, ForeignKey, Text, Enum as SAEnum, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.mixins import UUIDMixin, TimestampMixin, TenantMixin


class ActivityType(str, enum.Enum):
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    TASK = "task"
    NOTE = "note"


class Activity(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """
    فعالیت‌ها و تسک‌ها — می‌تونن به Contact و/یا Deal متصل باشن.
    تایم‌لاین این جدول همون چیزیه که در صفحه‌ی هر مشتری به کاربر نشون داده می‌شه.
    """
    __tablename__ = "activities"

    type: Mapped[ActivityType] = mapped_column(SAEnum(ActivityType))
    subject: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    contact_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=True, index=True
    )
    deal_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("deals.id"), nullable=True, index=True
    )
    assigned_to_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    contact: Mapped["Contact"] = relationship(back_populates="activities")
    deal: Mapped["Deal"] = relationship(back_populates="activities")
