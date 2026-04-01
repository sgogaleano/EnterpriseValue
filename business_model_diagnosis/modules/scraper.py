import requests
import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class CompanyScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()

    def _headers(self) -> dict:
        return {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

    def _safe_get(self, url: str, timeout: int = 10) -> Optional[requests.Response]:
        try:
            resp = self.session.get(url, headers=self._headers(), timeout=timeout)
            if resp.status_code == 200:
                return resp
        except Exception as e:
            logger.warning(f"Failed to fetch {url}: {e}")
        return None

    def scrape_wikipedia(self, company_name: str) -> str:
        search_url = f"https://en.wikipedia.org/w/index.php?search={company_name.replace(' ', '+')}&title=Special:Search"
        resp = self._safe_get(search_url)
        if not resp:
            return ""
        soup = BeautifulSoup(resp.text, "lxml")
        first_result = soup.select_one(".mw-search-result-heading a")
        if not first_result:
            return ""
        page_url = "https://en.wikipedia.org" + first_result["href"]
        page_resp = self._safe_get(page_url)
        if not page_resp:
            return ""
        page_soup = BeautifulSoup(page_resp.text, "lxml")
        for tag in page_soup(["table", "style", "script", "sup", "span.mw-editsection"]):
            tag.decompose()
        content_div = page_soup.select_one("#mw-content-text .mw-parser-output")
        if not content_div:
            return ""
        paragraphs = content_div.find_all("p", limit=25)
        text = " ".join(p.get_text(separator=" ", strip=True) for p in paragraphs if p.get_text(strip=True))
        return self._clean_text(text)[:6000]

    def scrape_reuters_news(self, company_name: str) -> str:
        query = company_name.replace(" ", "+")
        url = f"https://www.reuters.com/search/news?blob={query}&sortBy=date&dateRange=pastMonth"
        resp = self._safe_get(url)
        if not resp:
            return ""
        soup = BeautifulSoup(resp.text, "lxml")
        headlines = soup.select(".search-result-title, .story-title, h3.article-heading")
        texts = [h.get_text(strip=True) for h in headlines[:10]]
        return "; ".join(texts)

    def scrape_macrotrends(self, ticker: str, metric: str = "revenue") -> str:
        url = f"https://www.macrotrends.net/stocks/charts/{ticker}/{ticker.lower()}/{metric}"
        resp = self._safe_get(url)
        if not resp:
            return ""
        soup = BeautifulSoup(resp.text, "lxml")
        table = soup.select_one("table.historical_data_table")
        if not table:
            return ""
        rows = table.find_all("tr")[:10]
        data = []
        for row in rows:
            cells = row.find_all(["td", "th"])
            data.append(" | ".join(c.get_text(strip=True) for c in cells))
        return "\n".join(data)

    def scrape_google_news(self, company_name: str) -> str:
        query = company_name.replace(" ", "+")
        url = f"https://news.google.com/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        resp = self._safe_get(url)
        if not resp:
            return ""
        soup = BeautifulSoup(resp.text, "lxml")
        articles = soup.select("article h3, article h4")
        texts = [a.get_text(strip=True) for a in articles[:15]]
        return "; ".join(texts)

    def scrape_sec_filings_summary(self, ticker: str) -> str:
        url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company={ticker}&type=10-K&dateb=&owner=include&count=5&search_text="
        resp = self._safe_get(url)
        if not resp:
            return ""
        soup = BeautifulSoup(resp.text, "lxml")
        rows = soup.select("table.tableFile2 tr")[:6]
        data = []
        for row in rows:
            cells = row.find_all("td")
            if cells:
                data.append(" | ".join(c.get_text(strip=True) for c in cells))
        return "\n".join(data)

    def gather_company_context(self, company_name: str, ticker: Optional[str] = None) -> dict:
        print("  [scraper] Fetching Wikipedia overview...")
        wiki = self.scrape_wikipedia(company_name)
        time.sleep(0.5)
        print("  [scraper] Fetching recent news...")
        news = self.scrape_google_news(company_name)
        time.sleep(0.5)
        sec = ""
        if ticker:
            print("  [scraper] Fetching SEC filings index...")
            sec = self.scrape_sec_filings_summary(ticker)
        return {
            "wikipedia": wiki,
            "recent_news": news,
            "sec_filings": sec,
        }

    @staticmethod
    def _clean_text(text: str) -> str:
        text = re.sub(r'\[\d+\]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
