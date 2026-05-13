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

# ── Y Design System — Color Tokens ────────────────────────────────────────────
COLOR_PRIMARY = "#4f8ef7"       # Electric blue
COLOR_SUCCESS = "#34d399"       # Emerald
COLOR_DANGER  = "#fb7185"       # Rose
COLOR_WARNING = "#fbbf24"       # Amber
COLOR_INFO    = "#a78bfa"       # Violet

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

# ── Y — Global Design System CSS ──────────────────────────────────────────────
GLOBAL_CSS = """
<style>
/* ── Fonts: Space Grotesk + JetBrains Mono + Plus Jakarta Sans ─────────────── */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Plus+Jakarta+Sans:wght@700;800;900&display=swap');

/* ── Design Tokens ─────────────────────────────────────────────────────────── */
:root {
    --bg-base:        #06060a;
    --bg-surface:     #0c0c14;
    --bg-elevated:    #111119;
    --bg-overlay:     #16161f;
    --bg-hover:       #1c1c26;
    --border-subtle:  rgba(255,255,255,0.04);
    --border-default: rgba(255,255,255,0.07);
    --border-focus:   rgba(79,142,247,0.5);
    --text-primary:   #f0f0f6;
    --text-secondary: #868ea0;
    --text-muted:     #3d4452;
    --text-disabled:  #252830;
    --accent-blue:    #4f8ef7;
    --accent-violet:  #9c6cff;
    --accent-green:   #34d399;
    --accent-red:     #fb7185;
    --accent-amber:   #fbbf24;
    --accent-teal:    #2dd4bf;
    --radius-sm:      6px;
    --radius-md:      10px;
    --radius-lg:      14px;
    --radius-xl:      20px;
    --shadow-sm:      0 1px 3px rgba(0,0,0,0.4);
    --shadow-md:      0 4px 16px rgba(0,0,0,0.5);
    --shadow-lg:      0 12px 40px rgba(0,0,0,0.6);
    --transition:     150ms cubic-bezier(0.4,0,0.2,1);
}

/* ── Base reset ────────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

.stApp {
    background: var(--bg-base);
    background-image:
        radial-gradient(ellipse 70% 40% at 20% 0%,   rgba(79,142,247,0.05) 0%, transparent 60%),
        radial-gradient(ellipse 50% 35% at 80% 100%, rgba(156,108,255,0.04) 0%, transparent 55%);
    font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--text-primary);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* ── Page fade-in ──────────────────────────────────────────────────────────── */
@keyframes pageIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulseRing {
    0%   { transform: scale(1);    opacity: 1; }
    100% { transform: scale(1.8);  opacity: 0; }
}
@keyframes slideRight {
    from { width: 0%; }
    to   { width: var(--bar-w, 100%); }
}
@keyframes countUp {
    from { opacity: 0; transform: translateY(4px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.main .block-container {
    padding-top: 1.6rem;
    padding-bottom: 4rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 1400px;
    animation: pageIn 0.3s ease both;
}

/* ── Sidebar ───────────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: var(--bg-surface) !important;
    border-right: 1px solid var(--border-subtle) !important;
    box-shadow: 1px 0 0 var(--border-subtle);
}

/* ── Sidebar nav — group headers ──────────────────────────────────────────── */
[data-testid="stSidebarNavSeparator"] {
    padding: 4px 12px 2px !important;
    margin-top: 8px !important;
}
[data-testid="stSidebarNavSeparator"] span,
[data-testid="stSidebarNavSeparator"] div,
[data-testid="stSidebarNavSeparator"] p {
    font-size: 9px !important;
    font-weight: 700 !important;
    letter-spacing: 1.8px !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

/* ── Sidebar nav — page links ─────────────────────────────────────────────── */
[data-testid="stSidebarNavLink"] a {
    border-radius: var(--radius-sm) !important;
    padding: 6px 10px !important;
    margin: 1px 6px !important;
    font-size: 12.5px !important;
    font-weight: 500 !important;
    color: var(--text-secondary) !important;
    transition: background var(--transition), color var(--transition) !important;
    letter-spacing: 0.1px !important;
}
[data-testid="stSidebarNavLink"] a:hover {
    background: var(--bg-elevated) !important;
    color: var(--text-primary) !important;
}
[data-testid="stSidebarNavLink"] a[aria-current="page"] {
    background: rgba(79,142,247,0.1) !important;
    color: var(--accent-blue) !important;
    font-weight: 600 !important;
}

/* ── Metric Cards — rebuilt ────────────────────────────────────────────────── */
div[data-testid="metric-container"] {
    background: var(--bg-elevated);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    padding: 16px 18px;
    position: relative;
    overflow: hidden;
    transition: border-color var(--transition), box-shadow var(--transition);
}
div[data-testid="metric-container"]:hover {
    border-color: rgba(255,255,255,0.12);
    box-shadow: var(--shadow-sm);
}
div[data-testid="metric-container"] label {
    font-size: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
    font-family: 'Space Grotesk', sans-serif !important;
}
div[data-testid="metric-container"] [data-testid="metric-value"] {
    font-size: 22px !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-variant-numeric: tabular-nums !important;
    letter-spacing: -0.5px !important;
    animation: countUp 0.3s ease both !important;
}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 11px !important;
    font-weight: 600 !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── Buttons ───────────────────────────────────────────────────────────────── */
.stButton > button {
    background: var(--bg-elevated) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 7px 16px !important;
    letter-spacing: 0.2px !important;
    transition: background var(--transition), border-color var(--transition), box-shadow var(--transition) !important;
    height: auto !important;
    line-height: 1.4 !important;
}
.stButton > button:hover {
    background: var(--bg-overlay) !important;
    border-color: rgba(255,255,255,0.12) !important;
    box-shadow: var(--shadow-sm) !important;
}
.stButton > button:active {
    background: var(--bg-surface) !important;
    transform: none !important;
}

/* Primary button — brand gradient */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-violet) 100%) !important;
    border: none !important;
    color: #fff !important;
    box-shadow: 0 2px 12px rgba(79,142,247,0.25) !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 4px 20px rgba(79,142,247,0.35) !important;
    filter: brightness(1.08) !important;
}

/* Secondary button */
.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: var(--text-secondary) !important;
}
.stButton > button[kind="secondary"]:hover {
    color: var(--text-primary) !important;
}

/* ── Page Headers ──────────────────────────────────────────────────────────── */
.page-header {
    margin-bottom: 1.8rem;
    padding-bottom: 1.2rem;
    border-bottom: 1px solid var(--border-subtle);
}
.page-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.75rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.8px;
    margin-bottom: 0.3rem;
    line-height: 1.2;
}
.page-subtitle {
    font-size: 0.82rem;
    color: var(--text-secondary);
    font-weight: 400;
    letter-spacing: 0.1px;
}

/* ── Cards ─────────────────────────────────────────────────────────────────── */
.card {
    background: var(--bg-elevated);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    padding: 18px 20px;
    margin-bottom: 12px;
    transition: border-color var(--transition), box-shadow var(--transition);
    position: relative;
}
.card:hover {
    border-color: rgba(255,255,255,0.1);
    box-shadow: var(--shadow-sm);
}

/* Card with left accent */
.card-accent {
    border-left: 2px solid var(--accent-blue) !important;
}
.card-success  { border-left: 2px solid var(--accent-green) !important; }
.card-danger   { border-left: 2px solid var(--accent-red) !important; }
.card-warning  { border-left: 2px solid var(--accent-amber) !important; }

/* ── Tabs ──────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border-subtle) !important;
    gap: 0 !important;
    padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    color: var(--text-muted) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 500 !important;
    font-size: 12.5px !important;
    padding: 8px 16px !important;
    border-radius: 0 !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -1px !important;
    transition: color var(--transition) !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-secondary) !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    border-bottom: 2px solid var(--accent-blue) !important;
    background: transparent !important;
}

/* ── DataFrames ────────────────────────────────────────────────────────────── */
.stDataFrame {
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--border-default) !important;
    overflow: hidden !important;
}
.stDataFrame [data-testid="stDataFrameResizable"] {
    background: var(--bg-elevated) !important;
}

/* ── Inputs ────────────────────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 13px !important;
    transition: border-color var(--transition) !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--border-focus) !important;
    box-shadow: 0 0 0 3px rgba(79,142,247,0.08) !important;
    outline: none !important;
}

.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 13px !important;
}

/* ── Expanders ─────────────────────────────────────────────────────────────── */
div[data-testid="stExpander"] {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: var(--radius-md) !important;
    transition: border-color var(--transition) !important;
}
div[data-testid="stExpander"]:hover {
    border-color: rgba(255,255,255,0.1) !important;
}
div[data-testid="stExpander"] summary {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
    font-size: 13px !important;
}

/* ── Alerts ────────────────────────────────────────────────────────────────── */
.stAlert {
    border-radius: var(--radius-sm) !important;
    border-left-width: 2px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 13px !important;
}
[data-testid="stSuccess"] {
    background: rgba(52,211,153,0.06) !important;
    border-color: var(--accent-green) !important;
}
[data-testid="stWarning"] {
    background: rgba(251,191,36,0.06) !important;
    border-color: var(--accent-amber) !important;
}
[data-testid="stError"] {
    background: rgba(251,113,133,0.06) !important;
    border-color: var(--accent-red) !important;
}
[data-testid="stInfo"] {
    background: rgba(79,142,247,0.06) !important;
    border-color: var(--accent-blue) !important;
}

/* ── Dividers ──────────────────────────────────────────────────────────────── */
hr {
    border: none !important;
    height: 1px !important;
    background: var(--border-subtle) !important;
    margin: 1.5rem 0 !important;
}

/* ── Scrollbar ─────────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: var(--bg-overlay);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: var(--bg-hover);
}

/* ── Spinner ───────────────────────────────────────────────────────────────── */
.stSpinner > div { border-top-color: var(--accent-blue) !important; }

/* ── Progress bars ─────────────────────────────────────────────────────────── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-violet)) !important;
    border-radius: 3px !important;
}
.stProgress > div > div {
    background: var(--bg-overlay) !important;
    border-radius: 3px !important;
}

/* ── Typography ────────────────────────────────────────────────────────────── */
h1, h2, h3, h4, h5 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.4px !important;
    font-weight: 700 !important;
}
h2 { font-size: 1.25rem !important; }
h3 { font-size: 1.05rem !important; }
p, li, span, div { font-family: 'Space Grotesk', sans-serif; }

.stCaption, small {
    color: var(--text-muted) !important;
    font-size: 11px !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

/* Numbers everywhere → monospace */
[data-testid="metric-value"],
[data-testid="stMetricDelta"],
.mono {
    font-family: 'JetBrains Mono', monospace !important;
    font-variant-numeric: tabular-nums !important;
}

/* ── Toast ─────────────────────────────────────────────────────────────────── */
div[data-testid="stToast"] {
    background: var(--bg-overlay) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: var(--radius-md) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--text-primary) !important;
    box-shadow: var(--shadow-lg) !important;
}

/* ── Radio / Checkbox ──────────────────────────────────────────────────────── */
.stRadio > div, .stCheckbox > div {
    gap: 8px !important;
}
.stRadio label, .stCheckbox label {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 13px !important;
    color: var(--text-secondary) !important;
}

/* ── Slider ────────────────────────────────────────────────────────────────── */
.stSlider [data-testid="stThumbValue"],
.stSlider [data-testid="StyledThumbValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    background: var(--bg-overlay) !important;
    color: var(--text-secondary) !important;
}

/* ──────────────────────────────────────────────────────────────────────────── */
/* Y COMPONENT LIBRARY                                                          */
/* ──────────────────────────────────────────────────────────────────────────── */

/* ── Y Logo mark ───────────────────────────────────────────────────────────── */
.y-logo-mark {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px; height: 32px;
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-violet));
    border-radius: 9px;
    box-shadow: 0 0 20px rgba(79,142,247,0.3);
}

/* ── Page header block ─────────────────────────────────────────────────────── */
.y-page-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 1.8rem;
    padding-bottom: 1.2rem;
    border-bottom: 1px solid var(--border-subtle);
}
.y-page-header .title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.7rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.8px;
    line-height: 1.2;
}
.y-page-header .subtitle {
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-top: 4px;
    font-weight: 400;
    letter-spacing: 0.2px;
}

/* ── Status badges ─────────────────────────────────────────────────────────── */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 2px 8px;
    border-radius: 20px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    font-family: 'Space Grotesk', sans-serif;
}
.badge-blue   { background: rgba(79,142,247,0.12);  color: var(--accent-blue);   border: 1px solid rgba(79,142,247,0.2); }
.badge-green  { background: rgba(52,211,153,0.1);   color: var(--accent-green);  border: 1px solid rgba(52,211,153,0.2); }
.badge-red    { background: rgba(251,113,133,0.1);  color: var(--accent-red);    border: 1px solid rgba(251,113,133,0.2); }
.badge-amber  { background: rgba(251,191,36,0.1);   color: var(--accent-amber);  border: 1px solid rgba(251,191,36,0.2); }
.badge-violet { background: rgba(156,108,255,0.1);  color: var(--accent-violet); border: 1px solid rgba(156,108,255,0.2); }
.badge-muted  { background: var(--bg-overlay);      color: var(--text-muted);    border: 1px solid var(--border-default); }

/* ── Live dot ──────────────────────────────────────────────────────────────── */
.live-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(52,211,153,0.08);
    border: 1px solid rgba(52,211,153,0.2);
    color: var(--accent-green);
    font-size: 10px;
    font-weight: 700;
    padding: 3px 9px;
    border-radius: 20px;
    letter-spacing: 1px;
    text-transform: uppercase;
    font-family: 'Space Grotesk', sans-serif;
}
.live-badge::before {
    content: '';
    width: 5px; height: 5px;
    background: var(--accent-green);
    border-radius: 50%;
    animation: pulseRing 1.8s ease-out infinite;
    box-shadow: 0 0 0 0 var(--accent-green);
}

/* ── Tier badges ───────────────────────────────────────────────────────────── */
.tier1 { color: var(--accent-green) !important;  font-weight: 700; }
.tier2 { color: var(--accent-amber) !important;  font-weight: 700; }
.tier3 { color: var(--accent-red) !important;    font-weight: 700; }

/* ── Score pill ────────────────────────────────────────────────────────────── */
.stat-pill {
    display: inline-block;
    background: var(--bg-overlay);
    border: 1px solid var(--border-default);
    color: var(--text-secondary);
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 9px;
    border-radius: 20px;
}

/* ── Section label ─────────────────────────────────────────────────────────── */
.y-section-label {
    font-size: 10px;
    font-weight: 700;
    color: var(--text-muted);
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 12px;
    font-family: 'Space Grotesk', sans-serif;
}

/* ── Data row (horizontal key-value) ──────────────────────────────────────── */
.data-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid var(--border-subtle);
    font-size: 13px;
}
.data-row:last-child { border-bottom: none; }
.data-row .label { color: var(--text-muted); font-weight: 500; }
.data-row .value {
    color: var(--text-primary);
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
}

/* ── Y Feature cards (Home page) ───────────────────────────────────────────── */
.feature-card {
    background: var(--bg-elevated);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    padding: 14px 16px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 12px;
    transition: border-color var(--transition), background var(--transition);
    cursor: default;
}
.feature-card:hover {
    border-color: rgba(255,255,255,0.1);
    background: var(--bg-overlay);
}
.feature-icon {
    font-size: 18px;
    width: 34px; height: 34px;
    background: var(--bg-overlay);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-sm);
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.feature-name { font-size: 12.5px; font-weight: 600; color: var(--text-primary); font-family: 'Space Grotesk', sans-serif; }
.feature-desc { font-size: 11px; color: var(--text-muted); margin-top: 1px; font-family: 'Space Grotesk', sans-serif; }

/* ── Step indicator ────────────────────────────────────────────────────────── */
.step-num {
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-violet));
    color: white;
    border-radius: 50%;
    width: 24px; height: 24px;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 11px;
    flex-shrink: 0;
}

/* ── Price change indicators ───────────────────────────────────────────────── */
.change-positive { color: var(--accent-green) !important; font-family: 'JetBrains Mono', monospace; font-weight: 600; }
.change-negative { color: var(--accent-red) !important;   font-family: 'JetBrains Mono', monospace; font-weight: 600; }
.change-neutral  { color: var(--text-muted) !important;   font-family: 'JetBrains Mono', monospace; }

/* ── Ticker chip ───────────────────────────────────────────────────────────── */
.ticker-chip {
    display: inline-flex;
    align-items: center;
    background: rgba(79,142,247,0.08);
    border: 1px solid rgba(79,142,247,0.15);
    color: var(--accent-blue);
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: var(--radius-sm);
    letter-spacing: 0.5px;
}

/* ── Sidebar user badge ────────────────────────────────────────────────────── */
.y-user-badge {
    padding: 10px 12px;
    background: var(--bg-elevated);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-sm);
    margin-bottom: 12px;
}

/* ── Clean table rows ──────────────────────────────────────────────────────── */
.stDataFrame tbody tr:hover td {
    background: rgba(79,142,247,0.04) !important;
}
.stDataFrame thead tr th {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 10px !important;
    font-weight: 700 !important;
    letter-spacing: 0.8px !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
    background: var(--bg-elevated) !important;
}

/* ── Y Sidebar branding header ─────────────────────────────────────────────── */
.y-sidebar-header {
    padding: 16px 12px 14px 12px;
    border-bottom: 1px solid var(--border-subtle);
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.y-wordmark {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 20px;
    font-weight: 900;
    background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-violet) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1px;
    line-height: 1;
}
.y-tagline {
    font-size: 8px;
    font-weight: 700;
    letter-spacing: 2.5px;
    color: var(--text-muted);
    text-transform: uppercase;
    margin-top: 1px;
}

/* ── Sidebar bottom links ──────────────────────────────────────────────────── */
section[data-testid="stSidebar"] a {
    transition: color var(--transition) !important;
}

/* ── Hide Streamlit chrome ─────────────────────────────────────────────────── */
#MainMenu    { visibility: hidden; }
footer       { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; height: 0 !important; }

/* ── Plotly charts — dark theme fix ───────────────────────────────────────── */
.js-plotly-plot .plotly .modebar {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: var(--radius-sm) !important;
}
.js-plotly-plot .plotly .modebar-btn path {
    fill: var(--text-muted) !important;
}
</style>
"""
