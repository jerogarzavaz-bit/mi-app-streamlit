import streamlit as st
import pandas as pd
import numpy as np
from datetime import date

st.markdown("""
<div class='page-header'>
  <div class='page-title'>🤖 AI Workspace</div>
  <div class='page-subtitle'>Chat · Deep Analysis · Financials · Memos · History · Backtester</div>
</div>""", unsafe_allow_html=True)

tab_chat, tab_analysis, tab_fin, tab_memos, tab_ideas, tab_history, tab_bt = st.tabs([
    "💬 AI Chat", "📊 Deep Analysis", "💰 Financials", "📝 Memos", "💡 Trade Ideas", "📚 History", "⚡ Backtester"
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — AI CHAT
# ══════════════════════════════════════════════════════════════════════════════
with tab_chat:
    from utils.ai import has_key, no_key_banner, chat

    if not has_key():
        no_key_banner("AI Chat")

    portfolio  = st.session_state.get("portfolio", [])
    watchlists = st.session_state.get("watchlists", {})
    analyses   = st.session_state.get("analyses", [])
    profile    = st.session_state.get("profile", {})

    def _build_ctx():
        lines = []
        if profile:
            lines.append(f"INVESTOR PROFILE: Risk={profile.get('riesgo','N/A')} | Style={profile.get('estilo','N/A')} | Objective={profile.get('objetivo','N/A')}")
        if portfolio:
            lines.append(f"PORTFOLIO ({len(portfolio)} positions):")
            total = sum(h.get("current_value", h.get("purchase_price",0)*h.get("quantity",0)) for h in portfolio)
            for h in portfolio:
                val = h.get("current_value", h.get("purchase_price",0)*h.get("quantity",0))
                lines.append(f"  {h['ticker']}: {h['quantity']} shares | ${val:,.0f} ({val/total*100:.1f}%)" if total else f"  {h['ticker']}: {h['quantity']} shares")
        else:
            lines.append("PORTFOLIO: No positions yet.")
        for wl_name, wl_tickers in watchlists.items():
            lines.append(f"WATCHLIST '{wl_name}': {', '.join(wl_tickers[:10])}")
        if analyses:
            lines.append("RECENT ANALYSES: " + ", ".join(f"{a['ticker']}({a.get('rec','')})" for a in analyses[-3:]))
        return "\n".join(lines)

    with st.expander("Platform context loaded"):
        st.text(_build_ctx() or "No portfolio or watchlist data yet.")

    suggestions = [
        "How is my portfolio positioned in the current macro environment?",
        "Which of my holdings has the most risk right now?",
        "Give me 3 ideas from my watchlist that deserve a closer look.",
        "What's my biggest concentration risk?",
        "Explain my portfolio's exposure to rising interest rates.",
        "Which sectors am I over- and under-weight in?",
    ]

    messages = st.session_state.get("chat_messages", [])

    if not messages:
        st.subheader("Suggested Questions")
        cols = st.columns(2)
        for i, q in enumerate(suggestions):
            if cols[i % 2].button(q, key=f"ai_sugg_{i}", use_container_width=True):
                messages.append({"role": "user", "content": q})
                st.session_state.chat_messages = messages
                st.rerun()

    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask about your portfolio, any stock, market conditions…",
                           disabled=not has_key())

    if prompt:
        messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                resp = chat(messages, platform_ctx=_build_ctx())
            if resp:
                st.markdown(resp)
                messages.append({"role": "assistant", "content": resp})
            else:
                st.error("Error generating response.")
        st.session_state.chat_messages = messages

    if messages:
        if st.button("🗑️ Clear Chat", type="secondary", key="ai_clear_chat"):
            st.session_state.chat_messages = []
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DEEP ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab_analysis:
    from utils.data import get_stock_data, get_ticker_news, get_analyst_targets
    from utils.plots import price_chart, candlestick_chart
    from utils.screener import score_stock
    from utils.ai import has_key, no_key_banner, analyze_stock
    from utils.config import COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING
    from utils.db import save_user_data, is_configured

    analysis_sub1, analysis_sub2 = st.tabs(["📊 Score Analysis", "📄 10-K / Filing Analyzer"])

    with analysis_sub2:
        from utils.ai import analyze_filing
        if not has_key():
            no_key_banner("10-K Analyzer")
        else:
            st.markdown("Upload or paste a SEC annual report (10-K) or any earnings filing to get an AI-powered deep analysis.")
            input_method = st.radio("Input method", ["Paste text", "Upload file"], horizontal=True, key="tenk_method")
            filing_text = ""
            if input_method == "Paste text":
                filing_text = st.text_area("Paste filing text here", height=200, key="tenk_text",
                                           placeholder="Paste 10-K text, earnings release, or any SEC filing…")
            else:
                upl = st.file_uploader("Upload TXT or PDF", type=["txt", "pdf"], key="tenk_file")
                if upl:
                    if upl.name.endswith(".pdf"):
                        try:
                            import PyPDF2
                            import io as _io
                            reader = PyPDF2.PdfReader(_io.BytesIO(upl.read()))
                            filing_text = "\n".join(p.extract_text() or "" for p in reader.pages[:30])
                        except Exception:
                            try:
                                import pdfplumber
                                import io as _io2
                                with pdfplumber.open(_io2.BytesIO(upl.read())) as pdf:
                                    filing_text = "\n".join(p.extract_text() or "" for p in pdf.pages[:30])
                            except Exception:
                                st.error("Could not parse PDF. Try pasting text instead.")
                    else:
                        filing_text = upl.read().decode("utf-8", errors="replace")

            tenk_ticker = st.text_input("Ticker (optional, for context)", placeholder="AAPL", key="tenk_ticker").upper()
            if filing_text and st.button("🔍 Analyze Filing", type="primary", key="tenk_run"):
                with st.spinner("Claude is reading the filing…"):
                    result_filing = analyze_filing(filing_text, tenk_ticker or "Unknown")
                if result_filing:
                    st.markdown(result_filing)
                else:
                    st.error("Analysis failed. Check your API key.")

    with analysis_sub1:
        if not has_key():
            st.info("💡 Go to **Settings** to add your Anthropic API key and unlock AI analysis.")

        col_in, col_btn = st.columns([3, 1])
        default_ticker = st.session_state.get("analyze_ticker", "")
        ticker_input = col_in.text_input("Ticker symbol", value=default_ticker,
                                          placeholder="e.g. NVDA, AAPL, AMXL.MX", key="ai_analysis_ticker")
        period = st.session_state.get("period", "1y")
        analyze = col_btn.button("Analyze", type="primary", use_container_width=True, key="ai_analyze_btn")

        if not ticker_input:
            st.info("Enter a ticker symbol above to begin analysis.")
        else:
            ticker = ticker_input.strip().upper()
            st.session_state.analyze_ticker = ticker

            with st.spinner(f"Loading data for {ticker}…"):
                info, hist = get_stock_data(ticker, period)

            if info is None or hist is None or len(hist) == 0:
                st.error(f"Could not retrieve data for **{ticker}**. Check the symbol and try again.")
            else:
                price   = info.get("currentPrice") or info.get("regularMarketPrice") or hist["Close"].iloc[-1]
                prev    = info.get("previousClose", price) or price
                delta   = price - prev
                delta_p = delta / prev * 100 if prev else 0
                name    = info.get("longName", ticker)

                st.markdown(f"## {ticker} — {name}")
                c1, c2, c3, c4, c5, c6 = st.columns(6)
                c1.metric("Price",      f"${price:.2f}", f"{delta_p:+.2f}%")
                pe = info.get("trailingPE")
                c2.metric("P/E (TTM)",  f"{pe:.1f}" if pe else "N/A")
                mc = info.get("marketCap", 0)
                c3.metric("Market Cap", f"${mc/1e9:.1f}B" if mc else "N/A")
                c4.metric("52W High",   f"${info.get('fiftyTwoWeekHigh', 0):.2f}")
                c5.metric("52W Low",    f"${info.get('fiftyTwoWeekLow',  0):.2f}")
                div = (info.get("dividendYield") or 0) * 100
                c6.metric("Div Yield",  f"{div:.2f}%")

                scores = score_stock(info, hist)
                sc_cols = st.columns(7)
                tier_color = COLOR_SUCCESS if scores["tier"] == 1 else COLOR_WARNING if scores["tier"] == 2 else COLOR_DANGER
                sc_cols[0].metric("Composite",  f"{scores['composite']}/10")
                sc_cols[1].metric("Valuation",  scores["valuation"])
                sc_cols[2].metric("Growth",     scores["growth"])
                sc_cols[3].metric("Quality",    scores["quality"])
                sc_cols[4].metric("Technical",  scores["technical"])
                sc_cols[5].metric("Momentum",   scores["momentum"])
                sc_cols[6].metric("Sentiment",  scores["sentiment"])
                st.markdown(f"**Recommendation: <span style='color:{tier_color};font-size:20px;'>{scores['rec']}</span>**",
                            unsafe_allow_html=True)

                st.divider()
                chart_type = st.radio("Chart type", ["Line + MAs", "Candlestick"], horizontal=True, key="ai_chart_type")
                period_sel = st.select_slider("Period", options=["30d","100d","6mo","1y","2y","3y","5y"],
                                              value=period, key="ai_period_sel")
                if period_sel != period:
                    st.session_state.period = period_sel
                    st.rerun()

                if chart_type == "Candlestick":
                    st.plotly_chart(candlestick_chart(hist, ticker), use_container_width=True)
                else:
                    st.plotly_chart(price_chart(hist, ticker), use_container_width=True)

                st.divider()
                col_l, col_r = st.columns(2)
                with col_l:
                    st.subheader("Company")
                    st.write(f"**Sector:** {info.get('sector','N/A')}")
                    st.write(f"**Industry:** {info.get('industry','N/A')}")
                    st.write(f"**Country:** {info.get('country','N/A')}")
                    employees = info.get('fullTimeEmployees')
                    st.write(f"**Employees:** {employees:,}" if isinstance(employees, int) else f"**Employees:** {employees or 'N/A'}")
                with col_r:
                    st.subheader("Financials")
                    c1, c2 = st.columns(2)
                    c1.metric("Rev Growth",    f"{(info.get('revenueGrowth') or 0)*100:.1f}%")
                    c2.metric("Profit Margin", f"{(info.get('profitMargins') or 0)*100:.1f}%")
                    c1.metric("ROE",           f"{(info.get('returnOnEquity') or 0)*100:.1f}%")
                    c2.metric("D/E Ratio",     f"{info.get('debtToEquity','N/A')}")

                summary = info.get("longBusinessSummary", "")
                if summary:
                    with st.expander("Business Summary"):
                        st.write(summary)

                targets = get_analyst_targets(ticker)
                if targets.get("mean"):
                    st.divider()
                    st.markdown("<div style='font-size:11px;font-weight:700;color:#4a6a8a;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:10px;'>Analyst Consensus</div>", unsafe_allow_html=True)
                    curr = targets.get("current") or price
                    mean = targets["mean"]
                    upside = ((mean - curr) / curr * 100) if curr else 0
                    tc1, tc2, tc3, tc4, tc5 = st.columns(5)
                    tc1.metric("Low",       f"${targets.get('low',0):.2f}")
                    tc2.metric("Consensus", f"${mean:.2f}", f"{upside:+.1f}% upside")
                    tc3.metric("High",      f"${targets.get('high',0):.2f}")
                    tc4.metric("Rating",    (targets.get("rec") or "").replace("_"," ").upper() or "N/A")
                    tc5.metric("Analysts",  targets.get("num", 0))

                news = get_ticker_news(ticker)
                if news:
                    st.divider()
                    st.markdown("<div style='font-size:11px;font-weight:700;color:#4a6a8a;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:10px;'>Latest News</div>", unsafe_allow_html=True)
                    for n in news[:5]:
                        st.markdown(f"""
                        <div class='card' style='padding:12px 16px;margin-bottom:8px;'>
                          <a href='{n.get("url","#")}' target='_blank' style='color:#7eb8e8;font-weight:600;font-size:13px;text-decoration:none;'>{n.get("title","")}</a>
                          <div style='color:#4a6a8a;font-size:11px;margin-top:4px;'>{n.get("publisher","")} · {n.get("date","")[:10]}</div>
                        </div>""", unsafe_allow_html=True)

                st.divider()
                st.subheader("🤖 AI Analysis")
                if not has_key():
                    no_key_banner("AI analysis")
                else:
                    if analyze or st.button("🔍 Run AI Analysis", type="primary", key="ai_run_analysis"):
                        analysis_box = st.empty()
                        full_text = ""
                        with st.spinner(f"Analyzing {ticker} with Claude AI…"):
                            for chunk in analyze_stock(ticker):
                                full_text += chunk
                                analysis_box.markdown(full_text + "▌")
                        analysis_box.markdown(full_text)
                        st.session_state.analyses.append({
                            "ticker": ticker, "name": name, "date": date.today().isoformat(),
                            "rec": scores["rec"], "score": scores["composite"], "text": full_text,
                            "info": {k: info.get(k) for k in ("sector","industry","currentPrice","marketCap")},
                        })
                        if is_configured(): save_user_data(st.session_state.get("username",""))
                        st.success("Analysis saved to History.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — FINANCIALS
# ══════════════════════════════════════════════════════════════════════════════
with tab_fin:
    from utils.data import get_stock_data
    from utils.ai import has_key, no_key_banner, chat

    fin_ticker = st.text_input("Ticker", placeholder="AAPL, MSFT, NVDA…", key="ai_fin_ticker")
    if not fin_ticker:
        st.info("Enter a ticker to view detailed financial statements.")
    else:
        fin_ticker = fin_ticker.strip().upper()
        with st.spinner(f"Loading financials for {fin_ticker}…"):
            info, hist = get_stock_data(fin_ticker, "1y")

        if info is None:
            st.error(f"Could not load data for {fin_ticker}.")
        else:
            import yfinance as yf
            t = yf.Ticker(fin_ticker)

            st.subheader(f"{fin_ticker} — {info.get('longName', fin_ticker)}")

            fin_tabs = st.tabs(["Key Metrics", "Income Statement", "Balance Sheet", "Cash Flow"])

            with fin_tabs[0]:
                c1, c2, c3, c4 = st.columns(4)
                price = info.get("currentPrice") or info.get("regularMarketPrice") or (hist["Close"].iloc[-1] if hist is not None and len(hist) > 0 else 0)
                c1.metric("Price",         f"${price:.2f}")
                c2.metric("Market Cap",    f"${(info.get('marketCap',0) or 0)/1e9:.1f}B")
                c3.metric("EV",            f"${(info.get('enterpriseValue',0) or 0)/1e9:.1f}B")
                c4.metric("P/E (TTM)",     f"{info.get('trailingPE','N/A')}")
                c1.metric("P/E (Fwd)",     f"{info.get('forwardPE','N/A')}")
                c2.metric("P/B",           f"{info.get('priceToBook','N/A')}")
                c3.metric("EV/EBITDA",     f"{info.get('enterpriseToEbitda','N/A')}")
                c4.metric("P/S",           f"{info.get('priceToSalesTrailing12Months','N/A')}")
                st.divider()
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Revenue Growth", f"{(info.get('revenueGrowth') or 0)*100:.1f}%")
                c2.metric("Earnings Growth",f"{(info.get('earningsGrowth') or 0)*100:.1f}%")
                c3.metric("Profit Margin",  f"{(info.get('profitMargins') or 0)*100:.1f}%")
                c4.metric("Op Margin",      f"{(info.get('operatingMargins') or 0)*100:.1f}%")
                c1.metric("ROE",            f"{(info.get('returnOnEquity') or 0)*100:.1f}%")
                c2.metric("ROA",            f"{(info.get('returnOnAssets') or 0)*100:.1f}%")
                c3.metric("D/E",            f"{info.get('debtToEquity','N/A')}")
                c4.metric("Current Ratio",  f"{info.get('currentRatio','N/A')}")

            with fin_tabs[1]:
                try:
                    income = t.financials
                    if income is not None and not income.empty:
                        st.dataframe(income.fillna(0).applymap(lambda x: f"${x/1e6:,.0f}M" if isinstance(x, (int,float)) else x),
                                     use_container_width=True)
                    else:
                        st.info("Income statement data not available.")
                except Exception as e:
                    st.error(f"Could not load income statement: {e}")

            with fin_tabs[2]:
                try:
                    bs = t.balance_sheet
                    if bs is not None and not bs.empty:
                        st.dataframe(bs.fillna(0).applymap(lambda x: f"${x/1e6:,.0f}M" if isinstance(x, (int,float)) else x),
                                     use_container_width=True)
                    else:
                        st.info("Balance sheet data not available.")
                except Exception as e:
                    st.error(f"Could not load balance sheet: {e}")

            with fin_tabs[3]:
                try:
                    cf = t.cashflow
                    if cf is not None and not cf.empty:
                        st.dataframe(cf.fillna(0).applymap(lambda x: f"${x/1e6:,.0f}M" if isinstance(x, (int,float)) else x),
                                     use_container_width=True)
                    else:
                        st.info("Cash flow data not available.")
                except Exception as e:
                    st.error(f"Could not load cash flow: {e}")

            if has_key():
                st.divider()
                if st.button("🤖 AI Financial Commentary", type="primary", key="ai_fin_commentary"):
                    ctx = f"""Ticker: {fin_ticker}
Revenue Growth: {(info.get('revenueGrowth') or 0)*100:.1f}%
Profit Margin: {(info.get('profitMargins') or 0)*100:.1f}%
ROE: {(info.get('returnOnEquity') or 0)*100:.1f}%
D/E: {info.get('debtToEquity','N/A')}
P/E: {info.get('trailingPE','N/A')}
P/B: {info.get('priceToBook','N/A')}"""
                    with st.spinner("Generating commentary…"):
                        resp = chat([{"role": "user", "content": f"Analyze these financial metrics for {fin_ticker} and give a brief investment commentary:\n{ctx}"}])
                    if resp: st.markdown(resp)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — MEMOS
# ══════════════════════════════════════════════════════════════════════════════
with tab_memos:
    from utils.ai import has_key, no_key_banner, generate_memo
    from utils.data import get_stock_data as _gsd

    analyses = st.session_state.get("analyses", [])

    memo_sub1, memo_sub2 = st.tabs(["From Past Analysis", "New Memo"])

    with memo_sub1:
        if not analyses:
            st.markdown("""
            <div class='card' style='text-align:center;color:#4a6a8a;padding:36px;'>
              No analyses yet. Run a stock analysis in <strong style='color:#7eb8e8;'>Deep Analysis</strong> first.
            </div>""", unsafe_allow_html=True)
        elif not has_key():
            no_key_banner("memo generation")
        else:
            sel = st.selectbox("Select analysis:",
                               [f"{a['ticker']} — {a['date']} ({a.get('rec','')})" for a in reversed(analyses)],
                               key="ai_memo_sel")
            idx = len(analyses) - 1 - [f"{a['ticker']} — {a['date']} ({a.get('rec','')})"
                                        for a in reversed(analyses)].index(sel)
            analysis = analyses[idx]
            st.markdown(f"""
            <div class='card' style='padding:12px 16px;'>
              <strong style='color:#c8d8f0;'>{analysis['ticker']}</strong>
              <span style='color:#4a6a8a;margin-left:8px;'>{analysis.get('name','')} · {analysis['date']} · Score: {analysis.get('score','')}/10</span>
            </div>""", unsafe_allow_html=True)
            if st.button("📄 Generate Investment Memo", type="primary", key="ai_gen_memo"):
                info_m, _ = _gsd(analysis["ticker"], "5d")
                with st.spinner("Generating memo…"):
                    memo = generate_memo(analysis["text"], analysis["ticker"], info_m or {})
                if memo:
                    st.markdown("---")
                    st.markdown(memo)
                    st.download_button("⬇️ Download Memo", memo,
                                       file_name=f"memo_{analysis['ticker']}_{analysis['date']}.txt",
                                       key="ai_dl_memo")
                else:
                    st.error("Memo generation failed. Check your Anthropic API key.")

    with memo_sub2:
        if not has_key():
            no_key_banner("memo generation")
        else:
            m_ticker = st.text_input("Ticker", placeholder="NVDA", key="ai_memo_ticker")
            if m_ticker and st.button("Generate Memo", type="primary", key="ai_new_memo_run"):
                info_m, _ = _gsd(m_ticker.upper(), "1y")
                if info_m is None:
                    st.error("Could not fetch data.")
                else:
                    from utils.ai import analyze_stock
                    with st.spinner("Analyzing and writing memo…"):
                        full = "".join(analyze_stock(m_ticker.upper()))
                        memo = generate_memo(full, m_ticker.upper(), info_m)
                    if memo:
                        st.markdown(memo)
                        st.download_button("⬇️ Download", memo,
                                           file_name=f"memo_{m_ticker.upper()}.txt",
                                           key="ai_new_memo_dl")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — TRADE IDEAS
# ══════════════════════════════════════════════════════════════════════════════
with tab_ideas:
    from utils.ai import has_key, no_key_banner, generate_trade_ideas

    if not has_key():
        no_key_banner("Trade Ideas")
    else:
        st.markdown("<div style='color:#8aadcc;font-size:13px;margin-bottom:16px;'>AI-generated trade setups with specific entry, target, and stop-loss levels based on your watchlist and market context.</div>", unsafe_allow_html=True)

        portfolio  = st.session_state.get("portfolio", [])
        watchlists = st.session_state.get("watchlists", {})
        all_tickers = list({h["ticker"] for h in portfolio})
        for wl in watchlists.values():
            all_tickers.extend(wl)
        all_tickers = sorted(set(all_tickers))

        c1, c2, c3 = st.columns(3)
        selected_tickers = c1.multiselect("Tickers", all_tickers,
                                           default=all_tickers[:5] if all_tickers else [],
                                           key="ti_tickers")
        bias    = c2.radio("Market Bias", ["Bullish", "Neutral", "Bearish"], key="ti_bias", horizontal=True)
        horizon = c3.selectbox("Horizon", ["Intraday", "Swing (3-10 days)", "Position (1-4 weeks)", "Trend (1-3 months)"], key="ti_horizon")

        if not selected_tickers:
            st.info("Add tickers to your watchlist or portfolio first.")
        elif st.button("🧠 Generate Trade Ideas", type="primary", key="ti_run"):
            ctx = f"Portfolio: {', '.join(h['ticker'] for h in portfolio[:10])}\n"
            ctx += f"Watchlists: {', '.join(all_tickers[:15])}"
            with st.spinner("Generating trade setups…"):
                ideas = generate_trade_ideas(selected_tickers, bias, horizon, ctx)
            if ideas:
                st.session_state["_trade_ideas"] = ideas
            else:
                st.error("Generation failed. Check your Anthropic API key.")

        if st.session_state.get("_trade_ideas"):
            st.markdown(st.session_state["_trade_ideas"])
            st.download_button("⬇️ Export Ideas",
                               st.session_state["_trade_ideas"],
                               file_name="trade_ideas.md", key="ti_dl")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — HISTORY
# ══════════════════════════════════════════════════════════════════════════════
with tab_history:
    analyses    = st.session_state.get("analyses", [])
    screen_hist = st.session_state.get("screen_history", [])

    hist_sub1, hist_sub2 = st.tabs(["Deep Analyses", "Screen History"])

    with hist_sub1:
        if not analyses:
            st.markdown("""
            <div class='card' style='text-align:center;color:#4a6a8a;padding:36px;'>
              <div style='font-size:32px;margin-bottom:10px;'>📊</div>
              <div>Run your first analysis in <strong style='color:#7eb8e8;'>Deep Analysis</strong></div>
            </div>""", unsafe_allow_html=True)
        else:
            cc1, cc2, cc3 = st.columns([3, 1, 1])
            search  = cc1.text_input("🔍", "", label_visibility="collapsed", placeholder="Search ticker or company…", key="ai_hist_search")
            sort_by = cc2.selectbox("Sort", ["Newest", "Highest Score", "A–Z"], label_visibility="collapsed", key="ai_hist_sort")
            if cc3.button("🗑️ Clear All", type="secondary", key="ai_hist_clear"):
                st.session_state.analyses = []
                st.rerun()

            filtered = [a for a in analyses
                        if search.upper() in a["ticker"].upper()
                        or search.lower() in a.get("name","").lower()] if search else list(analyses)

            if sort_by == "Newest":         filtered = list(reversed(filtered))
            elif sort_by == "Highest Score": filtered = sorted(filtered, key=lambda x: x.get("score", 0) or 0, reverse=True)
            else:                            filtered = sorted(filtered, key=lambda x: x["ticker"])

            st.markdown(f"<div style='color:#4a6a8a;font-size:12px;margin-bottom:12px;'>{len(filtered)} result{'s' if len(filtered)!=1 else ''}</div>", unsafe_allow_html=True)

            for a in filtered:
                score    = a.get("score", 0) or 0
                rec      = a.get("rec", "N/A")
                ticker   = a["ticker"]
                name     = a.get("name", "")
                date_str = a.get("date", "")
                info_d   = a.get("info", {})

                tier_color = "#22c55e" if score >= 6.5 else "#f59e0b" if score >= 4.0 else "#ef4444"
                tier_label = "BUY" if score >= 6.5 else "HOLD" if score >= 4.0 else "AVOID"
                tier_bg    = ("rgba(34,197,94,0.08)" if score >= 6.5 else "rgba(245,158,11,0.08)" if score >= 4.0 else "rgba(239,68,68,0.08)")
                bar_w      = int(score / 10 * 100)

                with st.expander(f"**{ticker}** · {name or ticker}  ·  {date_str}  ·  {rec}", expanded=False):
                    left, right = st.columns([3, 1])
                    with left:
                        st.markdown(f"""
                        <div style='margin-bottom:14px;'>
                          <div style='display:flex;align-items:center;gap:12px;margin-bottom:6px;'>
                            <span style='font-size:28px;font-weight:800;color:{tier_color};'>{score:.1f}</span>
                            <span style='font-size:13px;color:#4a6a8a;'>/10</span>
                            <span style='background:rgba(0,0,0,0.3);border:1px solid {tier_color}55;color:{tier_color};font-size:11px;font-weight:700;padding:2px 10px;border-radius:20px;'>{tier_label}</span>
                          </div>
                          <div style='background:rgba(255,255,255,0.06);border-radius:6px;height:6px;width:100%;overflow:hidden;'>
                            <div style='width:{bar_w}%;height:100%;background:linear-gradient(90deg,{tier_color},{tier_color}88);border-radius:6px;'></div>
                          </div>
                        </div>""", unsafe_allow_html=True)

                        sector   = info_d.get("sector", "")
                        industry = info_d.get("industry", "")
                        px       = info_d.get("currentPrice", 0) or 0
                        mc       = (info_d.get("marketCap", 0) or 0) / 1e9
                        chips = []
                        if sector:   chips.append(f"<span class='badge badge-blue'>{sector}</span>")
                        if industry: chips.append(f"<span class='badge'>{industry}</span>")
                        if px:       chips.append(f"<span class='badge'>${px:.2f}</span>")
                        if mc:       chips.append(f"<span class='badge'>${mc:.1f}B</span>")
                        if chips:
                            st.markdown(f"<div style='display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px;'>{''.join(chips)}</div>", unsafe_allow_html=True)
                        st.markdown(a.get("text",""))

                    with right:
                        if st.button("🔍 Re-analyze", key=f"hist_reanalyze_{ticker}_{date_str}"):
                            st.session_state.analyze_ticker = ticker
                            st.rerun()
                        if st.button("📄 Memo", key=f"hist_memo_{ticker}_{date_str}"):
                            st.session_state["_memo_from_hist"] = a
                            st.rerun()

    with hist_sub2:
        if not screen_hist:
            st.info("Run a screen in **Discover → Screener** to see history here.")
        else:
            df_sh = pd.DataFrame(reversed(screen_hist))
            st.dataframe(df_sh, use_container_width=True, hide_index=True)
            if st.button("🗑️ Clear Screen History", key="ai_clear_screen_hist"):
                st.session_state.screen_history = []
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — BACKTESTER
# ══════════════════════════════════════════════════════════════════════════════
with tab_bt:
    from utils.data import get_stock_data as _gsd_bt, compute_rsi
    from utils.plots import backtest_chart

    col1, col2, col3 = st.columns(3)
    bt_ticker   = col1.text_input("Ticker", value="AAPL", placeholder="AAPL, NVDA…", key="ai_bt_ticker")
    bt_strategy = col2.selectbox("Strategy", [
        "RSI Mean Reversion", "Golden Cross (MA50 > MA200)", "Momentum (3-Month)", "Breakout (52W High)",
    ], key="ai_bt_strategy")
    bt_period = col3.select_slider("Period", ["1Y","2Y","3Y","5Y"], value="3Y", key="ai_bt_period")

    period_map = {"1Y":"1y","2Y":"2y","3Y":"3y","5Y":"5y"}

    with st.expander("⚙️ Strategy Parameters"):
        if bt_strategy == "RSI Mean Reversion":
            rsi_buy    = st.slider("RSI Buy (oversold)",   10, 45, 30, key="ai_rsi_buy")
            rsi_sell   = st.slider("RSI Sell (overbought)",55, 90, 70, key="ai_rsi_sell")
            rsi_period = st.slider("RSI Period", 5, 30, 14, key="ai_rsi_period")
        elif "Golden Cross" in bt_strategy:
            ma_fast = st.slider("Fast MA",  10, 100, 50,  key="ai_ma_fast")
            ma_slow = st.slider("Slow MA",  50, 300, 200, key="ai_ma_slow")
        elif "Momentum" in bt_strategy:
            mom_period = st.slider("Lookback (days)", 20, 120, 63, key="ai_mom_period")
        else:
            breakout_lookback = st.slider("Breakout Lookback (days)", 20, 252, 252, key="ai_bt_lookback")

    if st.button("▶ Run Backtest", type="primary", disabled=not bt_ticker, key="ai_bt_run"):
        bt_ticker = bt_ticker.strip().upper()
        with st.spinner(f"Running {bt_strategy} on {bt_ticker}…"):
            info_bt, hist_bt = _gsd_bt(bt_ticker, period_map.get(bt_period, "3y"))

        if hist_bt is None or len(hist_bt) < 50:
            st.error("Not enough data for backtesting. Try a longer period or different ticker.")
        else:
            prices  = hist_bt["Close"].copy().reset_index(drop=True)
            dates   = hist_bt.index
            n       = len(prices)
            initial = 10_000.0
            signals = pd.Series([0] * n)

            if bt_strategy == "RSI Mean Reversion":
                for i in range(rsi_period + 1, n):
                    rsi = compute_rsi(prices.iloc[:i+1], rsi_period)
                    signals.iloc[i] = 1 if rsi < rsi_buy else (-1 if rsi > rsi_sell else 0)
            elif "Golden Cross" in bt_strategy:
                prev_fast = prev_slow = None
                for i in range(ma_slow, n):
                    fast = prices.iloc[i-ma_fast:i].mean()
                    slow = prices.iloc[i-ma_slow:i].mean()
                    if prev_fast is not None:
                        if prev_fast <= prev_slow and fast > slow:
                            signals.iloc[i] = 1   # golden cross — buy
                        elif prev_fast >= prev_slow and fast < slow:
                            signals.iloc[i] = -1  # death cross — sell
                    prev_fast, prev_slow = fast, slow
            elif "Momentum" in bt_strategy:
                for i in range(mom_period, n):
                    ret = (prices.iloc[i] / prices.iloc[i - mom_period] - 1) * 100
                    signals.iloc[i] = 1 if ret > 5 else (-1 if ret < -5 else 0)
            else:
                for i in range(breakout_lookback, n):
                    high52 = prices.iloc[i-breakout_lookback:i].max()
                    signals.iloc[i] = 1 if prices.iloc[i] >= high52 * 0.99 else 0

            cash, shares, port, trades, position = initial, 0.0, [], [], False
            for i in range(n):
                price = prices.iloc[i]
                if signals.iloc[i] == 1 and not position and cash > price:
                    shares = cash / price; cash = 0.0; position = True
                    trades.append({"type":"BUY","date":str(dates[i])[:10],"price":price,"shares":shares})
                elif signals.iloc[i] == -1 and position:
                    cash = shares * price; shares = 0.0; position = False
                    trades.append({"type":"SELL","date":str(dates[i])[:10],"price":price,"value":cash})
                port.append(cash + shares * price)

            final_val = port[-1]
            total_ret = (final_val / initial - 1) * 100
            bnh_val   = initial * (prices.iloc[-1] / prices.iloc[0])
            bnh_ret   = (bnh_val / initial - 1) * 100
            port_arr  = np.array(port)
            peak      = np.maximum.accumulate(port_arr)
            drawdown  = ((port_arr - peak) / peak).min() * 100
            daily_rets = np.diff(port_arr) / port_arr[:-1]
            sharpe    = (daily_rets.mean() * 252 - 0.04) / (daily_rets.std() * np.sqrt(252) + 1e-9)

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Strategy Return",   f"{total_ret:+.2f}%")
            c2.metric("Buy & Hold Return", f"{bnh_ret:+.2f}%")
            c3.metric("Alpha",             f"{total_ret - bnh_ret:+.2f}%")
            c4.metric("Max Drawdown",      f"{drawdown:.2f}%")
            c5.metric("Sharpe Ratio",      f"{sharpe:.2f}")

            port_norm = [v / initial * 10_000 for v in port]
            bnh_norm  = [initial * (p / prices.iloc[0]) / initial * 10_000 for p in prices]
            st.plotly_chart(backtest_chart(dates, port_norm, bnh_norm, bt_ticker), use_container_width=True)

            if trades:
                with st.expander(f"Trade Log ({len(trades)} trades)"):
                    st.dataframe(pd.DataFrame(trades), use_container_width=True, hide_index=True)
            else:
                st.info("No trades executed. The strategy had no signals in this period.")
    else:
        st.info("Configure a strategy above and click **▶ Run Backtest**.")
