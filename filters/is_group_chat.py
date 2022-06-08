from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message


class IsGroupChat(BoundFilter):
    """
    Фильтр проверяет из какого канала пришло сообщениеЖ из личного или
    группового.
    """
    async def check(self, message: Message) -> bool:
        """
        Возвращает True, когда канал является лисным
        False: когда сообщение из группового канала
        """
        user_id: int = message.from_user.id
        chat_id: int = message.chat.id
        return user_id == chat_id
