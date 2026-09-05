"""
وابستگی‌های مشترک همه‌ی endpoint ها:
  - گرفتن کاربر جاری از روی JWT
  - جداسازی Tenant (خیلی مهم: تضمین می‌کنه کاربر فقط داده‌ی سازمان خودش رو ببینه)
  - کنترل دسترسی بر اساس نقش (RBAC)
"""
import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.session import get_db
from app.models.organization import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class CurrentUser:
    """موجودیت سبک‌وزن که از توکن استخراج می‌شه - برای هر ریکوئست یک‌بار دیتابیس رو نمی‌زنیم"""

    def __init__(self, id: uuid.UUID, organization_id: uuid.UUID, role: str):
        self.id = id
        self.organization_id = organization_id
        self.role = role


async def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> CurrentUser:
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return CurrentUser(
        id=uuid.UUID(payload["sub"]),
        organization_id=uuid.UUID(payload["org"]),
        role=payload["role"],
    )


def require_roles(*allowed_roles: UserRole):
    """
    Dependency Factory برای RBAC:
        @router.delete(..., dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.OWNER))])
    """

    async def checker(current_user: CurrentUser = Depends(get_current_user)):
        if current_user.role not in [r.value for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="دسترسی کافی برای این عملیات ندارید",
            )
        return current_user

    return checker
