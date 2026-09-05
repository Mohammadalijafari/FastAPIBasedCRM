"""
نمونه تست برای منطق کسب‌وکار حیاتی: قفل شدن معامله‌ی بسته‌شده.
این نوع تست‌ها مهم‌ترین بخش پروژه‌ن چون قوانین کسب‌وکار رو مستند و محافظت می‌کنن.

اجرا: pytest tests/ -v
(نیازمند دیتابیس تست PostgreSQL - جزئیات در README)
"""
import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from datetime import date

from app.services.deal_service import DealService
from app.schemas.deal import DealUpdate


@pytest.mark.asyncio
async def test_cannot_update_closed_deal():
    """معامله‌ی بسته‌شده نباید قابل ویرایش باشه - یک قانون کسب‌وکار حیاتی"""
    db = AsyncMock()
    service = DealService(db)

    org_id = uuid.uuid4()
    deal_id = uuid.uuid4()

    closed_deal = MagicMock()
    closed_deal.organization_id = org_id
    closed_deal.is_deleted = False
    closed_deal.closed_at = date.today()  # معامله بسته شده

    service.repo.get = AsyncMock(return_value=closed_deal)

    with pytest.raises(HTTPException) as exc_info:
        await service.update_deal(org_id, deal_id, DealUpdate(title="New Title"))

    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_get_deal_wrong_organization_raises_404():
    """جداسازی tenant: کاربر سازمان A نباید بتونه دیل سازمان B رو ببینه"""
    db = AsyncMock()
    service = DealService(db)

    deal = MagicMock()
    deal.organization_id = uuid.uuid4()  # سازمان دیگه
    deal.is_deleted = False
    service.repo.get = AsyncMock(return_value=deal)

    with pytest.raises(HTTPException) as exc_info:
        await service.get_deal_or_404(uuid.uuid4(), uuid.uuid4())

    assert exc_info.value.status_code == 404
