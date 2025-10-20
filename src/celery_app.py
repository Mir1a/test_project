# region -----External Imports-----
from celery import Celery
from celery.schedules import crontab
from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND
# endregion

celery_app = Celery(
    "app",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["src.tasks"]
)

# Основные настройки Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_hijack_root_logger=False,
)

# Настройки Celery Beat с задачей проверки сессий
# celery_app.conf.beat_schedule = {
#     # Задача проверки истекших сессий запускается каждые 30 минут
#     "cleanup-expired-sessions": {
#         "task": "src.tasks.cleanup_expired_sessions",
#         "schedule": crontab(minute="*/30"),
#     },
# }