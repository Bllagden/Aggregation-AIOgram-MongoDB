from datetime import datetime, timedelta
from typing import Literal

from dateutil.relativedelta import relativedelta
from motor.core import AgnosticCollection

from db import create_session

GROUP_TYPE = Literal["year", "month", "day", "hour", "minute"]
YEAR_FORMAT = "%Y-01-01T00:00:00"
MONTH_FORMAT = "%Y-%m-01T00:00:00"
DAY_FORMAT = "%Y-%m-%dT00:00:00"
HOUR_FORMAT = "%Y-%m-%dT%H:00:00"
MINUTE_FORMAT = "%Y-%m-%dT%H:%M:00"


async def aggregate_salaries(
    collection: AgnosticCollection,
    dt_from: str,
    dt_upto: str,
    group_type: GROUP_TYPE,
) -> dict[str, list]:

    dt_from: datetime = _str_to_datetime(dt_from)
    dt_upto: datetime = _str_to_datetime(dt_upto)
    group_format: str = _define_group_type(group_type)
    pipeline = _create_pipeline(dt_from, dt_upto, group_format)

    async def coro(session) -> list[dict]:
        """results = [{'total': 8177, 'date': '2022-02-01T00:00:00'}, ... , {...}]"""
        cursor = collection.aggregate(pipeline, session=session)
        results: list[dict] = []
        async for document in cursor:
            results.append(document)
        return results

    async with create_session() as session:
        results: list[dict] = await session.with_transaction(coro)

    all_dates: list[str] = _create_all_dates(dt_from, dt_upto, group_format)
    if len(results) != len(all_dates):
        return _convert_results(_fill_missing_dates(results, all_dates))
    return _convert_results(results)


def _str_to_datetime(_date: str, _format: str = "%Y-%m-%dT%H:%M:%S") -> datetime:
    try:
        return datetime.strptime(_date, _format)
    except ValueError as e:
        raise ValueError(f"Error converting date: {e}")


def _define_group_type(group_type: GROUP_TYPE) -> str:
    """``Example``:
    if group_type == 'month': return '%Y-%m-01T00:00:00'"""
    if group_type == "year":
        return YEAR_FORMAT
    elif group_type == "month":
        return MONTH_FORMAT
    elif group_type == "day":
        return DAY_FORMAT
    elif group_type == "hour":
        return HOUR_FORMAT
    elif group_type == "minute":
        return MINUTE_FORMAT
    else:
        raise ValueError(f"Unsupported group_type: {group_type}")


def _create_pipeline(
    dt_from: datetime,
    dt_upto: datetime,
    group_format: str,
) -> list[dict]:

    match_stage = {"$match": {"dt": {"$gte": dt_from, "$lte": dt_upto}}}

    group_stage = {
        "$group": {
            "_id": {"$dateToString": {"format": group_format, "date": "$dt"}},
            "total": {"$sum": "$value"},
        }
    }

    project_stage = {
        "$project": {
            "_id": 0,
            "date": "$_id",
            "total": 1,
        }
    }
    sort_stage = {"$sort": {"date": 1}}

    return [match_stage, group_stage, project_stage, sort_stage]


def _create_all_dates(
    dt_from: datetime,
    dt_upto: datetime,
    group_format: str,
) -> list[str]:
    """Вычисление списка всех возможных дат промежутка для добавления недостающих дат.
    ``all_dates`` = ['2022-02-01T00:00:00', '2022-02-01T01:00:00', ...]"""
    all_dates: list[str] = []
    dt = dt_from

    if group_format == YEAR_FORMAT:
        _timedelta = relativedelta(years=1)
    elif group_format == MONTH_FORMAT:
        _timedelta = relativedelta(months=1)
    elif group_format == DAY_FORMAT:
        _timedelta = timedelta(days=1)
    elif group_format == HOUR_FORMAT:
        _timedelta = timedelta(hours=1)
    elif group_format == MINUTE_FORMAT:
        _timedelta = timedelta(minutes=1)

    while dt <= dt_upto:
        all_dates.append(dt.strftime(group_format))  # append (datetime to str)
        dt += _timedelta
    return all_dates


def _convert_results(results: list[dict]) -> dict[str, list]:
    """``return``:

    {
    'dataset': [5906586, 5515874, 5889803, 6092634],
    'labels': ['2022-09-01T00:00:00', '2022-10-01T00:00:00',
                '2022-11-01T00:00:00', '2022-12-01T00:00:00']
    }"""
    if results:
        dataset: list[int] = [res["total"] for res in results]
        labels: list[str] = [res["date"] for res in results]
        return {"dataset": dataset, "labels": labels}
    return dict()


def _fill_missing_dates(results: list[dict], all_dates: list[str]) -> list[dict]:
    """Добавление недостающих дат вместе с нулевыми 'total'.

    ``results`` = [{'total': 8177, 'date': '2022-02-01T00:00:00'}, ... , {...}] -
    (входные данные).

    ``results_dict`` = {'2022-02-01T00:00:00': 8177, '2022-02-01T01:00:00': 8407, ...} -
    (нужен для удобства поиска дат при создании filled_results).

    ``filled_results`` - как 'results', но с недостающими датами и нулевыми 'total' для них.
    """
    results_dict: dict[str, int]
    results_dict = {result["date"]: result["total"] for result in results}

    filled_results: list[dict]
    filled_results = [
        {"total": results_dict.get(date, 0), "date": date} for date in all_dates
    ]
    return filled_results
