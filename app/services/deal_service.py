"""
Service Layer: منطق کسب‌وکار اینجا زندگی می‌کنه — نه در endpoint، نه در repository.
Endpoint فقط HTTP رو مدیریت می‌کنه، Repository فقط SQL رو.
قوانینی مثل «معامله‌ی بسته‌شده رو نمی‌شه جابه‌جا کرد» اینجا پیاده می‌شه.
"""
import uuid
from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deal import Deal
from app.models.pipeline import Stage
from app.repositories.deal_repository import DealRepository
from app.schemas.deal import DealCreate, DealUpdate
from app.tasks.notifications import notify_deal_stage_changed


class DealService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = DealRepository(db)

    async def create_deal(
        self, organization_id: uuid.UUID, data: DealCreate
    ) -> Deal:
        deal = await self.repo.create(
            {**data.model_dump(), "organization_id": organization_id}
        )
        await self.db.commit()
        return deal

    async def get_deal_or_404(
        self, organization_id: uuid.UUID, deal_id: uuid.UUID
    ) -> Deal:
        deal = await self.repo.get(deal_id)
        if not deal or deal.organization_id != organization_id or deal.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found"
            )
        return deal

    async def update_deal(
        self, organization_id: uuid.UUID, deal_id: uuid.UUID, data: DealUpdate
    ) -> Deal:
        deal = await self.get_deal_or_404(organization_id, deal_id)
        if deal.closed_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="نمی‌توان معامله‌ی بسته‌شده را ویرایش کرد",
            )
        updated = await self.repo.update(
            deal, data.model_dump(exclude_unset=True)
        )
        await self.db.commit()
        return updated

    async def move_stage(
        self,
        organization_id: uuid.UUID,
        deal_id: uuid.UUID,
        new_stage_id: uuid.UUID,
        actor_id: uuid.UUID,
    ) -> Deal:
        deal = await self.get_deal_or_404(organization_id, deal_id)

        if deal.closed_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="معامله قبلاً بسته شده و قابل جابه‌جایی نیست",
            )

        new_stage = await self.db.get(Stage, new_stage_id)
        if not new_stage or new_stage.pipeline_id != deal.pipeline_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="مرحله‌ی نامعتبر یا متعلق به پایپ‌لاین دیگر",
            )

        updated = await self.repo.move_stage(deal, new_stage_id, actor_id)

        # اگه مرحله‌ی برد یا باخت باشه، معامله بسته می‌شه
        if new_stage.is_won_stage or new_stage.is_lost_stage:
            updated.closed_at = date.today()

        await self.db.commit()

        # ارسال نوتیفیکیشن به‌صورت async (Celery) تا ریسپانس کند نشه
        notify_deal_stage_changed.delay(str(deal.id), str(new_stage_id))

        return updated

    async def get_pipeline_board(
        self, organization_id: uuid.UUID, pipeline_id: uuid.UUID
    ) -> list[dict]:
        return await self.repo.get_pipeline_summary(organization_id, pipeline_id)
