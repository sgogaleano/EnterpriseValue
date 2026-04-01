import os
import re
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.rule import Rule
from rich.table import Table
from rich import box

console = Console(width=120)


def _strip_markdown(text: str) -> str:
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'#{1,6}\s?', '', text)
    text = re.sub(r'`{1,3}', '', text)
    return text


def _extract_score(text: str, label: str = "SCORE") -> str:
    pattern = rf'{label}[^\d]*([\d]{{1,3}})'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1)
    return "N/A"


def _score_color(score_str: str) -> str:
    try:
        s = int(score_str)
        if s >= 75:
            return "bold green"
        elif s >= 50:
            return "bold yellow"
        else:
            return "bold red"
    except Exception:
        return "white"


def _extract_recommendation(text: str) -> tuple[str, str]:
    match = re.search(r'\b(BUY|HOLD|AVOID|SELL)\b', text, re.IGNORECASE)
    if match:
        rec = match.group(1).upper()
        colors = {"BUY": "bold green", "HOLD": "bold yellow", "AVOID": "bold red", "SELL": "bold red"}
        return rec, colors.get(rec, "white")
    return "N/A", "white"


class ReportGenerator:
    def __init__(self, company_name: str, ticker: str | None, output_dir: str = "reports"):
        self.company_name = company_name
        self.ticker = ticker
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._lines: list[str] = []

    def _w(self, line: str = ""):
        self._lines.append(line)

    def _section_header(self, title: str):
        console.print()
        console.print(Rule(f"[bold cyan]{title}[/bold cyan]", style="cyan"))

    def print_header(self):
        console.print()
        title_text = Text(justify="center")
        title_text.append("BUSINESS MODEL DIAGNOSIS\n", style="bold white on blue")
        title_text.append(f"  {self.company_name.upper()}  ", style="bold yellow")
        if self.ticker:
            title_text.append(f"  [{self.ticker}]  ", style="bold cyan")
        title_text.append(f"\n  Generated: {datetime.now().strftime('%B %d, %Y %H:%M UTC')}  ", style="dim white")
        console.print(Panel(title_text, border_style="blue", padding=(1, 4)))

    def print_canvas_analysis(self, canvas_text: str):
        self._section_header("OSTERWALDER BUSINESS MODEL CANVAS ANALYSIS")
        score = _extract_score(canvas_text, "HEALTH SCORE")
        score_color = _score_color(score)

        info_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        info_table.add_column(style="bold cyan", width=30)
        info_table.add_column(style="white", width=60)
        info_table.add_row("Company", self.company_name)
        if self.ticker:
            info_table.add_row("Ticker", self.ticker)
        info_table.add_row("Business Model Health", Text(f"{score}/100", style=score_color))
        console.print(info_table)

        canvas_blocks = [
            "Customer Segments", "Value Propositions", "Channels",
            "Customer Relationships", "Revenue Streams", "Key Resources",
            "Key Activities", "Key Partnerships", "Cost Structure",
        ]

        for block in canvas_blocks:
            pattern = rf'(?:^|\n)#{0,3}\s*\*{{0,2}}{re.escape(block)}\*{{0,2}}(.*?)(?=\n#{0,3}\s*\*{{0,2}}(?:{"| ".join(canvas_blocks[i] for i in range(len(canvas_blocks)))}|OVERALL|TOP 3|BUSINESS MODEL ARCHETYPE)\*{{0,2}}|\Z)'
            match = re.search(pattern, canvas_text, re.DOTALL | re.IGNORECASE)
            if match:
                content = _strip_markdown(match.group(1).strip())
                console.print(Panel(
                    content[:1200],
                    title=f"[bold yellow]{block}[/bold yellow]",
                    border_style="yellow",
                    padding=(0, 2),
                ))

        archetype_match = re.search(r'BUSINESS MODEL ARCHETYPE(.*?)(?=\n#|\Z)', canvas_text, re.DOTALL | re.IGNORECASE)
        overall_match = re.search(r'(?:OVERALL BUSINESS MODEL|HEALTH SCORE)(.*?)(?=TOP 3 STRATEGIC|\Z)', canvas_text, re.DOTALL | re.IGNORECASE)
        opp_match = re.search(r'TOP 3 STRATEGIC OPPORTUNITIES(.*?)(?=TOP 3 CRITICAL|\Z)', canvas_text, re.DOTALL | re.IGNORECASE)
        risk_match = re.search(r'TOP 3 CRITICAL RISKS(.*?)(?=BUSINESS MODEL ARCHETYPE|OVERALL|\Z)', canvas_text, re.DOTALL | re.IGNORECASE)

        summary_table = Table(title="Canvas Summary", box=box.ROUNDED, border_style="blue", padding=(0, 1))
        summary_table.add_column("Section", style="bold cyan", width=28)
        summary_table.add_column("Details", style="white", width=80)

        if archetype_match:
            summary_table.add_row("Business Model Archetype", _strip_markdown(archetype_match.group(1).strip()[:300]))
        if opp_match:
            summary_table.add_row("Top 3 Opportunities", _strip_markdown(opp_match.group(1).strip()[:400]))
        if risk_match:
            summary_table.add_row("Top 3 Critical Risks", _strip_markdown(risk_match.group(1).strip()[:400]))
        summary_table.add_row("Health Score", Text(f"{score}/100", style=score_color))

        console.print(summary_table)

    def print_financial_analysis(self, financial_text: str):
        self._section_header("FINANCIAL DIAGNOSIS")
        score = _extract_score(financial_text, "FINANCIAL HEALTH SCORE")
        score_color = _score_color(score)

        sections = [
            ("CAPITAL INTENSITY", "Capital Intensity Analysis"),
            ("DEBT STRUCTURE", "Debt Structure Analysis"),
            ("PROFITABILITY", "Profitability Metrics"),
            ("LIQUIDITY", "Liquidity & Efficiency"),
            ("GROWTH", "Growth Metrics"),
            ("KEY FINANCIAL RISKS", "Key Financial Risks"),
        ]

        for keyword, display_name in sections:
            pattern = rf'{re.escape(keyword)}(.*?)(?=\n\d+\.\s+[A-Z]{{3,}}|\n===|\Z)'
            match = re.search(pattern, financial_text, re.DOTALL | re.IGNORECASE)
            if match:
                content = _strip_markdown(match.group(1).strip())
                border = "red" if "RISK" in keyword else "green"
                console.print(Panel(
                    content[:1000],
                    title=f"[bold white]{display_name}[/bold white]",
                    border_style=border,
                    padding=(0, 2),
                ))

        console.print(Panel(
            Text(f"Financial Health Score: {score}/100", style=score_color, justify="center"),
            border_style=score_color.replace("bold ", ""),
            padding=(0, 4),
        ))

    def print_market_analysis(self, market_text: str):
        self._section_header("MARKET & EQUITY ANALYSIS")
        score = _extract_score(market_text, "MARKET ATTRACTIVENESS SCORE")
        score_color = _score_color(score)
        rec, rec_color = _extract_recommendation(market_text)

        rec_panel = Table.grid(padding=(0, 4))
        rec_panel.add_column(style="bold white", width=30)
        rec_panel.add_column(width=60)
        rec_panel.add_row("Stock Recommendation:", Text(rec, style=rec_color))
        rec_panel.add_row("Market Attractiveness:", Text(f"{score}/100", style=score_color))
        console.print(Panel(rec_panel, title="[bold]Investment Summary[/bold]", border_style="magenta", padding=(0, 2)))

        market_sections = [
            ("VALUATION ANALYSIS", "Valuation Analysis"),
            ("MARKET POSITIONING", "Market Positioning"),
            ("DIVIDEND", "Dividend & Shareholder Returns"),
            ("STOCK PURCHASE OPPORTUNITY", "Stock Purchase Opportunity"),
            ("ANALYST SENTIMENT", "Analyst Sentiment"),
        ]

        for keyword, display_name in market_sections:
            pattern = rf'{re.escape(keyword)}(.*?)(?=\n\d+\.\s+[A-Z]{{3,}}|\n===|\Z)'
            match = re.search(pattern, market_text, re.DOTALL | re.IGNORECASE)
            if match:
                content = _strip_markdown(match.group(1).strip())
                console.print(Panel(
                    content[:1000],
                    title=f"[bold magenta]{display_name}[/bold magenta]",
                    border_style="magenta",
                    padding=(0, 2),
                ))

    def save_report(self, canvas_text: str, financial_text: str, market_text: str):
        safe_name = re.sub(r'[^\w\s-]', '', self.company_name).strip().replace(' ', '_')
        filename = self.output_dir / f"{safe_name}_{self.timestamp}.txt"

        with open(filename, "w", encoding="utf-8") as f:
            f.write("=" * 100 + "\n")
            f.write(f"BUSINESS MODEL DIAGNOSIS REPORT\n")
            f.write(f"Company: {self.company_name}")
            if self.ticker:
                f.write(f"  |  Ticker: {self.ticker}")
            f.write(f"\nGenerated: {datetime.now().strftime('%B %d, %Y %H:%M UTC')}\n")
            f.write("=" * 100 + "\n\n")

            f.write("SECTION 1: OSTERWALDER BUSINESS MODEL CANVAS ANALYSIS\n")
            f.write("-" * 80 + "\n")
            f.write(canvas_text + "\n\n")

            f.write("SECTION 2: FINANCIAL DIAGNOSIS\n")
            f.write("-" * 80 + "\n")
            f.write(financial_text + "\n\n")

            if market_text:
                f.write("SECTION 3: MARKET & EQUITY ANALYSIS\n")
                f.write("-" * 80 + "\n")
                f.write(market_text + "\n\n")

            f.write("=" * 100 + "\n")
            f.write("END OF REPORT\n")

        return str(filename)
