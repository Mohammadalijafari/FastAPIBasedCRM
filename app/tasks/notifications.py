"""
تسک‌های Async با Celery.
کارهایی مثل ارسال ایمیل یا نوتیفیکیشن نباید ریسپانس API رو کند کنن،
پس به صف Redis می‌رن و یک Worker جداگانه پردازش‌شون می‌کنه.
"""
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "crm_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    task_track_started=True,
    task_time_limit=30,
)


@celery_app.task(name="notify_deal_stage_changed", bind=True, max_retries=3)
def notify_deal_stage_changed(self, deal_id: str, stage_id: str):
    """
    نوتیفای کردن اعضای مرتبط وقتی معامله جابه‌جا می‌شه.
    در پروداکشن اینجا به سرویس ایمیل/Slack/WebSocket وصل می‌شه.
    """
    try:
        # TODO: اتصال به سرویس ایمیل یا WebSocket برای آپدیت لحظه‌ای UI
        print(f"[notify] Deal {deal_id} moved to stage {stage_id}")
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


@celery_app.task(name="send_daily_activity_digest")
def send_daily_activity_digest():
    """
    تسک زمان‌بندی‌شده (Celery Beat) که هر روز صبح خلاصه‌ی فعالیت‌های
    امروز رو برای هر کاربر ایمیل می‌کنه.
    """
    # TODO: query فعالیت‌های امروز به تفکیک assigned_to و ارسال ایمیل
    pass
