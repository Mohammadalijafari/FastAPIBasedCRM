"""
Repository Pattern: لایه‌ی دسترسی به داده کاملاً از منطق کسب‌وکار (Service) جداست.
این کار باعث می‌شه:
  1) تست‌نویسی راحت‌تر بشه (میشه Repository رو mock کرد)
  2) اگه روزی خواستیم ORM عوض کنیم، فقط این لایه تغییر می‌کنه
  3) Query های پیچیده یک‌جا و قابل بازبینی باشن
"""
import uuid
from typing import Generic, TypeVar, Type, Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: uuid.UUID) -> ModelType | None:
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
        **filters,
    ) -> Sequence[ModelType]:
        stmt = select(self.model).where(
            self.model.organization_id == organization_id
        )
        # فیلترهای پویا (مثلاً owner_id=..., stage_id=...)
        for field, value in filters.items():
            if value is not None and hasattr(self.model, field):
                stmt = stmt.where(getattr(self.model, field) == value)
        # اگه مدل soft-delete داره، حذف‌شده‌ها رو مخفی کن
        if hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted == False)  # noqa: E712
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def count(self, organization_id: uuid.UUID, **filters) -> int:
        stmt = select(func.count()).select_from(self.model).where(
            self.model.organization_id == organization_id
        )
        for field, value in filters.items():
            if value is not None and hasattr(self.model, field):
                stmt = stmt.where(getattr(self.model, field) == value)
        if hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted == False)  # noqa: E712
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def create(self, obj_in: dict) -> ModelType:
        obj = self.model(**obj_in)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, db_obj: ModelType, obj_in: dict) -> ModelType:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def soft_delete(self, db_obj: ModelType) -> None:
        if hasattr(db_obj, "is_deleted"):
            from datetime import datetime, timezone
            db_obj.is_deleted = True
            db_obj.deleted_at = datetime.now(timezone.utc)
            await self.db.flush()
        else:
            await self.db.delete(db_obj)
            await self.db.flush()
