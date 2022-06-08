from datetime import date, datetime, timedelta

from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from data import REDIS_HOST, REDIS_PORT
from loader import db_manager
from services import is_day_off, send_graph_to_all, send_reminder_to_user

DEFAULT = "default"

jobstores = {DEFAULT: RedisJobStore(host=REDIS_HOST, port=REDIS_PORT)}
executors = {DEFAULT: AsyncIOExecutor()}

SCHEDULER = AsyncIOScheduler(jobstores=jobstores, executors=executors)


def set_scheduler_for_payday() -> None:
    """
    Формирует задачу планировщика на будний день.

    :return: None
    :rtype: NoneType
    """
    today: date = date.today()
    day: date = today
    while is_day_off(date=day):
        day += timedelta(days=1)
    SCHEDULER.add_job(send_graph_to_all, "date", run_date=f"{day} 17:12:10",
                      args=(today, ))


SCHEDULER.add_job(set_scheduler_for_payday, "cron", day="12", hour=17, minute=12)


def set_scheduler_event(
    user_id: int,
    event: str,
    event_date: str,
    event_time: str,
    comment: str,
) -> None:
    """
    Формирует задачу в планировщике и отдаёт напоминание на отправку
    пользователю в установленный срок.

    :param user_id: id пользователя
    :type user_id: int
    :param event: название события
    :type event: str
    :param event_date: дата события
    :type event_date: str
    :param event_time: время события
    :type event_time: str
    :param comment: комментарий пользователя
    :type comment: str

    :return: None
    :rtype: NoneType
    """

    text_for_scheduler: str = (
        f"Напоминание! Сегодня {event} в {event_time}: {comment}"
    )
    event_date: datetime = datetime.strptime(
        f"{event_date} {event_time}",
        "%d/%m/%Y %H:%M",
    )
    reminder_time = event_date - timedelta(minutes=30)
    created_at = datetime.now()

    if db_manager.send_task_to_bq(
        user_id=user_id,
        message_text=text_for_scheduler,
        planned_at=event_date,
        created_at=created_at,
    ):
        SCHEDULER.add_job(
            send_reminder_to_user,
            "date",
            run_date=reminder_time,
            args=[user_id, event_date],
        )
