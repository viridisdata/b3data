
__version__ = "0.1.0"

import datetime as dt
from pathlib import Path

import httpx
from tqdm import tqdm

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


def get_url(datetuple: DateTuple) -> str:
    BASE_URL = "https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_"
    year, month, day = datetuple
    if month is None:
        return f"{BASE_URL}A{year}.zip"
    elif day is None:
        return f"{BASE_URL}M{month:02}{year}.zip"
    else:
        return f"{BASE_URL}D{day:02}{month:02}{year}.zip"


def get_filename(datetuple: DateTuple, modified: dt.datetime = None) -> str:
    year, month, day = datetuple
    dataset_name = "cotacaohistorica"
    if month is None:
        return f"{dataset_name}_{year}_{modified:%Y%m%d}.zip"
    elif day is None:
        return f"{dataset_name}_{year}{month:02}_{modified:%Y%m%d}.zip"
    else:
        return f"{dataset_name}_{year}{month:02}{day:02}_{modified:%Y%m%d}.zip"


def get_dest_filepath(
    datadir: Path,
    datetuple: DateTuple,
    modified: dt.date = None,
) -> Path:
    year, _, _ = datetuple
    filename = get_filename(datetuple, modified)
    return datadir / f"{year}" / filename


def fetch_data_file(
    datadir: Path,
    datetuple: DateTuple,
    client: httpx.Client = None,
    blocksize: int = 8192,
) -> None:
    if not valid_date(datetuple):
        raise InvalidDate(f"Invalid date {datetuple}")
    year, month, day = datetuple
    url = get_url(datetuple)
    if client is not None:
        r = client.get(url)
    else:
        r = httpx.get(url, verify=False)

    if r.status_code != 200:
        print(f"Error fetching {url}: {r.status_code}")
        r.raise_for_status()
    elif r.headers.get("content-type") != "application/x-zip-compressed":
        error_msg = f"Error fetching {url}: {r.headers.get('content-type')}"
        raise Exception(error_msg)

    file_size = int(r.headers.get("content-length", 0))
    modified = r.headers.get("last-modified")
    if modified:
        modified = dt.datetime.strptime(modified, "%a, %d %b %Y %H:%M:%S %Z")

    # Destination file path
    dest_filepath = get_dest_filepath(datadir, datetuple, modified)
    if dest_filepath.exists():
        return
    elif not dest_filepath.parent.exists():
        dest_filepath.parent.mkdir(parents=True)

    progress = tqdm(
        total=file_size,
        unit="B",
        unit_scale=True,
        desc=f"{dest_filepath.name}",
    )
    with open(dest_filepath, "wb") as f:
        for chunk in r.iter_bytes(blocksize):
            f.write(chunk)
            progress.update(len(chunk))
    progress.close()
