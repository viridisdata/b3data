import datetime as dt
from pathlib import Path

import httpx
from tqdm import tqdm

from .dates import DateTuple, InvalidDate, valid_date


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


def fetch_dates(dates, output, http_headers=None):
    client = httpx.Client(headers=http_headers, verify=False)
    for date in dates:
        try:
            fetch_data_file(
                datadir=output,
                datetuple=date,
                client=client,
            )
        except InvalidDate:
            print(f"Invalid date: {date}")
        except httpx.HTTPStatusError:
            print(f"HTTP error: {date}")
