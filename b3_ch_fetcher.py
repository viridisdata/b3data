
__version__ = "0.0.1"

import os
import pathlib
from typing import Union
from urllib import request


def get_url(year: int, month: int = None, day: int = None) -> str:
    BASE_URL = "http://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_"
    if month is None:
        return f"{BASE_URL}A{year}.zip"
    elif day is None:
        return f"{BASE_URL}M{month:02}{year}.zip"
    else:
        return f"{BASE_URL}D{day:02}{month:02}{year}.zip"


def get_filename(year: int, month: int = None, day: int = None) -> str:
    if month is None:
        return f"{year}.zip"
    elif day is None:
        return f"{year}{month:02}.zip"
    else:
        return f"{year}{month:02}{day:02}.zip"


def download_file(
    url: str,
    dest: pathlib.Path,
    blocksize: int = 1024,
) -> int:
    resp = request.urlopen(url)
    file_size = resp.getheader("content-length")
    if file_size:
        file_size = int(file_size)
    if not dest.parent.exists():
        dest.parent.mkdir(parents=True)
    with open(dest, "wb") as f:
        while True:
            buf1 = resp.read(blocksize)
            if not buf1:
                break
            f.write(buf1)
    return file_size


def fetch_year(year, dest):
    url = get_url(year)
    filename = get_filename(year)
    dest_path = dest / filename
    print(f"Downloading {url}")
    download_file(url, dest_path)
    print(f"Downloaded {url}")


def get_dest(
    dest_folder: Union[pathlib.Path, str, os.PathLike],
    year: int,
    month: int = None,
    day: int = None,
) -> str:
    dest_folder = pathlib.Path(dest_folder)
    if month is None:
        return dest_folder / f"{year}.zip"
    elif day is None:
        return dest_folder / f"{year}{month:02}.zip"
    else:
        return dest_folder / f"{year}{month:02}{day:02}.zip"
