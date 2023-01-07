import datetime as dt
from pathlib import Path
from typing import Iterable

import httpx

from .dates import DateTuple, valid_date


def get_url(datetuple: DateTuple) -> str:
    BASE_URL = "https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_"
    year, month, day = datetuple
    match datetuple:
        case int(), None, None:
            return f"{BASE_URL}A{year}.zip"
        case int(), int(), None:
            return f"{BASE_URL}M{month:02}{year}.zip"
        case int(), int(), int():
            return f"{BASE_URL}D{day:02}{month:02}{year}.zip"


def get_filename(datetuple: DateTuple, modified: dt.datetime = None) -> str:
    year, month, day = datetuple
    dataset_name = "cotacaohistorica"
    str_modified = f"{modified:%Y%m%d%H%M}"
    match datetuple:
        case int(), None, None:
            str_date = f"{year}"
        case int(), int(), None:
            str_date = f"{year}{month:02}"
        case int(), int(), int():
            str_date = f"{year}{month:02}{day:02}"
    return f"{dataset_name}_{str_date}_{str_modified}.zip"


def get_dest_filepath(
    datadir: Path,
    datetuple: DateTuple,
    modified: dt.date = None,
) -> Path:
    year, _, _ = datetuple
    filename = get_filename(datetuple, modified)
    return datadir / f"{year}" / filename


def get_resource_metadata(datetuple: DateTuple, client: httpx.Client):
    # Get URL
    url = get_url(datetuple)

    # Get Metadata ------------------------------------------------------------
    r = client.head(url)

    if r.status_code != 200:
        print(f"Error fetching {url}: {r.status_code}")
        r.raise_for_status()
    elif r.headers.get("Content-Type") != "application/x-zip-compressed":
        error_msg = f"Error fetching {url}: {r.headers.get('content-type')}"
        raise Exception(error_msg)

    size = int(r.headers.get("Content-Length", 0))

    modified = r.headers.get("Last-Modified")
    if modified:
        modified = dt.datetime.strptime(modified, "%a, %d %b %Y %H:%M:%S %Z")

    return {
        "url": url,
        "modified": modified,
        "size": size,
    }


def fetch_data_file(
    datadir: Path,
    datetuple: DateTuple,
    client: httpx.Client,
    blocksize: int = 8192,
) -> Path:
    # Check if date is valid
    if not valid_date(datetuple):
        raise ValueError(f"Invalid date {datetuple}")
    url = get_url(datetuple)

    # Get Metadata ------------------------------------------------------------
    metadata = get_resource_metadata(datetuple=datetuple, client=client)
    modified = metadata["modified"]

    # Destination file path ---------------------------------------------------
    dest_filepath = get_dest_filepath(datadir, datetuple, modified)
    if dest_filepath.exists():
        return
    dest_filepath.parent.mkdir(parents=True, exist_ok=True)

    # Actual download ---------------------------------------------------------
    with client.stream("GET", url) as r:
        with open(dest_filepath, "wb") as f:
            for chunk in r.iter_bytes(blocksize):
                f.write(chunk)

    return dest_filepath


def fetch_dates(
    dates: Iterable[tuple[int | None]],
    output: Path,
    http_headers: dict[str, str] = None,
):
    """Fetch a list of data files based on `dates` iterable"""
    client = httpx.Client(headers=http_headers, verify=False)
    for date in dates:
        try:
            fetch_data_file(
                datadir=output,
                datetuple=date,
                client=client,
            )
        except ValueError:
            print(f"Invalid date: {date}")
        except httpx.HTTPStatusError:
            print(f"HTTP error: {date}")
