#!/usr/bin/env python3
import os
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
    return jsonify({"found": True, "company_name": hit.get("company_name"), "ticker": hit.get("ticker"), "updated_at": hit.get("updated_at_epoch")})


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
            return jsonify({"company_name": hit.get("company_name", company_name), "ticker": hit.get("ticker"), "cached": True, "canvas_text": hit.get("canvas_text", ""), "financial_text": hit.get("financial_text", ""), "market_text": hit.get("market_text", ""), "updated_at": hit.get("updated_at_epoch")})

        gemini_key = os.getenv("GEMINI_API_KEY", "")
        if not gemini_key:
            return jsonify({"error": "GEMINI_API_KEY is not configured on the server."}), 503

        from modules.scraper import CompanyScraper
        from modules.financial_analyzer import FinancialAnalyzer
        from modules.ai_analyzer import GeminiAnalyzer

        scraper = CompanyScraper()
        ai = GeminiAnalyzer(api_key=gemini_key)
        financial_data_str, market_data_str, financial_ai_text, market_ai_text = "", "", "", ""
        canvas_financial_summary = "No ticker provided — financial data not available."
        if ticker:
            try:
                fin = FinancialAnalyzer(ticker)
                fin.load_data()
                financial_data_str = fin.build_financial_data_string()
                market_data_str = fin.get_market_data_string()
                canvas_financial_summary = fin.get_summary_for_canvas()
            except Exception as exc:
                logger.warning(f"Financial data error for {ticker}: {exc}")

        context = scraper.gather_company_context(company_name, ticker)
        canvas_ai_text = ai.analyze_business_model_canvas(company_name=company_name, context=context, financial_summary=canvas_financial_summary, market_summary=market_data_str)
        if ticker and financial_data_str:
            financial_ai_text = ai.analyze_financials(company_name=company_name, financial_data=financial_data_str)
        if ticker and market_data_str and not skip_market:
            market_ai_text = ai.analyze_market(company_name=company_name, ticker=ticker, market_data=market_data_str)

        cache.upsert(company_name=company_name, ticker=ticker, context=context, canvas_text=canvas_ai_text, financial_text=financial_ai_text, market_text=market_ai_text)
        return jsonify({"company_name": company_name, "ticker": ticker, "cached": False, "canvas_text": canvas_ai_text, "financial_text": financial_ai_text, "market_text": market_ai_text, "updated_at": None})
    except Exception as exc:
        logger.exception("Unhandled error in /api/diagnose")
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("API_PORT", "5000")), debug=True, use_reloader=False)
