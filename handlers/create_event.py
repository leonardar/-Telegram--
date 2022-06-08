import datetime
import logging
import re
import keyboards as key

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardMarkup
from aiogram.utils.markdown import text
from aiogram_calendar import SimpleCalendar, simple_cal_callback
from inline_timepicker.exceptions import WrongCallbackException
from inline_timepicker.inline_timepicker import InlineTimepicker

from filters import IsRegistered
from loader import dp, bot
from services.set_scheduler import set_scheduler_event
from states import CreateEventForm

start_kb = ReplyKeyboardMarkup(resize_keyboard=True)

inline_timepicker = InlineTimepicker()


@dp.message_handler(
    IsRegistered(),
    commands=["create_event"],
    state="*")
async def create_event_start(message: Message) -> None:
    """
    Перехватывает команду create_event
    Устанавливает стейт event_name
    Спрашивает у пользователя название события

    :param message: объект Message
    :type message : Message

    :return: None
    :rtype: NoneType
    """

    await CreateEventForm.event_name.set()
    await message.reply("Укажите название события или нажмите \n"
                        "/event_text для введения текста события целиком: ")


@dp.message_handler(IsRegistered(), commands=["event_text"], state="*")
async def parse_event_start(message: Message) -> None:
    """
    Перехватывает команду f и выводит сообщение с
    просьбой ввести пользователя текст события целиком

    :param message: объект Message
    :type message : Message

    :return: None
    :rtype: NoneType
    """

    await CreateEventForm.event_text.set()
    await message.reply("Введите сообщение через пробел как в примере: "
                        "\nДень рождения 11/05/2022 17:10 Купить торт")


@dp.message_handler(state=CreateEventForm.event_text)
async def set_event_text(message: Message, state: FSMContext) -> None:
    """
    Парсит сообщение пользователя и извлекает из него
    названия, дату, время события и комментарий

    :param message: объект Message
    :type message : Message
    :param state: объект FSMContext
    :type state : FSMContext

    :return: None
    :rtype: NoneType
    """
    try:
        event_date = re.search(r"(?:0?[1-9]|[12][0-9]|3[01])/"
                               r"(?:0?[1-9]|1[0-2])/(20[0-9][0-9])(?!\d)",
                               message.text).group()

        event_time = re.search(r"(([01]\d|2[0-3]):([0-5]\d)|24:00)",
                               message.text).group()

        event_name = message.text[0:message.text.find(event_date)]
        event_comment = message.text[message.text.rfind(event_time) + 5:]

        async with state.proxy() as data:
            data["event_date"] = event_date
            time = datetime.timedelta(
                hours=int(event_time.split(':')[0]),
                minutes=int(event_time.split(':')[1]))
            date_and_time = datetime.datetime.strptime(
                event_date,
                "%d/%m/%Y")
            date_and_time += time
            if date_check(date_and_time):
                data["event_time"] = event_time
                data["event_name"] = event_name
                data["event_comment"] = event_comment

                await CreateEventForm.event_confirm.set()

                await message.reply("Подтвердить?", reply_markup=key.yn_kb)
            else:
                await message.reply("Нельзя выбирать дату и время раньше, "
                                    "чем сейчас.")

    except (ValueError, AttributeError):
        await message.reply("Неверный формат ввода. Повторите попытку.")


@dp.message_handler(state=CreateEventForm.event_name)
async def set_event_name(message: Message, state: FSMContext) -> None:
    """
    Перехватывает сообщение со стейтом event_name
    Записывает название события в state.proxy() по ключу "event_name"
    Устанавливает следующее значение стейта event_date
    Просит у пользователя выбрать дату и выводит календарик

    :param message: объект Message
    :type message : Message
    :param state: объект FSMContext
    :type state : FSMContext

    :return: None
    :rtype: NoneType
    """

    async with state.proxy() as data:
        data["event_name"] = message.text

    await CreateEventForm.next()

    await message.answer(
        text="Выберите дату: ",
        reply_markup=await SimpleCalendar().start_calendar()
    )


@dp.callback_query_handler(
    simple_cal_callback.filter(),
    state=CreateEventForm.event_date
)
async def set_event_date(
        callback_query: CallbackQuery,
        callback_data,
        state: FSMContext
) -> None:
    """
    Перехватывает событие нажимания на кнопку
    даты из календарика со стейтом event_date
    Записывает значение нажатой кнопки в state.proxy() по ключу "event_date"
    Устанавливает следующее значение стейта event_time
    Просит у пользователя написать время

    :param callback_query: объект Message
    :type callback_query : Message
    :param callback_data: словарь для значений даты
    :param state: объект FSMContext
    :type state : FSMContext

    :return: None
    :rtype: NoneType
    """

    inline_timepicker.init(
        datetime.time(12),
        datetime.time(0),
        datetime.time(hour=23, minute=45)
    )

    selected, date = await SimpleCalendar().process_selection(
        callback_query,
        callback_data
    )

    if selected and date_check(date):
        await callback_query.message.answer(
            f'Вы выбрали: {date.strftime("%d/%m/%Y")}',
        )

        async with state.proxy() as data:
            data["event_date"] = f"{date:%d/%m/%Y}"

        await callback_query.message.answer(
            text="Выберите время: ",
            reply_markup=inline_timepicker.get_keyboard()
        )
        await CreateEventForm.next()

    else:
        await callback_query.message.answer(
            text="Выберите дату не раньше сегодняшнего числа: ",
            reply_markup=await SimpleCalendar().start_calendar()
        )


@dp.callback_query_handler(inline_timepicker.filter(),
                           state=CreateEventForm.event_time)
async def set_event_time(callback_query: CallbackQuery,
                         callback_data: dict[str, str], state: FSMContext) \
        -> None:
    """
    Перехватывает стейт выбора времени
    Записывает значение нажатой кнопки в state.proxy() по ключу "event_time"
    Устанавливает следующее значение стейта event_comment
    Просит у пользователя написать комментарий

    :param callback_query: объект CallbackQuery
    :type callback_query : CallbackQuery
    :param callback_data: словарь для временных значений
    :type callback_data: dict
    :param state: объект FSMContext
    :type state : FSMContext

    :return: None
    :rtype: NoneType
    """

    await callback_query.answer()

    try:
        handle_result = inline_timepicker.handle(callback_query.from_user.id,
                                                 callback_data)

        if handle_result is not None:
            await callback_query.message.edit_text(handle_result)
            async with state.proxy() as data:
                date = datetime.datetime.strptime(
                    data["event_date"],
                    "%d/%m/%Y"
                )
                dt = datetime.datetime.combine(date, handle_result)
                if date_check(dt):

                    data["event_time"] = \
                        f"{handle_result:%H:%M}"

                    await CreateEventForm.next()

                    await callback_query.message.answer(
                        text="Напишите комментарий."
                    )
                else:
                    inline_timepicker.init(
                        datetime.time(12),
                        datetime.time(0),
                        datetime.time(hour=23, minute=45)
                    )
                    await callback_query.message.answer(
                        text="Время должно быть не раньше, чем сейчас: ",
                        reply_markup=inline_timepicker.get_keyboard()
                    )

        else:
            await bot.edit_message_reply_markup(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                reply_markup=inline_timepicker.get_keyboard())

    except WrongCallbackException as e:
        logging.error(e)


@dp.message_handler(state=CreateEventForm.event_comment)
async def set_event_comment(message: Message, state: FSMContext) -> None:
    """
    Перехватывает комментарий со стейтом event_comment
    Записывает в state.proxy() комментарий по ключу "event_comment"
    Спрашивает у пользователя будет ли это событие персональным

    :param message: объект Message
    :type message : Message
    :param state: объект FSMContext
    :type state : FSMContext

    :return: None
    :rtype: NoneType
    """

    async with state.proxy() as data:
        data["event_comment"] = message.text

    await message.answer(
        text(
            text(data["event_name"]),
            text(data["event_date"]),
            text(data["event_time"]),
            text(data["event_comment"]),
            sep="\n",
        ),
    )
    await CreateEventForm.next()
    await message.answer("Подтвердить?", reply_markup=key.yn_kb)


@dp.callback_query_handler(state=CreateEventForm.event_confirm,
                           text=key.confirm.text)
async def set_event_confirm(callback_query: CallbackQuery,
                            state: FSMContext) -> None:
    """
    Перехватывает комментарий со стейтом event_confirm на кнопке "да"
    Создаёт запись в set_scheduler

    :param callback_query: объект CallbackQuery
    :type callback_query : CallbackQuery
    :param state: объект FSMContext
    :type state : FSMContext

    :return: None
    :rtype: NoneType
    """

    await callback_query.message.delete()

    async with state.proxy() as data:
        await callback_query.message.answer("Событие создано.")
        if callback_query.from_user.id == callback_query.message.chat.id:
            user_id = callback_query.from_user.id
        else:
            user_id = callback_query.message.chat.id
        set_scheduler_event(
            user_id=user_id,
            event=data["event_name"],
            event_date=data["event_date"],
            event_time=data["event_time"],
            comment=data["event_comment"],
        )
        await state.finish()


@dp.callback_query_handler(state=CreateEventForm.event_confirm,
                           text=key.dn_confirm.text)
async def set_event_not_created(callback_query: CallbackQuery,
                                state: FSMContext) -> None:
    """
    Перехватывает комментарий со стейтом event_confirm на кнопке "нет"
    Отправляет сообщение что событие не создано

    :param callback_query: объект CallbackQuery
    :type callback_query : CallbackQuery
    :param state: объект FSMContext
    :type state : FSMContext

    :return: None
    :rtype: NoneType
    """
    await callback_query.message.delete()

    async with state.proxy():
        await callback_query.message.answer("Событие не создано.")

        await state.finish()


def date_check(date: datetime) -> bool:
    """
    Функция для проверки времени, даты

    :param date: дата
    :type: datetime

    :return: true or False
    :rtype: bool
    """

    date_now = datetime.datetime.now()
    if date.time() == datetime.time(hour=0, minute=0):
        return date.date() >= date_now.date()
    else:
        return date > date_now
