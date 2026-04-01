#!/usr/bin/env python3
import os
import sys
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.spinner import Spinner
from rich.live import Live
from rich.text import Text
from rich.panel import Panel

load_dotenv()

console = Console(width=120)
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


def _spinner_status(message: str):
    return Live(
        Panel(Text(f"  {message}", style="bold cyan"), border_style="cyan", padding=(0, 2)),
        refresh_per_second=10,
        transient=True,
    )


def resolve_ticker_interactively(company_name: str) -> tuple[str | None, bool]:
    console.print()
    console.print(Panel(
        f"[bold]Ticker Symbol[/bold]\n\nIs [cyan]{company_name}[/cyan] a publicly traded company?",
        border_style="yellow",
        padding=(0, 2),
    ))
    is_public = Confirm.ask("  Publicly traded?", default=True)
    if not is_public:
        return None, False
    ticker = Prompt.ask("  Enter ticker symbol (e.g. AAPL, MSFT, TSLA)").strip().upper()
    return ticker if ticker else None, True


def run_diagnosis(company_name: str, ticker: str | None, output_dir: str, skip_market: bool = False):
    from modules.scraper import CompanyScraper
    from modules.financial_analyzer import FinancialAnalyzer
    from modules.ai_analyzer import GeminiAnalyzer
    from modules.report_generator import ReportGenerator

    gemini_key = os.getenv("GEMINI_API_KEY", "")
    if not gemini_key or gemini_key == "your_gemini_api_key_here":
        console.print(Panel(
            "[bold red]ERROR:[/bold red] GEMINI_API_KEY is not set.\n"
            "Please set it in your [yellow].env[/yellow] file or as an environment variable.\n\n"
            "Get your free API key at: [link]https://aistudio.google.com/app/apikey[/link]",
            border_style="red",
            padding=(1, 2),
        ))
        sys.exit(1)

    report = ReportGenerator(company_name, ticker, output_dir=output_dir)
    report.print_header()

    scraper = CompanyScraper()
    ai = GeminiAnalyzer(api_key=gemini_key)

    financial_data_str = ""
    market_data_str = ""
    financial_ai_text = ""
    market_ai_text = ""
    fin_analyzer = None

    if ticker:
        console.print()
        console.print("[bold cyan]Step 1/4[/bold cyan] — Loading financial data from Yahoo Finance...")
        fin_analyzer = FinancialAnalyzer(ticker)
        fin_analyzer.load_data()
        financial_data_str = fin_analyzer.build_financial_data_string()
        market_data_str = fin_analyzer.get_market_data_string()
        canvas_financial_summary = fin_analyzer.get_summary_for_canvas()
        console.print("[green]  Financial data loaded.[/green]")
    else:
        canvas_financial_summary = "No ticker provided — financial data not available."

    console.print()
    console.print("[bold cyan]Step 2/4[/bold cyan] — Scraping company information from the web...")
    context = scraper.gather_company_context(company_name, ticker)
    console.print("[green]  Web scraping complete.[/green]")

    console.print()
    console.print("[bold cyan]Step 3/4[/bold cyan] — Running AI analysis (Gemini)...")

    console.print("  [ai] Analyzing Business Model Canvas...")
    canvas_ai_text = ai.analyze_business_model_canvas(
        company_name=company_name,
        context=context,
        financial_summary=canvas_financial_summary,
        market_summary=market_data_str,
    )

    if ticker and financial_data_str:
        console.print("  [ai] Analyzing financial statements...")
        financial_ai_text = ai.analyze_financials(
            company_name=company_name,
            financial_data=financial_data_str,
        )

    if ticker and market_data_str and not skip_market:
        console.print("  [ai] Analyzing market & equity...")
        market_ai_text = ai.analyze_market(
            company_name=company_name,
            ticker=ticker,
            market_data=market_data_str,
        )

    console.print("[green]  AI analysis complete.[/green]")

    console.print()
    console.print("[bold cyan]Step 4/4[/bold cyan] — Generating report...")

    report.print_canvas_analysis(canvas_ai_text)

    if financial_ai_text:
        report.print_financial_analysis(financial_ai_text)

    if market_ai_text:
        report.print_market_analysis(market_ai_text)

    saved_path = report.save_report(canvas_ai_text, financial_ai_text, market_ai_text)

    console.print()
    console.print(Panel(
        f"[bold green]Diagnosis complete![/bold green]\n\n"
        f"Report saved to: [cyan]{saved_path}[/cyan]",
        border_style="green",
        padding=(1, 2),
    ))


def interactive_mode(output_dir: str):
    console.print()
    console.print(Panel(
        "[bold white]BUSINESS MODEL DIAGNOSIS TOOL[/bold white]\n"
        "[dim]Powered by Osterwalder Canvas + Gemini AI + Yahoo Finance[/dim]",
        border_style="blue",
        padding=(1, 4),
    ))

    while True:
        console.print()
        company_name = Prompt.ask("[bold yellow]Enter company name[/bold yellow] (or 'quit' to exit)").strip()
        if company_name.lower() in ("quit", "exit", "q"):
            console.print("\n[dim]Goodbye.[/dim]\n")
            break
        if not company_name:
            continue

        ticker, is_public = resolve_ticker_interactively(company_name)
        skip_market = not is_public

        try:
            run_diagnosis(
                company_name=company_name,
                ticker=ticker,
                output_dir=output_dir,
                skip_market=skip_market,
            )
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted.[/yellow]")
        except Exception as e:
            console.print(f"\n[bold red]Error during diagnosis:[/bold red] {e}")
            logging.exception("Diagnosis failed")

        console.print()
        again = Confirm.ask("Run another diagnosis?", default=True)
        if not again:
            console.print("\n[dim]Goodbye.[/dim]\n")
            break


def main():
    parser = argparse.ArgumentParser(
        description="Business Model Diagnosis — Osterwalder Canvas + Financial + Market Analysis",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "company", nargs="?", default=None,
        help="Company name to analyze (e.g. 'Apple Inc'). If omitted, interactive mode starts.",
    )
    parser.add_argument(
        "--ticker", "-t", default=None,
        help="Stock ticker symbol (e.g. AAPL). Required for financial & market analysis.",
    )
    parser.add_argument(
        "--output-dir", "-o", default="reports",
        help="Directory to save the report (default: reports/)",
    )
    parser.add_argument(
        "--no-market", action="store_true",
        help="Skip market/equity analysis even if ticker is provided.",
    )
    args = parser.parse_args()

    if args.company:
        ticker = args.ticker.upper() if args.ticker else None
        if not ticker and args.company:
            _, is_public = resolve_ticker_interactively(args.company)
            if is_public:
                ticker = Prompt.ask("  Enter ticker symbol").strip().upper() or None
        run_diagnosis(
            company_name=args.company,
            ticker=ticker,
            output_dir=args.output_dir,
            skip_market=args.no_market,
        )
    else:
        interactive_mode(output_dir=args.output_dir)


if __name__ == "__main__":
    main()
