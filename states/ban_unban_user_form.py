from aiogram.dispatcher.filters.state import State, StatesGroup


class BanUserForm(StatesGroup):
    """
    Устанавливает команду для бана пользователя
    """
    ban_user_name = State()
    ban_confirm = State()


class UnBanUserForm(StatesGroup):
    """
    Устанавливает команду для разбана пользователя
    """
    unban_user_name = State()
    unban_confirm = State()
