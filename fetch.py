import argparse
from pathlib import Path

from b3data.historic.dates import parse_dates
from b3data.historic.fetcher import fetch_dates


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--ouput",
        dest="output",
        type=Path,
        default=Path("data"),
    )
    parser.add_argument("dates", help="start:end")
    args = parser.parse_args()
    return {
        "output": args.output,
        "dates": parse_dates(args.dates),
    }


def main():
    args = get_args()
    dates = args["dates"]
    output = args["output"]
    fetch_dates(dates, output)


if __name__ == "__main__":
    main()
