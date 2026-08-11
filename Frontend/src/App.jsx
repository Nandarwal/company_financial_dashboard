import { useState } from "react";
import "./App.css";

const API_URL =
  import.meta.env.VITE_API_URL || "https://company-financial-dashboard.onrender.com";

function App() {
  const [ticker, setTicker] = useState("AAPL");
  const [input, setInput] = useState("AAPL");
  const [analysis, setAnalysis] = useState(null);
  const [ratios, setRatios] = useState(null);

  const [comparison, setComparison] = useState(null);
  const [comparisonLoading, setComparisonLoading] = useState(false);
  const [comparisonError, setComparisonError] = useState("");
  const [comparisonInputs, setComparisonInputs] = useState(["", "", ""]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const analyzeCompany = async () => {
    const symbol = input.trim().toUpperCase();

    if (!symbol) return;

    setLoading(true);
    setError("");

    try {
      const [analysisResponse, ratiosResponse] = await Promise.all([
        fetch(`${API_URL}/analysis/${symbol}`),
        fetch(`${API_URL}/ratios/${symbol}`),
      ]);

      if (!analysisResponse.ok) {
        throw new Error("Could not retrieve company analysis.");
      }

      if (!ratiosResponse.ok) {
        throw new Error("Could not retrieve company ratios.");
      }

      const analysisData = await analysisResponse.json();
      const ratiosData = await ratiosResponse.json();

      setTicker(symbol);
      setAnalysis(analysisData);
      setRatios(ratiosData);
    } catch (err) {
      setError(err.message);
      setAnalysis(null);
      setRatios(null);
    } finally {
      setLoading(false);
    }
  };

  const compareCompanies = async () => {
  const tickers = comparisonInputs
    .map((ticker) => ticker.trim().toUpperCase())
    .filter((ticker) => ticker !== "");

  if (tickers.length < 2) {
    setComparisonError(
      "Please enter at least two companies to compare."
    );
    return;
  }

  if (tickers.length > 5) {
    setComparisonError(
      "You can compare a maximum of five companies."
    );
    return;
  }

  // Prevent duplicate companies
  const uniqueTickers = [...new Set(tickers)];

  if (uniqueTickers.length !== tickers.length) {
    setComparisonError(
      "Please enter each company only once."
    );
    return;
  }

  setComparisonLoading(true);
  setComparisonError("");
  setComparison(null);

  try {
    const response = await fetch(
      `${API_URL}/compare?tickers=${encodeURIComponent(
        tickers.join(",")
      )}`
    );

    if (!response.ok) {
      throw new Error(
        "Could not retrieve peer comparison."
      );
    }

    const data = await response.json();

    setComparison(data);

  } catch (err) {

    setComparisonError(err.message);
    setComparison(null);

  } finally {

    setComparisonLoading(false);

  }
};

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Company Financial Dashboard</h1>
          <p>Financial analysis made simple.</p>
        </div>
      </header>

      <main className="container">
        <section className="search-section">
          <h2>Analyze a Company</h2>

          <div className="search-box">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  analyzeCompany();
                }
              }}
              placeholder="Enter ticker e.g. AAPL"
            />

            <button onClick={analyzeCompany} disabled={loading}>
              {loading ? "Analyzing..." : "Analyze"}
            </button>
          </div>

          <p className="example">
            Try: AAPL, MSFT, NVDA, GOOGL
          </p>
        </section>

        {error && <div className="error">{error}</div>}

        {analysis && ratios && (
          <>
            <section className="company-header">
              <div>
                <p className="eyebrow">COMPANY</p>
                <h2>{ticker}</h2>
              </div>

              <div className="health-score">
                <p>Financial Health</p>
                <strong>
                  {analysis.financial_health.overall_score}/10
                </strong>
                <span>
                  {analysis.financial_health.interpretation}
                </span>
              </div>
            </section>

            <section className="metrics-grid">
              <MetricCard
                title="Revenue CAGR"
                value={`${analysis.growth.revenue_growth.cagr}%`}
              />

              <MetricCard
                title="Profit CAGR"
                value={`${analysis.growth.profit_growth.cagr}%`}
              />

              <MetricCard
                title="P/E Ratio"
                value={
                  ratios.pe_ratio !== null
                    ? `${ratios.pe_ratio}x`
                    : "N/A"
                }
              />

              <MetricCard
                title="ROE"
                value={
                  ratios.roe_percent !== null
                    ? `${ratios.roe_percent}%`
                    : "N/A"
                }
              />

              <MetricCard
                title="Debt / Equity"
                value={
                  ratios.debt_to_equity !== null
                    ? `${ratios.debt_to_equity}x`
                    : "N/A"
                }
              />

              <MetricCard
                title="Profit Margin"
                value={
                  ratios.profit_margin_percent !== null
                    ? `${ratios.profit_margin_percent}%`
                    : "N/A"
                }
              />
            </section>

            <section className="section">
              <h2>Financial Performance</h2>

              <div className="cards">
                <InfoCard
                  title="Revenue"
                  value={`${formatBillions(
                    analysis.growth.revenue_growth.end_value
                  )}B`}
                  subtitle={`CAGR: ${analysis.growth.revenue_growth.cagr}%`}
                />

                <InfoCard
                  title="Net Income"
                  value={`${formatBillions(
                    analysis.growth.profit_growth.end_value
                  )}B`}
                  subtitle={`CAGR: ${analysis.growth.profit_growth.cagr}%`}
                />

                <InfoCard
                  title="Operating Margin"
                  value={`${analysis.margins.operating_margin.trend.end_margin}%`}
                  subtitle={
                    analysis.margins.operating_margin.trend.trend
                  }
                />

                <InfoCard
                  title="Free Cash Flow"
                  value={`${formatBillions(
                    analysis.cash_flow.free_cash_flow.latest_value
                  )}B`}
                  subtitle={`Margin: ${analysis.cash_flow.free_cash_flow_margin.latest_value}%`}
                />
              </div>
            </section>

            <section className="section">
              <h2>Financial Health Breakdown</h2>

              <div className="score-list">
                <ScoreRow
                  name="Growth"
                  score={analysis.financial_health.component_scores.growth}
                />

                <ScoreRow
                  name="Profitability"
                  score={
                    analysis.financial_health.component_scores
                      .profitability
                  }
                />

                <ScoreRow
                  name="Margin Trend"
                  score={
                    analysis.financial_health.component_scores
                      .margin_trend
                  }
                />

                <ScoreRow
                  name="Cash Flow"
                  score={
                    analysis.financial_health.component_scores
                      .cash_flow
                  }
                />

                <ScoreRow
                  name="Debt"
                  score={analysis.financial_health.component_scores.debt}
                />

                <ScoreRow
                  name="Liquidity"
                  score={
                    analysis.financial_health.component_scores
                      .liquidity
                  }
                />
              </div>
            </section>

            <section className="section">
              <h2>Key Insights</h2>

              <div className="insights">
                {analysis.insights.map((insight, index) => (
                  <div className="insight" key={index}>
                    <span>•</span>
                    <p>{insight}</p>
                  </div>
                ))}
              </div>
            </section>

            <section className="section">
              <h2>Liquidity</h2>

              <div className="cards">
                <InfoCard
                  title="Current Ratio"
                  value={analysis.liquidity.current_ratio.latest_value}
                  subtitle={
                    analysis.liquidity.current_ratio.trend.trend
                  }
                />

                <InfoCard
                  title="Quick Ratio"
                  value={analysis.liquidity.quick_ratio.latest_value}
                  subtitle={
                    analysis.liquidity.quick_ratio.trend.trend
                  }
                />

                <InfoCard
                  title="Cash Ratio"
                  value={analysis.liquidity.cash_ratio.latest_value}
                  subtitle={
                    analysis.liquidity.cash_ratio.trend.trend
                  }
                />
              </div>
            </section>
          </>
        )}
          <section className="section comparison-section">
  <h2>Compare Companies</h2>

  <p className="section-description">
    Compare financial performance across companies.
  </p>

  <div className="comparison-controls">

  {comparisonInputs.map((value, index) => (
    <input
      key={index}
      type="text"
      value={value}
      onChange={(e) => {
        const updatedInputs = [
          ...comparisonInputs
        ];

        updatedInputs[index] =
          e.target.value.toUpperCase();

        setComparisonInputs(updatedInputs);
      }}
      placeholder={`Company ${index + 1} ticker`}
      maxLength={10}
    />
  ))}

  <button
    onClick={compareCompanies}
    disabled={comparisonLoading}
  >
    {comparisonLoading
      ? "Comparing..."
      : "Compare"}
  </button>

</div>


  {comparisonError && (
    <div className="error">
      {comparisonError}
    </div>
  )}

  {comparison && (
    <div className="comparison-table-wrapper">
      <table className="comparison-table">

        <thead>
          <tr>
            <th>Metric</th>

            {comparison.companies.map((company) => (
              <th key={company.ticker}>
                {company.ticker}
              </th>
            ))}
          </tr>
        </thead>

        <tbody>

          <tr>
            <td>Revenue</td>

            {comparison.companies.map((company) => (
              <td key={company.ticker}>
                {formatBillions(company.revenue)}B
              </td>
            ))}
          </tr>

          <tr>
            <td>Revenue Growth</td>

            {comparison.companies.map((company) => (
              <td key={company.ticker}>
                {company.revenue_growth !== null
                  ? `${company.revenue_growth}%`
                  : "N/A"}
              </td>
            ))}
          </tr>

          <tr>
            <td>Profit Growth</td>

            {comparison.companies.map((company) => (
              <td key={company.ticker}>
                {company.profit_growth !== null
                  ? `${company.profit_growth}%`
                  : "N/A"}
              </td>
            ))}
          </tr>

          <tr>
            <td>Profit Margin</td>

            {comparison.companies.map((company) => (
              <td key={company.ticker}>
                {company.profit_margin !== null
                  ? `${company.profit_margin}%`
                  : "N/A"}
              </td>
            ))}
          </tr>

          <tr>
            <td>ROE</td>

            {comparison.companies.map((company) => (
              <td key={company.ticker}>
                {company.roe_percent !== null
                  ? `${company.roe_percent}%`
                  : "N/A"}
              </td>
            ))}
          </tr>

          <tr>
            <td>P/E Ratio</td>

            {comparison.companies.map((company) => (
              <td key={company.ticker}>
                {company.pe_ratio !== null
                  ? `${company.pe_ratio}x`
                  : "N/A"}
              </td>
            ))}
          </tr>

          <tr>
            <td>Debt / Equity</td>

            {comparison.companies.map((company) => (
              <td key={company.ticker}>
                {company.debt_to_equity !== null
                  ? `${company.debt_to_equity}x`
                  : "N/A"}
              </td>
            ))}
          </tr>

          <tr>
            <td>Financial Health</td>

            {comparison.companies.map((company) => (
              <td key={company.ticker}>
                {company.financial_health !== null
                  ? `${company.financial_health}/10`
                  : "N/A"}
              </td>
            ))}
          </tr>

        </tbody>

      </table>
    </div>
  )}
</section>
      </main>
    </div>
  );
}

function MetricCard({ title, value }) {
  return (
    <div className="metric-card">
      <p>{title}</p>
      <strong>{value}</strong>
    </div>
  );
}

function InfoCard({ title, value, subtitle }) {
  return (
    <div className="info-card">
      <p>{title}</p>
      <strong>{value}</strong>
      <span>{subtitle}</span>
    </div>
  );
}

function ScoreRow({ name, score }) {
  const percentage = (score / 10) * 100;

  return (
    <div className="score-row">
      <div className="score-name">
        <span>{name}</span>
        <strong>{score}/10</strong>
      </div>

      <div className="score-bar">
        <div
          className="score-fill"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

function formatBillions(value) {
  if (value === null || value === undefined) {
    return "N/A";
  }

  return (value / 1_000_000_000).toFixed(2);
}

export default App;