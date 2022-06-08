from datetime import datetime

import requests


def is_day_off(date: datetime.date) -> bool:
    """
    Возвращает True, если выходной день.

    :param date: проверяемая дата
    :type date: datetime.date

    :return: True or False
    :rtype: bool
    """

    year, month, day = date.year, date.month, date.day
    link: str = (
        f"https://isdayoff.ru/api/getdata?year={year}&month={month}&day={day}"
    )
    response: requests.Response = requests.get(url=link)
    return response.ok and response.text != "0"
