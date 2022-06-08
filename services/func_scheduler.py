import logging
from datetime import date, datetime

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards import get_keyboard_for_graph
from loader import bot, db_manager, dp
from services.graph import get_image, get_salary_period, get_xlabel_for_graph
from states import GraphConfirmForm
from utils import get_logger

log = get_logger(__name__)


def save_graph(df) -> bytes:
    """
    Функция принимает DataFrame, формирует ось Х и сохраняет график.

    :param df: DataFrame пользователя по зарплатному периоду
    :type df: DataFrame

    :return: Возвращет график
    :rtype: bytes
    """

    labels = get_xlabel_for_graph(df)
    return get_image(df, labels)


async def send_graph_to_all(day: date) -> None:
    """
    Отправляет график пользователю и делает отметку в БД,
    если сообщение было успешно доставлено.

    :param day: день запроса периода
    :type : date

    :return: None
    :rtype: NoneType
    """
    salary_period = get_salary_period(day)
    df_iterable = db_manager.get_users_salaryperiod(
        salary_period
    ).to_dataframe_iterable()
    for df in df_iterable:
        user_ids = df.telegram_id.unique()
        for user_id in user_ids:
            dataframe = df.loc[df.telegram_id == user_id].sort_values(
                 by=['trackdate']
             )
            try:
                caption = salary_period
                msg = await bot.send_photo(
                    user_id, save_graph(dataframe), caption=caption
                )
                db_manager.send_confirm_for_salaryperiod(
                     user_id, msg.message_id, datetime.now(), salary_period)
                await set_keyboard(user_id, salary_period)
            except Exception as e:
                logging.error(e)


async def set_keyboard(user_id: int, salary_period: str) -> None:
    """
    Функция устанавливает две кнопки "согласиться/отклонить".

    :param user_id: id пользователя
    :type user_id: int
    :param salary_period: ЗП
    :type salary_period: str

    :return: None
    :rtype: NoneType
    """
    confirmed_kb = get_keyboard_for_graph(salary_period)
    await bot.send_message(
        chat_id=user_id,
        text="Подтвердить часы",
        reply_markup=confirmed_kb,
    )
    state = dp.current_state(user=user_id)
    await state.reset_state()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("kb"))
async def confirmed_call(callback_query: CallbackQuery,
                         state: FSMContext) -> None:
    """
    Функция определяет нажатую кнопку и в случае, если пользователь нажал на
    кнопку "согласиться", его ответ загружается в БД, в противном случае
    пользователю предлагается ввести комментарий.

    :param callback_query: объект CallbackQuery
    :type callback_query: CallbackQuery
    :param state: объект FSMContext
    :type state: FSMContext

    :return: None
    :rtype: NoneType
    """
    await callback_query.answer("Ответ загружается")
    await bot.delete_message(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
    )
    code: int = int(callback_query.data[2])
    async with state.proxy() as data:
        data["is_confirmed"] = bool(code)
        data["salary_period"] = callback_query.data[3:]
    if code:
        try:
            db_manager.update_data_for_salaryperiod(
                 callback_query.from_user.id,
                 data["salary_period"],
                 data["is_confirmed"],
                 None,
                 datetime.now(),
             )
            await callback_query.message.answer(
                f"Отработанное время за {data['salary_period']}, согласовано."
            )
            await state.finish()
        except Exception as e:
            await callback_query.message.answer("Возникла ошибка.")
            logging.error(e)
    else:
        await callback_query.message.answer(
            f"Отработанное время за за {data['salary_period']} "
            f"не согласовано, укажите причину."

        )
        await GraphConfirmForm.comment_to_graph.set()


@dp.message_handler(state=GraphConfirmForm.comment_to_graph)
async def send_confirmed_to_db(message: Message, state: FSMContext) -> None:
    """
    Функция принимает комментарий и загружает ответ в БД.

    :param message: объект Message
    :type message: Message
    :param state: объект FSMContext
    :type state: FSMContext

    :return: None
    :rtype: NoneType
    """

    async with state.proxy() as data:
        data["response_comment"] = message.text
    try:
        db_manager.update_data_for_salaryperiod(
            message.from_user.id,
            data["salary_period"],
            data["is_confirmed"],
            data["response_comment"],
            datetime.now(),
        )
        await message.answer("Комментарий отправлен.")
    except Exception as e:
        await message.answer("Возникла ошибка при отправке комментария.")
        logging.error(e)
    await state.finish()


async def form_list_of_chat_users(chat_id: int) -> list:
    """
    Функция формирует список из зарегистрированных в боте сотрудников,
    которые находятся в передаваемом чат-канале

    :param chat_id: id канала
    :type chat_id: int

    :return: список пользователей
    :rtype: list
    """

    list_of_reg_users: list = db_manager.get_user_id_list()
    list_of_chat_users: list = []
    for i_user in list_of_reg_users:
        try:
            user_status = await bot.get_chat_member(
                chat_id=chat_id,
                user_id=int(i_user[0])
            )
            if user_status['status'] != 'left':
                list_of_chat_users.append(i_user[0])
        except Exception as e:
            log.error(e)
    return list_of_chat_users


async def send_reminder_to_user(user_id: int, planned_at: datetime) -> None:
    """
    Отправляет напоминание пользователю.

    :param user_id: id пользователя
    :type user_id: int
    :param planned_at: дата события
    :type planned_at: datetime

    :return: None
    :rtype: NoneType
    """
    reminder_text = db_manager.get_reminder_text(planned_at)

    for row in reminder_text:
        if user_id < 0:
            list_of_chat_users = await form_list_of_chat_users(
                 chat_id=user_id
            )
            for telegram_id in list_of_chat_users:
                try:
                    await bot.send_message(telegram_id, text=row[1])
                except Exception as e:
                    log.error(e)
        await bot.send_message(row[0], text=row[1])
