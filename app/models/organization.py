import uuid
import enum
from sqlalchemy import String, Enum as SAEnum, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.mixins import UUIDMixin, TimestampMixin


class Organization(Base, UUIDMixin, TimestampMixin):
    """
    هر مشتری از CRM (یک شرکت که از سیستم استفاده می‌کنه) یک Organization ست.
    این ریشه‌ی Multi-Tenancy کل سیستمه.
    """
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    plan: Mapped[str] = mapped_column(String(50), default="free")  # free/pro/enterprise

    users: Mapped[list["User"]] = relationship(back_populates="organization")


class UserRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    SALES_REP = "sales_rep"
    VIEWER = "viewer"


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), index=True
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole), default=UserRole.SALES_REP
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    organization: Mapped["Organization"] = relationship(back_populates="users")
