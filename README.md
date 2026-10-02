# Company Financial Dashboard

A full-stack financial analysis dashboard that allows users to analyze individual companies and compare multiple companies using financial statement and market data.

## Live Application

**Frontend:**  
https://company-financial-dashboard-iota.vercel.app

**Backend API:**  
https://company-financial-dashboard.onrender.com

**API Health Check:**  
https://company-financial-dashboard.onrender.com/health

---
## What This Project Does

Company Financial Dashboard is a full-stack web application for analyzing public companies using financial statement and market data.

Users can enter a company name or ticker symbol, retrieve financial data, analyze historical performance, and compare multiple companies using standardized financial metrics.

The application combines a React frontend with a FastAPI backend and retrieves financial data through `yfinance`.

---

## Features

### Individual Company Analysis

Users can enter either a company name or ticker symbol and view:

- Company information
- Revenue growth
- Profit growth
- Gross margin
- Operating margin
- Net profit margin
- Operating cash flow
- Free cash flow
- Free cash flow margin
- Cash conversion
- Total debt
- Net debt
- Debt-to-equity ratio
- Current ratio
- Quick ratio
- Cash ratio
- Financial health score
- Financial health component scores
- Automated financial insights

### Company Name Resolution

The dashboard accepts both company names and ticker symbols.

Examples:

- Apple → AAPL
- Microsoft → MSFT
- Amazon → AMZN
- Reliance → RELIANCE.NS
- HDFC Bank → HDFCBANK.NS
- Bharti Airtel → BHARTIARTL.NS

The backend resolves company names into the appropriate Yahoo Finance ticker before retrieving financial data.

### Peer Comparison

Users can compare between 2 and 5 companies.

The comparison includes:

- Revenue
- Revenue growth
- Profit growth
- Profit margin
- ROE
- P/E ratio
- Debt-to-equity ratio
- Financial health score

The comparison supports both Indian and international companies.

---

## Technical Highlights

- Built a full-stack application using React and FastAPI
- Implemented REST API endpoints for financial data and analysis
- Built a company-name-to-ticker resolution system
- Implemented financial statement processing using Python and Pandas
- Calculated growth, profitability, cash flow, debt, and liquidity metrics
- Developed a financial health scoring framework
- Implemented multi-company peer comparison
- Added support for both Indian and international companies
- Deployed the frontend on Vercel and backend on Render
- Configured communication between the deployed frontend and backend through REST APIs

---

## Technology Stack

### Frontend

- React
- Vite
- JavaScript
- CSS

### Backend

- Python
- FastAPI
- Uvicorn
- Pandas
- yfinance

### Deployment

- Vercel — frontend
- Render — backend

### Data

Financial and market data is retrieved through Yahoo Finance using `yfinance`.

---

## Project Structure

```text
Company Dashboard/
│
├── Backend/
│   ├── data/
│   │   └── global_companies.csv
│   │
│   ├── services/
│   │   ├── company_resolver.py
│   │   ├── finance.py
│   │   └── analysis.py
│   │
│   ├── utils/
│   │   └── formatter.py
│   │
│   ├── create_global_company_list.py
│   ├── main.py
│   └── requirements.txt
│
├── Frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.jsx
│   │   └── ...
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
├── .gitignore
└── README.md
```

---

## Running the Backend Locally

Navigate to the backend directory:

```bash
cd Backend
```

Create a virtual environment if needed:

```bash
python3 -m venv venv
```

Activate the virtual environment:

```bash
source venv/bin/activate
```

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
python -m uvicorn main:app --reload
```

The backend will normally be available at:

```text
http://127.0.0.1:8000
```

### FastAPI Documentation

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### Health Check

```text
http://127.0.0.1:8000/health
```

---

## Running the Frontend Locally

Open another terminal and navigate to the frontend:

```bash
cd Frontend
```

Install the frontend dependencies:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

---

## Environment Variables

The frontend uses the following environment variable to determine which backend API it should communicate with:

```text
VITE_API_URL
```

### Local Development

For local development:

```text
VITE_API_URL=http://127.0.0.1:8000
```

### Production

For the deployed application:

```text
VITE_API_URL=https://company-financial-dashboard.onrender.com
```

Environment files containing local or deployment-specific configuration should not be committed to Git.

---

## API Endpoints

### Health Check

```http
GET /health
```

Example:

```text
https://company-financial-dashboard.onrender.com/health
```

### Company Information

```http
GET /company/{ticker}
```

### Financial Statements

```http
GET /financials/{ticker}
```

### Stock History

```http
GET /stock/{ticker}
```

### Financial Ratios

```http
GET /ratios/{ticker}
```

### Detailed Financial Statements

```http
GET /statements/{ticker}
```

### Financial Analysis

```http
GET /analysis/{ticker}
```

### Peer Comparison

```http
GET /compare?tickers=Apple,Microsoft,Amazon
```

The comparison endpoint accepts between 2 and 5 companies.

---

## Financial Analysis

The dashboard analyzes several dimensions of a company's financial performance.

### Growth

The growth analysis includes:

- Revenue growth
- Revenue CAGR
- Profit growth
- Profit CAGR
- Historical yearly values
- Growth trends

### Profitability and Margins

The dashboard evaluates:

- Gross margin
- Operating margin
- Net profit margin
- Margin trends

### Cash Flow

The dashboard analyzes:

- Operating cash flow
- Free cash flow
- Free cash flow margin
- Cash conversion

### Debt

The dashboard evaluates:

- Total debt
- Net debt
- Debt-to-equity ratio
- Debt trends

### Liquidity

The dashboard calculates:

- Current ratio
- Quick ratio
- Cash ratio
- Liquidity trends

### Financial Health Score

The dashboard combines multiple financial dimensions into an overall financial health score.

The score incorporates components including:

- Growth
- Profitability
- Margin trends
- Cash flow
- Debt
- Liquidity

The overall score is displayed on a 0–10 scale together with component-level scores.

---
## Financial Metrics

The application calculates a range of financial metrics from company financial statements.

| Metric | Description |
|---|---|
| Revenue CAGR | Compound annual growth rate of revenue |
| Profit CAGR | Compound annual growth rate of net income |
| Gross Margin | Gross profit as a percentage of revenue |
| Operating Margin | Operating income as a percentage of revenue |
| Net Profit Margin | Net income as a percentage of revenue |
| Free Cash Flow | Operating cash flow less capital expenditure |
| Free Cash Flow Margin | Free cash flow as a percentage of revenue |
| Current Ratio | Current assets divided by current liabilities |
| Quick Ratio | Liquid current assets relative to current liabilities |
| Cash Ratio | Cash and cash equivalents relative to current liabilities |
| Debt-to-Equity | Total debt relative to shareholders' equity |
| ROE | Return on shareholders' equity |
| P/E Ratio | Market price relative to earnings |

### Example Formulas

Revenue CAGR:

$$
CAGR = \left(\frac{Ending\ Revenue}{Beginning\ Revenue}\right)^{1/n} - 1
$$

Current Ratio:

$$
Current\ Ratio = \frac{Current\ Assets}{Current\ Liabilities}
$$

Free Cash Flow:

$$
FCF = Operating\ Cash\ Flow - Capital\ Expenditure
$$
---

## Company Comparison

The peer comparison feature allows users to enter between 2 and 5 companies.

For example:

```text
Apple
Microsoft
Amazon
```

The application resolves the company names into their corresponding market tickers and retrieves comparable financial metrics.

The comparison table includes metrics such as:

| Metric | Description |
|---|---|
| Revenue | Latest available revenue |
| Revenue Growth | Recent revenue growth |
| Profit Growth | Recent net income growth |
| Profit Margin | Net income as a percentage of revenue |
| ROE | Return on equity |
| P/E | Price-to-earnings ratio |
| Debt-to-Equity | Relative level of debt financing |
| Financial Health Score | Overall dashboard score |

---

## Company Name Resolution

The backend contains a company resolution system that allows users to search using company names instead of requiring exact ticker symbols.

The resolver uses company reference data and exchange-specific information to map user input to market tickers.

Examples:

```text
Apple
    ↓
AAPL

Microsoft
    ↓
MSFT

Amazon
    ↓
AMZN

Reliance
    ↓
RELIANCE.NS

HDFC Bank
    ↓
HDFCBANK.NS

Bharti Airtel
    ↓
BHARTIARTL.NS
```

This makes the dashboard easier to use for users who may not know a company's exact ticker symbol.

---

## Data Sources

The dashboard retrieves financial and market information using the `yfinance` Python library and Yahoo Finance data.

The application may use:

- Income statement data
- Balance sheet data
- Cash flow data
- Market price data
- Company information
- Financial ratios

Data availability can vary between companies and reporting periods.

---

## Important Data Considerations

Financial data is dependent on the availability and quality of the underlying market-data provider.

Different companies may have:

- Different fiscal year-end dates
- Different reporting periods
- Different accounting classifications
- Missing financial statement fields
- Different levels of historical data availability

Therefore, metrics may not always be directly comparable across every company.

The dashboard attempts to handle unavailable data gracefully rather than assuming that every financial metric is available for every company.

---

## Deployment Architecture

The project is deployed using separate frontend and backend services.

```text
                    User
                      │
                      ▼
          ┌──────────────────────┐
          │   React / Vite       │
          │   Frontend           │
          │   Vercel             │
          └──────────┬───────────┘
                     │
                     │ HTTPS API Requests
                     ▼
          ┌──────────────────────┐
          │   FastAPI Backend    │
          │   Render             │
          └──────────┬───────────┘
                     │
                     │ Financial Data
                     ▼
          ┌──────────────────────┐
          │ Yahoo Finance        │
          │ via yfinance         │
          └──────────────────────┘
```

### Frontend

The React/Vite frontend is hosted on Vercel.

### Backend

The FastAPI backend is hosted on Render.

### Communication

The frontend communicates with the backend through HTTPS API requests.

---

## Local Development Architecture

When running the project locally:

```text
React / Vite
    │
    │ HTTP API Requests
    ▼
FastAPI
    │
    ▼
yfinance / Yahoo Finance
```

The frontend normally runs on:

```text
http://localhost:5173
```

The backend normally runs on:

```text
http://127.0.0.1:8000
```

---

## Example Workflow

A typical user workflow is:

```text
1. Enter a company name or ticker
              ↓
2. Backend resolves the company
              ↓
3. Financial data is retrieved
              ↓
4. Financial statements are processed
              ↓
5. Growth, profitability, cash flow,
   debt and liquidity are analyzed
              ↓
6. Financial health score is calculated
              ↓
7. Financial insights are generated
              ↓
8. Results are displayed in the dashboard
```

For company comparison:

```text
1. Enter 2–5 companies
              ↓
2. Resolve company names to tickers
              ↓
3. Retrieve financial data
              ↓
4. Calculate comparable metrics
              ↓
5. Display comparison table
```

---

## GitHub

The source code for the project is available on GitHub:

https://github.com/Nandarwal/company_financial_dashboard

---

## Project Purpose

This project was developed as a full-stack financial analysis application combining:

- Financial data analysis
- Python programming
- API development
- React frontend development
- Data processing
- Financial ratio analysis
- Company comparison
- Deployment

It is intended for educational, analytical, and project purposes.

---

## Disclaimer

The information presented by this dashboard is for educational and analytical purposes only.

Financial data may contain delays, omissions, estimation differences, or classification differences depending on the underlying data provider.

The financial health score and automated insights are analytical outputs generated by the application and should not be interpreted as personalized investment advice or a recommendation to buy or sell any security.

---

## Author

**Nandini Agarwal**