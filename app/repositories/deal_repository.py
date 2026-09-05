import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.deal import Deal, DealStageHistory
from app.models.pipeline import Stage


class DealRepository(BaseRepository[Deal]):
    def __init__(self, db: AsyncSession):
        super().__init__(Deal, db)

    async def get_pipeline_summary(
        self, organization_id: uuid.UUID, pipeline_id: uuid.UUID
    ) -> list[dict]:
        """
        برای نمای کانبان: تعداد و مجموع ارزش معاملات به تفکیک مرحله.
        این کوئری روی دیتابیس انجام می‌شه، نه در پایتون، تا سریع بمونه
        حتی وقتی هزاران معامله وجود داره.
        """
        stmt = (
            select(
                Stage.id,
                Stage.name,
                Stage.order,
                func.count(Deal.id).label("deal_count"),
                func.coalesce(func.sum(Deal.amount), 0).label("total_amount"),
            )
            .join(Deal, Deal.stage_id == Stage.id, isouter=True)
            .where(
                Stage.pipeline_id == pipeline_id,
                (Deal.organization_id == organization_id) | (Deal.id.is_(None)),
                (Deal.is_deleted == False) | (Deal.id.is_(None)),  # noqa: E712
            )
            .group_by(Stage.id, Stage.name, Stage.order)
            .order_by(Stage.order)
        )
        result = await self.db.execute(stmt)
        return [dict(row._mapping) for row in result]

    async def move_stage(
        self,
        deal: Deal,
        new_stage_id: uuid.UUID,
        changed_by_id: uuid.UUID | None,
    ) -> Deal:
        """
        جابه‌جایی معامله بین مراحل + ثبت تاریخچه.
        این تاریخچه برای گزارش 'میانگین مدت‌زمان در هر مرحله' استفاده می‌شه.
        """
        history = DealStageHistory(
            deal_id=deal.id,
            from_stage_id=deal.stage_id,
            to_stage_id=new_stage_id,
            changed_by_id=changed_by_id,
        )
        self.db.add(history)
        deal.stage_id = new_stage_id
        await self.db.flush()
        await self.db.refresh(deal)
        return deal
