import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from data import cache
from filters import UserRoleFilter, IsGroupChat
from loader import db_manager, dp
from states import BanUserForm
import keyboards as key


@dp.message_handler(
    UserRoleFilter(role='admin'),
    IsGroupChat(),
    commands=["ban_user"],
    state="*"
)
async def ban_user_start(message: Message) -> None:
    """
    Перехватывает команду "/ban_user"

    :param message: объект Message
    :type message : Message

    :return: None
    :rtype: NoneType
    """
    await BanUserForm.ban_user_name.set()
    await message.reply("Укажите id пользователя: ")


@dp.message_handler(state=BanUserForm.ban_user_name)
async def ban_user_check(message: Message, state: FSMContext) -> None:
    """
    Проверяет есть ли юзер в базе

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
                "Подтвердите, вы точно хотите заблокировать этого "
                "пользователя?",
                reply_markup=key.yn_kb
            )
            await BanUserForm.next()
        else:
            await message.answer('Пользователь не найден. Повторите попытку: ')
    except ValueError:
        await message.answer('Неверный ввод. Укажите id пользователя: ')


@dp.callback_query_handler(
    state=BanUserForm.ban_confirm,
    text=key.confirm.text
)
async def ban_user_confirm(
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
        db_manager.send_to_blacklist(user_id=user_id)
        await cache.update_data(
            user=user_id,
            data={'black_list': True}
        )
        await callback_query.message.answer('Пользователь заблокирован.')
    except Exception as e:
        logging.error(e)
        await callback_query.answer('Произошла ошибка!')
    await callback_query.message.delete()
    await state.finish()


@dp.callback_query_handler(
    state=BanUserForm.ban_confirm,
    text=key.dn_confirm.text
)
async def ban_user_cancel(
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
