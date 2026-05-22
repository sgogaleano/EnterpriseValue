import json
import sqlite3
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional


class CompanyCacheStore:
    def __init__(self, db_path: str = "business_model_diagnosis/cache/company_cache.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _ensure_schema(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS company_cache (
                    company_key TEXT PRIMARY KEY,
                    company_name TEXT NOT NULL,
                    ticker TEXT,
                    context_json TEXT NOT NULL,
                    canvas_text TEXT NOT NULL,
                    financial_text TEXT NOT NULL,
                    market_text TEXT NOT NULL,
                    dashboard_json TEXT NOT NULL DEFAULT '{}',
                    kpis_json TEXT NOT NULL DEFAULT '[]',
                    created_at_epoch INTEGER NOT NULL,
                    updated_at_epoch INTEGER NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_company_cache_updated_at
                ON company_cache(updated_at_epoch)
                """
            )
            columns = {row[1] for row in conn.execute("PRAGMA table_info(company_cache)").fetchall()}
            if "dashboard_json" not in columns:
                conn.execute("ALTER TABLE company_cache ADD COLUMN dashboard_json TEXT NOT NULL DEFAULT '{}' ")
            if "kpis_json" not in columns:
                conn.execute("ALTER TABLE company_cache ADD COLUMN kpis_json TEXT NOT NULL DEFAULT '[]' ")

    @staticmethod
    def _company_key(company_name: str) -> str:
        key = re.sub(r"\s+", " ", company_name.strip().lower())
        key = re.sub(r"[^a-z0-9 ]", "", key)
        return key

    def get_recent(self, company_name: str, max_age_days: int = 30) -> Optional[dict]:
        company_key = self._company_key(company_name)
        cutoff_epoch = int(datetime.now(timezone.utc).timestamp()) - (max_age_days * 24 * 60 * 60)
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT company_name, ticker, context_json, canvas_text, financial_text, market_text, dashboard_json, kpis_json, updated_at_epoch
                FROM company_cache
                WHERE company_key = ? AND updated_at_epoch >= ?
                """,
                (company_key, cutoff_epoch),
            ).fetchone()
        if not row:
            return None
        return {
            "company_name": row[0],
            "ticker": row[1],
            "context": json.loads(row[2]),
            "canvas_text": row[3],
            "financial_text": row[4],
            "market_text": row[5],
            "dashboard": json.loads(row[6] or "{}"),
            "kpis": json.loads(row[7] or "[]"),
            "updated_at_epoch": row[8],
        }

    def upsert(
        self,
        company_name: str,
        ticker: Optional[str],
        context: dict,
        canvas_text: str,
        financial_text: str,
        market_text: str,
        dashboard: Optional[dict] = None,
        kpis: Optional[list] = None,
    ):
        company_key = self._company_key(company_name)
        now_epoch = int(datetime.now(timezone.utc).timestamp())
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO company_cache (
                    company_key, company_name, ticker, context_json, canvas_text, financial_text, market_text, dashboard_json, kpis_json, created_at_epoch, updated_at_epoch
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(company_key) DO UPDATE SET
                    company_name=excluded.company_name,
                    ticker=excluded.ticker,
                    context_json=excluded.context_json,
                    canvas_text=excluded.canvas_text,
                    financial_text=excluded.financial_text,
                    market_text=excluded.market_text,
                    dashboard_json=excluded.dashboard_json,
                    kpis_json=excluded.kpis_json,
                    updated_at_epoch=excluded.updated_at_epoch
                """,
                (
                    company_key,
                    company_name,
                    ticker,
                    json.dumps(context, ensure_ascii=False),
                    canvas_text,
                    financial_text,
                    market_text,
                    json.dumps(dashboard or {}, ensure_ascii=False),
                    json.dumps(kpis or [], ensure_ascii=False),
                    now_epoch,
                    now_epoch,
                ),
            )