import argparse
import pathlib
from b3_ch_fetcher import fetcher


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--ouput", dest="output", type=pathlib.Path)
    parser.add_argument("years", nargs="+", type=int)
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    output = args.output
    years = args.years
    for year in years:
        fetcher.fetch_year(year, dest=dest)


if __name__ == "__main__":
    main()
