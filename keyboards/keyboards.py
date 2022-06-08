import enum

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from loader import db_manager


class FaqKeyboard(str, enum.Enum):
    """
    Данный класс содержит аргументы для формирования
    клавиатуры с категорией вопросов

    Args:
    FWD_STR: кнопка вперёд
    BCK_STR: кнопка назад
    UP_STR: кнопка на стартовое меню
    FIN_STR: категория Финансы
    ORG_STR: категория Организация
    OT_STR: категория Прочие
    TECH_STR: категория Тех часть
    ACC_STR: категория Бухгалтерия
    """

    FWD_STR = "➡️️"
    BCK_STR = "⬅️"
    UP_STR = "Назад ↩️"
    FIN_STR = "Финансы"
    ORG_STR = "Организация"
    OT_STR = "Прочее"
    TECH_STR = "Тех часть"
    ACC_STR = "Бухгалтерия"
    FIN_Q1_STR = "Какие треки идут в аванс?"
    FIN_Q2_STR = "Какие треки идут в зарплату?"
    FIN_Q4_STR = "Когда ждать аванс?"
    FIN_Q3_STR = "Когда ждать зарплату?"
    FIN_Q5_STR = "Неверная инфо в Data Studio"
    ORG_Q1_STR = "Хочу оформить отпуск"
    OTH_Q1_STR = "Простои, хочу задачи на обучение"
    TECH_Q1_STR = "Хочу получить надбавку"
    TECH_Q2_STR = "Хочу проходить курсы"
    TECH_Q3_STR = "Есть ли у нас система грейдов?"
    ACC_Q1_STR = "Мне нужна справка 2НДФЛ"
    ACC_Q2_STR = "Когда придут отпускные?"
    CLS_BTN = "Закрыть"


class DrawKeyboardsPeriods:
    """
    Данный класс формирует кнопки для ЗП

    """

    extra_kb: dict = {
        "next_kb": InlineKeyboardButton(text="Вперед >>",
                                        callback_data="Next"),
        "back_kb": InlineKeyboardButton(text="<< Назад", callback_data="Back"),
        "yaers_all_kb": InlineKeyboardButton(text="Все периоды",
                                             callback_data="Periods")
    }

    @staticmethod
    def draw_years(years: list) -> InlineKeyboardMarkup:
        """
        Функция формирует кнопки с годами ЗП

        :param years: список с годамим
        :type years: list

        :return: клавиатура с годами
        :rtype: InlineKeyboardMarkup
        """
        kb_periods = InlineKeyboardMarkup()
        for y in years:
            kb_periods.add(
                InlineKeyboardButton(text=y,
                                     callback_data=f"year{y[-2::]}")
            )
        return kb_periods

    @staticmethod
    def draw_periods(
            periods: list, start: int, stop: int
    ) -> InlineKeyboardMarkup:
        """
        Функция формирует кнопки с периодами ЗП

        :param periods: список с периодами
        :type periods: list
        :param start: начальный индекс
        :type start: int
        :param stop: последний индекс
        :type stop: int

        :return: клавиатура с годами
        :rtype: InlineKeyboardMarkup
        """
        kb_periods = InlineKeyboardMarkup()
        for i in range(start, stop):
            kb_periods.add(
                InlineKeyboardButton(text=periods[i],
                                     callback_data=f"p{periods[i]}")
            )
        return kb_periods

    def draw_extra_kb(
            self, periods: list, start: int, stop: int, *args
    ) -> InlineKeyboardMarkup:
        """
        Функция формирует дополнителные кнопки

        :param periods: список с периодами
        :type periods: list
        :param start: начальный индекс
        :type start: int
        :param stop: последний индекс
        :type stop: int

        :return: клавиатура с годами
        :rtype: InlineKeyboardMarkup
        """
        kb_periods = self.draw_periods(periods, start, stop)
        if args:
            buttons = [self.extra_kb[kb] for kb in args]
            kb_periods.add(*buttons)
            return kb_periods


def collect_keyboard(faq_category: str,
                     user_id: int,
                     bck_button: InlineKeyboardButton) \
        -> InlineKeyboardMarkup:
    """
    Функция формирует и возвращает клавиатуру из
    полученных из BQ данных, отфильтрованных по
    категории вопросов и user_id,

    :param faq_category: категория вопросов
    :type faq_category: str
    :param user_id: id пользователя
    :type user_id: int
    :param bck_button: объект InlineKeyboardButton
    :type bck_button: InlineKeyboardButton

    :return: клавиатура с вопросами
    :rtype: InlineKeyboardMarkup
    """

    selected_kb = InlineKeyboardMarkup(row_width=1)
    filtered_questions = db_manager.get_quest_faq(faq_category, user_id)

    for question in filtered_questions:
        button = InlineKeyboardButton(text=question[0],
                                      callback_data=question[0])
        selected_kb.add(button)

    selected_kb.add(bck_button)
    return selected_kb


def get_keyboard_for_graph(salary_period: str) -> InlineKeyboardMarkup:
    """
    Функция формирует кнопки для подтверждения отправки графка

    :param salary_period: ЗП
    :type salary_period: str

    :return: клавиатура с подтверждением
    :rtype: InlineKeyboardMarkup
    """
    accept = InlineKeyboardButton(text="Согласиться",
                                  callback_data=f"kb1{salary_period}")
    refuse = InlineKeyboardButton(text="Отказаться",
                                  callback_data=f"kb0{salary_period}")
    confirmed_kb = InlineKeyboardMarkup(row_width=2).add(accept, refuse)
    return confirmed_kb


fwd = InlineKeyboardButton(text=FaqKeyboard.FWD_STR,
                           callback_data=FaqKeyboard.FWD_STR)
bck = InlineKeyboardButton(text=FaqKeyboard.BCK_STR,
                           callback_data=FaqKeyboard.BCK_STR)
up = InlineKeyboardButton(text=FaqKeyboard.UP_STR,
                          callback_data=FaqKeyboard.UP_STR)
fin = InlineKeyboardButton(text=FaqKeyboard.FIN_STR,
                           callback_data=FaqKeyboard.FIN_STR)
org = InlineKeyboardButton(text=FaqKeyboard.ORG_STR,
                           callback_data=FaqKeyboard.ORG_STR)
oth = InlineKeyboardButton(text=FaqKeyboard.OT_STR,
                           callback_data=FaqKeyboard.OT_STR)
tech = InlineKeyboardButton(text=FaqKeyboard.TECH_STR,
                            callback_data=FaqKeyboard.TECH_STR)
acc = InlineKeyboardButton(text=FaqKeyboard.ACC_STR,
                           callback_data=FaqKeyboard.ACC_STR)


confirm = InlineKeyboardButton(text="Да", callback_data='Да')
dn_confirm = InlineKeyboardButton(text="Нет", callback_data='Нет')
close = InlineKeyboardButton(text="Закрыть", callback_data='Закрыть')

category_kb = InlineKeyboardMarkup(row_width=1).add(fin, org, acc, tech,
                                                    oth, close)
up_kb = InlineKeyboardMarkup(row_width=1).add(up)

yn_kb = InlineKeyboardMarkup(row_width=2).add(confirm, dn_confirm)
