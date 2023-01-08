import datetime as dt
import re
from typing import Generator

from dateutil.relativedelta import relativedelta

DateTuple = tuple[int]


def get_year_holidays(year: int) -> dt.date:
    brazilian_holidays = (
        dt.date(year, 1, 1),  # 1 de janeiro (Ano novo)
        dt.date(year, 4, 21),  # 21 de abril (Tiradentes)
        dt.date(year, 5, 1),  # 1 de maio (Dia do Trabalhador)
        dt.date(year, 9, 7),  # 7 de setembro (Dia da Independência)
        dt.date(year, 10, 12),  # 12 de outubro (Nossa Senhora Aparecida)
        dt.date(year, 11, 2),  # 2 de novembro (Dia do Finados)
        dt.date(year, 11, 15),  # 15 de novembro (Proclamação da República)
        dt.date(year, 12, 25),  # 25 de dezembro (Natal)
    )
    return brazilian_holidays


def carnaval_date(year: int) -> tuple[dt.date]:
    # https://www.vivaolinux.com.br/script/Calcular-a-data-do-Carnaval-e-da-Pascoa
    x = 24
    y = 5
    a = year % 19
    b = year % 4
    c = year % 7
    d = (19 * a + x) % 30
    e = (2 * b + 4 * c + 6 * d + y) % 7
    if (d + e) > 9:
        day = d + e - 9
        pascoa = dt.date(year, 4, day)
        month = 4
        data1 = dt.date(year, month, day)
        # O carnaval sera a subtração de 47 dias da data da pascoa
        carnaval = dt.date.fromordinal(data1.toordinal() - 47)
    else:
        day = d + e + 22
        pascoa = dt.date(year, 3, day)
        month = 3
        data1 = dt.date(year, month, day)
        carnaval = dt.date.fromordinal(data1.toordinal() - 47)
    return carnaval, pascoa


def valid_year(year: int) -> bool:
    return year > 1985 and year <= dt.date.today().year


def valid_month(year: int, month: int) -> bool:
    today = dt.date.today()
    if not valid_year(year):
        return False
    if month not in range(1, 13):
        return False
    if month == today.month and year == today.year:
        return False
    if year == today.year:
        return month < today.month
    else:
        if year == today.year - 1:
            return month >= today.month
    return False


def valid_day(datetuple: DateTuple) -> bool:
    year, month, day = datetuple
    return dt.date(year, month, day).year == dt.date.today().year


def valid_date(datetuple: DateTuple) -> bool:
    year, month, day = datetuple
    if day is None:
        return True
    date = dt.date(year, month, day)
    weekday = date.weekday()
    is_workday = weekday != 5 and weekday != 6
    is_holiday = any(date == holiday for holiday in get_year_holidays(year))
    return is_workday and not is_holiday


def date_range(start: DateTuple, end: DateTuple) -> Generator[DateTuple, None, None]:
    match start, end:
        case (int(), None, None), (int(), None, None):  # dates are yearly
            start_date = dt.date(start[0], 1, 1)
            end_date = dt.date(end[0], 1, 1)
            date = start_date
            while date <= end_date:
                datetuple = (date.year, None, None)
                yield datetuple
                date += dt.timedelta(year=1)

        case (int(), int(), None), (int(), int(), None):  # dates are monthly
            start_date = dt.date(start[0], start[1], 1)
            end_date = dt.date(end[0], end[1], 1)
            date = start_date
            while date <= end_date:
                datetuple = (date.year, date.month, None)
                yield datetuple
                date += relativedelta(months=+1)

        case (int(), int(), int()), (int(), int(), int()):  # dates are daily
            start_date = dt.date(*start)
            end_date = dt.date(*end)
            date = start_date
            while date <= end_date:
                datetuple = (date.year, date.month, date.day)
                if not valid_date(datetuple):
                    continue
                yield datetuple
                date += dt.timedelta(days=1)
        case _:
            print("Something is wrong with the arguments provided", start, end)


def expand_date_range(date_range: str) -> list[DateTuple]:
    dates = []
    start, end = sorted(date_range.split(":"))

    yearly_match = re.match(r"\d{4}:\d{4}", date_range)
    monthly_match = re.match(r"\d{4}-\d{2}:\d{4}-\d{2}", date_range)
    daily_match = re.match(r"\d{4}-\d{2}-\d{2}:\d{4}-\d{2}-\d{2}", date_range)

    if yearly_match:
        start, end = int(start), int(end)
        dates.extend([(year, None, None) for year in range(start, end + 1)])
    elif monthly_match:
        start_year, start_month = start.split("-")
        end_year, end_month = end.split("-")
        start_year, start_month = int(start_year), int(start_month)
        end_year, end_month = int(end_year), int(end_month)
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                if month < start_month and year == start_year:
                    continue
                elif month > end_month and year == end_year:
                    continue
                dates.append((year, month, None))
    elif daily_match:
        start_date = dt.datetime.strptime(start, "%Y-%m-%d").date()
        end_date = dt.datetime.strptime(end, "%Y-%m-%d").date()
        date = start_date
        while date <= end_date:
            dates.append((date.year, date.month, date.day))
            date += dt.timedelta(days=1)
    return dates


def parse_dates(dates_string: str) -> list[DateTuple]:
    if ":" in dates_string:
        return expand_date_range(dates_string)
    tz = dt.timezone(dt.timedelta(hours=-3))
    if dates_string == "today":
        now = dt.datetime.now(tz)
        return [(now.year, now.month, now.day)]
    if dates_string == "yesterday":
        now = dt.datetime.now(tz)
        return [(now.year, now.month, now.day - 1)]
    year_match = re.match(r"^\d{4}$", dates_string)
    month_match = re.match(r"^\d{4}-\d{2}$", dates_string)
    day_match = re.match(r"^\d{4}-\d{2}-\d{2}$", dates_string)
    year = month = day = None
    if year_match:
        year = int(dates_string)
    elif month_match:
        year, month = dates_string.split("-")
        year, month = int(year), int(month)
    elif day_match:
        year, month, day = dates_string.split("-")
        year, month, day = int(year), int(month), int(day)
    return [(year, month, day)]
