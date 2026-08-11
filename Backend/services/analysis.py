# =========================================================
# BASIC HELPERS
# =========================================================


def calculate_cagr(
    start_value,
    end_value,
    years
):
    """
    Calculate Compound Annual Growth Rate.

    Returns CAGR as a percentage.
    """

    if (
        start_value is None
        or end_value is None
        or years <= 0
    ):
        return None

    if (
        start_value <= 0
        or end_value <= 0
    ):
        return None

    cagr = (
        (end_value / start_value)
        ** (1 / years)
        - 1
    ) * 100

    return round(
        cagr,
        2
    )


def get_valid_data(data):
    """
    Remove missing values from a financial series.
    """

    if not data:
        return {}

    return {
        year: value
        for year, value in data.items()
        if value is not None
    }


def get_latest_value(data):
    """
    Return the latest available value.
    """

    valid_data = get_valid_data(
        data
    )

    if not valid_data:
        return None

    latest_year = max(
        valid_data.keys(),
        key=lambda x: int(x)
    )

    return valid_data[
        latest_year
    ]


def get_earliest_value(data):
    """
    Return the earliest available value.
    """

    valid_data = get_valid_data(
        data
    )

    if not valid_data:
        return None

    earliest_year = min(
        valid_data.keys(),
        key=lambda x: int(x)
    )

    return valid_data[
        earliest_year
    ]


def calculate_growth_metric(data):
    """
    Calculate CAGR using the earliest and
    latest available values.
    """

    valid_data = get_valid_data(
        data
    )

    if len(valid_data) < 2:

        return {
            "cagr": None,
            "start_year": None,
            "end_year": None,
            "start_value": None,
            "end_value": None,
            "years": None
        }

    sorted_years = sorted(
        valid_data.keys(),
        key=lambda x: int(x)
    )

    start_year = sorted_years[0]
    end_year = sorted_years[-1]

    start_value = valid_data[
        start_year
    ]

    end_value = valid_data[
        end_year
    ]

    years = (
        int(end_year)
        - int(start_year)
    )

    cagr = calculate_cagr(
        start_value,
        end_value,
        years
    )

    return {
        "cagr": cagr,
        "start_year": start_year,
        "end_year": end_year,
        "start_value": start_value,
        "end_value": end_value,
        "years": years
    }


# =========================================================
# YEAR-OVER-YEAR GROWTH
# =========================================================


def calculate_yoy_growth(data):
    """
    Calculate year-over-year growth percentages.
    """

    valid_data = get_valid_data(
        data
    )

    sorted_years = sorted(
        valid_data.keys(),
        key=lambda x: int(x)
    )

    yoy_growth = {}

    for i in range(
        1,
        len(sorted_years)
    ):

        previous_year = (
            sorted_years[i - 1]
        )

        current_year = (
            sorted_years[i]
        )

        previous_value = valid_data[
            previous_year
        ]

        current_value = valid_data[
            current_year
        ]

        if previous_value <= 0:

            yoy_growth[
                current_year
            ] = None

            continue

        growth = (
            (
                current_value
                - previous_value
            )
            / previous_value
        ) * 100

        yoy_growth[
            current_year
        ] = round(
            growth,
            2
        )

    return yoy_growth


# =========================================================
# MARGIN CALCULATIONS
# =========================================================


def calculate_margin_series(
    revenue,
    metric
):
    """
    Calculate a margin series.

    Example:
    Operating Margin =
    Operating Income / Revenue × 100
    """

    if (
        not revenue
        or not metric
    ):
        return {}

    common_years = sorted(
        set(revenue.keys())
        & set(metric.keys()),
        key=lambda x: int(x)
    )

    margins = {}

    for year in common_years:

        revenue_value = revenue[
            year
        ]

        metric_value = metric[
            year
        ]

        if (
            revenue_value is None
            or metric_value is None
            or revenue_value == 0
        ):

            margins[
                year
            ] = None

            continue

        margin = (
            metric_value
            / revenue_value
        ) * 100

        margins[
            year
        ] = round(
            margin,
            2
        )

    return margins


def analyze_margin_trend(
    margins
):
    """
    Analyze change in a margin
    from earliest to latest year.
    """

    valid_data = get_valid_data(
        margins
    )

    if len(valid_data) < 2:

        return {
            "start_year": None,
            "end_year": None,
            "start_margin": None,
            "end_margin": None,
            "change_percentage_points": None,
            "trend": "insufficient_data"
        }

    sorted_years = sorted(
        valid_data.keys(),
        key=lambda x: int(x)
    )

    start_year = sorted_years[0]
    end_year = sorted_years[-1]

    start_margin = valid_data[
        start_year
    ]

    end_margin = valid_data[
        end_year
    ]

    change = (
        end_margin
        - start_margin
    )

    if change > 0.5:

        trend = "improving"

    elif change < -0.5:

        trend = "declining"

    else:

        trend = "stable"

    return {
        "start_year": start_year,
        "end_year": end_year,
        "start_margin": start_margin,
        "end_margin": end_margin,
        "change_percentage_points":
            round(
                change,
                2
            ),
        "trend": trend
    }

def analyze_value_trend(
    values
):
    """
    Analyze change in a generic financial ratio
    or value from earliest to latest year.
    """

    valid_data = get_valid_data(
        values
    )

    if len(valid_data) < 2:

        return {
            "start_year": None,
            "end_year": None,
            "start_value": None,
            "end_value": None,
            "change": None,
            "trend": "insufficient_data"
        }

    sorted_years = sorted(
        valid_data.keys(),
        key=lambda x: int(x)
    )

    start_year = sorted_years[0]
    end_year = sorted_years[-1]

    start_value = valid_data[
        start_year
    ]

    end_value = valid_data[
        end_year
    ]

    change = (
        end_value
        - start_value
    )

    if change > 0.05:

        trend = "improving"

    elif change < -0.05:

        trend = "declining"

    else:

        trend = "stable"

    return {
        "start_year": start_year,
        "end_year": end_year,
        "start_value": start_value,
        "end_value": end_value,
        "change": round(
            change,
            2
        ),
        "trend": trend
    }


# =========================================================
# RATIO SERIES
# =========================================================


def calculate_ratio_series(
    numerator,
    denominator,
    multiplier=1
):
    """
    Calculate numerator / denominator
    for each common year.
    """

    if (
        not numerator
        or not denominator
    ):
        return {}

    common_years = sorted(
        set(numerator.keys())
        & set(denominator.keys()),
        key=lambda x: int(x)
    )

    result = {}

    for year in common_years:

        numerator_value = numerator[
            year
        ]

        denominator_value = denominator[
            year
        ]

        if (
            numerator_value is None
            or denominator_value is None
            or denominator_value == 0
        ):

            result[
                year
            ] = None

            continue

        value = (
            numerator_value
            / denominator_value
        ) * multiplier

        result[
            year
        ] = round(
            value,
            2
        )

    return result


def calculate_difference_series(
    first,
    second
):
    """
    Calculate first - second
    for each common year.
    """

    if (
        not first
        or not second
    ):
        return {}

    common_years = sorted(
        set(first.keys())
        & set(second.keys()),
        key=lambda x: int(x)
    )

    result = {}

    for year in common_years:

        first_value = first[
            year
        ]

        second_value = second[
            year
        ]

        if (
            first_value is None
            or second_value is None
        ):

            result[
                year
            ] = None

            continue

        result[
            year
        ] = first_value - second_value

    return result


def calculate_percentage_change(
    data
):
    """
    Calculate percentage change from
    earliest to latest available value.
    """

    valid_data = get_valid_data(
        data
    )

    if len(valid_data) < 2:
        return None

    start_value = get_earliest_value(
        valid_data
    )

    end_value = get_latest_value(
        valid_data
    )

    if (
        start_value is None
        or end_value is None
        or start_value == 0
    ):
        return None

    change = (
        (
            end_value
            - start_value
        )
        / abs(start_value)
    ) * 100

    return round(
        change,
        2
    )


# =========================================================
# GROWTH ANALYSIS
# =========================================================


def analyze_growth(
    statements
):
    """
    Analyze revenue and net income growth.
    """

    income_statement = statements.get(
        "income_statement",
        {}
    )

    revenue = income_statement.get(
        "revenue",
        {}
    )

    net_income = income_statement.get(
        "net_income",
        {}
    )

    revenue_analysis = calculate_growth_metric(
        revenue
    )

    profit_analysis = calculate_growth_metric(
        net_income
    )

    revenue_yoy = calculate_yoy_growth(
        revenue
    )

    profit_yoy = calculate_yoy_growth(
        net_income
    )

    return {

        "revenue_growth": {

            "cagr":
                revenue_analysis[
                    "cagr"
                ],

            "start_year":
                revenue_analysis[
                    "start_year"
                ],

            "end_year":
                revenue_analysis[
                    "end_year"
                ],

            "start_value":
                revenue_analysis[
                    "start_value"
                ],

            "end_value":
                revenue_analysis[
                    "end_value"
                ],

            "years":
                revenue_analysis[
                    "years"
                ],

            "yoy_growth":
                revenue_yoy
        },

        "profit_growth": {

            "cagr":
                profit_analysis[
                    "cagr"
                ],

            "start_year":
                profit_analysis[
                    "start_year"
                ],

            "end_year":
                profit_analysis[
                    "end_year"
                ],

            "start_value":
                profit_analysis[
                    "start_value"
                ],

            "end_value":
                profit_analysis[
                    "end_value"
                ],

            "years":
                profit_analysis[
                    "years"
                ],

            "yoy_growth":
                profit_yoy
        }
    }


# =========================================================
# MARGIN ANALYSIS
# =========================================================


def analyze_margins(
    statements
):
    """
    Analyze gross, operating,
    and net profit margins.
    """

    income_statement = statements.get(
        "income_statement",
        {}
    )

    revenue = income_statement.get(
        "revenue",
        {}
    )

    gross_profit = income_statement.get(
        "gross_profit",
        {}
    )

    operating_income = income_statement.get(
        "operating_income",
        {}
    )

    net_income = income_statement.get(
        "net_income",
        {}
    )

    gross_margin = calculate_margin_series(
        revenue,
        gross_profit
    )

    operating_margin = calculate_margin_series(
        revenue,
        operating_income
    )

    net_margin = calculate_margin_series(
        revenue,
        net_income
    )

    return {

        "gross_margin": {

            "yearly_values":
                gross_margin,

            "trend":
                analyze_margin_trend(
                    gross_margin
                )
        },

        "operating_margin": {

            "yearly_values":
                operating_margin,

            "trend":
                analyze_margin_trend(
                    operating_margin
                )
        },

        "net_profit_margin": {

            "yearly_values":
                net_margin,

            "trend":
                analyze_margin_trend(
                    net_margin
                )
        }
    }


# =========================================================
# CASH FLOW ANALYSIS
# =========================================================


def build_free_cash_flow_series(
    cash_flow
):
    """
    Use reported Free Cash Flow where available.

    If missing, calculate:
    FCF = Operating Cash Flow + Capital Expenditure
    """

    operating_cash_flow = cash_flow.get(
        "operating_cash_flow",
        {}
    )

    capital_expenditure = cash_flow.get(
        "capital_expenditure",
        {}
    )

    reported_fcf = cash_flow.get(
        "free_cash_flow",
        {}
    )

    years = set(
        operating_cash_flow.keys()
    )

    years.update(
        capital_expenditure.keys()
    )

    years.update(
        reported_fcf.keys()
    )

    free_cash_flow = {}

    for year in years:

        if (
            reported_fcf.get(year)
            is not None
        ):

            free_cash_flow[
                year
            ] = reported_fcf[
                year
            ]

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

            free_cash_flow[
                year
            ] = ocf + capex

        else:

            free_cash_flow[
                year
            ] = None

    return free_cash_flow


def analyze_cash_flow(
    statements
):
    """
    Analyze operating cash flow,
    free cash flow, FCF margin,
    and cash conversion.
    """

    income_statement = statements.get(
        "income_statement",
        {}
    )

    cash_flow = statements.get(
        "cash_flow",
        {}
    )

    revenue = income_statement.get(
        "revenue",
        {}
    )

    net_income = income_statement.get(
        "net_income",
        {}
    )

    operating_cash_flow = cash_flow.get(
        "operating_cash_flow",
        {}
    )

    free_cash_flow = build_free_cash_flow_series(
        cash_flow
    )

    fcf_margin = calculate_margin_series(
        revenue,
        free_cash_flow
    )

    cash_conversion = calculate_ratio_series(
        operating_cash_flow,
        net_income,
        multiplier=100
    )

    return {

        "operating_cash_flow": {

            "yearly_values":
                operating_cash_flow,

            "cagr":
                calculate_growth_metric(
                    operating_cash_flow
                ),

            "latest_value":
                get_latest_value(
                    operating_cash_flow
                )
        },

        "free_cash_flow": {

            "yearly_values":
                free_cash_flow,

            "cagr":
                calculate_growth_metric(
                    free_cash_flow
                ),

            "latest_value":
                get_latest_value(
                    free_cash_flow
                )
        },

        "free_cash_flow_margin": {

            "yearly_values":
                fcf_margin,

            "trend":
                analyze_margin_trend(
                    fcf_margin
                ),

            "latest_value":
                get_latest_value(
                    fcf_margin
                )
        },

        "cash_conversion": {

            "yearly_values":
                cash_conversion,

            "latest_value":
                get_latest_value(
                    cash_conversion
                )
        }
    }


# =========================================================
# DEBT ANALYSIS
# =========================================================


def analyze_debt(
    statements
):
    """
    Analyze debt, net debt,
    and debt-to-equity.
    """

    balance_sheet = statements.get(
        "balance_sheet",
        {}
    )

    total_debt = balance_sheet.get(
        "total_debt",
        {}
    )

    cash = balance_sheet.get(
        "cash",
        {}
    )

    equity = balance_sheet.get(
        "stockholders_equity",
        {}
    )

    net_debt = calculate_difference_series(
        total_debt,
        cash
    )

    debt_to_equity = calculate_ratio_series(
        total_debt,
        equity,
        multiplier=1
    )

    debt_change = calculate_percentage_change(
        total_debt
    )

    net_debt_change = calculate_percentage_change(
        net_debt
    )

    if debt_change is None:

        debt_trend = "insufficient_data"

    elif debt_change < -5:

        debt_trend = "improving"

    elif debt_change > 5:

        debt_trend = "deteriorating"

    else:

        debt_trend = "stable"

    return {

        "total_debt": {

            "yearly_values":
                total_debt,

            "latest_value":
                get_latest_value(
                    total_debt
                ),

            "percentage_change":
                debt_change,

            "trend":
                debt_trend
        },

        "net_debt": {

            "yearly_values":
                net_debt,

            "latest_value":
                get_latest_value(
                    net_debt
                ),

            "percentage_change":
                net_debt_change
        },

        "debt_to_equity": {

            "yearly_values":
                debt_to_equity,

            "latest_value":
                get_latest_value(
                    debt_to_equity
                )
        }
    }


# =========================================================
# LIQUIDITY ANALYSIS
# =========================================================


def add_series(
    first,
    second
):
    """
    Add two financial series
    for common or available years.
    """

    years = set(
        first.keys()
    )

    years.update(
        second.keys()
    )

    result = {}

    for year in years:

        first_value = first.get(
            year
        )

        second_value = second.get(
            year
        )

        if (
            first_value is not None
            and second_value is not None
        ):

            result[
                year
            ] = (
                first_value
                + second_value
            )

        else:

            result[
                year
            ] = None

    return result


def analyze_liquidity(
    statements
):
    """
    Analyze current ratio,
    quick ratio, and cash ratio.

    Quick Assets =
    Cash + Short-Term Investments
    + Accounts Receivable
    """

    balance_sheet = statements.get(
        "balance_sheet",
        {}
    )

    current_assets = balance_sheet.get(
        "current_assets",
        {}
    )

    current_liabilities = balance_sheet.get(
        "current_liabilities",
        {}
    )

    cash = balance_sheet.get(
        "cash",
        {}
    )

    cash_and_short_term_investments = (
        balance_sheet.get(
            "cash_and_short_term_investments",
            {}
        )
    )

    accounts_receivable = (
        balance_sheet.get(
            "accounts_receivable",
            {}
        )
    )

    current_ratio = calculate_ratio_series(
        current_assets,
        current_liabilities
    )

    quick_assets = add_series(
        cash_and_short_term_investments,
        accounts_receivable
    )

    quick_ratio = calculate_ratio_series(
        quick_assets,
        current_liabilities
    )

    cash_ratio = calculate_ratio_series(
        cash,
        current_liabilities
    )

    return {

        "current_ratio": {

            "yearly_values": current_ratio,

            "latest_value": get_latest_value(current_ratio),

            "trend": analyze_value_trend(current_ratio)
        },

        "quick_ratio": {

            "yearly_values":
                quick_ratio,

            "latest_value":
                get_latest_value(
                    quick_ratio
                ),

            "trend":
                analyze_value_trend(
                    quick_ratio
                )
        },

        "cash_ratio": {

            "yearly_values":
                cash_ratio,

            "latest_value":
                get_latest_value(
                    cash_ratio
                ),

            "trend":
                analyze_value_trend(
                    cash_ratio
                )
        }
    }


# =========================================================
# SCORE HELPERS
# =========================================================


def score_growth_cagr(
    cagr
):
    """
    Score growth CAGR from 0 to 10.

    This is a heuristic, not an industry benchmark.
    """

    if cagr is None:
        return None

    if cagr < 0:
        return 2

    if cagr < 5:
        return 5

    if cagr < 10:
        return 7

    if cagr < 20:
        return 9

    return 10


def score_margin_level(
    margin
):
    """
    Score a profitability margin from 0 to 10.
    """

    if margin is None:
        return None

    if margin < 0:
        return 1

    if margin < 5:
        return 4

    if margin < 10:
        return 6

    if margin < 20:
        return 8

    return 10


def score_margin_change(
    change
):
    """
    Score margin improvement from 0 to 10.
    """

    if change is None:
        return None

    if change <= -5:
        return 2

    if change <= -2:
        return 4

    if change < 0:
        return 5

    if change < 2:
        return 7

    if change < 5:
        return 9

    return 10


def score_positive_cash_flow(
    value,
    strong_score=10
):
    """
    Score whether the latest cash flow is positive.
    """

    if value is None:
        return None

    if value > 0:
        return strong_score

    return 2


def score_fcf_margin(
    margin
):
    """
    Score free cash flow margin.
    """

    if margin is None:
        return None

    if margin < 0:
        return 2

    if margin < 5:
        return 4

    if margin < 10:
        return 6

    if margin < 20:
        return 8

    return 10


def score_cash_conversion(
    conversion
):
    """
    Score operating cash flow
    relative to net income.
    """

    if conversion is None:
        return None

    if conversion < 0:
        return 2

    if conversion < 50:
        return 4

    if conversion < 80:
        return 6

    if conversion < 100:
        return 8

    return 10


def score_debt_change(
    change
):
    """
    Score debt movement.

    Lower debt growth is treated as better.
    """

    if change is None:
        return None

    if change < -20:
        return 10

    if change < -5:
        return 8

    if change <= 5:
        return 7

    if change <= 20:
        return 5

    return 3


def score_debt_to_equity(
    debt_to_equity
):
    """
    Score debt-to-equity.

    Heuristic thresholds.
    """

    if debt_to_equity is None:
        return None

    if debt_to_equity <= 0.5:
        return 10

    if debt_to_equity <= 1:
        return 8

    if debt_to_equity <= 2:
        return 6

    if debt_to_equity <= 3:
        return 4

    return 2


def score_current_ratio(
    ratio
):
    """

    Heuristic current-ratio score.
    """

    if ratio is None:
        return None

    if ratio < 0.75:
        return 2

    if ratio < 1:
        return 4

    if ratio < 1.5:
        return 6

    if ratio < 2:
        return 8

    return 10


def score_quick_ratio(
    ratio
):
    """
    Heuristic quick-ratio score.
    """

    if ratio is None:
        return None

    if ratio < 0.5:
        return 2

    if ratio < 0.75:
        return 4

    if ratio < 1:
        return 6

    if ratio < 1.5:
        return 8

    return 10


def score_cash_ratio(
    ratio
):
    """
    Heuristic cash-ratio score.
    """

    if ratio is None:
        return None

    if ratio < 0.05:
        return 2

    if ratio < 0.1:
        return 4

    if ratio < 0.25:
        return 6

    if ratio < 0.5:
        return 8

    return 10


def average_available(
    values
):
    """
    Average only values that are available.
    """

    available = [
        value
        for value in values
        if value is not None
    ]

    if not available:
        return None

    return round(
        sum(available)
        / len(available),
        2
    )


# =========================================================
# FINANCIAL HEALTH SCORE
# =========================================================


def calculate_financial_health_score(
    growth,
    margins,
    cash_flow,
    debt,
    liquidity
):
    """
    Calculate an overall financial health score
    from 0 to 10.

    Weighting:
    Growth       20%
    Profitability 20%
    Margin Trend 15%
    Cash Flow    15%
    Debt         15%
    Liquidity    15%

    The score is a transparent heuristic.
    """

    # -----------------------------------------
    # 1. GROWTH SCORE
    # -----------------------------------------

    revenue_cagr = growth[
        "revenue_growth"
    ][
        "cagr"
    ]

    profit_cagr = growth[
        "profit_growth"
    ][
        "cagr"
    ]

    growth_score = average_available(
        [
            score_growth_cagr(
                revenue_cagr
            ),

            score_growth_cagr(
                profit_cagr
            )
        ]
    )

    # -----------------------------------------
    # 2. PROFITABILITY SCORE
    # -----------------------------------------

    operating_margin = (
        margins[
            "operating_margin"
        ][
            "trend"
        ][
            "end_margin"
        ]
    )

    net_margin = (
        margins[
            "net_profit_margin"
        ][
            "trend"
        ][
            "end_margin"
        ]
    )

    profitability_score = average_available(
        [
            score_margin_level(
                operating_margin
            ),

            score_margin_level(
                net_margin
            )
        ]
    )

    # -----------------------------------------
    # 3. MARGIN TREND SCORE
    # -----------------------------------------

    operating_margin_change = (
        margins[
            "operating_margin"
        ][
            "trend"
        ][
            "change_percentage_points"
        ]
    )

    net_margin_change = (
        margins[
            "net_profit_margin"
        ][
            "trend"
        ][
            "change_percentage_points"
        ]
    )

    margin_trend_score = average_available(
        [
            score_margin_change(
                operating_margin_change
            ),

            score_margin_change(
                net_margin_change
            )
        ]
    )

    # -----------------------------------------
    # 4. CASH FLOW SCORE
    # -----------------------------------------

    latest_ocf = cash_flow[
        "operating_cash_flow"
    ][
        "latest_value"
    ]

    latest_fcf = cash_flow[
        "free_cash_flow"
    ][
        "latest_value"
    ]

    latest_fcf_margin = cash_flow[
        "free_cash_flow_margin"
    ][
        "latest_value"
    ]

    latest_cash_conversion = cash_flow[
        "cash_conversion"
    ][
        "latest_value"
    ]

    cash_flow_score = average_available(
        [
            score_positive_cash_flow(
                latest_ocf,
                strong_score=8
            ),

            score_positive_cash_flow(
                latest_fcf,
                strong_score=10
            ),

            score_fcf_margin(
                latest_fcf_margin
            ),

            score_cash_conversion(
                latest_cash_conversion
            )
        ]
    )

    # -----------------------------------------
    # 5. DEBT SCORE
    # -----------------------------------------

    debt_change = debt[
        "total_debt"
    ][
        "percentage_change"
    ]

    latest_debt_to_equity = debt[
        "debt_to_equity"
    ][
        "latest_value"
    ]

    debt_to_equity_multiple = (
        latest_debt_to_equity
        if latest_debt_to_equity is not None
        else None
    )

    debt_score = average_available(
        [
            score_debt_change(
                debt_change
            ),

            score_debt_to_equity(
                debt_to_equity_multiple
            )
        ]
    )

    # -----------------------------------------
    # 6. LIQUIDITY SCORE
    # -----------------------------------------

    latest_current_ratio = liquidity[
        "current_ratio"
    ][
        "latest_value"
    ]

    latest_quick_ratio = liquidity[
        "quick_ratio"
    ][
        "latest_value"
    ]

    latest_cash_ratio = liquidity[
        "cash_ratio"
    ][
        "latest_value"
    ]

    liquidity_score = average_available(
        [
            score_current_ratio(
                latest_current_ratio
            ),

            score_quick_ratio(
                latest_quick_ratio
            ),

            score_cash_ratio(
                latest_cash_ratio
            )
        ]
    )

    # -----------------------------------------
    # WEIGHTS
    # -----------------------------------------

    weights = {

        "growth": 20,

        "profitability": 20,

        "margin_trend": 15,

        "cash_flow": 15,

        "debt": 15,

        "liquidity": 15
    }

    scores = {

        "growth": growth_score,

        "profitability":
            profitability_score,

        "margin_trend":
            margin_trend_score,

        "cash_flow":
            cash_flow_score,

        "debt": debt_score,

        "liquidity":
            liquidity_score
    }

    # -----------------------------------------
    # CALCULATE WEIGHTED SCORE
    # -----------------------------------------

    weighted_sum = 0

    available_weight = 0

    for category, score in scores.items():

        if score is None:
            continue

        weighted_sum += (
            score
            * weights[category]
        )

        available_weight += (
            weights[category]
        )

    if available_weight == 0:

        overall_score = None

    else:

        overall_score = round(
            weighted_sum
            / available_weight,
            2
        )

    # -----------------------------------------
    # INTERPRETATION
    # -----------------------------------------

    if overall_score is None:

        interpretation = (
            "Insufficient data"
        )

    elif overall_score >= 8.5:

        interpretation = (
            "Excellent financial health"
        )

    elif overall_score >= 7:

        interpretation = (
            "Strong financial health"
        )

    elif overall_score >= 5.5:

        interpretation = (
            "Moderate financial health"
        )

    elif overall_score >= 4:

        interpretation = (
            "Weak financial health"
        )

    else:

        interpretation = (
            "Poor financial health"
        )

    return {

        "overall_score":
            overall_score,

        "interpretation":
            interpretation,

        "component_scores":
            scores,

        "weights":
            weights,

        "available_weight":
            available_weight
    }


# =========================================================
# INSIGHT GENERATION
# =========================================================


def generate_basic_insights(
    growth,
    margins,
    cash_flow,
    debt,
    liquidity,
    health
):
    """
    Generate rule-based financial insights.
    """

    insights = []

    # -----------------------------------------
    # REVENUE
    # -----------------------------------------

    revenue_cagr = growth[
        "revenue_growth"
    ][
        "cagr"
    ]

    if revenue_cagr is not None:

        insights.append(
            f"Revenue grew at a "
            f"{revenue_cagr}% CAGR."
        )

    # -----------------------------------------
    # PROFIT
    # -----------------------------------------

    profit_cagr = growth[
        "profit_growth"
    ][
        "cagr"
    ]

    if profit_cagr is not None:

        insights.append(
            f"Net income grew at a "
            f"{profit_cagr}% CAGR."
        )

    # -----------------------------------------
    # OPERATING MARGIN
    # -----------------------------------------

    operating_trend = margins[
        "operating_margin"
    ][
        "trend"
    ]

    if (
        operating_trend[
            "start_margin"
        ]
        is not None
        and operating_trend[
            "end_margin"
        ]
        is not None
    ):

        if operating_trend[
            "trend"
        ] == "improving":

            insights.append(
                f"Operating margin improved "
                f"from "
                f"{operating_trend['start_margin']}% "
                f"to "
                f"{operating_trend['end_margin']}%."
            )

        elif operating_trend[
            "trend"
        ] == "declining":

            insights.append(
                f"Operating margin declined "
                f"from "
                f"{operating_trend['start_margin']}% "
                f"to "
                f"{operating_trend['end_margin']}%."
            )

    # -----------------------------------------
    # FREE CASH FLOW
    # -----------------------------------------

    latest_fcf = cash_flow[
        "free_cash_flow"
    ][
        "latest_value"
    ]

    if latest_fcf is not None:

        if latest_fcf > 0:

            insights.append(
                "The company generated "
                "positive free cash flow "
                "in the latest available year."
            )

        else:

            insights.append(
                "The company reported "
                "negative free cash flow "
                "in the latest available year."
            )

    # -----------------------------------------
    # DEBT
    # -----------------------------------------

    debt_change = debt[
        "total_debt"
    ][
        "percentage_change"
    ]

    if debt_change is not None:

        if debt_change < 0:

            insights.append(
                f"Total debt decreased by "
                f"{abs(debt_change)}% "
                f"over the available period."
            )

        elif debt_change > 0:

            insights.append(
                f"Total debt increased by "
                f"{debt_change}% "
                f"over the available period."
            )

        else:

            insights.append(
                "Total debt remained "
                "broadly stable."
            )

    # -----------------------------------------
    # LIQUIDITY
    # -----------------------------------------

    current_ratio = liquidity[
        "current_ratio"
    ][
        "latest_value"
    ]

    if current_ratio is not None:

        insights.append(
            f"The latest current ratio "
            f"was {current_ratio}."
        )

    # -----------------------------------------
    # HEALTH SCORE
    # -----------------------------------------

    score = health[
        "overall_score"
    ]

    if score is not None:

        insights.append(
            f"Overall financial health "
            f"score: {score}/10."
        )

    return insights

# =========================================================
# PEER COMPARISON
# =========================================================

def build_peer_comparison(tickers, get_statements_func, get_ratios_func):
    """
    Build a comparable financial snapshot for multiple companies
    using the same analysis logic as the individual company endpoint.
    """

    companies = []

    for ticker in tickers:

        ticker = ticker.strip().upper()

        if not ticker:
            continue

        try:

            # -------------------------------------------------
            # 1. FETCH FINANCIAL STATEMENTS
            # -------------------------------------------------

            statements = get_statements_func(ticker)

            # -------------------------------------------------
            # 2. RUN EXISTING ANALYSIS FUNCTIONS
            # -------------------------------------------------

            growth_analysis = analyze_growth(
                statements
            )

            margin_analysis = analyze_margins(
                statements
            )

            cash_flow_analysis = analyze_cash_flow(
                statements
            )

            debt_analysis = analyze_debt(
                statements
            )

            liquidity_analysis = analyze_liquidity(
                statements
            )

            financial_health = calculate_financial_health_score(
                growth_analysis,
                margin_analysis,
                cash_flow_analysis,
                debt_analysis,
                liquidity_analysis
            )

            # -------------------------------------------------
            # 3. GET EXISTING RATIOS
            # -------------------------------------------------

            ratios = get_ratios_func(ticker)

            # -------------------------------------------------
            # 4. EXTRACT REVENUE
            # -------------------------------------------------

            income_statement = statements.get(
                "income_statement",
                {}
            )

            revenue = income_statement.get(
                "revenue",
                {}
            )

            valid_revenue = {
                year: value
                for year, value in revenue.items()
                if value is not None
            }

            latest_revenue_year = (
                max(valid_revenue.keys(), key=int)
                if valid_revenue
                else None
            )

            latest_revenue = (
                valid_revenue[latest_revenue_year]
                if latest_revenue_year
                else None
            )

            # -------------------------------------------------
            # 5. EXTRACT NET INCOME
            # -------------------------------------------------

            net_income = income_statement.get(
                "net_income",
                {}
            )

            valid_income = {
                year: value
                for year, value in net_income.items()
                if value is not None
            }

            latest_income_year = (
                max(valid_income.keys(), key=int)
                if valid_income
                else None
            )

            latest_net_income = (
                valid_income[latest_income_year]
                if latest_income_year
                else None
            )

            # -------------------------------------------------
            # 6. EXTRACT GROWTH
            # -------------------------------------------------

            revenue_growth = (
                growth_analysis
                .get("revenue_growth", {})
                .get("cagr")
            )

            profit_growth = (
                growth_analysis
                .get("profit_growth", {})
                .get("cagr")
            )

            # -------------------------------------------------
            # 7. RETURN COMPARISON RECORD
            # -------------------------------------------------

            companies.append({

                "ticker": ticker,

                "revenue": latest_revenue,

                "revenue_growth": revenue_growth,

                "profit_growth": profit_growth,

                "profit_margin": ratios.get(
                    "profit_margin_percent"
                ),

                "pe_ratio": ratios.get(
                    "pe_ratio"
                ),

                "roe_percent": ratios.get(
                    "roe_percent"
                ),

                "debt_to_equity": ratios.get(
                    "debt_to_equity"
                ),

                "financial_health": (
                    financial_health.get("overall_score")
                    if financial_health
                    else None
                )
            })

        except Exception as e:

            companies.append({
                "ticker": ticker,
                "error": str(e)
            })

    return companies