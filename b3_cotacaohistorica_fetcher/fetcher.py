import datetime as dt
import logging
import sys
from pathlib import Path

import httpx

from .dates import DateTuple, InvalidDate, valid_date

logger = logging.getLogger(__name__)


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
    client: httpx.Client,
    blocksize: int = 8192,
) -> None:
    if not valid_date(datetuple):
        raise InvalidDate(f"Invalid date {datetuple}")
    year, month, day = datetuple
    url = get_url(datetuple)

    # Get Metadata ------------------------------------------------------------
    r = client.head(url)
    if r.status_code != 200:
        print(f"Error fetching {url}: {r.status_code}")
        r.raise_for_status()
    elif r.headers.get("Content-Type") != "application/x-zip-compressed":
        error_msg = f"Error fetching {url}: {r.headers.get('content-type')}"
        raise Exception(error_msg)
    file_size = int(r.headers.get("Content-Length", 0))
    modified = r.headers.get("Last-Modified")
    if modified:
        modified = dt.datetime.strptime(modified, "%a, %d %b %Y %H:%M:%S %Z")

    # Destination file path ---------------------------------------------------
    dest_filepath = get_dest_filepath(datadir, datetuple, modified)
    if dest_filepath.exists():
        return
    dest_filepath.parent.mkdir(parents=True, exist_ok=True)

    str_file_size = f"{file_size/10**6:.2f} MB"

    logger.info(
        f"Downloading file {url} -> {dest_filepath}\n"
        f"File size: {str_file_size}\n"
        f"Timestamp: {modified:%Y-%m-%d %H:%M}"
    )

    # Actual download ---------------------------------------------------------
    downloaded_size = 0
    with client.stream("GET", url) as r:
        with open(dest_filepath, "wb") as f:
            for chunk in r.iter_bytes(blocksize):
                f.write(chunk)
                downloaded_size += len(chunk)
                perc = (downloaded_size / file_size) * 100
                sys.stdout.write(
                    f"{downloaded_size/10**6:.2f} MB "
                    f"of {str_file_size} "
                    f"[{perc: >6.2f}%]\r"
                )
                sys.stdout.flush()
    sys.stdout.write("\n")
    sys.stdout.flush()


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
