from aiogram.dispatcher.filters.state import State, StatesGroup


class DetailsJobForm(StatesGroup):
    """
    Устанавливает команду для отправки комментария пользователем.
    """
    choose_kb = State()
