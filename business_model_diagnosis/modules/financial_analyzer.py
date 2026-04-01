import yfinance as yf
import pandas as pd
import numpy as np
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def _safe(val, default="N/A"):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return default
    return val


class FinancialAnalyzer:
    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.yf_ticker = yf.Ticker(self.ticker)
        self._info: dict = {}
        self._financials: Optional[pd.DataFrame] = None
        self._balance_sheet: Optional[pd.DataFrame] = None
        self._cashflow: Optional[pd.DataFrame] = None
        self._quarterly_financials: Optional[pd.DataFrame] = None

    def load_data(self):
        print("  [finance] Loading financial statements from Yahoo Finance...")
        try:
            self._info = self.yf_ticker.info or {}
        except Exception as e:
            logger.warning(f"Could not load info: {e}")
            self._info = {}
        try:
            self._financials = self.yf_ticker.financials
        except Exception as e:
            logger.warning(f"Could not load financials: {e}")
        try:
            self._balance_sheet = self.yf_ticker.balance_sheet
        except Exception as e:
            logger.warning(f"Could not load balance sheet: {e}")
        try:
            self._cashflow = self.yf_ticker.cashflow
        except Exception as e:
            logger.warning(f"Could not load cashflow: {e}")
        try:
            self._quarterly_financials = self.yf_ticker.quarterly_financials
        except Exception as e:
            logger.warning(f"Could not load quarterly financials: {e}")

    def _get_row(self, df: Optional[pd.DataFrame], *keys) -> Optional[pd.Series]:
        if df is None or df.empty:
            return None
        for key in keys:
            if key in df.index:
                return df.loc[key]
        return None

    def _fmt(self, value, unit="B") -> str:
        try:
            v = float(value)
            if unit == "B":
                return f"${v / 1e9:.2f}B"
            elif unit == "M":
                return f"${v / 1e6:.2f}M"
            elif unit == "%":
                return f"{v * 100:.2f}%"
            elif unit == "x":
                return f"{v:.2f}x"
            return str(round(v, 4))
        except Exception:
            return "N/A"

    def _compute_ratios(self) -> dict:
        info = self._info
        ratios = {}

        ratios["market_cap"] = _safe(info.get("marketCap"))
        ratios["enterprise_value"] = _safe(info.get("enterpriseValue"))
        ratios["pe_ratio"] = _safe(info.get("trailingPE"))
        ratios["forward_pe"] = _safe(info.get("forwardPE"))
        ratios["pb_ratio"] = _safe(info.get("priceToBook"))
        ratios["ps_ratio"] = _safe(info.get("priceToSalesTrailing12Months"))
        ratios["peg_ratio"] = _safe(info.get("pegRatio"))
        ratios["ev_ebitda"] = _safe(info.get("enterpriseToEbitda"))
        ratios["ev_revenue"] = _safe(info.get("enterpriseToRevenue"))
        ratios["dividend_yield"] = _safe(info.get("dividendYield"))
        ratios["payout_ratio"] = _safe(info.get("payoutRatio"))
        ratios["beta"] = _safe(info.get("beta"))
        ratios["52w_high"] = _safe(info.get("fiftyTwoWeekHigh"))
        ratios["52w_low"] = _safe(info.get("fiftyTwoWeekLow"))
        ratios["current_price"] = _safe(info.get("currentPrice") or info.get("regularMarketPrice"))
        ratios["50d_avg"] = _safe(info.get("fiftyDayAverage"))
        ratios["200d_avg"] = _safe(info.get("twoHundredDayAverage"))
        ratios["gross_margins"] = _safe(info.get("grossMargins"))
        ratios["operating_margins"] = _safe(info.get("operatingMargins"))
        ratios["profit_margins"] = _safe(info.get("profitMargins"))
        ratios["ebitda_margins"] = _safe(info.get("ebitdaMargins"))
        ratios["revenue_growth"] = _safe(info.get("revenueGrowth"))
        ratios["earnings_growth"] = _safe(info.get("earningsGrowth"))
        ratios["return_on_assets"] = _safe(info.get("returnOnAssets"))
        ratios["return_on_equity"] = _safe(info.get("returnOnEquity"))
        ratios["debt_to_equity"] = _safe(info.get("debtToEquity"))
        ratios["current_ratio"] = _safe(info.get("currentRatio"))
        ratios["quick_ratio"] = _safe(info.get("quickRatio"))
        ratios["total_cash"] = _safe(info.get("totalCash"))
        ratios["total_debt"] = _safe(info.get("totalDebt"))
        ratios["free_cashflow"] = _safe(info.get("freeCashflow"))
        ratios["operating_cashflow"] = _safe(info.get("operatingCashflow"))
        ratios["revenue_ttm"] = _safe(info.get("totalRevenue"))
        ratios["ebitda"] = _safe(info.get("ebitda"))
        ratios["eps_ttm"] = _safe(info.get("trailingEps"))
        ratios["eps_forward"] = _safe(info.get("forwardEps"))
        ratios["shares_outstanding"] = _safe(info.get("sharesOutstanding"))
        ratios["float_shares"] = _safe(info.get("floatShares"))
        ratios["short_ratio"] = _safe(info.get("shortRatio"))
        ratios["sector"] = _safe(info.get("sector"))
        ratios["industry"] = _safe(info.get("industry"))
        ratios["country"] = _safe(info.get("country"))
        ratios["employees"] = _safe(info.get("fullTimeEmployees"))
        ratios["recommendation"] = _safe(info.get("recommendationKey"))

        return ratios

    def _compute_capital_intensity(self) -> dict:
        result = {}
        capex_row = self._get_row(self._cashflow, "Capital Expenditure", "CapEx", "Purchase Of Property Plant And Equipment")
        revenue_row = self._get_row(self._financials, "Total Revenue")
        asset_row = self._get_row(self._balance_sheet, "Total Assets")

        if capex_row is not None and revenue_row is not None:
            try:
                latest_capex = abs(float(capex_row.iloc[0]))
                latest_rev = float(revenue_row.iloc[0])
                result["capex_to_revenue"] = latest_capex / latest_rev if latest_rev else None
            except Exception:
                result["capex_to_revenue"] = None

        if asset_row is not None and revenue_row is not None:
            try:
                result["asset_turnover"] = float(revenue_row.iloc[0]) / float(asset_row.iloc[0])
            except Exception:
                result["asset_turnover"] = None

        return result

    def _compute_debt_metrics(self) -> dict:
        result = {}
        total_debt = self._get_row(self._balance_sheet, "Total Debt", "Long Term Debt")
        equity_row = self._get_row(self._balance_sheet, "Stockholders Equity", "Total Stockholder Equity")
        ebitda_val = self._info.get("ebitda")
        interest_row = self._get_row(self._financials, "Interest Expense")
        ebit_row = self._get_row(self._financials, "EBIT", "Operating Income")

        if total_debt is not None and equity_row is not None:
            try:
                result["debt_to_equity_calc"] = float(total_debt.iloc[0]) / float(equity_row.iloc[0])
            except Exception:
                result["debt_to_equity_calc"] = None

        if total_debt is not None and ebitda_val:
            try:
                cash_row = self._get_row(self._balance_sheet, "Cash And Cash Equivalents", "Cash")
                cash = float(cash_row.iloc[0]) if cash_row is not None else 0
                net_debt = float(total_debt.iloc[0]) - cash
                result["net_debt_ebitda"] = net_debt / float(ebitda_val)
            except Exception:
                result["net_debt_ebitda"] = None

        if interest_row is not None and ebit_row is not None:
            try:
                interest = abs(float(interest_row.iloc[0]))
                ebit = float(ebit_row.iloc[0])
                result["interest_coverage"] = ebit / interest if interest else None
            except Exception:
                result["interest_coverage"] = None

        return result

    def _build_income_table(self) -> str:
        if self._financials is None or self._financials.empty:
            return "No income statement data available."
        rows_of_interest = [
            "Total Revenue", "Gross Profit", "Operating Income",
            "EBIT", "EBITDA", "Net Income", "Interest Expense",
        ]
        lines = ["Income Statement (Annual, last 4 years):"]
        cols = self._financials.columns[:4]
        header = "Metric".ljust(35) + " | " + " | ".join(str(c.date()) for c in cols)
        lines.append(header)
        lines.append("-" * len(header))
        for row_name in rows_of_interest:
            row = self._get_row(self._financials, row_name)
            if row is not None:
                vals = " | ".join(self._fmt(row[c] if c in row.index else None, "B") for c in cols)
                lines.append(f"{row_name.ljust(35)} | {vals}")
        return "\n".join(lines)

    def _build_balance_table(self) -> str:
        if self._balance_sheet is None or self._balance_sheet.empty:
            return "No balance sheet data available."
        rows_of_interest = [
            "Total Assets", "Total Liabilities Net Minority Interest",
            "Stockholders Equity", "Total Debt", "Cash And Cash Equivalents",
            "Current Assets", "Current Liabilities",
        ]
        lines = ["Balance Sheet (Annual, last 4 years):"]
        cols = self._balance_sheet.columns[:4]
        header = "Metric".ljust(45) + " | " + " | ".join(str(c.date()) for c in cols)
        lines.append(header)
        lines.append("-" * len(header))
        for row_name in rows_of_interest:
            row = self._get_row(self._balance_sheet, row_name)
            if row is not None:
                vals = " | ".join(self._fmt(row[c] if c in row.index else None, "B") for c in cols)
                lines.append(f"{row_name.ljust(45)} | {vals}")
        return "\n".join(lines)

    def _build_cashflow_table(self) -> str:
        if self._cashflow is None or self._cashflow.empty:
            return "No cash flow data available."
        rows_of_interest = [
            "Operating Cash Flow", "Free Cash Flow",
            "Capital Expenditure", "Investing Cash Flow",
            "Financing Cash Flow",
        ]
        lines = ["Cash Flow Statement (Annual, last 4 years):"]
        cols = self._cashflow.columns[:4]
        header = "Metric".ljust(35) + " | " + " | ".join(str(c.date()) for c in cols)
        lines.append(header)
        lines.append("-" * len(header))
        for row_name in rows_of_interest:
            row = self._get_row(self._cashflow, row_name)
            if row is not None:
                vals = " | ".join(self._fmt(row[c] if c in row.index else None, "B") for c in cols)
                lines.append(f"{row_name.ljust(35)} | {vals}")
        return "\n".join(lines)

    def build_financial_data_string(self) -> str:
        ratios = self._compute_ratios()
        cap_intensity = self._compute_capital_intensity()
        debt_metrics = self._compute_debt_metrics()

        sections = []

        sections.append("=== KEY METRICS & RATIOS ===")
        sections.append(f"Sector: {ratios['sector']} | Industry: {ratios['industry']} | Country: {ratios['country']}")
        sections.append(f"Employees: {ratios['employees']}")
        sections.append(f"Market Cap: {self._fmt(ratios['market_cap'], 'B')} | Enterprise Value: {self._fmt(ratios['enterprise_value'], 'B')}")
        sections.append(f"Current Price: ${ratios['current_price']} | 52W High: ${ratios['52w_high']} | 52W Low: ${ratios['52w_low']}")
        sections.append(f"50D Avg: ${ratios['50d_avg']} | 200D Avg: ${ratios['200d_avg']} | Beta: {ratios['beta']}")
        sections.append("")
        sections.append("=== VALUATION ===")
        sections.append(f"P/E (TTM): {ratios['pe_ratio']} | Forward P/E: {ratios['forward_pe']} | PEG: {ratios['peg_ratio']}")
        sections.append(f"P/B: {ratios['pb_ratio']} | P/S: {ratios['ps_ratio']}")
        sections.append(f"EV/EBITDA: {ratios['ev_ebitda']} | EV/Revenue: {ratios['ev_revenue']}")
        sections.append(f"EPS (TTM): {ratios['eps_ttm']} | EPS (Forward): {ratios['eps_forward']}")
        sections.append("")
        sections.append("=== PROFITABILITY ===")
        sections.append(f"Gross Margin: {self._fmt(ratios['gross_margins'], '%')} | Operating Margin: {self._fmt(ratios['operating_margins'], '%')}")
        sections.append(f"Net Margin: {self._fmt(ratios['profit_margins'], '%')} | EBITDA Margin: {self._fmt(ratios['ebitda_margins'], '%')}")
        sections.append(f"ROA: {self._fmt(ratios['return_on_assets'], '%')} | ROE: {self._fmt(ratios['return_on_equity'], '%')}")
        sections.append(f"Revenue (TTM): {self._fmt(ratios['revenue_ttm'], 'B')} | EBITDA: {self._fmt(ratios['ebitda'], 'B')}")
        sections.append(f"Revenue Growth (YoY): {self._fmt(ratios['revenue_growth'], '%')} | Earnings Growth: {self._fmt(ratios['earnings_growth'], '%')}")
        sections.append("")
        sections.append("=== LIQUIDITY & DEBT ===")
        sections.append(f"Current Ratio: {ratios['current_ratio']} | Quick Ratio: {ratios['quick_ratio']}")
        sections.append(f"Total Cash: {self._fmt(ratios['total_cash'], 'B')} | Total Debt: {self._fmt(ratios['total_debt'], 'B')}")
        sections.append(f"Debt/Equity (reported): {ratios['debt_to_equity']}")
        sections.append(f"Debt/Equity (calculated): {round(debt_metrics.get('debt_to_equity_calc') or 0, 2)}")
        sections.append(f"Net Debt/EBITDA: {round(debt_metrics.get('net_debt_ebitda') or 0, 2)}x")
        sections.append(f"Interest Coverage: {round(debt_metrics.get('interest_coverage') or 0, 2)}x")
        sections.append(f"Free Cash Flow: {self._fmt(ratios['free_cashflow'], 'B')} | Operating CF: {self._fmt(ratios['operating_cashflow'], 'B')}")
        sections.append("")
        sections.append("=== CAPITAL INTENSITY ===")
        sections.append(f"CapEx/Revenue: {self._fmt(cap_intensity.get('capex_to_revenue'), '%')}")
        sections.append(f"Asset Turnover: {round(cap_intensity.get('asset_turnover') or 0, 2)}x")
        sections.append("")
        sections.append("=== SHAREHOLDER INFO ===")
        sections.append(f"Dividend Yield: {self._fmt(ratios['dividend_yield'], '%')} | Payout Ratio: {self._fmt(ratios['payout_ratio'], '%')}")
        sections.append(f"Shares Outstanding: {self._fmt(ratios['shares_outstanding'], 'B')}")
        sections.append(f"Short Ratio: {ratios['short_ratio']}")
        sections.append(f"Analyst Recommendation: {ratios['recommendation']}")
        sections.append("")
        sections.append(self._build_income_table())
        sections.append("")
        sections.append(self._build_balance_table())
        sections.append("")
        sections.append(self._build_cashflow_table())

        return "\n".join(sections)

    def get_summary_for_canvas(self) -> str:
        r = self._compute_ratios()
        lines = [
            f"Revenue (TTM): {self._fmt(r['revenue_ttm'], 'B')}",
            f"Net Margin: {self._fmt(r['profit_margins'], '%')}",
            f"Market Cap: {self._fmt(r['market_cap'], 'B')}",
            f"ROE: {self._fmt(r['return_on_equity'], '%')}",
            f"Debt/Equity: {r['debt_to_equity']}",
            f"Revenue Growth: {self._fmt(r['revenue_growth'], '%')}",
            f"Employees: {r['employees']}",
            f"Sector: {r['sector']} | Industry: {r['industry']}",
        ]
        return "\n".join(lines)

    def get_market_data_string(self) -> str:
        r = self._compute_ratios()
        lines = [
            f"Ticker: {self.ticker}",
            f"Sector: {r['sector']} | Industry: {r['industry']}",
            f"Current Price: ${r['current_price']}",
            f"52W High: ${r['52w_high']} | 52W Low: ${r['52w_low']}",
            f"50D MA: ${r['50d_avg']} | 200D MA: ${r['200d_avg']}",
            f"Market Cap: {self._fmt(r['market_cap'], 'B')}",
            f"Beta: {r['beta']}",
            f"P/E (TTM): {r['pe_ratio']} | Forward P/E: {r['forward_pe']}",
            f"PEG: {r['peg_ratio']} | P/B: {r['pb_ratio']} | P/S: {r['ps_ratio']}",
            f"EV/EBITDA: {r['ev_ebitda']} | EV/Revenue: {r['ev_revenue']}",
            f"EPS TTM: {r['eps_ttm']} | EPS Forward: {r['eps_forward']}",
            f"Gross Margin: {self._fmt(r['gross_margins'], '%')}",
            f"Operating Margin: {self._fmt(r['operating_margins'], '%')}",
            f"Net Margin: {self._fmt(r['profit_margins'], '%')}",
            f"ROA: {self._fmt(r['return_on_assets'], '%')} | ROE: {self._fmt(r['return_on_equity'], '%')}",
            f"Revenue Growth (YoY): {self._fmt(r['revenue_growth'], '%')}",
            f"Earnings Growth: {self._fmt(r['earnings_growth'], '%')}",
            f"Dividend Yield: {self._fmt(r['dividend_yield'], '%')} | Payout Ratio: {self._fmt(r['payout_ratio'], '%')}",
            f"Total Debt: {self._fmt(r['total_debt'], 'B')} | Total Cash: {self._fmt(r['total_cash'], 'B')}",
            f"Free Cash Flow: {self._fmt(r['free_cashflow'], 'B')}",
            f"Debt/Equity: {r['debt_to_equity']}",
            f"Current Ratio: {r['current_ratio']} | Quick Ratio: {r['quick_ratio']}",
            f"Short Ratio: {r['short_ratio']}",
            f"Analyst Recommendation: {r['recommendation']}",
            f"Shares Outstanding: {self._fmt(r['shares_outstanding'], 'B')}",
        ]
        return "\n".join(lines)
