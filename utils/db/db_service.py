import logging
from datetime import datetime
from typing import Union

from aiogram.types import Message
from google.cloud import bigquery

from utils.decorators import bq_error_handler

from .storage import AbstractDBManager


class DBManager(AbstractDBManager):
    """
    Данный класс содержит методы для работы с базой данных

    Args:
    credentials (service_account.Credentials): файл доступа
    project (str): название проекта
    bqclient(bigquery.Client): клиент
    """

    def make_query(self, query: str) -> \
            Union[bigquery.table.RowIterator, bool]:
        """
        Отправляет запрос и возвращает результат

        :param query: запрос
        :type query: str

        :return: объект Bigquery
        :rtype: bigquery.table.RowIterator, bool
        """

        query_job = self.bqclient.query(query)
        return query_job.result()

    @bq_error_handler
    async def check_user(self, message: Message) -> bool:
        """
        Возвращает зарегистрирован ли пользователь

        :param message: сообщение пользователя
        :type message: Message

        :return: True or False
        :rtype: bool
        """

        tg_id = message.from_user.id

        qry: str = (f"SELECT telegram_id FROM "
                    f"TG_Bot_Stager.users "
                    f"WHERE telegram_id = {tg_id} AND "
                    f"is_confirmed = true")

        return len(list(self.make_query(qry))) != 0

    @bq_error_handler
    async def check_user_role(self, message: Message, role: str) \
            -> bool:
        """
        Проверяет пользователя на права админа, возвращает True/False

        :param message: сообщение пользователя
        :type message: Message
        :param role: проверяемая роль
        :type role: str

        :return: True or False
        :rtype: bool
        """

        tg_id = message.from_user.id

        qry: str = (f"SELECT role FROM TG_Bot_Stager.users "
                    f"WHERE telegram_id = {tg_id}")

        if list(self.make_query(qry))[0][0] == role:
            return True
        return False

    @bq_error_handler
    async def check_auth(self, message: Message) -> bool:
        """
        Возвращает авторизован ли пользователь

        :param message: сообщение пользователя
        :type message: Message

        :return: True or False
        :rtype: bool
        """

        tg_id = int(message.from_user.id)
        email = message.text

        qry: str = (f"SELECT telegram_id FROM "
                    f"TG_Bot_Stager.users "
                    f"WHERE telegram_id = {tg_id} AND"
                    f" is_confirmed = false AND"
                    f" email = '{email}'")
        return len(list(self.make_query(qry))) != 0

    @bq_error_handler
    async def registration(self, message: Message) -> None:
        """
        Записывает пользователя

        :param message: сообщение пользователя из которого ожидается email
        :type message: types.Message

        :return: None
        :rtype: NoneType
        """

        tg_id = message.from_user.id
        tg_name = f"@{message.from_user.username}"
        email = message.text
        date = str(datetime.now().today())
        query: str = (
            f"INSERT INTO TG_Bot_Stager.users"
            f"(telegram_id, telegram_name, email, registration_code, "
            f"is_confirmed, regiestred_at, is_active, role)"
            f" VALUES ({tg_id}, '{tg_name}', '{email}', "
            f"'{None}', {False}, '{date}', {True}, '{None}')"
        )

        self.make_query(query)

    @bq_error_handler
    async def authentication(self, message: Message, email: str) -> None:
        """
        Аутентифицирует пользователя

        :param message: сообщение пользователя из которого ожидается
        secret key
        :type message: types.Message
        :param email: email пользователя
        :type email: str

        :return: None
        :rtype: NoneType
        """

        tg_id: int = message.from_user.id
        secret_key: str = message.text
        query: str = (f"UPDATE TG_Bot_Stager.users"
                      f" SET is_confirmed = true ,"
                      f" registration_code = '{secret_key}'"
                      f" WHERE telegram_id = {tg_id} AND"
                      f" email = '{email}'")

        self.make_query(query)

    def send_to_blacklist(self, user_id: int) -> None:
        """
        Отправляет в bigquery значение поля "is_active" True для юзера
        добавляет в блэклист простыми словами
        :param user_id: сообщение пользователя
        :type user_id: int

        :return: None
        :rtype: NoneType
        """

        tg_id: int = user_id
        query: str = (
            f"UPDATE TG_Bot_Stager.users"
            f" SET is_active = false"
            f" WHERE telegram_id = {tg_id}"
        )
        try:
            self.make_query(query)
        except Exception as e:
            logging.error(e)

    def remove_from_blacklist(self, user_id: int) -> None:
        """
        Отправляет в bigquery значение поля "is_active" False для юзера
        убирает из блэклиста простыми словами

        :param user_id: id пользователя
        :type user_id: int

        :return: None
        :rtype: NoneType
        """

        tg_id: int = user_id
        query: str = (
            f"UPDATE TG_Bot_Stager.users"
            f" SET is_active = true"
            f" WHERE telegram_id = {tg_id}"
        )
        try:
            self.make_query(query)
        except Exception as e:
            logging.error(e)

    @bq_error_handler
    async def check_black_list(self, message: Message) -> bool:
        """
        Возвращает True, если пользователь в блэклисте

        :param message: сообщение пользователя
        :type message: Message

        :return: True or False
        :rtype: bool
        """

        tg_id: int = message.from_user.id
        query: str = (
            f"SELECT telegram_id FROM TG_Bot_Stager."
            f"users WHERE telegram_id = {tg_id} AND is_active = false"
        )

        return not (self.make_query(query).total_rows == 0)

    def send_task_to_bq(self,
                        user_id:
                        int, message_text: str,
                        planned_at: datetime,
                        created_at: datetime) \
            -> Union[bigquery.table.RowIterator, bool]:
        """
         Отправляет данные о событии в хранилище BigQuery
        :param user_id: id пользователя
        :type user_id: int
        :param message_text: текст дл напоминания
        :type message_text: str
        :param planned_at: дата события
        :type planned_at: datetime
        :param created_at: время создания
        :type created_at: datetime
        :return: True/False или объект Bigquery
        :rtype: bigquery.table.RowIterator or bool
        """

        query: str = (
            f"INSERT INTO TG_Bot_Stager.remind_msg"
            f"(telegram_id, message_text, planned_at, is_sent, created_at)"
            f" VALUES ({user_id}, '{message_text}', '{planned_at}', {True},"
            f"'{created_at}')"
        )
        try:
            self.make_query(query)
            return True
        except Exception as e:
            logging.error(e)
            return False

    def get_reminder_text(self, planned_at: datetime) -> list:

        """
        Функция выгружает из БД сообщение напоминание

        :param planned_at: дата события
        :type planned_at: datetime

        :return: напоминание для пользователя
        :rtype: list
        """

        query: str = (
            f"SELECT * FROM "
            f"TG_Bot_Stager.remind_msg WHERE "
            f"planned_at = DATETIME({planned_at.year}, {planned_at.month}, "
            f"{planned_at.day}, {planned_at.hour},{planned_at.minute}, 0) "
        )

        try:
            return list(self.make_query(query))
        except Exception as e:
            logging.error(e)

    def get_df_for_graph(self,
                         user_id: int,
                         salary_period: datetime.date
                         ) -> bigquery.table.RowIterator:

        """
        Формирует Dataframe через запрос к БД

        :param user_id: id пользователя
        :type user_id: int
        :param salary_period: дата составления графика
        :type salary_period: datetime.date

        :return: объект Bigquery
        :rtype: bigquery.table.RowIterator
        """
        query: str = (
            f"SELECT  trackdate, projectName, SUM(timefact) AS time FROM "
            f"TG_Bot_Stager.salaryDetailsByTrackdate  "
            f"WHERE  telegram_id = {user_id} and (salaryPeriod = "
            f"'{salary_period}' "
            f"OR notApprovedSalaryPeriod  = '{salary_period}')"
            f" GROUP BY telegram_id, "
            f"trackdate, projectName, salaryPeriod, notApprovedSalaryPeriod "
            f" order by trackdate "
        )

        try:
            return self.make_query(query)
        except Exception as e:
            logging.error(e)

    def get_salary_periods_user(self,
                                user_id: int)\
            -> bigquery.table.RowIterator:
        """
        Функция выгружает из БД зарплатные периоды

        :param user_id: id пользователя
        :type user_id: int

        :return: объект Bigquery
        :rtype: bigquery.table.RowIterator
        """

        query: str = (
            f"SELECT DISTINCT salaryPeriod, notApprovedSalaryPeriod"
            f" FROM TG_Bot_Stager.salaryDetailsByTrackdate "
            f"WHERE telegram_id ={user_id}"
        )
        try:
            return self.make_query(query)
        except Exception as e:
            logging.error(e)

    def get_df_for_faq(self, faq_key: str) -> list:
        """
        Функция выгружает из БД ответ по ключу FAQ и
        возвращает в строковом виде

        :param faq_key: ключ записи
        :type faq_key: str

        :return: ответ для пользоватееля
        :rtype: list
        """

        query: str = (f"SELECT * FROM "
                      f"TG_Bot_Stager.faq_datas "
                      f"WHERE key ='{faq_key}'")
        try:
            return list(self.make_query(query))[0][3]
        except Exception as e:
            logging.error(e)

    def get_quest_faq(self, faq_category: str, user_id: int) \
            -> bigquery.table.RowIterator:
        """
        Функция выгружает из БД вопросы по категории
        и id пользователя, возвращает список

        :param faq_category: категории вопросов
        :type faq_category: str
        :param user_id: id пользователя
        :type user_id: int

        :return: объект Bigquery
        :rtype: bigquery.table.RowIterator
        """

        query: str = (f"SELECT question, role, key "
                      f"FROM TG_Bot_Stager.faq_datas "
                      f"WHERE key LIKE '{faq_category}%' "
                      f"AND (role LIKE CONCAT('%', (SELECT role "
                      f"FROM handy-digit-312214.TG_Bot_Stager.users "
                      f"WHERE telegram_id ={user_id}), '%') "
                      f"OR role = 'common')")

        try:
            return self.make_query(query)
        except Exception as e:
            logging.error(e)

    def send_confirm_for_salaryperiod(
            self, user_id: int,
            message_id: int,
            mailing_date: datetime,
            salary_period: str) -> None:
        """
        Функция добавляет в БД данные по зарплатному периоду

        :param user_id: id пользователя
        :type user_id: int
        :param message_id: id сообщения
        :type message_id: int
        :param mailing_date: дата отправки
        :type mailing_date: datetime
        :param salary_period: зарплатный период
        :type salary_period: str

        :return: None
        :rtype: NoneType
        """

        query: str = (
            f"INSERT INTO TG_Bot_Stager.salary_response"
            f"(mailing_date, telegram_id, message_id, salary_period)"
            f"VALUES ('{mailing_date.strftime('%Y-%m-%d %H:%M:%S')}',"
            f"{user_id}, "
            f"{message_id},'{salary_period}')"
        )
        try:
            self.make_query(query)
        except Exception as e:
            logging.error(e)

    def update_data_for_salaryperiod(
            self,
            user_id: int,
            salary_period: str,
            is_confirmed: bool,
            response_comment: str,
            confirmed_at: datetime
    ) -> None:
        """
        Функция обновляет значения согласовано/не согласовано отработанное
        время, проставляет время согласования и заполняет поле комментарий,
        если он есть

        :param user_id: id пользователя
        :type user_id: int
        :param salary_period: ЗП
        :type salary_period: str
        :param is_confirmed: статус подтверждения
        :type is_confirmed: bool
        :param response_comment: комментарий пользователя
        :type response_comment: str
        :param confirmed_at: время подтверждения
        :type confirmed_at: datetime

        :return: None
        :rtype: NoneType
        """

        if response_comment:
            query: str = (
                f"UPDATE TG_Bot_Stager.salary_response "
                f"SET is_confirmed = {is_confirmed}, "
                f"response_comment = '{response_comment}', "
                f"confirmed_at = "
                f"'{confirmed_at.strftime('%Y-%m-%d %H:%M:%S')}'"
                f"WHERE telegram_id = {user_id} "
                f"AND salary_period = '{salary_period}' "
            )

        else:
            query: str = (
                f"UPDATE TG_Bot_Stager.salary_response "
                f"SET is_confirmed = {is_confirmed}, "
                f"confirmed_at = "
                f"'{confirmed_at.strftime('%Y-%m-%d %H:%M:%S')}'"
                f"WHERE telegram_id = {user_id} "
                f"AND salary_period = '{salary_period}'"
            )
        try:
            self.make_query(query)
        except Exception as e:
            logging.error(e)

    def get_df_for_search(self, parse_data: dict)\
            -> bigquery.table.RowIterator:
        """
        Функция выгружает из БД ФИО, email, имя в телеграме
        согласно запрошенным данным

        :param parse_data: словарь с данными поиска
        :type parse_data: dict

        :return: объект Bigquery
        :rtype: bigquery.table.RowIterator
        """

        query_data: str = f"""SELECT DISTINCT fullname, email, telegram_name
                     FROM TG_Bot_Stager.dev_search_view \
                     WHERE fullname LIKE '%{parse_data['full_name'][0]}%' OR \
                     fullname LIKE '%{parse_data['full_name'][-1]}%' OR \
                     email LIKE '%{parse_data['email']}%' OR \
                     telegram_name LIKE '%{parse_data['telegram_name']}%';"""
        try:
            return self.make_query(query_data)
        except Exception as e:
            logging.error(e)

    def get_users_salaryperiod(
            self,
            salary_period: str
    ) -> bigquery.table.RowIterator:
        """
        Функция выгружает из БД всех пользователей по заданному периоду

        :param salary_period: зарплатный период
        :type salary_period: str

        :return: объект Bigquery
        :rtype: bigquery.table.RowIterator
        """

        query: str = (f"SELECT us.telegram_id, sal.trackdate,"
                      f"sal.projectName, SUM(sal.timefact) as time "
                      f"FROM TG_Bot_Stager.users as us "
                      f"JOIN TG_Bot_Stager.salaryDetailsByTrackdate as sal "
                      f"ON us.telegram_id = sal.telegram_id "
                      f"WHERE  us.is_active = True AND us.is_confirmed = True "
                      f"AND (sal.salaryPeriod = '{salary_period}'"
                      f"OR sal.notApprovedSalaryPeriod  = '{salary_period}')"
                      f"GROUP BY us.telegram_id, sal.trackdate,"
                      f" sal.projectName"
                      f" ORDER BY us.telegram_id "
                      )
        try:
            return self.make_query(query)
        except Exception as e:
            logging.error(e)

    def get_user_id_list(self, confirm_flag=True) -> list:
        """
        Метод выводит список telegram_id
        уникальных подтвержденных сотрудников из бд

        :return: список уникальных сотрудников
        :rtype: list
        """
        if confirm_flag:
            query = (
                "SELECT DISTINCT telegram_id "
                "FROM TG_Bot_Stager.users "
                "WHERE is_confirmed is true"
            )
        else:
            query = (
                "SELECT DISTINCT telegram_id "
                "FROM TG_Bot_Stager.users"
            )
        try:
            result = list(self.make_query(query=query))
            return result
        except Exception as e:
            logging.error(e)
