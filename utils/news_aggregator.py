"""
Multi-source financial news & data aggregator.
All sources are free / public — no extra API keys required for core features.
Optional: Alpha Vantage key for sentiment scoring.
"""
import streamlit as st
import requests
from datetime import datetime, date, timedelta
import yfinance as yf

_HEADERS = {"User-Agent": "StockAnalyzerPro contact@stockanalyzerpro.app"}


# ── 1. General market news (yfinance + RSS) ────────────────────────────────────

@st.cache_data(ttl=1800)
def get_market_news(max_items: int = 25) -> list[dict]:
    """Aggregate top financial headlines from multiple free sources."""
    items: list[dict] = []

    # Source A: yfinance SPY news (proxy for market news)
    try:
        raw = yf.Ticker("SPY").news or []
        for n in raw[:10]:
            url = n.get("link") or n.get("url", "#")
            ts  = n.get("providerPublishTime", 0)
            items.append({
                "source":    n.get("publisher", "Yahoo Finance"),
                "title":     n.get("title", ""),
                "url":       url,
                "date":      datetime.fromtimestamp(ts).strftime("%Y-%m-%d") if ts else "",
                "summary":   "",
                "category":  "Market",
            })
    except Exception:
        pass

    # Source B: RSS feeds (Reuters, CNBC, Investing.com)
    try:
        import feedparser
        rss_sources = [
            ("Reuters Business", "https://feeds.reuters.com/reuters/businessNews"),
            ("CNBC Markets",     "https://www.cnbc.com/id/100003114/device/rss/rss.html"),
            ("MarketWatch",      "https://feeds.content.dowjones.io/public/rss/mw_topstories"),
        ]
        for source_name, url in rss_sources:
            try:
                feed = feedparser.parse(url)
                for entry in (feed.entries or [])[:5]:
                    pub = entry.get("published", "")
                    items.append({
                        "source":   source_name,
                        "title":    entry.get("title", ""),
                        "url":      entry.get("link", "#"),
                        "date":     pub[:10] if pub else "",
                        "summary":  entry.get("summary", "")[:180],
                        "category": "News",
                    })
            except Exception:
                pass
    except ImportError:
        pass

    # Deduplicate by title prefix
    seen: set[str] = set()
    unique: list[dict] = []
    for item in items:
        key = item["title"][:50].lower()
        if key not in seen:
            seen.add(key)
            unique.append(item)

    return unique[:max_items]


# ── 2. Ticker-specific news ────────────────────────────────────────────────────

@st.cache_data(ttl=900)
def get_ticker_multi_news(ticker: str, max_items: int = 12) -> list[dict]:
    """News for a specific ticker from yfinance + Yahoo Finance RSS."""
    items: list[dict] = []

    # yfinance news
    try:
        raw = yf.Ticker(ticker).news or []
        for n in raw[:8]:
            url = n.get("link") or n.get("url", "#")
            ts  = n.get("providerPublishTime", 0)
            items.append({
                "source":   n.get("publisher", "Yahoo Finance"),
                "title":    n.get("title", ""),
                "url":      url,
                "date":     datetime.fromtimestamp(ts).strftime("%Y-%m-%d") if ts else "",
                "summary":  "",
                "category": "Ticker",
            })
    except Exception:
        pass

    # Yahoo Finance RSS for ticker
    try:
        import feedparser
        rss_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
        feed = feedparser.parse(rss_url)
        for entry in (feed.entries or [])[:5]:
            pub = entry.get("published", "")
            items.append({
                "source":  "Yahoo Finance RSS",
                "title":   entry.get("title", ""),
                "url":     entry.get("link", "#"),
                "date":    pub[:10] if pub else "",
                "summary": entry.get("summary", "")[:180],
                "category": "Ticker",
            })
    except Exception:
        pass

    seen: set[str] = set()
    unique: list[dict] = []
    for item in items:
        key = item["title"][:50].lower()
        if key not in seen:
            seen.add(key)
            unique.append(item)

    return unique[:max_items]


# ── 3. SEC EDGAR insider transactions (Form 4) ────────────────────────────────

@st.cache_data(ttl=3600)
def get_insider_transactions(ticker: str, days: int = 60) -> list[dict]:
    """
    Fetch recent Form 4 insider transactions from SEC EDGAR.
    Free public API — no key required.
    """
    try:
        end   = date.today()
        start = end - timedelta(days=days)
        url   = (
            "https://efts.sec.gov/LATEST/search-index?"
            f"q=%22{ticker}%22&forms=4"
            f"&dateRange=custom&startdt={start.isoformat()}&enddt={end.isoformat()}"
            "&hits.hits._source.period_of_report=true"
            "&hits.hits._source.file_date=true"
            "&hits.hits._source.display_names=true"
            "&hits.hits._source.entity_name=true"
        )
        resp = requests.get(url, headers=_HEADERS, timeout=10)
        if resp.status_code != 200:
            return []
        hits = resp.json().get("hits", {}).get("hits", [])
        results: list[dict] = []
        for hit in hits[:10]:
            src = hit.get("_source", {})
            names = src.get("display_names", [])
            filer = names[0] if names else src.get("entity_name", "")
            results.append({
                "date":        src.get("file_date", "")[:10],
                "form":        src.get("form_type", "4"),
                "filer":       filer,
                "ticker":      ticker,
                "period":      src.get("period_of_report", "")[:10],
                "edgar_url":   f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company={ticker}&type=4&dateb=&owner=include&count=10",
            })
        return results
    except Exception:
        return []


@st.cache_data(ttl=7200)
def get_bulk_insider_transactions(tickers: list, days: int = 30) -> list[dict]:
    """Insider transactions for a list of tickers (portfolio overview)."""
    all_txns: list[dict] = []
    for t in tickers[:8]:  # limit to avoid rate limits
        txns = get_insider_transactions(t, days=days)
        all_txns.extend(txns)
    return sorted(all_txns, key=lambda x: x.get("date", ""), reverse=True)


# ── 4. Earnings calendar ───────────────────────────────────────────────────────

@st.cache_data(ttl=3600)
def get_earnings_calendar(tickers: list) -> list[dict]:
    """Upcoming earnings dates for a list of tickers."""
    results: list[dict] = []
    today_str = date.today().isoformat()
    for ticker in tickers[:15]:
        try:
            cal = yf.Ticker(ticker).calendar
            if cal is None:
                continue
            # calendar can be a dict or DataFrame depending on yfinance version
            if isinstance(cal, dict):
                ed = cal.get("Earnings Date")
                if ed:
                    d = ed[0] if hasattr(ed, "__iter__") and not isinstance(ed, str) else ed
                    d_str = str(d)[:10]
                    if d_str >= today_str:
                        results.append({"ticker": ticker, "date": d_str,
                                        "eps_est": cal.get("EPS Estimate", ""),
                                        "rev_est": cal.get("Revenue Estimate", "")})
            else:
                try:
                    row = cal.T if hasattr(cal, "T") else cal
                    if "Earnings Date" in row.columns:
                        d = row["Earnings Date"].iloc[0]
                        d_str = str(d)[:10]
                        if d_str >= today_str:
                            results.append({"ticker": ticker, "date": d_str,
                                            "eps_est": "", "rev_est": ""})
                except Exception:
                    pass
        except Exception:
            pass
    return sorted(results, key=lambda x: x["date"])


# ── 5. Macro economic events (FRED + hard-coded schedule fallback) ─────────────

@st.cache_data(ttl=86400)
def get_macro_events_this_week() -> list[dict]:
    """
    Returns a short list of macro events for the current week.
    Ideally from FRED release calendar; falls back to a static snapshot.
    """
    events: list[dict] = []
    try:
        # FRED release calendar (free, no key for basic endpoint)
        today   = date.today()
        monday  = today - timedelta(days=today.weekday())
        friday  = monday + timedelta(days=4)
        url = (
            "https://api.stlouisfed.org/fred/releases/dates?"
            f"realtime_start={monday.isoformat()}&realtime_end={friday.isoformat()}"
            "&limit=20&sort_order=asc&output_type=1&file_type=json"
        )
        resp = requests.get(url, timeout=8)
        if resp.status_code == 200:
            for r in resp.json().get("release_dates", [])[:15]:
                events.append({
                    "date":  r.get("date", ""),
                    "name":  r.get("release_name", ""),
                    "source":"FRED",
                })
    except Exception:
        pass

    if not events:
        # Static fallback with typical recurring events
        today = date.today()
        wd = today.weekday()
        events = [
            {"date": "This week", "name": "Initial Jobless Claims (Thursday)",    "source": "DOL"},
            {"date": "This week", "name": "Fed Speakers / FOMC Minutes",          "source": "Federal Reserve"},
            {"date": "This week", "name": "S&P Global PMI Flash",                 "source": "S&P Global"},
        ]

    return events


# ── 6. Portfolio-specific news feed ───────────────────────────────────────────

@st.cache_data(ttl=1800)
def get_portfolio_news(tickers: list, max_per_ticker: int = 3) -> list[dict]:
    """Aggregate news for all tickers in a portfolio (deduplicated)."""
    items: list[dict] = []
    seen: set[str] = set()
    for ticker in tickers[:10]:
        try:
            raw = yf.Ticker(ticker).news or []
            for n in raw[:max_per_ticker]:
                key = (n.get("title", ""))[:40].lower()
                if key in seen:
                    continue
                seen.add(key)
                ts = n.get("providerPublishTime", 0)
                items.append({
                    "ticker":    ticker,
                    "source":    n.get("publisher", "Yahoo Finance"),
                    "title":     n.get("title", ""),
                    "url":       n.get("link") or n.get("url", "#"),
                    "date":      datetime.fromtimestamp(ts).strftime("%Y-%m-%d") if ts else "",
                    "summary":   "",
                })
        except Exception:
            pass
    # Sort by date descending
    return sorted(items, key=lambda x: x.get("date", ""), reverse=True)


# ── 7. Alpha Vantage sentiment (optional, needs key) ──────────────────────────

@st.cache_data(ttl=3600)
def get_av_sentiment(ticker: str, av_key: str) -> dict:
    """
    Fetch news sentiment from Alpha Vantage (optional, requires free key).
    Returns: {"sentiment": "Bullish"|"Bearish"|"Neutral", "score": float, "articles": list}
    """
    if not av_key:
        return {}
    try:
        url = (
            f"https://www.alphavantage.co/query?"
            f"function=NEWS_SENTIMENT&tickers={ticker}"
            f"&apikey={av_key}&limit=10"
        )
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return {}
        data = resp.json()
        feed = data.get("feed", [])
        if not feed:
            return {}
        scores = [float(a.get("overall_sentiment_score", 0)) for a in feed if a.get("overall_sentiment_score")]
        avg = sum(scores) / len(scores) if scores else 0
        label = "Bullish" if avg > 0.15 else "Bearish" if avg < -0.15 else "Neutral"
        articles = [{"title": a.get("title"), "url": a.get("url"), "score": a.get("overall_sentiment_score")}
                    for a in feed[:5]]
        return {"sentiment": label, "score": round(avg, 3), "articles": articles}
    except Exception:
        return {}
