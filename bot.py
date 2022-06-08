import logging

from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

import data
import filters
import handlers
import middlewares
from data import config
from loader import bot, dp
from services.set_scheduler import SCHEDULER
from utils import get_logger

logger = get_logger('bot_log', logging.INFO)


# async def on_startup(dp: Dispatcher):
#     SCHEDULER.start()
#     await bot.set_webhook(data.webhook_url)


if __name__ == "__main__":
    SCHEDULER.start()
    executor.start_polling(dp, skip_updates=True)
    # executor.start_webhook(dispatcher=dp,
    #                        webhook_path=config.WEBHOOK_PATH,
    #                        on_startup=on_startup,
    #                        skip_updates=True,
    #                        host=config.WEBAPP_HOST,
    #                        port=config.WEBAPP_PORT)
