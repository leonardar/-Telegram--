from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message

from data import cache
from loader import db_manager


class UserRoleFilter(BoundFilter):
    """
    Функция проверяет является ли пользователь администратором.
    Сначала она проверяет есть ли role в редиc, если нет, то обращается
    в bigquery, получает значение, и пишет его в редисовский кэш.
    """
    def __init__(self, role: str):
        self.role = role

    async def check(self, message: Message) -> bool:
        user_id = message.from_user.id
        chat_id = message.chat.id
        try:
            data = await cache.get_data(
                user=user_id,
                chat=chat_id
            )
            is_reg_flag = data[self.role]
            return is_reg_flag

        except KeyError:
            correct = await db_manager.check_user_role(
                message=message,
                role=self.role
            )
            if correct in [True, False]:
                await cache.update_data(
                    user=user_id,
                    chat=chat_id,
                    data={self.role: correct},
                )
                return correct
            else:
                await message.answer("Произошла непредвиденная ошибка, "
                                     "свяжитесь с администратором.")
                return False
