import yfinance as yf


def get_ticker(ticker):
    """
    Create a yfinance Ticker object.
    """

    ticker = ticker.strip().upper()

    if not ticker:
        raise ValueError("Ticker cannot be empty.")

    return yf.Ticker(ticker)


def get_company_profile(ticker):
    """
    Retrieve basic company information.
    """

    company = get_ticker(ticker)

    try:
        info = company.get_info()

    except Exception as e:
        raise ValueError(
            f"Could not retrieve company profile for '{ticker.upper()}'."
        ) from e

    if not info:
        raise ValueError(
            f"No company profile data found for '{ticker.upper()}'."
        )

    return {
        "symbol": info.get("symbol"),
        "name": info.get("longName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "country": info.get("country"),
        "currency": info.get("currency"),
        "exchange": info.get("exchange"),
        "market_cap": info.get("marketCap"),
        "website": info.get("website"),
    }


def get_financial_statements(ticker):
    """
    Retrieve annual financial statements.
    """

    company = get_ticker(ticker)

    try:
        income_statement = company.get_income_stmt(
            freq="yearly"
        )

        balance_sheet = company.get_balance_sheet(
            freq="yearly"
        )

        cash_flow = company.get_cashflow(
            freq="yearly"
        )

    except Exception as e:
        raise ValueError(
            f"Could not retrieve financial statements "
            f"for '{ticker.upper()}'."
        ) from e

    return {
        "income_statement": income_statement,
        "balance_sheet": balance_sheet,
        "cash_flow": cash_flow,
    }