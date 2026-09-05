import uuid
from sqlalchemy import String, ForeignKey, Integer, Numeric, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.mixins import UUIDMixin, TimestampMixin, TenantMixin


class Pipeline(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """
    هر Pipeline یک فرآیند فروش جداست (مثلاً 'فروش مستقیم' یا 'تمدید قرارداد').
    یک سازمان می‌تونه چند Pipeline موازی داشته باشه.
    """
    __tablename__ = "pipelines"

    name: Mapped[str] = mapped_column(String(150))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    stages: Mapped[list["Stage"]] = relationship(
        back_populates="pipeline", order_by="Stage.order"
    )


class Stage(Base, UUIDMixin, TimestampMixin):
    """
    مراحل داخل یک Pipeline (مثلاً: Lead -> Qualified -> Proposal -> Won/Lost)
    ترتیب با فیلد order مشخص می‌شه که برای UI کانبان لازمه.
    """
    __tablename__ = "stages"

    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pipelines.id"), index=True
    )
    name: Mapped[str] = mapped_column(String(100))
    order: Mapped[int] = mapped_column(Integer)
    # درصد احتمال بستن معامله در این مرحله (برای forecast)
    win_probability: Mapped[int] = mapped_column(Integer, default=0)
    is_won_stage: Mapped[bool] = mapped_column(Boolean, default=False)
    is_lost_stage: Mapped[bool] = mapped_column(Boolean, default=False)

    pipeline: Mapped["Pipeline"] = relationship(back_populates="stages")
