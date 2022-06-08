from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from filters import UserRoleFilter, IsGroupChat
from loader import bot, db_manager, dp
from states import AdminMessageStates
from utils import get_logger
import keyboards as key

logger = get_logger(__name__)


@dp.message_handler(
    UserRoleFilter(role='admin'),
    IsGroupChat(),
    commands=["admin_message"],
    state="*"
)
async def admin_message_start(message: Message) -> None:
    """
    Перехватывает команду "/ban_user"

    :param message: объект Message
    :type message : Message

    :return: None
    :rtype: NoneType
    """

    await AdminMessageStates.admin_message_text.set()
    await message.reply("Введите сообщение для всех пользователей: ")


@dp.message_handler(state=AdminMessageStates.admin_message_text)
async def admin_message_text(message: Message, state: FSMContext) -> None:
    """
    Пишет текст сообщения для всех пользователей в proxy

    :param message: объект Message
    :type message : Message
    :param state: FSMContext
    :type state : объект FSMContext

    :return: None
    :rtype: NoneType
    """
    text = f'Сообщение от администратора {message.from_user.username}:\n'
    async with state.proxy() as data:
        data['message_text'] = text + message.text
    await AdminMessageStates.next()
    await message.answer(
        "Подтвердите, вы точно хотите отправить это "
        "сообщение остальным пользователям?",
        reply_markup=key.yn_kb
    )


@dp.callback_query_handler(
    state=AdminMessageStates.admin_message_confirm,
    text=key.confirm.text
)
async def admin_message_fin(
        callback_query: CallbackQuery,
        state: FSMContext
) -> None:
    """
    Подтверждение, завершение работы

    :param callback_query: объект CallbackQuery
    :type callback_query : CallbackQuery
    :param state: FSMContext
    :type state : объект FSMContext

    :return: None
    :rtype: NoneType
    """
    await callback_query.message.delete()

    async with state.proxy() as data:
        text = data['message_text']
    result = db_manager.get_user_id_list()
    if not result:
        await callback_query.message.answer('Произошла ошибка!')
    for row in result:
        try:
            await bot.send_message(chat_id=row[0], text=text)
        except Exception as e:
            logger.error(e)
    await state.finish()


@dp.callback_query_handler(
    state=AdminMessageStates.admin_message_confirm,
    text=key.dn_confirm.text
)
async def admin_message_cancel(
        callback_query: CallbackQuery,
        state: FSMContext
) -> None:
    """
    Отмена, завершение работы

    :param callback_query: объект CallbackQuery
    :type callback_query : CallbackQuery
    :param state: FSMContext
    :type state : объект FSMContext

    :return: None
    :rtype: NoneType
    """
    await callback_query.message.delete()
    await callback_query.message.answer("Отправка сообщения отменена.")
    await state.finish()
