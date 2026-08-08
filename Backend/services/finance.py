import math
import yfinance as yf


def clean_number(value):
    """
    Convert a value into a JSON-safe number.

    Returns None if the value is missing,
    invalid, NaN, or infinite.
    """
    if value is None:
        return None

    try:
        value = float(value)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(value):
        return None

    return value


def get_ticker(ticker):
    """
    Create a yfinance Ticker object after
    cleaning the ticker entered by the user.
    """

    ticker = ticker.strip().upper()

    if not ticker:
        raise ValueError("Ticker cannot be empty.")

    return yf.Ticker(ticker)


def get_company_profile(ticker):
    """
    Fetch basic company information from Yahoo Finance.
    """

    company = get_ticker(ticker)

    try:
        info = company.get_info()
    except Exception as e:
        raise ValueError(
            f"Could not retrieve data for ticker '{ticker.upper()}'."
        ) from e

    # Check whether Yahoo Finance actually returned
    # meaningful company information.
    if not info or not info.get("longName"):
        raise ValueError(
            f"Company '{ticker.upper()}' was not found."
        )

    return {
        "company": info.get("longName"),
        "symbol": info.get("symbol"),
        "industry": info.get("industry"),
        "sector": info.get("sector"),
        "country": info.get("country"),
        "website": info.get("website"),
        "market_cap": clean_number(info.get("marketCap")),
        "employees": info.get("fullTimeEmployees"),
        "summary": info.get("longBusinessSummary")
    }


def get_financials(ticker):
    """
    Fetch revenue and net income
    for the available financial years.
    """

    company = get_ticker(ticker)

    try:
        financials = company.financials
    except Exception as e:
        raise ValueError(
            f"Could not retrieve financial data for '{ticker.upper()}'."
        ) from e

    if financials is None or financials.empty:
        raise ValueError(
            f"No financial data found for '{ticker.upper()}'."
        )

    # Check that the required rows exist.
    if "Total Revenue" not in financials.index:
        raise ValueError(
            f"Revenue data is unavailable for '{ticker.upper()}'."
        )

    if "Net Income" not in financials.index:
        raise ValueError(
            f"Net income data is unavailable for '{ticker.upper()}'."
        )

    revenue = financials.loc["Total Revenue"]
    net_income = financials.loc["Net Income"]

    revenue_dict = {}
    income_dict = {}

    for date, value in revenue.items():

        cleaned_value = clean_number(value)

        revenue_dict[str(date.year)] = (
            int(cleaned_value)
            if cleaned_value is not None
            else None
        )

    for date, value in net_income.items():

        cleaned_value = clean_number(value)

        income_dict[str(date.year)] = (
            int(cleaned_value)
            if cleaned_value is not None
            else None
        )

    return {
        "ticker": ticker.strip().upper(),
        "revenue": revenue_dict,
        "net_income": income_dict
    }


def get_stock_history(ticker):
    """
    Fetch 5 years of daily stock price data.
    """

    company = get_ticker(ticker)

    try:
        history = company.history(period="5y")
    except Exception as e:
        raise ValueError(
            f"Could not retrieve stock data for '{ticker.upper()}'."
        ) from e

    if history is None or history.empty:
        raise ValueError(
            f"No stock price data found for '{ticker.upper()}'."
        )

    prices = []

    for date, row in history.iterrows():

        close_price = clean_number(row.get("Close"))

        # Skip rows where closing price is unavailable.
        if close_price is None:
            continue

        prices.append({
            "date": str(date.date()),
            "close": round(close_price, 2)
        })

    if not prices:
        raise ValueError(
            f"No valid stock prices found for '{ticker.upper()}'."
        )

    return {
        "ticker": ticker.strip().upper(),
        "prices": prices
    }


def get_ratios(ticker):
    """
    Fetch key financial ratios for a company.
    Uses Yahoo info for PE/ROE/profit margin,
    and balance sheet values for debt-to-equity
    so it matches /analysis/{ticker}.
    """

    company = get_ticker(ticker)

    try:
        info = company.get_info()
        balance_sheet = company.get_balance_sheet(freq="yearly")
    except Exception as e:
        raise ValueError(
            f"Could not retrieve ratio data for '{ticker.upper()}'."
        ) from e

    if not info or not info.get("longName"):
        raise ValueError(
            f"Company '{ticker.upper()}' was not found."
        )

    # P/E ratio from Yahoo info
    pe_ratio = clean_number(info.get("trailingPE"))

    # ROE from Yahoo info (decimal -> percent)
    roe = clean_number(info.get("returnOnEquity"))
    if roe is not None:
        roe = round(roe * 100, 2)

    # Profit margin from Yahoo info (decimal -> percent)
    profit_margin = clean_number(info.get("profitMargins"))
    if profit_margin is not None:
        profit_margin = round(profit_margin * 100, 2)

    # Debt-to-equity from balance sheet, same logic as /analysis/{ticker}
    debt_to_equity = None

    if balance_sheet is not None and not balance_sheet.empty:
        debt_row = None
        equity_row = None

        for candidate in ["TotalDebt"]:
            if candidate in balance_sheet.index:
                debt_row = balance_sheet.loc[candidate]
                break

        for candidate in ["StockholdersEquity", "CommonStockEquity"]:
            if candidate in balance_sheet.index:
                equity_row = balance_sheet.loc[candidate]
                break

        if debt_row is not None and equity_row is not None:
            debt_dict = {}
            equity_dict = {}

            for date, value in debt_row.items():
                cleaned = clean_number(value)
                debt_dict[str(date.year)] = cleaned

            for date, value in equity_row.items():
                cleaned = clean_number(value)
                equity_dict[str(date.year)] = cleaned

            common_years = sorted(
                set(debt_dict.keys()) & set(equity_dict.keys()),
                key=lambda x: int(x)
            )

            if common_years:
                latest_year = common_years[-1]
                debt_value = debt_dict.get(latest_year)
                equity_value = equity_dict.get(latest_year)

                if debt_value is not None and equity_value not in (None, 0):
                    debt_to_equity = round(debt_value / equity_value, 2)

    return {
        "ticker": ticker.strip().upper(),
        "pe_ratio": round(pe_ratio, 2) if pe_ratio is not None else None,
        "roe_percent": roe,
        "debt_to_equity": debt_to_equity,
        "profit_margin_percent": profit_margin
    }

def statement_to_year_dict(statement, row_name):
    """
    Extract one financial metric from a statement
    and convert it into a clean year -> value dictionary.
    """

    if statement is None or statement.empty:
        return {}

    if row_name not in statement.index:
        return {}

    row = statement.loc[row_name]

    result = {}

    for date, value in row.items():

        cleaned_value = clean_number(value)

        result[str(date.year)] = (
            int(cleaned_value)
            if cleaned_value is not None
            else None
        )

    return result

def statement_to_year_dict_any(statement, row_names):
    """
    Try multiple possible row names and return
    the first matching financial metric found.
    """

    if statement is None or statement.empty:
        return {}

    for row_name in row_names:

        if row_name in statement.index:
            return statement_to_year_dict(
                statement,
                row_name
            )

    return {}


def get_financial_statements(ticker):
    """
    Fetch annual income statement, balance sheet,
    and cash flow statement data.
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

    # -----------------------------------------
    # INCOME STATEMENT
    # -----------------------------------------

    revenue = statement_to_year_dict_any(
        income_statement,
        [
            "TotalRevenue",
            "OperatingRevenue"
        ]
    )

    operating_income = statement_to_year_dict_any(
        income_statement,
        [
            "OperatingIncome"
        ]
    )

    net_income = statement_to_year_dict_any(
        income_statement,
        [
            "NetIncome",
            "NetIncomeCommonStockholders"
        ]
    )

    gross_profit = statement_to_year_dict_any(
        income_statement,
        [
            "GrossProfit"
        ]
    )

    # -----------------------------------------
    # BALANCE SHEET
    # -----------------------------------------

    total_assets = statement_to_year_dict_any(
        balance_sheet,
        [
            "TotalAssets"
        ]
    )

    total_liabilities = statement_to_year_dict_any(
        balance_sheet,
        [
            "TotalLiabilitiesNetMinorityInterest",
            "TotalLiabilities"
        ]
    )

    total_debt = statement_to_year_dict_any(
        balance_sheet,
        [
            "TotalDebt"
        ]
    )

    cash = statement_to_year_dict_any(
        balance_sheet,
        [
            "CashAndCashEquivalents"
        ]
    )

    cash_and_short_term_investments = statement_to_year_dict_any(
        balance_sheet,
        [
            "CashCashEquivalentsAndShortTermInvestments",
            "CashAndCashEquivalents"
        ]
    )

    accounts_receivable = statement_to_year_dict_any(
        balance_sheet,
        [
            "AccountsReceivable"
        ]
    )

    stockholders_equity = statement_to_year_dict_any(
        balance_sheet,
        [
            "StockholdersEquity",
            "CommonStockEquity"
        ]
    )

    current_assets = statement_to_year_dict_any(
        balance_sheet,
        [
            "CurrentAssets"
        ]
    )

    current_liabilities = statement_to_year_dict_any(
        balance_sheet,
        [
            "CurrentLiabilities"
        ]
    )

    # -----------------------------------------
    # CASH FLOW STATEMENT
    # -----------------------------------------

    operating_cash_flow = statement_to_year_dict_any(
        cash_flow,
        [
            "OperatingCashFlow"
        ]
    )

    capital_expenditure = statement_to_year_dict_any(
        cash_flow,
        [
            "CapitalExpenditure"
        ]
    )

    free_cash_flow = statement_to_year_dict_any(
        cash_flow,
        [
            "FreeCashFlow"
        ]
    )

    # -----------------------------------------
    # CALCULATE FREE CASH FLOW IF MISSING
    # FCF = Operating Cash Flow + CapEx
    #
    # CapEx is usually stored as a negative
    # cash outflow.
    # -----------------------------------------

    all_fcf_years = set(
        operating_cash_flow.keys()
    ) | set(
        capital_expenditure.keys()
    ) | set(
        free_cash_flow.keys()
    )

    for year in all_fcf_years:

        existing_fcf = free_cash_flow.get(
            year
        )

        if existing_fcf is not None:
            continue

        ocf = operating_cash_flow.get(
            year
        )

        capex = capital_expenditure.get(
            year
        )

        if (
            ocf is not None
            and capex is not None
        ):
            free_cash_flow[year] = (
                ocf + capex
            )

    # -----------------------------------------
    # RETURN CLEAN STRUCTURE
    # -----------------------------------------

    return {
        "ticker": ticker.strip().upper(),

        "income_statement": {

            "revenue": revenue,

            "operating_income": operating_income,

            "net_income": net_income,

            "gross_profit": gross_profit
        },

        "balance_sheet": {

            "total_assets": total_assets,

            "total_liabilities": total_liabilities,

            "cash": cash,

            "cash_and_short_term_investments":
                cash_and_short_term_investments,

            "accounts_receivable":
                accounts_receivable,

            "total_debt": total_debt,

            "stockholders_equity":
                stockholders_equity,

            "current_assets":
                current_assets,

            "current_liabilities":
                current_liabilities
        },

        "cash_flow": {

            "operating_cash_flow":
                operating_cash_flow,

            "capital_expenditure":
                capital_expenditure,

            "free_cash_flow":
                free_cash_flow
        }
    }