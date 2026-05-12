import streamlit as st
from utils.data import get_stock_data, compute_rsi, compute_momentum
from utils.config import CACHE_TTL


def _key() -> str:
    return st.session_state.get("api_keys", {}).get("anthropic", "")


def has_key() -> bool:
    return bool(_key())


def _client():
    try:
        import anthropic
        k = _key()
        return anthropic.Anthropic(api_key=k) if k else None
    except ImportError:
        return None


def no_key_banner(feature: str = "this feature"):
    st.error(f"**Anthropic API key required** to use {feature}.  "
             "Go to **Settings** to add your key.")


def _profile_ctx() -> str:
    p = st.session_state.get("profile", {})
    if not p:
        return ""
    return (f"\nINVESTOR PROFILE — Risk: {p.get('riesgo','N/A')} | "
            f"Style: {p.get('estilo','N/A')} | Objective: {p.get('objetivo','N/A')}")


def _stock_ctx(ticker: str, info: dict, hist) -> str:
    from utils.screener import score_stock
    sc = score_stock(info, hist) if info and hist is not None else {}
    rsi = compute_rsi(hist["Close"]) if hist is not None and len(hist) > 0 else 50
    mom = compute_momentum(hist) if hist is not None else {}
    price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
    return f"""
TICKER: {ticker} | {info.get("longName", ticker)}
Sector: {info.get("sector","N/A")} | {info.get("industry","N/A")}
Price: ${price:.2f}  Mkt Cap: ${(info.get("marketCap",0) or 0)/1e9:.1f}B
P/E: {info.get("trailingPE","N/A")} | Fwd P/E: {info.get("forwardPE","N/A")} | PEG: {info.get("pegRatio","N/A")}
Rev Growth: {(info.get("revenueGrowth") or 0)*100:.1f}%  Net Margin: {(info.get("profitMargins") or 0)*100:.1f}%
ROE: {(info.get("returnOnEquity") or 0)*100:.1f}%  D/E: {info.get("debtToEquity","N/A")}
52W: ${info.get("fiftyTwoWeekLow",0):.2f} – ${info.get("fiftyTwoWeekHigh",0):.2f}
RSI(14): {rsi:.1f}  | Momentum 1M: {mom.get("1m",0):.1f}%  3M: {mom.get("3m",0):.1f}%
Analyst: {info.get("recommendationKey","N/A")} | Target: ${info.get("targetMeanPrice",0) or 0:.2f}
Composite Score: {sc.get("composite","N/A")}/10 | Tier {sc.get("tier","?")} | {sc.get("rec","?")}
{_profile_ctx()}"""


def analyze_stock(ticker: str):
    client = _client()
    if not client:
        return None
    info, hist = get_stock_data(ticker, "1y")
    if not info:
        return "⚠️ Could not fetch data for this ticker."
    ctx  = _stock_ctx(ticker, info, hist)
    prompt = f"""You are a senior institutional equity analyst. Analyze {ticker} in depth.

{ctx}

Write a professional investment note covering:
1. **Executive Summary** (2-3 sentences, lead with the most important insight)
2. **Investment Thesis** — Bull case + Bear case with specific data points
3. **Valuation** — Is it cheap, fair or expensive? Reference specific multiples.
4. **Growth Outlook** — Revenue & earnings trajectory
5. **Quality & Balance Sheet** — Margins, capital efficiency, leverage
6. **Technical Setup** — Trend, RSI, key levels
7. **Key Risks** — Top 3 specific risks (not generic)
8. **Catalysts** — Near-term (1-3 months) and medium-term (6-12 months)
9. **Recommendation** — BUY / HOLD / SELL, conviction (1-5★), 12-month price target

Be precise and data-driven. No generic disclaimers."""
    try:
        with client.messages.stream(model="claude-sonnet-4-6", max_tokens=2500,
                                    messages=[{"role": "user", "content": prompt}]) as s:
            for chunk in s.text_stream:
                yield chunk
    except Exception as e:
        yield f"\n\n⚠️ Error: {e}"


def chat(messages: list, platform_ctx: str = "") -> str:
    client = _client()
    if not client:
        return None
    system = f"""You are an expert financial analyst embedded in Stock Analyzer Pro.
Be concise, data-driven, and actionable. Use markdown. No disclaimers.

{platform_ctx}"""
    try:
        r = client.messages.create(model="claude-sonnet-4-6", max_tokens=1500,
                                   system=system, messages=messages)
        return r.content[0].text
    except Exception as e:
        return f"⚠️ Error: {e}"


def market_brief(market_data: dict, extended: bool = False) -> str:
    client = _client()
    if not client:
        return None
    lines = "\n".join(f"{k}: {v['price']:.2f} ({v['change_pct']:+.2f}%)"
                      for k, v in market_data.items())
    prompt = f"""Generate a crisp institutional daily market brief.

LIVE DATA:
{lines}

Cover:
1. **Market Tone** — Risk-on or risk-off? Key driver today.
2. **What Moved Markets** — Top 2-3 macro catalysts.
3. **Sector Rotation** — What's leading / lagging and why.
4. **Key Levels** — S&P 500 and NASDAQ support/resistance.
5. **Trade Ideas** — 2-3 specific actionable setups with rationale.
6. **Risk Radar** — Top 2 tail risks for the week.
7. **Calendar** — Key events / data drops to watch.

Institutional tone. Bullet points where useful. No fluff."""
    try:
        kwargs = dict(model="claude-sonnet-4-6", max_tokens=2000,
                      messages=[{"role": "user", "content": prompt}])
        if extended:
            kwargs["thinking"] = {"type": "enabled", "budget_tokens": 8000}
        r = client.messages.create(**kwargs)
        return r.content[-1].text if extended else r.content[0].text
    except Exception as e:
        return f"⚠️ Error: {e}"


def analyze_transcript(transcript: str) -> str:
    client = _client()
    if not client:
        return None
    prompt = f"""Analyze this earnings call transcript like a senior sell-side analyst.

TRANSCRIPT:
{transcript[:12000]}

Provide:
1. **Management Tone** — Confident / Cautious / Defensive?
2. **Key Guidance** — Revenue, margins, capex
3. **Beats / Misses** — vs estimates
4. **Growth Drivers** — New products, geographies, pricing
5. **Risk Flags** — What management is worried about
6. **Analyst Q&A** — Most probing questions & quality of answers
7. **Verdict** — Bullish / Neutral / Bearish and why"""
    try:
        r = client.messages.create(model="claude-sonnet-4-6", max_tokens=2000,
                                   messages=[{"role": "user", "content": prompt}])
        return r.content[0].text
    except Exception as e:
        return f"⚠️ Error: {e}"


def generate_recommendations(watchlist: list, profile: dict) -> str:
    client = _client()
    if not client:
        return None
    tickers_str = ", ".join(watchlist[:20])
    profile_str = f"Risk: {profile.get('riesgo','moderate')} | Style: {profile.get('estilo','mixed')} | Objective: {profile.get('objetivo','growth')}"
    prompt = f"""Generate today's top 3 stock picks from this watchlist: {tickers_str}

Investor profile: {profile_str}

For each pick:
- **Ticker & Company**
- **Why now** — specific catalyst or setup
- **Score** (1-10 conviction)
- **Entry zone** and **Stop loss**
- **1-sentence thesis**

Be selective and specific. Quality over quantity."""
    try:
        r = client.messages.create(model="claude-sonnet-4-6", max_tokens=1200,
                                   messages=[{"role": "user", "content": prompt}])
        return r.content[0].text
    except Exception as e:
        return f"⚠️ Error: {e}"


def generate_memo(analysis_text: str, ticker: str, info: dict) -> str:
    client = _client()
    if not client:
        return None
    prompt = f"""Convert this analysis into a professional Investment Memo for {ticker}.

ANALYSIS:
{analysis_text[:3000]}

FORMAT — Investment Memo:
**INVESTMENT MEMO: {ticker} — {info.get("longName", ticker)}**
Date: [today]
Rating: [BUY/HOLD/SELL]  |  Target: $[price]  |  Conviction: [1-5★]

**EXECUTIVE SUMMARY**
[2-3 sentences]

**THESIS**
[Bull case + Bear case]

**VALUATION**
[Key multiples and comparison]

**RISKS**
[Numbered list of top 3]

**CATALYSTS**
[Bullet points]

**RECOMMENDATION**
[Final call with conviction and price target]

Keep it to 1 page equivalent. Professional font, institutional style."""
    try:
        r = client.messages.create(model="claude-sonnet-4-6", max_tokens=1500,
                                   messages=[{"role": "user", "content": prompt}])
        return r.content[0].text
    except Exception as e:
        return f"⚠️ Error: {e}"
