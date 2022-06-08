"""
Модуль содержит обработчики, осуществляющие регистрацию новых
пользователей по электронной почте, посредством команды /reg
"""
import secrets

from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from data import cache
from handlers.search import is_data_valid
from loader import db_manager as manager
from loader import dp
from services import sending_message
from states import RegStates
from filters import IsGroupChat


async def tracker(message: Message, key: str, state: FSMContext) -> None:
    """
    Функция проверяет количество вводов email и паролей пользователем
    и в случае превышения лимита в 3 ед. создает в редисе запись
    с ключом 'black_list' со значением True.

    :param message: объект Message
    :type message : Message
    :param key: ключ пользователя
    :type key : str
    :param state: FSMContext
    :type state : объект FSMContext

    :return: None
    :rtype: NoneType
    """

    limit: int = 3
    chat_id: int = message.chat.id
    user_id: int = message.from_user.id
    data: dict = await cache.get_data(chat=chat_id, user=user_id)
    try:
        if data[key] >= limit:
            data['black_list'] = True
            manager.send_to_blacklist(user_id=user_id)
            data.pop('email_try', None)
            data.pop('password_try', None)
            await state.finish()
        else:
            data[key] += 1
    except KeyError:
        data[key] = 2
    await cache.update_data(chat=chat_id, user=user_id, data=data)


@dp.message_handler(IsGroupChat(), commands=["reg"], state="*")
async def process_reg_command(message: Message) -> None:
    """
    Функция проверяет зарегистрирован ли пользователь и
    отправляет приветственное сообщение

    :param message: объект Message
    :type message : Message

    :return: None
    :rtype: NoneType
    """

    check_user = await manager.check_user(message=message)
    if check_user:
        sub_text = ""
        if message.from_user.username is not None:
            sub_text += f", {message.from_user.username}"

        registered_info = f"Вы уже зарегистрированы{sub_text}.\n" \
                          f"Нажмите /help и выберите команду."

        await message.answer(text=registered_info)
    else:
        await message.answer(
            text=("Для прохождения регистрации введите адрес рабочей почты в"
                  " домене @ylab.io :")
        )
        await RegStates.EMAIL_MESSAGE.set()


@dp.message_handler(state=RegStates.EMAIL_MESSAGE)
async def send_email_message(message: Message, state: FSMContext) -> None:
    """
    Функция отправляет на почту код подтверждения
    пользователю и сообщение в чат для его ввода

    :param message: объект Message
    :type message : Message
    :param state: объект FSMContext
    :type state : FSMContext

    :return: None
    :rtype: NoneType
    """

    await tracker(message=message, key='email_try', state=state)

    secret_key: str = secrets.token_urlsafe(8)
    chat_id: int = message.chat.id
    user_id: int = message.from_user.id
    target_email: str = message.text

    await cache.update_data(
        chat=chat_id,
        user=user_id,
        data={'secret_key': secret_key}
    )
    if is_data_valid(data=target_email, case='email'):
        if not await manager.check_auth(message=message):
            await manager.registration(message=message)
        await sending_message(to_email=target_email, secret_key=secret_key)

        await message.answer(
            text="На вашу почту отправлен ключ подтверждения, введите его:"
        )
        await cache.update_data(
            chat=chat_id,
            user=user_id,
            data={'email': target_email}
        )
        await RegStates.KEY_MESSAGE.set()
    else:
        await message.answer(
            text="Проверьте правильность введенного адреса."
        )


@dp.message_handler(state=RegStates.KEY_MESSAGE)
async def input_key_message(message: Message, state: FSMContext) -> None:
    """
    Функция проверяет введённый ключ и отправляет
    пользователю сообщение с результатом проверки

    :param message: объект Message
    :type message : Message
    :param state: объект FSMContext
    :type state : FSMContext

    :return: None
    :rtype: NoneType
    """

    await tracker(message=message, key='password_try', state=state)
    secret_key: dict = await cache.get_data(
        chat=message.chat.id,
        user=message.from_user.id
    )
    if secret_key.get('secret_key') != message.text:
        await message.answer(
            text="Неверный пароль. Пожалуйста, повторите попытку:"
        )
    else:
        sub_text = ""

        if message.from_user.username is not None:
            sub_text += f", {message.from_user.username}"

        email = secret_key.get('email')
        await manager.authentication(message, email)

        await message.answer(
            text=f"Вы ввели верный ключ! Добро пожаловать в чат-бот "
                 f"компании Ylab{sub_text}.\n"
                 "Для получения списка доступных команд нажмите /help."
        )
        await state.finish()
