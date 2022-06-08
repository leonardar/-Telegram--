import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from data import cache
from filters import UserRoleFilter, IsGroupChat
from loader import db_manager, dp
from states import UnBanUserForm
import keyboards as key


@dp.message_handler(
    UserRoleFilter(role='admin'),
    IsGroupChat(),
    commands=["unban_user"],
    state="*"
)
async def unban_user_start(message: Message) -> None:
    """
    Перехватывает команду "/unban_user"

    :param message: объект Message
    :type message : Message

    :return: None
    :rtype: NoneType
    """

    await UnBanUserForm.unban_user_name.set()
    await message.reply("Укажите id пользователя: ")


@dp.message_handler(state=UnBanUserForm.unban_user_name)
async def unban_user_name(message: Message, state: FSMContext) -> None:
    """
    Записывает в state.proxy id пользователя

    :param message: объект Message
    :type message : Message
    :param state: FSMContext
    :type state : объект FSMContext

    :return: None
    :rtype: NoneType
    """
    result = db_manager.get_user_id_list(confirm_flag=False)
    list_of_users = [row[0] for row in result]
    try:
        if int(message.text) in list_of_users:
            async with state.proxy() as data:
                data['user_id'] = message.text
            await message.answer(
                "Подтвердите, вы точно хотите разблокировать этого "
                "пользователя?",
                reply_markup=key.yn_kb
            )
            await UnBanUserForm.next()
        else:
            await message.answer('Пользователь не найден. Повторите попытку: ')
    except ValueError:
        await message.answer('Неверный ввод. Укажите id пользователя: ')


@dp.callback_query_handler(
    state=UnBanUserForm.unban_confirm,
    text=key.confirm.text
)
async def unban_user_confirm(
        callback_query: CallbackQuery,
        state: FSMContext
) -> None:
    """
    В зависимости от ответа отправляет запрос в бд

    :param callback_query: объект CallbackQuery
    :type callback_query : CallbackQuery
    :param state: FSMContext
    :type state : объект FSMContext

    :return: None
    :rtype: NoneType
    """

    async with state.proxy() as data:
        user_id = data['user_id']
    try:
        db_manager.remove_from_blacklist(user_id=user_id)
        await cache.update_data(
            user=user_id,
            data={'black_list': False}
        )
        await callback_query.message.answer('Пользователь разблокирован.')
    except Exception as e:
        logging.error(e)
        await callback_query.answer('Произошла ошибка!')
    await callback_query.message.delete()
    await state.finish()


@dp.callback_query_handler(
    state=UnBanUserForm.unban_confirm,
    text=key.dn_confirm.text
)
async def unban_user_cancel(
        callback_query: CallbackQuery,
        state: FSMContext
) -> None:
    """
    В зависимости от ответа отправляет запрос в бд

    :param callback_query: объект CallbackQuery
    :type callback_query : CallbackQuery
    :param state: FSMContext
    :type state : объект FSMContext

    :return: None
    :rtype: NoneType
    """
    await callback_query.message.delete()
    await callback_query.message.answer('Действие отменено.')
    await state.finish()
