from aiogram.dispatcher.filters.state import State, StatesGroup


class BotStates(StatesGroup):
    """
    Класс описывает состояния функций.
    """
    STATE_0 = State()
    STATE_1 = State()
    STATE_2 = State()
