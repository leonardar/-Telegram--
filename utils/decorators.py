from .logger import get_logger

logger = get_logger(__name__)


def bq_error_handler(func: callable) -> callable:
    """
    Декоратор. Возвращает пользователю ошибку в чат.

    :param func: функция, которая будет обернута
    :type func: callable

    :rtype: callable
    """

    async def wrapper(*args, **kwargs) -> None:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(e)
            await kwargs["message"].answer(
                text=("Произошла непредвиденная ошибка, "
                      "свяжитесь с администратором!")
            )
            await kwargs["state"].finish()
    return wrapper
