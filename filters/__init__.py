from aiogram import Dispatcher

from .is_reg import IsRegistered
from .user_role_filter import UserRoleFilter
from .is_group_chat import IsGroupChat


def setup(dp: Dispatcher) -> None:
    dp.filters_factory.bind(IsRegistered, event_handlers=dp.message_handlers)
    dp.filters_factory.bind(UserRoleFilter, event_handlers=dp.message_handlers)
    dp.filters_factory.bind(IsGroupChat, event_handlers=dp.message_handlers)
