
from aiogram.dispatcher.filters import BoundFilter

from data import cache
from loader import db_manager


class IsRegistered(BoundFilter):
    """
    Фильтр проверяет зарегистрирован ли пользователь.
    Сначала она обращается в редис, и если записи о регистрации там нет,
    То обращается в bigquery, получает значение, и пишет его в редисовский кэш.
    """
    async def check(self, obj) -> bool:

        try:
            user_id = obj.from_user.id
            chat_id = obj.chat.id

            data = await cache.get_data(
                user=user_id,
                chat=chat_id
            )
            is_reg_flag = data['reg_status']
            return is_reg_flag

        except (KeyError, AttributeError) as e:

            user_id = obj.from_user.id
            if type(e) is AttributeError:
                chat_id = obj.message.chat.id
            else:
                chat_id = obj.chat.id

            is_reg = await db_manager.check_user(message=obj)
            if is_reg:
                await cache.update_data(
                    user=user_id,
                    chat=chat_id,
                    data={'reg_status': True}
                )
                return True
            else:
                await cache.update_data(
                    user=user_id,
                    chat=chat_id,
                    data={'reg_status': False}
                )
                return False
