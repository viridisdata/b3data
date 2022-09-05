import datetime as dt

DateTuple = tuple[int]


class InvalidDate(Exception):
    pass


def carnaval_date(year: int) -> tuple[dt.date]:
    # https://www.vivaolinux.com.br/script/Calcular-a-data-do-Carnaval-e-da-Pascoa
    x = 24
    y = 5
    a = year % 19
    b = year % 4
    c = year % 7
    d = (19 * a + x) % 30
    e = (2 * b + 4 * c + 6 * d + y) % 7
    if ((d + e) > 9):
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
    brazillian_holidays = (
        dt.date(year, 1, 1),    # 1 de janeiro (Ano novo)
        dt.date(year, 4, 21),   # 21 de abril (Tiradentes)
        dt.date(year, 5, 1),    # 1 de maio (Dia do Trabalhador)
        dt.date(year, 9, 7),    # 7 de setembro (Dia da Independência)
        dt.date(year, 10, 12),  # 12 de outubro (Nossa Senhora Aparecida)
        dt.date(year, 11, 2),   # 2 de novembro (Dia do Finados)
        dt.date(year, 11, 15),  # 15 de novembro (Proclamação da República)
        dt.date(year, 12, 25),  # 25 de dezembro (Natal)
    )
    is_holiday = any(date == holiday for holiday in brazillian_holidays)
    return is_workday and not is_holiday
