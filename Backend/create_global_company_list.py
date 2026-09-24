import csv
import io
import json
import requests
from pathlib import Path


OUTPUT_FILE = Path("data/global_companies.csv")


HEADERS = {
    "User-Agent": (
        "CompanyFinancialDashboard/1.0 "
        "(educational-project)"
    )
}


def download_text(url):
    print(f"Downloading: {url}")

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return response.text


def add_company(companies, symbol, name, exchange, country):
    symbol = (symbol or "").strip()
    name = (name or "").strip()

    if not symbol or not name:
        return

    # Skip obvious non-equity instruments
    name_upper = name.upper()

    excluded_terms = [
        "WARRANT",
        "RIGHT",
        "UNIT",
        "PREFERRED",
        "PREFERENCE",
        "DEBENTURE",
        "NOTE",
        "BOND",
        "ETF",
        "ETN",
        "FUND",
        "TRUST",
        "INDEX",
    ]

    if any(term in name_upper for term in excluded_terms):
        return

    key = (
        symbol.upper(),
        exchange.upper(),
        country.upper()
    )

    if key not in companies:
        companies[key] = {
            "symbol": symbol.upper(),
            "name": name,
            "exchange": exchange,
            "country": country
        }


def load_sec_companies(companies):
    """
    Load U.S. public-company ticker data from the SEC.
    """

    url = (
        "https://www.sec.gov/files/"
        "company_tickers_exchange.json"
    )

    try:
        text = download_text(url)
        data = json.loads(text)

        rows = data.get("data", [])

        for row in rows:

            # SEC format:
            # cik, name, ticker, exchange

            if len(row) < 4:
                continue

            _, name, ticker, exchange = row[:4]

            add_company(
                companies,
                ticker,
                name,
                exchange or "US",
                "United States"
            )

        print(
            f"SEC companies loaded: {len(rows)}"
        )

    except Exception as e:

        print(
            f"SEC download failed: {e}"
        )


def load_nasdaq_listed(companies):
    """
    Load Nasdaq-listed securities.
    """

    url = (
        "https://www.nasdaqtrader.com/"
        "dynamic/SymDir/nasdaqlisted.txt"
    )

    try:

        text = download_text(url)

        reader = csv.DictReader(
            io.StringIO(text),
            delimiter="|"
        )

        count = 0

        for row in reader:

            symbol = row.get("Symbol")
            name = row.get("Security Name")

            if not symbol or not name:
                continue

            if symbol.startswith("File Creation"):
                continue

            add_company(
                companies,
                symbol,
                name,
                "NASDAQ",
                "United States"
            )

            count += 1

        print(
            f"Nasdaq-listed securities processed: {count}"
        )

    except Exception as e:

        print(
            f"Nasdaq download failed: {e}"
        )


def load_other_us_listed(companies):
    """
    Load securities listed on NYSE and other U.S.
    exchanges through Nasdaq Trader's directory.
    """

    url = (
        "https://www.nasdaqtrader.com/"
        "dynamic/SymDir/otherlisted.txt"
    )

    exchange_map = {
        "N": "NYSE",
        "A": "NYSE MKT",
        "P": "NYSE ARCA",
        "V": "IEX",
        "Z": "BATS",
    }

    try:

        text = download_text(url)

        reader = csv.DictReader(
            io.StringIO(text),
            delimiter="|"
        )

        count = 0

        for row in reader:

            symbol = (
                row.get("ACT Symbol")
                or row.get("NASDAQ Symbol")
                or ""
            ).strip()

            name = (
                row.get("Security Name")
                or ""
            ).strip()

            exchange_code = (
                row.get("Exchange")
                or ""
            ).strip()

            if not symbol or not name:
                continue

            if symbol.startswith("File Creation"):
                continue

            exchange = exchange_map.get(
                exchange_code,
                "US"
            )

            add_company(
                companies,
                symbol,
                name,
                exchange,
                "United States"
            )

            count += 1

        print(
            f"Other U.S. securities processed: {count}"
        )

    except Exception as e:

        print(
            f"Other U.S. exchange download failed: {e}"
        )


def main():

    companies = {}

    print()
    print("=" * 60)
    print("Creating global company reference list")
    print("=" * 60)
    print()

    load_sec_companies(companies)

    load_nasdaq_listed(companies)

    load_other_us_listed(companies)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    companies_list = sorted(
        companies.values(),
        key=lambda x: (
            x["country"],
            x["name"]
        )
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "symbol",
                "name",
                "exchange",
                "country"
            ]
        )

        writer.writeheader()

        writer.writerows(
            companies_list
        )

    print()
    print("=" * 60)
    print(
        f"Created {OUTPUT_FILE}"
    )
    print(
        f"Total companies: {len(companies_list)}"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()
