import math
import yfinance as yf
from functools import lru_cache

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


@lru_cache(maxsize=128)
def get_ratios(ticker):
    """
    Calculate key financial ratios without using Yahoo's get_info(),
    which can trigger rate limits on deployed servers.

    Ratios:
    - P/E = current stock price / trailing EPS
    - ROE = net income / shareholders' equity
    - Debt-to-equity = total debt / shareholders' equity
    - Profit margin = net income / revenue

    Results are cached in memory to reduce repeated Yahoo requests.
    """

    ticker = ticker.strip().upper()
    company = get_ticker(ticker)

    try:
        income_statement = company.get_income_stmt(freq="yearly")
        balance_sheet = company.get_balance_sheet(freq="yearly")

        # We need the latest stock price for P/E.
        history = company.history(period="5d")

    except Exception as e:
        raise ValueError(
            f"Could not retrieve ratio data for '{ticker}': {str(e)}"
        ) from e

    if income_statement is None or income_statement.empty:
        raise ValueError(
            f"No income statement data found for '{ticker}'."
        )

    if balance_sheet is None or balance_sheet.empty:
        raise ValueError(
            f"No balance sheet data found for '{ticker}'."
        )

    # ---------------------------------------------------------
    # Find latest year
    # ---------------------------------------------------------

    income_dates = list(income_statement.columns)

    if not income_dates:
        raise ValueError(
            f"No income statement periods found for '{ticker}'."
        )

    latest_income_date = max(income_dates)

    # ---------------------------------------------------------
    # Revenue
    # ---------------------------------------------------------

    revenue = None

    for row_name in ["TotalRevenue", "OperatingRevenue"]:
        if row_name in income_statement.index:
            revenue = clean_number(
                income_statement.loc[row_name, latest_income_date]
            )
            if revenue is not None:
                break

    # ---------------------------------------------------------
    # Net income
    # ---------------------------------------------------------

    net_income = None

    for row_name in ["NetIncome", "NetIncomeCommonStockholders"]:
        if row_name in income_statement.index:
            net_income = clean_number(
                income_statement.loc[row_name, latest_income_date]
            )
            if net_income is not None:
                break

    # ---------------------------------------------------------
    # EPS
    # ---------------------------------------------------------

    eps = None

    for row_name in [
        "DilutedEPS",
        "BasicEPS"
    ]:
        if row_name in income_statement.index:
            eps = clean_number(
                income_statement.loc[row_name, latest_income_date]
            )
            if eps is not None:
                break

    # ---------------------------------------------------------
    # Shareholders' equity
    # ---------------------------------------------------------

    equity = None

    for row_name in [
        "StockholdersEquity",
        "CommonStockEquity"
    ]:
        if row_name in balance_sheet.index:
            equity = clean_number(
                balance_sheet.loc[row_name, latest_income_date]
            )
            if equity is not None:
                break

    # ---------------------------------------------------------
    # Total debt
    # ---------------------------------------------------------

    total_debt = None

    if "TotalDebt" in balance_sheet.index:
        total_debt = clean_number(
            balance_sheet.loc["TotalDebt", latest_income_date]
        )

    # ---------------------------------------------------------
    # P/E ratio
    # ---------------------------------------------------------

    pe_ratio = None

    if (
        eps is not None
        and eps > 0
        and history is not None
        and not history.empty
    ):
        latest_close = clean_number(
            history["Close"].iloc[-1]
        )

        if latest_close is not None:
            pe_ratio = latest_close / eps

    # ---------------------------------------------------------
    # ROE
    # ---------------------------------------------------------

    roe = None

    if (
        net_income is not None
        and equity is not None
        and equity != 0
    ):
        roe = (net_income / equity) * 100

    # ---------------------------------------------------------
    # Profit margin
    # ---------------------------------------------------------

    profit_margin = None

    if (
        net_income is not None
        and revenue is not None
        and revenue != 0
    ):
        profit_margin = (net_income / revenue) * 100

    # ---------------------------------------------------------
    # Debt-to-equity
    # ---------------------------------------------------------

    debt_to_equity = None

    if (
        total_debt is not None
        and equity is not None
        and equity != 0
    ):
        debt_to_equity = total_debt / equity

    return {
        "ticker": ticker,
        "pe_ratio": round(pe_ratio, 2)
        if pe_ratio is not None
        else None,

        "roe_percent": round(roe, 2)
        if roe is not None
        else None,

        "debt_to_equity": round(debt_to_equity, 2)
        if debt_to_equity is not None
        else None,

        "profit_margin_percent": round(profit_margin, 2)
        if profit_margin is not None
        else None
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