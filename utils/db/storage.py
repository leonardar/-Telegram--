from abc import ABC, abstractmethod
from datetime import datetime

from aiogram.types import Message
from google.cloud import bigquery


class AbstractDBManager(ABC):
    def __init__(self, credentials, project):
        self.credentials = credentials
        self.project = project
        self.bqclient = bigquery.Client(credentials=self.credentials)

    @abstractmethod
    def make_query(self, query: str):
        pass

    @abstractmethod
    def check_user(self, message: Message):
        pass

    @abstractmethod
    def check_user_role(self, message: Message, role: str) -> bool or str:
        pass

    @abstractmethod
    def check_auth(self, message: Message):
        pass

    @abstractmethod
    def registration(self, message: Message):
        pass

    @abstractmethod
    def authentication(self, message: Message):
        pass

    @abstractmethod
    def send_to_blacklist(self, user_id: int):
        pass

    @abstractmethod
    def remove_from_blacklist(self, user_id: int):
        pass

    @abstractmethod
    def check_black_list(self, message: Message):
        pass

    @abstractmethod
    def send_task_to_bq(self,
                        user_id: int,
                        message_text: str,
                        planned_at: datetime,
                        created_at: datetime):
        pass

    @abstractmethod
    def get_reminder_text(self, planned_at: datetime):
        pass

    @abstractmethod
    def get_df_for_graph(self, user_id: int, salary_period: datetime.date):
        pass

    @abstractmethod
    def get_salary_periods_user(self, user_id: int):
        pass

    @abstractmethod
    def get_df_for_faq(self, faq_key: str):
        pass

    @abstractmethod
    def send_confirm_for_salaryperiod(
            self, user_id: int,
            message_id: int,
            mailing_date: datetime,
            salary_period: str) -> None:
        pass

    @abstractmethod
    def update_data_for_salaryperiod(
            self,
            user_id: int,
            message_id: int,
            is_confirmed: bool,
            response_comment: str,
            cofirmed_at: datetime
    ) -> None:
        pass

    @abstractmethod
    def get_df_for_search(self, parse_data: dict):
        pass

    @abstractmethod
    def get_users_salaryperiod(
            self,
            salary_period: str
    ) -> bigquery.table.RowIterator:
        pass

    @abstractmethod
    def get_user_id_list(self):
        pass
