from aiogram.dispatcher.filters.state import State, StatesGroup


class SearchStates(StatesGroup):
    """
    Класс описывает состояния обработчиков, отвечающих за поиск пользователей.
    """
    SEARCH_START = State()
    SEARCH_PROCESS = State()
    AFT_SEAR = State()
