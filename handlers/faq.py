from aiogram.types import CallbackQuery, Message

import keyboards as key
from filters import IsRegistered, IsGroupChat
from loader import dp
from aiogram.dispatcher import FSMContext


async def send_keyboard(faq_category: str, call: CallbackQuery) -> None:
    """
    Удаляет прежнее сообщение и выводит выбранное меню вопросов

    :param call: объект CallbackQuery
    :type call: CallbackQuery
    :param faq_category: категория вопроса
    :type faq_category: str

    :return: None
    :rtype: NoneType
    """
    keyboard = key.collect_keyboard(faq_category, call.from_user.id, key.bck)

    await call.message.delete()

    await call.message.answer("Выберите вопрос: ",
                              reply_markup=keyboard)


@dp.message_handler(
    IsRegistered(),
    IsGroupChat(),
    commands=['faq'],
    state="*")
async def start_category(message: Message, state: FSMContext) -> None:
    """
    Выводит стартовое меню FAQ

    :param message: объект Message
    :type message : Message

    :return: None
    :rtype: NoneType
    """
    await state.reset_state()
    await message.answer(text="Выберите раздел: ",
                         reply_markup=key.category_kb)


@dp.callback_query_handler(text=key.FaqKeyboard.CLS_BTN.value)
async def close_btn(call: CallbackQuery) -> None:
    """
    Закрывает меню

    :param call: объект CallbackQuery
    :type call : CallbackQuery

    :return: None
    :rtype: NoneType
    """

    await call.message.delete()


@dp.callback_query_handler(text=key.FaqKeyboard.FIN_STR.value)
async def fin_questions(call: CallbackQuery) -> None:
    """
    Выводит меню вопросов категории Финансы

    :param call: объект CallbackQuery
    :type call : CallbackQuery

    :return: None
    :rtype: NoneType
    """

    await send_keyboard('FIN', call)


@dp.callback_query_handler(text=key.FaqKeyboard.ORG_STR.value)
async def org_questions(call: CallbackQuery) -> None:
    """
    Выводит меню вопросов категории Организация

    :param call: объект CallbackQuery
    :type call : CallbackQuery

    :return: None
    :rtype: NoneType
    """

    await send_keyboard('ORG', call)


@dp.callback_query_handler(text=key.FaqKeyboard.OT_STR.value)
async def oth_questions(call: CallbackQuery) -> None:
    """
    Выводит меню вопросов категории Прочее

    :param call: объект CallbackQuery
    :type call : CallbackQuery

    :return: None
    :rtype: NoneType
    """

    await send_keyboard('ANO', call)


@dp.callback_query_handler(text=key.FaqKeyboard.ACC_STR.value)
async def acc_questions(call: CallbackQuery) -> None:
    """
    Выводит меню вопросов категории Бухгалтерия

    :param call: объект CallbackQuery
    :type call : CallbackQuery

    :return: None
    :rtype: NoneType
    """

    await send_keyboard('ACC', call)


@dp.callback_query_handler(text=key.FaqKeyboard.TECH_STR.value)
async def tech_questions(call: CallbackQuery) -> None:
    """
    Выводит меню вопросов категории Тех часть

    :param call: объект CallbackQuery
    :type call : CallbackQuery

    :return: None
    :rtype: NoneType
    """

    await send_keyboard('TDP', call)


@dp.callback_query_handler(text=key.FaqKeyboard.BCK_STR.value)
async def bck_to_category(call: CallbackQuery) -> None:
    """
    Выводит стартовое меню категорий

    :param call: объект CallbackQuery
    :type call : CallbackQuery

    :return: None
    :rtype: NoneType
    """

    await call.message.delete()

    await call.message.answer("Выберите раздел: ",
                              reply_markup=key.category_kb)


@dp.callback_query_handler(text=key.FaqKeyboard.UP_STR.value)
async def up_to_category(call: CallbackQuery) -> None:
    """
    Выводит стартовое меню категорий

    :param call: объект CallbackQuery
    :type call : CallbackQuery

    :return: None
    :rtype: NoneType
    """

    edt_txt = call.message['text']

    await call.message.edit_text(edt_txt)

    await call.message.answer("Выберите раздел: ",
                              reply_markup=key.category_kb)
