from aiogram.types import CallbackQuery

import keyboards as key
from data import cache
from loader import bot, db_manager, dp


async def get_reply(call: CallbackQuery,
                    faq_key: str) -> None:
    """
    Получает ответ на FAQ и отправляет пользователю

    :param call: объект CallbackQuery
    :type call: CallbackQuery
    :param faq_key: ключ записи
    :type faq_key: str

    :return: None
    :rtype: NoneType
    """

    await cache.set_data(chat=call.message.chat,
                         user=call.message.from_user.username,
                         data=call.message.text)

    await call.message.answer(db_manager.get_df_for_faq(faq_key),
                              reply_markup=key.up_kb)


async def send_message(call: CallbackQuery, text_button: str) -> None:
    """
    Удаляет прежнее сообщение и отправляет вопрос пользователю

    :param call: объект CallbackQuery
    :type call: CallbackQuery
    :param text_button: текст вопроса
    :type text_button: str

    :return: None
    :rtype: NoneType
    """

    await bot.delete_message(chat_id=call.from_user.id,
                             message_id=call.message.message_id)
    await call.message.answer(text=text_button)


@dp.callback_query_handler(text=key.FaqKeyboard.FIN_Q2_STR.value)
async def answer_fin_2(call: CallbackQuery) -> None:
    """
    Отправляет ответ в чат пользователю по записи 'FIN-2'

    :param call: объект CallbackQuery
    :type call: CallbackQuery

    :return: None
    :rtype: NoneType
    """

    await send_message(call, key.FaqKeyboard.FIN_Q2_STR.value)
    await get_reply(call, 'FIN-2')


@dp.callback_query_handler(text=key.FaqKeyboard.FIN_Q1_STR.value)
async def answer_fin_1(call: CallbackQuery) -> None:
    """
    Отправляет ответ в чат пользователю по записи 'FIN-2'

    :param call: объект CallbackQuery
    :type call: CallbackQuery

    :return: None
    :rtype: NoneType
    """

    await send_message(call, key.FaqKeyboard.FIN_Q1_STR.value)
    await get_reply(call, 'FIN-1')


@dp.callback_query_handler(text=key.FaqKeyboard.FIN_Q3_STR.value)
async def answer_fin_3(call: CallbackQuery) -> None:
    """
    Отправляет ответ в чат пользователю по записи 'FIN-3'

    :param call: объект CallbackQuery
    :type call: CallbackQuery

    :return: None
    :rtype: NoneType
    """

    await send_message(call, key.FaqKeyboard.FIN_Q3_STR.value)
    await get_reply(call, 'FIN-3')


@dp.callback_query_handler(text=key.FaqKeyboard.FIN_Q4_STR.value)
async def answer_fin_4(call: CallbackQuery) -> None:
    """
    Отправляет ответ в чат пользователю по записи 'FIN-4'

    :param call: объект CallbackQuery
    :type call: CallbackQuery

    :return: None
    :rtype: NoneType
    """

    await send_message(call, key.FaqKeyboard.FIN_Q4_STR.value)
    await get_reply(call, 'FIN-4')


@dp.callback_query_handler(text=key.FaqKeyboard.FIN_Q5_STR.value)
async def answer_fin_5(call: CallbackQuery) -> None:
    """
    Отправляет ответ в чат пользователю по записи 'FIN-5'

    :param call: объект CallbackQuery
    :type call: CallbackQuery

    :return: None
    :rtype: NoneType
    """

    await send_message(call, key.FaqKeyboard.FIN_Q5_STR.value)
    await get_reply(call, 'FIN-5')


@dp.callback_query_handler(text=key.FaqKeyboard.TECH_Q1_STR.value)
async def answer_tech_1(call: CallbackQuery) -> None:
    """
    Отправляет ответ в чат пользователю по записи 'TDP-1'

    :param call: объект CallbackQuery
    :type call: CallbackQuery

    :return: None
    :rtype: NoneType
    """

    await send_message(call, key.FaqKeyboard.TECH_Q1_STR.value)
    await get_reply(call, 'TDP-1')


@dp.callback_query_handler(text=key.FaqKeyboard.TECH_Q2_STR.value)
async def answer_tech_2(call: CallbackQuery) -> None:
    """
    Отправляет ответ в чат пользователю по записи 'TDP-2'

    :param call: объект CallbackQuery
    :type call: CallbackQuery

    :return: None
    :rtype: NoneType
    """

    await send_message(call, key.FaqKeyboard.TECH_Q2_STR.value)
    await get_reply(call, 'TDP-2')


@dp.callback_query_handler(text=key.FaqKeyboard.TECH_Q3_STR.value)
async def answer_tech_3(call: CallbackQuery) -> None:
    """
    Отправляет ответ в чат пользователю по записи 'TDP-3'

    :param call: объект CallbackQuery
    :type call: CallbackQuery

    :return: None
    :rtype: NoneType
    """

    await send_message(call, key.FaqKeyboard.TECH_Q3_STR.value)
    await get_reply(call, 'TDP-3')


@dp.callback_query_handler(text=key.FaqKeyboard.ACC_Q1_STR.value)
async def answer_acc_1(call: CallbackQuery) -> None:
    """
    Отправляет ответ в чат пользователю по записи 'ACC-1'

    :param call: объект CallbackQuery
    :type call: CallbackQuery

    :return: None
    :rtype: NoneType
    """

    await send_message(call, key.FaqKeyboard.ACC_Q1_STR.value)
    await get_reply(call, 'ACC-1')


@dp.callback_query_handler(text=key.FaqKeyboard.ACC_Q2_STR.value)
async def answer_acc_2(call: CallbackQuery) -> None:
    """
    Отправляет ответ в чат пользователю по записи 'ACC-2'

    :param call: объект CallbackQuery
    :type call: CallbackQuery

    :return: None
    :rtype: NoneType
    """

    await send_message(call, key.FaqKeyboard.ACC_Q2_STR.value)
    await get_reply(call, 'ACC-2')


@dp.callback_query_handler(text=key.FaqKeyboard.ORG_Q1_STR.value)
async def answer_org_1(call: CallbackQuery) -> None:
    """
    Отправляет ответ в чат пользователю по записи 'ORG-1'

    :param call: объект CallbackQuery
    :type call: CallbackQuery

    :return: None
    :rtype: NoneType
    """

    await send_message(call, key.FaqKeyboard.ORG_Q1_STR.value)
    await get_reply(call, 'ORG-1')


@dp.callback_query_handler(text=key.FaqKeyboard.OTH_Q1_STR.value)
async def answer_oth_1(call: CallbackQuery) -> None:
    """
    Отправляет ответ в чат пользователю по записи 'ANO-1'

    :param call: объект CallbackQuery
    :type call: CallbackQuery

    :return: None
    :rtype: NoneType
    """

    await send_message(call, key.FaqKeyboard.OTH_Q1_STR.value)
    await get_reply(call, 'ANO-1')
