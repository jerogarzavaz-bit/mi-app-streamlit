TICKERS_US = ["AAPL","MSFT","NVDA","TSLA","META","GOOGL","AMZN","JPM","XOM","CVX","UNH","JNJ","V","MA","NFLX"]
TICKERS_MX = ["AMXL.MX","WALMEX.MX","FEMSAUBD.MX","GMEXICOB.MX","TLEVICPO.MX","CEMEXCPO.MX","BIMBOA.MX","ALSEA.MX"]

CACHE_TTL = 3600
PERIOD_DAYS = "100d"

PERIODS = {
    "30 días": "30d",
    "100 días": "100d",
    "1 año": "1y",
    "3 años": "3y",
    "5 años": "5y",
}

COLOR_PRIMARY = "#1f77b4"
COLOR_SUCCESS = "#2ca02c"
COLOR_DANGER  = "#d62728"
COLOR_WARNING = "#FFA500"
COLOR_INFO    = "#4da6ff"

SCORE_WEIGHTS = {
    "valuation": 0.20,
    "growth":    0.20,
    "quality":   0.20,
    "technical": 0.15,
    "momentum":  0.15,
    "sentiment": 0.10,
}
TIER1_MIN = 6.5
TIER2_MIN = 4.0

MARKET_INDICES = {
    "S&P 500":  "^GSPC",
    "NASDAQ":   "^IXIC",
    "DOW":      "^DJI",
    "10Y Yield":"^TNX",
    "VIX":      "^VIX",
    "Gold":     "GC=F",
    "Oil WTI":  "CL=F",
}

SECTOR_ETFS = {
    "Technology":          "XLK",
    "Communication":       "XLC",
    "Consumer Cyclical":   "XLY",
    "Consumer Defensive":  "XLP",
    "Healthcare":          "XLV",
    "Financials":          "XLF",
    "Industrials":         "XLI",
    "Energy":              "XLE",
    "Materials":           "XLB",
    "Real Estate":         "XLRE",
    "Utilities":           "XLU",
}

SECTOR_LEADERS = {
    "Technology":         "NVDA",
    "Communication":      "META",
    "Consumer Cyclical":  "AMZN",
    "Consumer Defensive": "WMT",
    "Healthcare":         "UNH",
    "Financials":         "JPM",
    "Industrials":        "CAT",
    "Energy":             "XOM",
}

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Base & Background ─────────────────────────────────────────────────────── */
.stApp {
    background-color: #060810;
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(31,119,180,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 40% 30% at 90% 90%, rgba(99,51,180,0.07) 0%, transparent 50%);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* ── Fade-in on page load ──────────────────────────────────────────────────── */
@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes shimmer {
    0%   { background-position: -200% center; }
    100% { background-position:  200% center; }
}
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 8px rgba(31,119,180,0.3); }
    50%       { box-shadow: 0 0 20px rgba(31,119,180,0.6); }
}
@keyframes spin {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}
@keyframes borderGlow {
    0%, 100% { border-color: rgba(31,119,180,0.3); }
    50%       { border-color: rgba(31,119,180,0.8); }
}

.main .block-container {
    padding-top: 1.8rem;
    padding-bottom: 3rem;
    animation: fadeSlideIn 0.45s ease both;
}

/* ── Sidebar ───────────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0f1a 0%, #0a0c14 60%, #080a10 100%) !important;
    border-right: 1px solid rgba(31,119,180,0.2) !important;
    box-shadow: 4px 0 24px rgba(0,0,0,0.5);
}
section[data-testid="stSidebar"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, #1f77b4, transparent);
}

/* ── Metric Cards ──────────────────────────────────────────────────────────── */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #111520 0%, #0e1018 100%);
    border: 1px solid rgba(31,119,180,0.2);
    border-radius: 12px;
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}
div[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #1f77b4, #7c3aed, #1f77b4);
    background-size: 200% auto;
    animation: shimmer 3s linear infinite;
}
div[data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    border-color: rgba(31,119,180,0.5);
    box-shadow: 0 8px 32px rgba(31,119,180,0.15);
}
div[data-testid="metric-container"] label {
    font-size: 10px !important;
    color: #5a6a8a !important;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    font-weight: 600;
}
div[data-testid="metric-container"] [data-testid="metric-value"] {
    font-size: 24px !important;
    font-weight: 800 !important;
    color: #e8edf8 !important;
    letter-spacing: -0.5px;
}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 12px !important;
    font-weight: 600 !important;
}

/* ── Buttons ───────────────────────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #1f77b4 0%, #1560a0 100%);
    color: white !important;
    border: 1px solid rgba(31,119,180,0.4) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 8px 20px !important;
    letter-spacing: 0.3px;
    transition: all 0.2s ease !important;
    position: relative;
    overflow: hidden;
}
.stButton > button::after {
    content: '';
    position: absolute;
    top: -50%; left: -60%;
    width: 40%; height: 200%;
    background: rgba(255,255,255,0.08);
    transform: skewX(-20deg);
    transition: left 0.4s ease;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2a8fd4 0%, #1f77b4 100%) !important;
    border-color: rgba(31,119,180,0.8) !important;
    box-shadow: 0 4px 20px rgba(31,119,180,0.4) !important;
    transform: translateY(-1px);
}
.stButton > button:hover::after { left: 120%; }
.stButton > button:active { transform: translateY(0) !important; }

/* Primary button extra glow */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1f77b4 0%, #7c3aed 100%) !important;
    border-color: rgba(124,58,237,0.4) !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 4px 24px rgba(124,58,237,0.35) !important;
}

/* ── Page Headers ──────────────────────────────────────────────────────────── */
.page-header {
    margin-bottom: 2rem;
    padding-bottom: 1.2rem;
    border-bottom: 1px solid rgba(31,119,180,0.15);
    position: relative;
}
.page-header::after {
    content: '';
    position: absolute;
    bottom: -1px; left: 0;
    width: 80px; height: 2px;
    background: linear-gradient(90deg, #1f77b4, #7c3aed);
    border-radius: 2px;
}
.page-title {
    font-size: 1.9rem;
    font-weight: 800;
    background: linear-gradient(135deg, #e8edf8 30%, #7eb8e8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.3rem;
    letter-spacing: -0.5px;
}
.page-subtitle {
    font-size: 0.9rem;
    color: #4a90d9;
    font-weight: 500;
    letter-spacing: 0.5px;
}

/* ── Cards ─────────────────────────────────────────────────────────────────── */
.card {
    background: linear-gradient(135deg, #111520 0%, #0e1018 100%);
    border: 1px solid rgba(31,119,180,0.18);
    border-radius: 14px;
    padding: 22px 24px;
    margin-bottom: 16px;
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    position: relative;
    overflow: hidden;
}
.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(31,119,180,0.4), transparent);
}
.card:hover {
    transform: translateY(-2px);
    border-color: rgba(31,119,180,0.35);
    box-shadow: 0 8px 40px rgba(0,0,0,0.4), 0 0 0 1px rgba(31,119,180,0.1);
}

/* ── Tiers ─────────────────────────────────────────────────────────────────── */
.tier1 {
    color: #22c55e;
    font-weight: 700;
    text-shadow: 0 0 12px rgba(34,197,94,0.4);
}
.tier2 { color: #f59e0b; font-weight: 700; }
.tier3 { color: #ef4444; font-weight: 700; }

/* ── Tabs ──────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(31,119,180,0.2) !important;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    color: #5a6a8a !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 8px 18px !important;
    transition: color 0.2s, background 0.2s !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #a0b4d0 !important;
    background: rgba(31,119,180,0.08) !important;
}
.stTabs [aria-selected="true"] {
    color: white !important;
    background: rgba(31,119,180,0.15) !important;
    border-bottom: 2px solid #1f77b4 !important;
}

/* ── DataFrames ────────────────────────────────────────────────────────────── */
.stDataFrame {
    border-radius: 12px !important;
    overflow: hidden;
    border: 1px solid rgba(31,119,180,0.15) !important;
}
.stDataFrame [data-testid="stDataFrameResizable"] {
    border-radius: 12px !important;
}

/* ── Inputs & Selects ──────────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: #0e1018 !important;
    border: 1px solid rgba(31,119,180,0.25) !important;
    border-radius: 8px !important;
    color: #e8edf8 !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: rgba(31,119,180,0.7) !important;
    box-shadow: 0 0 0 3px rgba(31,119,180,0.12) !important;
}

/* ── Expanders ─────────────────────────────────────────────────────────────── */
div[data-testid="stExpander"] {
    background: #0e1018 !important;
    border: 1px solid rgba(31,119,180,0.18) !important;
    border-radius: 10px !important;
    transition: border-color 0.2s ease;
}
div[data-testid="stExpander"]:hover {
    border-color: rgba(31,119,180,0.35) !important;
}

/* ── Alerts ────────────────────────────────────────────────────────────────── */
.stAlert {
    border-radius: 10px !important;
    border-left-width: 3px !important;
}

/* ── Dividers ──────────────────────────────────────────────────────────────── */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(31,119,180,0.25), transparent) !important;
    margin: 1.5rem 0 !important;
}

/* ── Scrollbar ─────────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #060810; }
::-webkit-scrollbar-thumb {
    background: linear-gradient(#1f77b4, #7c3aed);
    border-radius: 3px;
}

/* ── Spinner ───────────────────────────────────────────────────────────────── */
.stSpinner > div { border-top-color: #1f77b4 !important; }

/* ── Progress bars ─────────────────────────────────────────────────────────── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #1f77b4, #7c3aed) !important;
    border-radius: 4px !important;
}
.stProgress > div > div {
    background: rgba(31,119,180,0.1) !important;
    border-radius: 4px !important;
}

/* ── Subheaders ────────────────────────────────────────────────────────────── */
h2, h3 {
    color: #c8d8f0 !important;
    font-weight: 700 !important;
    letter-spacing: -0.3px !important;
}

/* ── Caption & small text ──────────────────────────────────────────────────── */
.stCaption, small { color: #4a5a7a !important; }

/* ── Live badge ────────────────────────────────────────────────────────────── */
.live-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(34,197,94,0.1);
    border: 1px solid rgba(34,197,94,0.3);
    color: #22c55e;
    font-size: 10px; font-weight: 700;
    padding: 3px 10px; border-radius: 20px;
    letter-spacing: 1px; text-transform: uppercase;
}
.live-badge::before {
    content: '';
    width: 6px; height: 6px;
    background: #22c55e;
    border-radius: 50%;
    animation: pulse-glow 1.5s ease-in-out infinite;
    box-shadow: 0 0 6px #22c55e;
}

/* ── Stat pill ─────────────────────────────────────────────────────────────── */
.stat-pill {
    display: inline-block;
    background: rgba(31,119,180,0.1);
    border: 1px solid rgba(31,119,180,0.25);
    color: #7eb8e8;
    font-size: 11px; font-weight: 600;
    padding: 2px 10px; border-radius: 20px;
}

/* ── Feature grid cards (Main page) ───────────────────────────────────────── */
.feature-card {
    background: linear-gradient(135deg, #111520 0%, #0e1018 100%);
    border: 1px solid rgba(31,119,180,0.2);
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 10px;
    display: flex; align-items: center; gap: 12px;
    transition: all 0.2s ease;
    cursor: default;
}
.feature-card:hover {
    border-color: rgba(31,119,180,0.5);
    transform: translateX(4px);
    box-shadow: 0 4px 20px rgba(31,119,180,0.1);
}
.feature-icon {
    font-size: 20px;
    width: 38px; height: 38px;
    background: rgba(31,119,180,0.12);
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.feature-name  { font-size: 13px; font-weight: 700; color: #c8d8f0; }
.feature-desc  { font-size: 11px; color: #4a6a8a; margin-top: 1px; }

/* ── Step numbers ──────────────────────────────────────────────────────────── */
.step-num {
    background: linear-gradient(135deg, #1f77b4, #7c3aed);
    color: white;
    border-radius: 50%;
    width: 28px; height: 28px;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 12px;
    flex-shrink: 0;
    box-shadow: 0 0 12px rgba(31,119,180,0.4);
}

/* ── Table row hover ───────────────────────────────────────────────────────── */
.stDataFrame tbody tr:hover td {
    background: rgba(31,119,180,0.08) !important;
}

/* ── Sidebar nav links ─────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] a {
    transition: color 0.15s ease !important;
}
section[data-testid="stSidebar"] a:hover {
    color: #7eb8e8 !important;
}

/* ── Toast ─────────────────────────────────────────────────────────────────── */
div[data-testid="stToast"] {
    background: #111520 !important;
    border: 1px solid rgba(31,119,180,0.3) !important;
    border-radius: 10px !important;
}
</style>
"""
