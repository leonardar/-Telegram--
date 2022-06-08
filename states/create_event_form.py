from aiogram.dispatcher.filters.state import State, StatesGroup


class CreateEventForm(StatesGroup):
    """
    Состояния для команды /create_event.
    """
    event_name = State()
    event_date = State()
    event_time = State()
    event_comment = State()
    event_confirm = State()
    event_text = State()
