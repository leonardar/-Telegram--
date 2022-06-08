from aiogram.types import Message

from loader import dp
from filters import IsGroupChat, IsRegistered


@dp.message_handler(IsGroupChat())
async def text_handler(message: Message) -> None:
    """
    Отправляет приветственное сообщение
    пользователю

    :param message: объект Message
    :type message: Message

    :return: None
    :rtype: NoneType
    """
    sub_text = ""

    if message.from_user.username is not None:
        sub_text += f", {message.from_user.username}"

    welcome_info = f"Нужна помощь{sub_text}?\n"

    registered = await IsRegistered().check(message)

    if not registered:
        welcome_info += "Для регистрации в боте введите команду /reg.\n"
    else:
        welcome_info += "Для получения списка доступных команд нажмите /help."
    await message.answer(welcome_info)
