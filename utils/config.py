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
.stApp { background-color: #0a0a0a; }
section[data-testid="stSidebar"] { background-color: #111 !important; border-right: 1px solid #222; }
.main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
div[data-testid="metric-container"] {
    background: #1a1a1a; border: 1px solid #2a2a2a;
    border-radius: 8px; padding: 14px 18px;
}
div[data-testid="metric-container"] label {
    font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 0.5px;
}
div[data-testid="metric-container"] [data-testid="metric-value"] {
    font-size: 22px; font-weight: 700; color: white;
}
.stButton > button {
    background-color: #1f77b4; color: white; border: none;
    border-radius: 6px; font-weight: 600; padding: 8px 20px;
}
.stButton > button:hover { background-color: #2a8fd4; border: none; }
.page-header { margin-bottom: 1.5rem; }
.page-title { font-size: 2rem; font-weight: 700; color: white; margin-bottom: 0.2rem; }
.page-subtitle { font-size: 1rem; color: #1f77b4; margin-bottom: 0; }
.card {
    background: #1a1a1a; border: 1px solid #2a2a2a;
    border-radius: 10px; padding: 20px; margin-bottom: 16px;
}
.tier1 { color: #2ca02c; font-weight: 700; }
.tier2 { color: #FFA500; font-weight: 700; }
.tier3 { color: #d62728; font-weight: 700; }
.stTabs [data-baseweb="tab-list"] { background-color: #111; border-bottom: 1px solid #333; }
.stTabs [data-baseweb="tab"] { color: #888; }
.stTabs [aria-selected="true"] { color: white !important; }
.stDataFrame { background: #1a1a1a; }
div[data-testid="stExpander"] { background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 8px; }
.stAlert { border-radius: 8px; }
</style>
"""
