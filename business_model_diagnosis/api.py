#!/usr/bin/env python3
import os
import re
import sys
import logging
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

_API_DIR = os.path.dirname(os.path.abspath(__file__))
if _API_DIR not in sys.path:
    sys.path.insert(0, _API_DIR)

load_dotenv(os.path.join(_API_DIR, ".env"))
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


def _cache_store():
    from modules.cache_store import CompanyCacheStore
    return CompanyCacheStore(db_path=os.path.join(_API_DIR, "cache", "company_cache.db"))


def _extract_canvas_blocks(canvas_text: str) -> dict:
    labels = [
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
    result = {label: "" for label in labels}
    normalized = canvas_text or ""
    heading_pattern = re.compile(
        r"(?im)^\s*(?:#{1,6}\s*)?(?:\*\*)?\s*(\d+)\.\s*(Customer Segments|Value Propositions|Channels|Customer Relationships|Revenue Streams|Key Resources|Key Activities|Key Partnerships|Cost Structure)\s*(?:\*\*)?\s*:?\s*$"
    )
    matches = list(heading_pattern.finditer(normalized))
    if matches:
        for idx, match in enumerate(matches):
            label = match.group(2)
            start = match.end()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(normalized)
            section = normalized[start:end].strip()
            if section:
                result[label] = section
    if all(not value for value in result.values()) and canvas_text:
        split_lines = [line.strip() for line in canvas_text.splitlines() if line.strip()]
        for i, label in enumerate(labels):
            result[label] = split_lines[i] if i < len(split_lines) else ""
    return result


def _is_canvas_usable(canvas: dict) -> bool:
    required = {
        "Customer Segments",
        "Value Propositions",
        "Channels",
        "Customer Relationships",
        "Revenue Streams",
        "Key Resources",
        "Key Activities",
        "Key Partnerships",
        "Cost Structure",
    }
    if not isinstance(canvas, dict) or set(canvas.keys()) != required:
        return False
    rich_blocks = sum(1 for value in canvas.values() if isinstance(value, str) and len(value.strip()) >= 80)
    return rich_blocks >= 7


def _build_dashboard_payload(company_name: str, ticker: str | None, summary: dict, canvas_text: str, financial_text: str, market_text: str) -> dict:
    canvas_map = _extract_canvas_blocks(canvas_text)
    return {
        "name": company_name,
        "ticker": ticker,
        "summary": {
            "industry": summary.get("industry", "N/A"),
            "headquarters": summary.get("headquarters", "N/A"),
            "market_cap": summary.get("market_cap", "N/A"),
            "employees": summary.get("employees", "N/A"),
            "sector": summary.get("sector", "N/A"),
        },
        "canvas": canvas_map,
        "financial_text": financial_text or "",
        "market_text": market_text or "",
    }


def _response_payload(company_name: str, ticker: str | None, cached: bool, canvas_text: str, financial_text: str, market_text: str, updated_at: int | None, dashboard: dict, kpis: list) -> dict:
    return {
        "company_name": company_name,
        "ticker": ticker,
        "cached": cached,
        "canvas_text": canvas_text,
        "financial_text": financial_text,
        "market_text": market_text,
        "updated_at": updated_at,
        "dashboard": dashboard,
        "kpis": kpis,
    }


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/cached", methods=["GET"])
def cached():
    company_name = (request.args.get("company") or "").strip()
    if not company_name:
        return jsonify({"error": "company query param is required"}), 400
    hit = _cache_store().get_recent(company_name=company_name, max_age_days=30)
    if not hit:
        return jsonify({"found": False})
    return jsonify({"found": True, "company_name": hit.get("company_name"), "ticker": hit.get("ticker"), "updated_at": hit.get("updated_at_epoch"), "dashboard": hit.get("dashboard", {}), "kpis": hit.get("kpis", [])})


@app.route("/api/diagnose", methods=["POST"])
def diagnose():
    body = request.get_json(force=True) or {}
    company_name = (body.get("company_name") or "").strip()
    ticker = ((body.get("ticker") or "").strip().upper()) or None
    skip_market = bool(body.get("skip_market", False))
    if not company_name:
        return jsonify({"error": "company_name is required"}), 400
    try:
        cache = _cache_store()
        hit = cache.get_recent(company_name=company_name, max_age_days=30)
        if hit:
            cached_dashboard = hit.get("dashboard") or {}
            cached_canvas = cached_dashboard.get("canvas") if isinstance(cached_dashboard, dict) else None
            cached_kpis = hit.get("kpis") or []
            ticker_requires_financial = bool(ticker)
            cache_has_financial = bool(cached_kpis) and bool(hit.get("financial_text"))
            cache_has_dashboard = _is_canvas_usable(cached_canvas)
            cache_usable = cache_has_dashboard and (not ticker_requires_financial or cache_has_financial)
            if cache_usable:
                return jsonify(_response_payload(
                    company_name=hit.get("company_name", company_name),
                    ticker=hit.get("ticker"),
                    cached=True,
                    canvas_text=hit.get("canvas_text", ""),
                    financial_text=hit.get("financial_text", ""),
                    market_text=hit.get("market_text", ""),
                    updated_at=hit.get("updated_at_epoch"),
                    dashboard=cached_dashboard,
                    kpis=cached_kpis,
                ))

        gemini_key = os.getenv("GEMINI_API_KEY", "")
        if not gemini_key:
            return jsonify({"error": "GEMINI_API_KEY is not configured on the server."}), 503

        from modules.scraper import CompanyScraper
        from modules.financial_analyzer import FinancialAnalyzer
        from modules.ai_analyzer import GeminiAnalyzer

        scraper = CompanyScraper()
        ai = GeminiAnalyzer(api_key=gemini_key)
        financial_data_str, market_data_str, financial_ai_text, market_ai_text = "", "", "", ""
        dashboard_summary = {
            "industry": "N/A",
            "headquarters": "N/A",
            "market_cap": "N/A",
            "employees": "N/A",
            "sector": "N/A",
        }
        kpi_rows = []
        canvas_financial_summary = "No ticker provided — financial data not available."
        if ticker:
            try:
                fin = FinancialAnalyzer(ticker)
                fin.load_data()
                financial_data_str = fin.build_financial_data_string()
                market_data_str = fin.get_market_data_string()
                canvas_financial_summary = fin.get_summary_for_canvas()
                dashboard_summary = fin.get_dashboard_summary()
                kpi_rows = fin.get_kpi_table()
            except Exception as exc:
                logger.warning(f"Financial data error for {ticker}: {exc}")

        context = scraper.gather_company_context(company_name, ticker)
        canvas_ai_text = ai.analyze_business_model_canvas(company_name=company_name, context=context, financial_summary=canvas_financial_summary, market_summary=market_data_str)
        if ticker and financial_data_str:
            financial_ai_text = ai.analyze_financials(company_name=company_name, financial_data=financial_data_str)
        if ticker and market_data_str and not skip_market:
            market_ai_text = ai.analyze_market(company_name=company_name, ticker=ticker, market_data=market_data_str)

        dashboard = _build_dashboard_payload(
            company_name=company_name,
            ticker=ticker,
            summary=dashboard_summary,
            canvas_text=canvas_ai_text,
            financial_text=financial_ai_text,
            market_text=market_ai_text,
        )
        cache.upsert(
            company_name=company_name,
            ticker=ticker,
            context=context,
            canvas_text=canvas_ai_text,
            financial_text=financial_ai_text,
            market_text=market_ai_text,
            dashboard=dashboard,
            kpis=kpi_rows,
        )
        return jsonify(_response_payload(
            company_name=company_name,
            ticker=ticker,
            cached=False,
            canvas_text=canvas_ai_text,
            financial_text=financial_ai_text,
            market_text=market_ai_text,
            updated_at=None,
            dashboard=dashboard,
            kpis=kpi_rows,
        ))
    except Exception as exc:
        logger.exception("Unhandled error in /api/diagnose")
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("API_PORT", "5000")), debug=True, use_reloader=False)
