from google import genai
from google.genai import types
import logging

logger = logging.getLogger(__name__)

CANVAS_BLOCKS = [
    "Customer Segments",
    "Value Propositions",
    "Channels",
    "Customer Relationships",
    "Revenue Streams",
    "Key Resources",
    "Key Activities",
    "Key Partnerships",
    "Cost Structure",
]

CANVAS_PROMPT_TEMPLATE = """
You are a world-class business strategist and analyst specializing in the Osterwalder Business Model Canvas.

Using all the information provided below about the company "{company_name}", perform an exhaustive Business Model Canvas diagnosis.

--- COMPANY CONTEXT ---
{context}

--- FINANCIAL SUMMARY ---
{financial_summary}

--- MARKET DATA ---
{market_summary}

For each of the 9 building blocks of the Business Model Canvas, provide:
1. A detailed analysis (3-5 paragraphs) of the current state
2. Key strengths identified
3. Key weaknesses or risks
4. Strategic recommendations

The 9 building blocks are:
1. Customer Segments - Who are the customers? What are the market segments?
2. Value Propositions - What value is delivered? Which problems are solved?
3. Channels - How does the company reach its customer segments?
4. Customer Relationships - What type of relationship does the company establish?
5. Revenue Streams - How does the company generate revenue from each customer segment?
6. Key Resources - What assets are required to make the business model work?
7. Key Activities - What key activities does the value proposition require?
8. Key Partnerships - Who are the key partners and suppliers?
9. Cost Structure - What are the most important costs in the business model?

After the canvas analysis, provide:
- OVERALL BUSINESS MODEL HEALTH SCORE (0-100) with justification
- CEO AND MAJOR SHAREHOLDERS
- SECTOR
- COMPETITIVE ADVANTAGES
- MAIN COMPETITORS
- BUSINESS MODEL ARCHETYPE (e.g., Platform, Long-tail, Freemium, Razor & Blade, etc.)

Be specific, data-driven, and reference actual company details wherever possible.
"""

FINANCIAL_PROMPT_TEMPLATE = """
You are a senior financial analyst with expertise in fundamental analysis and corporate finance.

Analyze the following financial data for "{company_name}" and provide a comprehensive financial diagnosis:

--- FINANCIAL DATA ---
{financial_data}

Please analyze and report on:

1. CAPITAL INTENSITY ANALYSIS
   - Asset turnover ratios
   - Capital expenditure patterns
   - Fixed vs variable cost structure
   - Return on Assets (ROA) and Return on Invested Capital (ROIC)

2. DEBT STRUCTURE ANALYSIS
   - Debt-to-Equity ratio interpretation
   - Interest coverage ratio
   - Debt maturity profile (if available)
   - Credit risk assessment
   - Net Debt / EBITDA

3. PROFITABILITY METRICS
   - Gross margin trend
   - Operating margin trend
   - Net margin trend
   - EBITDA margin

4. LIQUIDITY & EFFICIENCY
   - Current ratio
   - Quick ratio
   - Cash conversion cycle (if data available)
   - Working capital adequacy

5. GROWTH METRICS
   - Revenue growth (YoY)
   - Earnings growth
   - Free Cash Flow growth

6. KEY FINANCIAL RISKS
   - Identify the top financial risks based on the data

7. FINANCIAL HEALTH SCORE (0-100) with justification

Be precise, cite specific numbers from the data provided, and flag any concerning trends.
"""

MARKET_PROMPT_TEMPLATE = """
You are an expert equity research analyst and portfolio manager.

Analyze the following market and valuation data for "{company_name}" (Ticker: {ticker}):

--- MARKET & VALUATION DATA ---
{market_data}

Provide a comprehensive market analysis covering:

1. VALUATION ANALYSIS
   - P/E Ratio assessment (vs industry average, historical average)
   - P/B Ratio interpretation
   - EV/EBITDA multiple analysis
   - Price/Sales ratio
   - PEG Ratio (if available)

2. MARKET POSITIONING
   - Market capitalization category (Micro/Small/Mid/Large/Mega cap)
   - Sector and industry positioning
   - 52-week price performance context

3. DIVIDEND & SHAREHOLDER RETURNS
   - Dividend yield assessment
   - Payout ratio sustainability
   - Buyback activity (if data available)

4. STOCK PURCHASE OPPORTUNITY ASSESSMENT
   Based on all valuation metrics, provide a clear BUY / HOLD / AVOID recommendation with:
   - Confidence level (Low / Medium / High)
   - Target price range (if calculable)
   - Key catalysts that could drive the stock higher
   - Key risks that could drive it lower
   - Suggested investment time horizon

5. ANALYST SENTIMENT SUMMARY (based on available data)

6. OVERALL MARKET ATTRACTIVENESS SCORE (0-100)

Be objective, cite specific numbers, and clearly explain the reasoning behind the purchase recommendation.
"""


class GeminiAnalyzer:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def _generate(self, prompt: str) -> str:
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.4,
                    max_output_tokens=8192,
                ),
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return f"[AI analysis unavailable: {e}]"

    def analyze_business_model_canvas(
        self,
        company_name: str,
        context: dict,
        financial_summary: str = "",
        market_summary: str = "",
    ) -> str:
        context_text = "\n\n".join([
            f"[Wikipedia Overview]\n{context.get('wikipedia', 'N/A')}",
            f"[Recent News]\n{context.get('recent_news', 'N/A')}",
            f"[SEC Filings]\n{context.get('sec_filings', 'N/A')}",
        ])
        prompt = CANVAS_PROMPT_TEMPLATE.format(
            company_name=company_name,
            context=context_text,
            financial_summary=financial_summary or "No financial data available.",
            market_summary=market_summary or "No market data available.",
        )
        return self._generate(prompt)

    def analyze_financials(self, company_name: str, financial_data: str) -> str:
        prompt = FINANCIAL_PROMPT_TEMPLATE.format(
            company_name=company_name,
            financial_data=financial_data,
        )
        return self._generate(prompt)

    def analyze_market(self, company_name: str, ticker: str, market_data: str) -> str:
        prompt = MARKET_PROMPT_TEMPLATE.format(
            company_name=company_name,
            ticker=ticker,
            market_data=market_data,
        )
        return self._generate(prompt)
