"""
میکسین‌های مشترک بین همه‌ی مدل‌ها
Multi-tenancy، Soft Delete و Audit Trail از همینجا اضافه می‌شن
"""
import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SoftDeleteMixin:
    """
    به‌جای حذف فیزیکی رکورد، فقط علامت‌گذاری می‌کنیم.
    برای CRM حیاتیه چون از دست دادن تاریخچه‌ی مشتری قابل جبران نیست.
    """
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class TenantMixin:
    """
    پشتیبانی از Multi-Tenancy (چند سازمان روی یک دیتابیس).
    هر رکورد به یک Organization/Workspace متصله.
    """
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), index=True
    )
