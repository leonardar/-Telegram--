from os import getenv

from aiogram.contrib.fsm_storage.redis import RedisStorage2
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.jobstores.redis import RedisJobStore
from dotenv import load_dotenv
from google.oauth2 import service_account

load_dotenv()

BOT_TOKEN: str = getenv("BOT_TOKEN")

FROM_EMAIL: str = getenv("FROM_EMAIL")
PASSWORD: str = getenv("PASSWORD")

REDIS_HOST: str = getenv("REDIS_HOST")  # это для редиса
REDIS_PORT: str = getenv("REDIS_PORT")  # это для редиса

WEBHOOK_HOST: str = getenv("WEBHOOK_HOST")
WEBHOOK_PATH: str = getenv("WEBHOOK_PATH")
WEBAPP_HOST: str = getenv("WEBAPP_HOST")
WEBAPP_PORT: str = getenv("WEBAPP_PORT")
CREDENTIALS_PATH: str = getenv("CREDENTIALS_PATH")  # BigQuery
PROJECT: str = getenv("PROJECT")  # BigQuery
TIMEZONE: str = getenv("TIMEZONE")
CHAT_ID: int = int(getenv("CHAT_ID"))
TIME_TO_LIVE_DATA = getenv("TIME_TO_LIVE_DATA")
TIME_TO_LIVE_STATE = getenv("TIME_TO_LIVE_STATE")


cache = RedisStorage2(
    host=REDIS_HOST,
    port=int(REDIS_PORT),
    data_ttl=TIME_TO_LIVE_DATA,
    state_ttl=TIME_TO_LIVE_STATE
)
webhook_url = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

DEFAULT = "default"

jobstores = {
    DEFAULT: RedisJobStore(
        host=REDIS_HOST, port=REDIS_PORT
    )
}
executors = {DEFAULT: AsyncIOExecutor()}

credentials = service_account.Credentials.from_service_account_file(
    CREDENTIALS_PATH
)
