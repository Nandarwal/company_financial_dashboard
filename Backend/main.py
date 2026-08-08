from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from services.finance import (
    get_company_profile,
    get_financials,
    get_stock_history,
    get_ratios,
    get_financial_statements
)

from services.analysis import (
    analyze_growth,
    analyze_margins,
    analyze_cash_flow,
    analyze_debt,
    analyze_liquidity,
    calculate_financial_health_score,
    generate_basic_insights
)


app = FastAPI(
    title="Company Financial Dashboard API",
    description="Financial data API for company analysis",
    version="1.0.0"
)


# --------------------------------------------------
# CORS CONFIGURATION
# --------------------------------------------------

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"]
)


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Welcome to the Company Financial Dashboard API"
    }


# --------------------------------------------------
# COMPANY PROFILE
# --------------------------------------------------

@app.get("/company/{ticker}")
def company(ticker: str):

    try:
        return get_company_profile(ticker)

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


# --------------------------------------------------
# FINANCIALS
# --------------------------------------------------

@app.get("/financials/{ticker}")
def financials(ticker: str):

    try:
        return get_financials(ticker)

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


# --------------------------------------------------
# STOCK HISTORY
# --------------------------------------------------

@app.get("/stock/{ticker}")
def stock(ticker: str):

    try:
        return get_stock_history(ticker)

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


# --------------------------------------------------
# FINANCIAL RATIOS
# --------------------------------------------------

@app.get("/ratios/{ticker}")
def ratios(ticker: str):

    try:
        return get_ratios(ticker)

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

# --------------------------------------------------
# FINANCIAL STATEMENTS
# --------------------------------------------------

@app.get("/statements/{ticker}")
def statements(ticker: str):

    try:
        return get_financial_statements(ticker)

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

# --------------------------------------------------
# STATEMENT ANALYSIS
# --------------------------------------------------

@app.get("/analysis/{ticker}")
def analysis(ticker: str):

    try:

        # -----------------------------------------
        # 1. FETCH RAW FINANCIAL DATA
        # -----------------------------------------

        statements_data = (
            get_financial_statements(
                ticker
            )
        )

        # -----------------------------------------
        # 2. ANALYZE GROWTH
        # -----------------------------------------

        growth_analysis = (
            analyze_growth(
                statements_data
            )
        )

        # -----------------------------------------
        # 3. ANALYZE MARGINS
        # -----------------------------------------

        margin_analysis = (
            analyze_margins(
                statements_data
            )
        )

        # -----------------------------------------
        # 4. ANALYZE CASH FLOW
        # -----------------------------------------

        cash_flow_analysis = (
            analyze_cash_flow(
                statements_data
            )
        )

        # -----------------------------------------
        # 5. ANALYZE DEBT
        # -----------------------------------------

        debt_analysis = (
            analyze_debt(
                statements_data
            )
        )

        # -----------------------------------------
        # 6. ANALYZE LIQUIDITY
        # -----------------------------------------

        liquidity_analysis = (
            analyze_liquidity(
                statements_data
            )
        )

        # -----------------------------------------
        # 7. CALCULATE HEALTH SCORE
        # -----------------------------------------

        financial_health = (
            calculate_financial_health_score(

                growth_analysis,

                margin_analysis,

                cash_flow_analysis,

                debt_analysis,

                liquidity_analysis
            )
        )

        # -----------------------------------------
        # 8. GENERATE INSIGHTS
        # -----------------------------------------

        insights = (
            generate_basic_insights(

                growth_analysis,

                margin_analysis,

                cash_flow_analysis,

                debt_analysis,

                liquidity_analysis,

                financial_health
            )
        )

        # -----------------------------------------
        # 9. RETURN COMPLETE ANALYSIS
        # -----------------------------------------

        return {

            "ticker":
                ticker.upper(),

            "growth":
                growth_analysis,

            "margins":
                margin_analysis,

            "cash_flow":
                cash_flow_analysis,

            "debt":
                debt_analysis,

            "liquidity":
                liquidity_analysis,

            "financial_health":
                financial_health,

            "insights":
                insights
        }

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )