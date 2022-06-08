from io import BytesIO
import pandas.core.series
from matplotlib.pyplot import figure
from numpy import arange
from pandas import DataFrame, date_range, to_datetime
from seaborn import histplot


from utils import constants


def get_salary_period(today) -> str:
    """
    Формирует строку зарплатного периода.

    :param today: день для определения зарплатного периода
    :type today: datetime.date

    :return: строка зарплатного периода
    :rtype: str
    """

    day: int = today.day
    month: int = today.month
    year: str = today.strftime("%y")

    if day < 6 or day > 20:
        salary_period = f"ЗП-{constants.MONTHS[month]}{year}"
    else:
        salary_period = f"Аванс-{constants.MONTHS[month]}{year}"
    return salary_period


def get_xlabel_for_graph(df: [DataFrame]) -> DataFrame:
    """
    Формирует Dataframe дат и возвращает столбец дата(день недели)

    :param df: Dataframe из БД
    :type df: pandas.core.frame.DataFrame

    :return: столбец дата(день недели)
    :rtype: pandas.core.frame.DataFrame
    """

    set_date: set = set(df["trackdate"])
    df_xlabel = DataFrame(
        {"trackdate": date_range(start=min(set_date), end=max(set_date))}
    )
    df_xlabel["dayOfWeek"] = to_datetime(df_xlabel.trackdate).dt.dayofweek.map(
        constants.DAYS_OF_THE_WEEK
    )
    df_xlabel["xticklabels"] = (
        df_xlabel["trackdate"].astype(str) + "(" + df_xlabel.dayOfWeek + ")"
    )
    return df_xlabel.xticklabels


def get_image(df: DataFrame, xlabel: [pandas.core.series.Series]) -> bytes:
    """
    Формирует и сохраняет картинку с графиком.

    :param df: Dataframe из БД
    :type df: pandas.core.frame.DataFrame
    :param xlabel: набор данных для подписи тиков по оси Х
    :type xlabel: pandas.core.series.Series

    :return: Возвращет график
    :rtype: bytes
    """

    fig = figure(figsize=(16, 8))
    graph = histplot(
        df,
        x="trackdate",
        weights="time",
        hue="projectName",
        multiple="stack",
        shrink=0.8,
    )

    mids = [rect.get_x() + rect.get_width() / 2 for rect in graph.patches]

    x_label_mids = list(set(mids))
    x_label_mids.sort()

    graph.set_xticks(x_label_mids)
    graph.set_xticklabels(xlabel.tolist())

    max_hour: int = max(df.groupby(["trackdate"])["time"].sum())
    graph.set_yticks(arange(0, max_hour + 1, 1))

    graph.set_xlabel("Дни")
    graph.set_ylabel("Часы")

    fig.autofmt_xdate()

    # Сохранение в буфер

    buffer = BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    return image_png
