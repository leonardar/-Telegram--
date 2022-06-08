"""
Модуль содержит обработчики, осуществляющие поиск зарегистрированных
пользователей в базе данных BigQuery, по команде /search.
"""
import logging
from utils import get_logger
from re import compile, fullmatch
from loader import db_manager, dp, bot
from states.search_states import SearchStates
from filters import IsRegistered, IsGroupChat
from aiogram.types import Message, InlineKeyboardMarkup, \
    InlineKeyboardButton, CallbackQuery
from aiogram.dispatcher import FSMContext

logger = get_logger('bot.log', logging.ERROR)


@dp.callback_query_handler(text=['/next_search'], state=SearchStates.AFT_SEAR)
@dp.message_handler(
    IsRegistered(),
    IsGroupChat(),
    commands=["search"],
    state="*"
)
async def search_info(event, state: FSMContext) -> None:
    """
    Обработчик осуществляет приветствие и информирует о
    правилах поиска пользователей.
    """
    try:
        if event.message.text == "Вы можете продолжить или завершить поиск.":
            await event.message.delete()
    except AttributeError:
        logger.error("AttributeError")

    keyboard_markup = InlineKeyboardMarkup(row_width=2)
    text_and_data = (
        ('Примеры запросов', '/example'),
        ('Правила поиска', '/rule'),
    )
    row_btns2 = (InlineKeyboardButton(text, callback_data=data) for
                 text, data in text_and_data)
    keyboard_markup.add(*row_btns2)

    search_inf = "Для поиска информации о сотруднике Ylab введите фамилию, " \
                 "имя, корпоративную почту или логин."
    try:
        msg = await event.message.answer(search_inf,
                                         reply_markup=keyboard_markup)
        next_id = msg.message_id

    except AttributeError:
        msg = await event.answer(search_inf, reply_markup=keyboard_markup)
        next_id = msg.message_id
    async with state.proxy() as data:
        data['msg_id'] = next_id

    await SearchStates.SEARCH_PROCESS.set()


@dp.callback_query_handler(text='/example', state=SearchStates.SEARCH_PROCESS)
async def search_example(query: CallbackQuery) -> None:
    """
    Обработчик показывает пользователю примеры запросов
    """
    await query.answer("Гуляев g.gulyaev@ylab.io @icedevil\n"
                       "Григорий Гуляев g.gulyaev@ylab.io\n"
                       "григорий Гуляев\nгуляев\ng.gulyaev@ylab.io\n"
                       "@icedevil",
                       show_alert=True)


@dp.callback_query_handler(text='/rule', state=SearchStates.SEARCH_PROCESS)
async def search_rule(query: CallbackQuery) -> None:
    """
    Обработчик показывает пользователю правила поиска
    """
    await query.answer(
        "Введите параметры поиска через пробел, "
        "корпоративная почта в домене @ylab.io, "
        "телеграм логин в формате @username", show_alert=True)


@dp.message_handler(state=SearchStates.SEARCH_PROCESS)
async def search_response(message: Message, state: FSMContext) -> None:
    """
    Обработчик принимает поисковый запрос от пользователя,
    и отправляет сообщение в чат с результатом поиска.
    """

    async with state.proxy() as data:
        msg_id = data['msg_id']

    keyboard_markup2 = InlineKeyboardMarkup(row_width=2)
    text_and_data2 = (
        ('Продолжить', '/next_search'),
        ('Завершить', '/end_search'),
    )
    row_btns2 = (InlineKeyboardButton(text2, callback_data=data2) for
                 text2, data2 in text_and_data2)

    keyboard_markup2.add(*row_btns2)
    parse_data = parsing(message.text)

    if isinstance(parse_data, str):
        await bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
        await message.answer(parse_data)
    else:
        await bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
        await message.answer(users_search(parse_data))

    await message.answer(
        "Вы можете продолжить или завершить поиск.",
        reply_markup=keyboard_markup2)

    await SearchStates.AFT_SEAR.set()


@dp.callback_query_handler(state=SearchStates.AFT_SEAR)
async def after_search_response(message: Message) -> None:
    """
    Обработчик реализует свои действия после того, как пользователь
    отправил поисковый запрос, и не зависимо от результата поиска
    пользователю будет предложено повторить поиск или покинуть его.
    """

    keyboard_markup = InlineKeyboardMarkup(row_width=2)
    text_and_data = (
        ('Примеры запросов', '/example'),
        ('Правила поиска', '/rule'),
    )
    row_btns2 = (InlineKeyboardButton(text, callback_data=data) for
                 text, data in text_and_data)
    keyboard_markup.add(*row_btns2)

    search_inf = "Для поиска информации о сотруднике Ylab введите фамилию, " \
                 "имя, корпоративную почту или логин."

    await message.answer(search_inf, reply_markup=keyboard_markup)
    await SearchStates.SEARCH_PROCESS.set()


def parsing(data: str) -> any:
    """
    Функция принимает поисковый запрос от пользователя и осуществляет его
    парсинг, таким образом, что функция возвращает словарь, ключи которого
    соответствуют названиям полей базы данных BigQuery.

    parse_data= {'email': 'gemail@ylab.io',
                 'telegram_name': '@username',
                 'full_name': ['имя', 'фамилия']}

    В случае ввода неверных данных (is_valid = False) функция
    отправит пользователю в чат сообщение об ошибке.

    :param data: "cырые" данные вытянутые из сообщения пользователя
    :type data: str.data

    :return: найденные данные пользователя
    :retype: -> any
    """

    data: list = data.split()
    parse_data: dict = {'full_name': 'str', 'email': 'str',
                        'telegram_name': 'str'}
    words: list = []
    for word in data:
        if 'ylab.io' in word:
            if is_data_valid(word, 'email'):
                parse_data.update({'email': word})
            else:
                return "Проверьте правильность электронной почты."
        elif '@' in word:
            if is_data_valid(word, 'telegram_name'):
                parse_data.update({'telegram_name': word})
            else:
                return "Проверьте правильность @username или @email."
        else:
            words.append(word.lower().capitalize())
            if is_data_valid(" ".join(words), 'full_name'):
                parse_data.update({'full_name': words})
            else:
                return "Проверьте правильность имени и фамилии."
    return parse_data


def is_data_valid(data: str, case: str) -> bool:
    """
    Функция принимает строки и сопоставляет их с регулярными выражениями,
    возвращает True в случае соответствия.

    :param data: спарсенные слова
    :type data: str.parse_data

    :param case: типа шаблона
    :type case: str

    :return: True or False
    :rtype: boo
    """

    re_telegram = compile(r"@+[a-zA-Z0-9_]{5,64}")
    re_email = compile(r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@ylab.io")
    re_text = compile(
        r"[а-яА-ЯёЁa-zA-Z]+\s+[а-яА-ЯёЁa-zA-Z]+|[а-яА-ЯёЁa-zA-Z]{2,32}")
    return True if \
        (case == 'telegram_name' and fullmatch(re_telegram, data)) or \
        (case == 'email' and fullmatch(re_email, data)) or \
        (case == 'full_name' and fullmatch(re_text, data)) else False


def users_search(parse_data: dict) -> str:
    """
    Функция принимает структурированные данные и использует их как ключи,
    для осуществления поиска в подключенной SQL-БД, который осуществляется
    при вызове функции get_df_for_search(). Найденные данные отправляются
    пользователю в чат.

    :param parse_data: структурированные данные
    :type parse_data: dict.parse_data

    :return: найденные данные
    :rtype: str
    """
    df_iterable = db_manager.get_df_for_search(parse_data). \
        to_dataframe_iterable()
    for frame_data in df_iterable:
        search_answer = frame_data.to_dict(orient="index")
        if search_answer:
            for index in search_answer:
                if len(parse_data['full_name']) != 2:
                    return view(search_answer)
                elif match(search_answer[index], parse_data):
                    return " ".join(list(search_answer[index].values()))
                else:
                    return view(search_answer)
        else:
            return "Пользователь не существует или данные введены " \
                   "некорректно."


def view(data: dict) -> str:
    """
    Функция принимает найденные данные в формате dict и
    преобразовывает их в строки для отправки пользователю.

    :param data: найденная информация в БД
    :type data: dict['str', str']

    :return: строка с данными
    :rtype: str
    """
    try:
        for index in data:
            for key in list(data[index]):
                if not isinstance(data[index][key], str):
                    data[index].pop(key)
        answer = '\n'.join([' '.join(data[index].values()) for index in data])
        return answer
    except TypeError:
        logger.error('Проверьте правильность полей в базе данных')


def match(search_answer: dict, parse_data: dict) -> bool:
    """
    Если пользователь найден и по имени и по фамилии, одновременно, то функция
    вернет True и в таком случае другие найденные совпавшие имена и
    фамилии выведены не будут.

    :param search_answer: найденная информация
    :type search_answer: dict[str, str]

    :param parse_data: структурированные данные
    :type parse_data: dict[str, str]

    :return: True or False
    :rtype: bool
    """

    s_name = search_answer['fullname'].split()
    p_name = parse_data['full_name']
    if s_name[0] == p_name[0] and s_name[1] == p_name[1] or \
            s_name[0] == p_name[1] and s_name[1] == p_name[0]:
        return True
    else:
        return False
