from b3_cotacaohistorica_fetcher.cli import get_args
from b3_cotacaohistorica_fetcher.fetcher import fetch_dates


def main():
    args = get_args()
    dates = args["dates"]
    output = args["output"]
    fetch_dates(dates, output)


if __name__ == "__main__":
    main()
