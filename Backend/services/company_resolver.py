import csv
import io
import os
import re
import difflib
import time
import requests
import yfinance as yf


# ============================================================
# NSE CONFIGURATION
# ============================================================

NSE_PAGE_URL = (
    "https://www.nseindia.com/static/market-data/"
    "securities-available-for-trading"
)

NSE_CACHE_SECONDS = 24 * 60 * 60

_nse_companies = []
_nse_last_loaded = 0


# ============================================================
# GLOBAL COMPANY REFERENCE DATA
# ============================================================

GLOBAL_COMPANIES_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "global_companies.csv"
)

_global_companies = None


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    """
    Normalize company names for matching.
    """

    if not text:
        return ""

    text = text.upper()

    text = re.sub(
        r"\b(PRIVATE|PVT|LIMITED|LTD|INC|CORP|CORPORATION|"
        r"COMPANY|CO|PLC|LLC|LLP)\b",
        "",
        text
    )

    text = re.sub(r"[^A-Z0-9]+", " ", text)

    return " ".join(text.split())


# ============================================================
# NSE SESSION
# ============================================================

def create_nse_session():
    session = requests.Session()

    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 "
            "(Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/150.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,"
            "application/xml;q=0.9,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/",
    })

    return session


# ============================================================
# FIND NSE CSV
# ============================================================

def find_equity_csv_url(session):
    """
    Find the current NSE equity CSV URL from the NSE page.
    """

    response = session.get(
        NSE_PAGE_URL,
        timeout=15
    )

    response.raise_for_status()

    html = response.text

    matches = re.findall(
        r'https?://[^"\']+\.csv',
        html,
        flags=re.IGNORECASE
    )

    for url in matches:

        if "EQUITY" in url.upper():

            return url

    # Current NSE archive URL fallback
    return (
        "https://nsearchives.nseindia.com/"
        "content/equities/EQUITY_L.csv"
    )


# ============================================================
# DOWNLOAD NSE COMPANIES
# ============================================================

def download_nse_companies():

    session = create_nse_session()

    try:

        csv_url = find_equity_csv_url(session)

        print(
            f"NSE equity CSV found: {csv_url}"
        )

        response = session.get(
            csv_url,
            timeout=20
        )

        response.raise_for_status()

        content = response.content

        text = content.decode(
            "utf-8-sig",
            errors="replace"
        )

        reader = csv.DictReader(
            io.StringIO(text)
        )

        companies = []

        for row in reader:

            symbol = (
                row.get("SYMBOL")
                or row.get("Symbol")
                or ""
            ).strip()

            name = (
                row.get("NAME OF COMPANY")
                or row.get("Name of Company")
                or row.get("COMPANY_NAME")
                or ""
            ).strip()

            if symbol and name:

                companies.append({
                    "symbol": symbol.upper(),
                    "name": name
                })

        if not companies:
            raise ValueError(
                "NSE CSV contained no companies."
            )

        print(
            f"Loaded {len(companies)} NSE securities."
        )

        return companies

    except Exception as e:

        print(
            f"Could not download NSE company list: {e}"
        )

        return []


# ============================================================
# GET NSE COMPANIES
# ============================================================

def get_nse_companies(force_refresh=False):

    global _nse_companies
    global _nse_last_loaded

    current_time = time.time()

    cache_valid = (
        _nse_companies
        and (
            current_time - _nse_last_loaded
            < NSE_CACHE_SECONDS
        )
    )

    if cache_valid and not force_refresh:

        return _nse_companies

    companies = download_nse_companies()

    if companies:

        _nse_companies = companies
        _nse_last_loaded = current_time

        return _nse_companies

    # If refresh fails, continue using old cache
    if _nse_companies:

        print(
            "Using previously loaded NSE company list."
        )

        return _nse_companies

    return []


# ============================================================
# NSE SEARCH FUNCTIONS
# ============================================================

def find_nse_by_symbol(query):

    query = query.strip().upper()

    if not query:
        return None

    companies = get_nse_companies()

    for company in companies:

        if company["symbol"] == query:

            return company["symbol"] + ".NS"

    return None


def find_nse_by_name(query):

    query_normalized = normalize_text(query)

    if not query_normalized:
        return None

    companies = get_nse_companies()

    for company in companies:

        company_name = normalize_text(
            company["name"]
        )

        if company_name == query_normalized:

            return company["symbol"] + ".NS"

    return None


def find_nse_by_partial_name(query):

    query_normalized = normalize_text(query)

    if not query_normalized:
        return None

    companies = get_nse_companies()

    matches = []

    for company in companies:

        company_name = normalize_text(
            company["name"]
        )

        if query_normalized in company_name:

            matches.append(company)

    if matches:

        return matches[0]["symbol"] + ".NS"

    return None


def find_nse_fuzzy(query):

    query_normalized = normalize_text(query)

    if not query_normalized:
        return None

    companies = get_nse_companies()

    names = [
        normalize_text(company["name"])
        for company in companies
    ]

    matches = difflib.get_close_matches(
        query_normalized,
        names,
        n=1,
        cutoff=0.75
    )

    if not matches:
        return None

    best_match = matches[0]

    for company in companies:

        if normalize_text(
            company["name"]
        ) == best_match:

            return company["symbol"] + ".NS"

    return None


# ============================================================
# GLOBAL COMPANY REFERENCE DATA
# ============================================================

def load_global_companies():

    global _global_companies

    if _global_companies is not None:

        return _global_companies

    companies = []

    if not os.path.exists(
        GLOBAL_COMPANIES_FILE
    ):

        print(
            "Global company file not found: "
            f"{GLOBAL_COMPANIES_FILE}"
        )

        return []

    try:

        with open(
            GLOBAL_COMPANIES_FILE,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                symbol = (
                    row.get("symbol")
                    or ""
                ).strip()

                name = (
                    row.get("name")
                    or ""
                ).strip()

                if not symbol or not name:
                    continue

                companies.append({
                    "symbol": symbol.upper(),
                    "name": name,
                    "exchange": (
                        row.get("exchange")
                        or ""
                    ).strip(),
                    "country": (
                        row.get("country")
                        or ""
                    ).strip()
                })

        _global_companies = companies

        print(
            f"Loaded {len(companies)} "
            "global companies."
        )

        return companies

    except Exception as e:

        print(
            "Could not load global company list: "
            f"{e}"
        )

        return []


# ============================================================
# GLOBAL SEARCH FUNCTIONS
# ============================================================

def find_global_by_symbol(query):

    query = query.strip().upper()

    if not query:
        return None

    companies = load_global_companies()

    for company in companies:

        if company["symbol"] == query:

            return company["symbol"]

    return None


def find_global_by_name(query):

    query_normalized = normalize_text(query)

    if not query_normalized:
        return None

    companies = load_global_companies()

    for company in companies:

        company_name = normalize_text(
            company["name"]
        )

        if company_name == query_normalized:

            return company["symbol"]

    return None


def find_global_by_partial_name(query):

    query_normalized = normalize_text(query)

    if not query_normalized:
        return None

    companies = load_global_companies()

    matches = []

    for company in companies:

        company_name = normalize_text(
            company["name"]
        )

        if query_normalized in company_name:

            matches.append(company)

    if not matches:
        return None

    # Prefer company names that start with the user's input
    starts_with = [
        company
        for company in matches
        if normalize_text(company["name"]).startswith(query_normalized)
    ]

    if starts_with:
        matches = starts_with

    # If multiple companies still match, prefer the shortest company name.
    matches.sort(
        key=lambda company: len(
            normalize_text(company["name"])
        )
    )

    return matches[0]["symbol"]


def find_global_fuzzy(query):

    query_normalized = normalize_text(query)

    if not query_normalized:
        return None

    companies = load_global_companies()

    names = [
        normalize_text(company["name"])
        for company in companies
    ]

    matches = difflib.get_close_matches(
        query_normalized,
        names,
        n=1,
        cutoff=0.75
    )

    if not matches:
        return None

    best_match = matches[0]

    for company in companies:

        if normalize_text(
            company["name"]
        ) == best_match:

            return company["symbol"]

    return None


# ============================================================
# TICKER VALIDATION
# ============================================================

def ticker_exists(ticker):

    try:

        stock = yf.Ticker(ticker)

        info = stock.get_info()

        if not info:
            return False

        return bool(
            info.get("symbol")
            or info.get("shortName")
            or info.get("longName")
        )

    except Exception:

        return False


# ============================================================
# MAIN TICKER RESOLVER
# ============================================================

def resolve_ticker(user_input):

    if not user_input:

        raise ValueError(
            "Company name or ticker cannot be empty."
        )

    original = user_input.strip()

    if not original:

        raise ValueError(
            "Company name or ticker cannot be empty."
        )

    # --------------------------------------------------------
    # 1. Explicit NSE ticker
    # --------------------------------------------------------

    if original.upper().endswith(".NS"):

        return original.upper()

    # --------------------------------------------------------
    # 2. NSE exact ticker
    # --------------------------------------------------------

    try:

        ticker = find_nse_by_symbol(original)

        if ticker:

            return ticker

    except Exception as e:

        print(
            f"NSE symbol search failed: {e}"
        )

    # --------------------------------------------------------
    # 3. NSE exact company name
    # --------------------------------------------------------

    try:

        ticker = find_nse_by_name(original)

        if ticker:

            return ticker

    except Exception as e:

        print(
            f"NSE exact name search failed: {e}"
        )

    # --------------------------------------------------------
    # 4. NSE partial company name
    # --------------------------------------------------------

    try:

        ticker = find_nse_by_partial_name(original)

        if ticker:

            return ticker

    except Exception as e:

        print(
            f"NSE partial search failed: {e}"
        )

    # --------------------------------------------------------
    # 5. NSE fuzzy company name
    # --------------------------------------------------------

    try:

        ticker = find_nse_fuzzy(original)

        if ticker:

            return ticker

    except Exception as e:

        print(
            f"NSE fuzzy search failed: {e}"
        )

    # --------------------------------------------------------
    # 6. Global exact ticker
    # --------------------------------------------------------

    try:

        ticker = find_global_by_symbol(original)

        if ticker:

            return ticker

    except Exception as e:

        print(
            f"Global symbol search failed: {e}"
        )

    # --------------------------------------------------------
    # 7. Global exact company name
    # --------------------------------------------------------

    try:

        ticker = find_global_by_name(original)

        if ticker:

            return ticker

    except Exception as e:

        print(
            f"Global exact name search failed: {e}"
        )

    # --------------------------------------------------------
    # 8. Global partial company name
    # --------------------------------------------------------

    try:

        ticker = find_global_by_partial_name(original)

        if ticker:

            return ticker

    except Exception as e:

        print(
            f"Global partial search failed: {e}"
        )

    # --------------------------------------------------------
    # 9. Global fuzzy company name
    # --------------------------------------------------------

    try:

        ticker = find_global_fuzzy(original)

        if ticker:

            return ticker

    except Exception as e:

        print(
            f"Global fuzzy search failed: {e}"
        )

    # --------------------------------------------------------
    # 10. Direct ticker fallback
    # --------------------------------------------------------

    ticker = original.upper()

    if ticker_exists(ticker):

        return ticker

    # --------------------------------------------------------
    # 11. Automatic NSE ticker fallback
    # --------------------------------------------------------

    possible_nse = ticker + ".NS"

    if ticker_exists(possible_nse):

        return possible_nse

    # --------------------------------------------------------
    # Nothing worked
    # --------------------------------------------------------

    raise ValueError(
        f"Could not identify '{original}'. "
        "Please enter a valid company name or ticker."
    )
