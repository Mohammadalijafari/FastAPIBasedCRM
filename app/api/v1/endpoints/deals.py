import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, CurrentUser, require_roles
from app.db.session import get_db
from app.models.organization import UserRole
from app.schemas.deal import DealCreate, DealUpdate, DealRead, DealStageMove
from app.services.deal_service import DealService

router = APIRouter(prefix="/deals", tags=["Deals"])


@router.post("", response_model=DealRead, status_code=201)
async def create_deal(
    data: DealCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DealService(db)
    return await service.create_deal(current_user.organization_id, data)


@router.get("/{deal_id}", response_model=DealRead)
async def get_deal(
    deal_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DealService(db)
    return await service.get_deal_or_404(current_user.organization_id, deal_id)


@router.patch("/{deal_id}", response_model=DealRead)
async def update_deal(
    deal_id: uuid.UUID,
    data: DealUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DealService(db)
    return await service.update_deal(current_user.organization_id, deal_id, data)


@router.post("/{deal_id}/move-stage", response_model=DealRead)
async def move_deal_stage(
    deal_id: uuid.UUID,
    data: DealStageMove,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DealService(db)
    return await service.move_stage(
        current_user.organization_id, deal_id, data.stage_id, current_user.id
    )


@router.delete(
    "/{deal_id}",
    status_code=204,
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.OWNER, UserRole.MANAGER))],
)
async def delete_deal(
    deal_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DealService(db)
    deal = await service.get_deal_or_404(current_user.organization_id, deal_id)
    await service.repo.soft_delete(deal)
    await db.commit()


@router.get("/pipeline/{pipeline_id}/board")
async def get_pipeline_board(
    pipeline_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """نمای کانبان: هر مرحله به همراه تعداد و مجموع ارزش معاملاتش"""
    service = DealService(db)
    return await service.get_pipeline_board(current_user.organization_id, pipeline_id)
