import re

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, Message
from pandas import read_json

from data import cache
from bot import logger
from filters import IsRegistered, IsGroupChat
from keyboards import DrawKeyboardsPeriods
from loader import bot, db_manager, dp
from services import save_graph
from utils import constants

draw_kb = DrawKeyboardsPeriods()
COUNT_PERIODS_PAGE: int = 4


async def get_menu_salary_period(message: Message) -> dict:
    """
    Функция проверяет есть ли в кеш периоды,
    если нет достает из БД и обновляет кеш

    :param message: объект Message
    :type message: message

    :return: словарь с зарплатными периодами
    :rtype: dict
    """

    try:

        data = await cache.get_data(
            user=message.from_user.id, chat=message.chat.id
        )
        salary_periods = data["salary_periods"]
        return read_json(salary_periods)

    except KeyError:
        df_iterable = db_manager.get_salary_periods_user(
            message.from_user.id
        ).to_dataframe_iterable()
        for salary_periods in df_iterable:
            df_json = salary_periods.to_json()
        await cache.update_data(
            user=message.from_user.id,
            chat=message.chat.id,
            data={"salary_periods": df_json},
        )
        return salary_periods


def sort_salary_periods(salary_periods: list) -> list:
    """
    Функция сортирует зарплатные периоды и возвращает отсортированный список

    :param salary_periods: список с зарплатными периодами
    :type salary_periods: list

    :return: отсортированный список
    :rtype: list
    """

    periods: list = []

    for period in salary_periods:
        for key, value in constants.MONTHS.items():
            month = re.search(r"-([а-яA-Я]+)", period).group(1)
            if value == month:
                str_period = re.sub(month, f" {key} ", period)
                periods.append(str_period.split())
                continue
    sort_periods = sorted(periods,
                          key=lambda p: (-int(p[2]), -int(p[1]), len(p[0])))
    return [f"{period[0]}{constants.MONTHS[int(period[1])]}{period[2]}"
            for period in sort_periods
            ]


@dp.message_handler(
    IsRegistered(),
    IsGroupChat(),
    Text(equals=["/details_job"]),
    commands=["details_job"]
)
async def print_menu_salary_period(message: Message,
                                   state: FSMContext) -> None:
    """
    Создает запрос в БД об имеющихся ЗП и формирует меню

    :param message: объект Message
    :type message: Message
    :param state: объект FSMContext
    :type state: FSMContext

    :return: None
    :rtype: NoneType
    """

    salary_periods = await get_menu_salary_period(message)
    df = salary_periods.melt(
        value_vars=["salaryPeriod", "notApprovedSalaryPeriod"]
    )
    df = df[
        df.value.astype(str).str.contains("ЗП")
        | df.value.astype(str).str.contains("Аванс")
        ]

    if df.empty:
        await message.answer("У вас нет доступных периодов.")
    else:
        periods: list = sort_salary_periods(list(set(df.value)))
        count_periods: int = len(periods)

        async with state.proxy() as data:
            data["periods"] = periods

        if count_periods <= COUNT_PERIODS_PAGE:
            kb_periods = draw_kb.draw_periods(periods, 0, count_periods)
        else:
            kb_periods = draw_kb.draw_extra_kb(periods, 0, COUNT_PERIODS_PAGE,
                                               "yaers_all_kb")

        await message.answer("Выберите период: ", reply_markup=kb_periods)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("p"))
async def send_graph(call: CallbackQuery) -> None:
    """
    Формирует график по ЗП и отправляет его

    :param call: объект CallbackQuery
    :type call: CallbackQuery

    :return: None
    :rtype: NoneType
    """
    await call.answer("Период формируется.")
    await bot.delete_message(chat_id=call.from_user.id,
                             message_id=call.message.message_id)
    df_iterable = db_manager.get_df_for_graph(
        call.from_user.id, call.data[1:]
    ).to_dataframe_iterable()
    try:
        for df in df_iterable:
            if not df.empty:
                img = save_graph(df)
                await call.bot.send_photo(
                    call.from_user.id,
                    img,
                    caption=call.data[1:]
                )
            else:
                await call.answer("Заданный период не найден.")
    except Exception as e:
        await call.message.answer("Возникла ошибка!")
        logger.error(e)


@dp.callback_query_handler(lambda c: c.data == "Periods")
async def get_years(call: CallbackQuery, state: FSMContext) -> None:
    """
    Формирует список кнопок по годам

    :param call: объект CallbackQuery
    :type call: CallbackQuery
    :param state: объект FSMContext
    :type state: FSMContext

    :return: None
    :rtype: NoneType

    """
    try:
        async with state.proxy() as data:
            periods = data["periods"]

        years: set = {f"20{period[-2::]}" for period in periods}

        kb_years = draw_kb.draw_years(years=years)

        await bot.delete_message(chat_id=call.from_user.id,
                                 message_id=call.message.message_id)
        await call.message.answer("Выберите год: ", reply_markup=kb_years)
    except Exception as e:
        await call.message.answer("Возникла ошибка!")
        logger.error(e)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("year"))
async def get_periods_of_year(call: CallbackQuery, state: FSMContext) -> None:
    """
    Формирует список с периодами по выбраному году
    :param call: объект CallbackQuery
    :type call: CallbackQuery
    :param state: объект FSMContext
    :type state: FSMContext

    :return: None
    :rtype: NoneType

    """
    try:
        year: str = call.data[-2::]
        async with state.proxy() as data:
            periods = data["periods"]

        periods_yaer: list = [period for period in periods if
                              period[-2::] == year]
        count_periods: int = len(periods_yaer)

        if count_periods <= COUNT_PERIODS_PAGE:
            kb_periods = draw_kb.draw_periods(periods_yaer, 0, count_periods)
        else:
            kb_periods = draw_kb.draw_extra_kb(periods_yaer, 0,
                                               COUNT_PERIODS_PAGE,
                                               "yaers_all_kb", "next_kb")
            async with state.proxy() as data:
                data["periods_yaer"] = periods_yaer
                data["period_index"] = COUNT_PERIODS_PAGE

        await bot.delete_message(chat_id=call.from_user.id,
                                 message_id=call.message.message_id)
        await call.message.answer("Выберите период: ", reply_markup=kb_periods)
    except Exception as e:
        await call.message.answer("Возникла ошибка!")
        logger.error(e)


@dp.callback_query_handler(lambda c: c.data == "Next")
async def get_next_page(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция формирует следующую страницу с периодами
    :param call: объект CallbackQuery
    :type call: CallbackQuery
    :param state: объект FSMContext
    :type state: FSMContext

    :return: None
    :rtype: NoneType

    """
    try:
        async with state.proxy() as data:
            periods_yaer = data["periods_yaer"]
            period_index = data["period_index"]

        count_periods: int = len(periods_yaer) - period_index

        if count_periods > COUNT_PERIODS_PAGE:
            stop = period_index + COUNT_PERIODS_PAGE
            kb_periods = draw_kb.draw_extra_kb(periods_yaer, period_index,
                                               stop,
                                               "back_kb",
                                               "next_kb")

        elif count_periods <= COUNT_PERIODS_PAGE:
            stop = period_index + count_periods
            kb_periods = draw_kb.draw_extra_kb(periods_yaer, period_index,
                                               stop,
                                               "back_kb")

        async with state.proxy() as data:
            data["period_index"] += COUNT_PERIODS_PAGE

        await bot.delete_message(chat_id=call.from_user.id,
                                 message_id=call.message.message_id)

        await call.message.answer("Выберите период: ", reply_markup=kb_periods)
    except Exception as e:
        await call.message.answer("Возникла ошибка!")
        logger.error(e)


@dp.callback_query_handler(lambda c: c.data == "Back")
async def get_back_page(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция возращает на предыдущую страницу с периодами
    :param call: объект CallbackQuery
    :type call: CallbackQuery
    :param state: объект FSMContext
    :type state: FSMContext

    :return: None
    :rtype: NoneType
    """
    try:
        async with state.proxy() as data:

            periods_yaer = data["periods_yaer"]
            period_index = data["period_index"]

        start: int = period_index - 2 * COUNT_PERIODS_PAGE
        stop: int = period_index - COUNT_PERIODS_PAGE

        if start > 0:
            kb_periods = draw_kb.draw_extra_kb(periods_yaer, start, stop,
                                               "back_kb", "next_kb")

        elif start <= 0:
            kb_periods = draw_kb.draw_extra_kb(periods_yaer, start, stop,
                                               "yaers_all_kb", "next_kb")

        async with state.proxy() as data:
            data["period_index"] -= COUNT_PERIODS_PAGE

        await bot.delete_message(chat_id=call.from_user.id,
                                 message_id=call.message.message_id)
        await call.message.answer("Выберите период: ", reply_markup=kb_periods)
    except Exception as e:
        await call.message.answer("Возникла ошибка!")
        logger.error(e)
