from aiogram.dispatcher.filters.state import State, StatesGroup


class AdminMessageStates(StatesGroup):
    """
    Класс описывает состояния функций.
    """
    admin_message_text = State()
    admin_message_confirm = State()
