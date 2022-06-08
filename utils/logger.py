import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional


def get_logger(logger_name: str,
               level: Optional[int] = logging.INFO) -> logging.Logger:
    log_format = '%(asctime)s %(name)-30s %(levelname)-8s %(message)s'
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    os.makedirs('logs/', exist_ok=True)
    handler = RotatingFileHandler(
        f'logs/{logger_name}.log', maxBytes=10 * 1024 * 1024,
        backupCount=5, encoding='utf-8',
    )
    handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(handler)

    return logger
