import argparse
import datetime as dt
import re
from pathlib import Path

import httpx

from b3_cotacaohistorica_fetcher import DateTuple, fetch_data_file, InvalidDate

HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/102.0.5005.149 Safari/537.36 "
        "Vivaldi/5.3.2679.68"
    ),
}


def expand_date_range(date_range: str) -> list[DateTuple]:
    dates = []
    start, end = sorted(date_range.split(":"))

    yearly_match = re.match(r"\d{4}:\d{4}", date_range)
    monthly_match = re.match(r"\d{4}-\d{2}:\d{4}-\d{2}", date_range)
    daily_match = re.match(r"\d{4}-\d{2}-\d{2}:\d{4}-\d{2}-\d{2}", date_range)

    if yearly_match:
        start, end = int(start), int(end)
        dates.extend(
            [
                (year, None, None)
                for year in range(start, end + 1)
            ]
        )
    elif monthly_match:
        start_year, start_month = start.split("-")
        end_year, end_month = end.split("-")
        start_year, start_month = int(start_year), int(start_month)
        end_year, end_month = int(end_year), int(end_month)
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                if (month < start_month and year == start_year):
                    continue
                elif (month > end_month and year == end_year):
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


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--ouput", dest="output", type=Path)
    parser.add_argument("dates", help="start:end")
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    output = args.output
    dates = parse_dates(args.dates)

    client = httpx.Client(headers=HTTP_HEADERS, verify=False)

    for date in dates:
        try:
            fetch_data_file(datadir=output, datetuple=date, client=client)
        except InvalidDate:
            print(f"Invalid date: {date}")
        except httpx.HTTPStatusError:
            print(f"HTTP error: {date}")


if __name__ == "__main__":
    main()
