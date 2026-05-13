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

# ── Design System — Color Tokens ──────────────────────────────────────────────
COLOR_PRIMARY = "#6172F3"       # Indigo (Linear-style)
COLOR_SUCCESS = "#22C55E"       # Green
COLOR_DANGER  = "#EF4444"       # Red
COLOR_WARNING = "#F59E0B"       # Amber
COLOR_INFO    = "#8B5CF6"       # Violet

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

# ── Bull Monkey — Global Design System CSS ────────────────────────────────────
GLOBAL_CSS = """
<style>
/* ── Fonts ──────────────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Syne:wght@700;800&display=swap');

/* ── Design Tokens ─────────────────────────────────────────────────────────── */
:root {
    /* Layered charcoal depth system — Raycast / Vercel inspired */
    --bg-base:        #09090B;
    --bg-surface:     #0F0F12;
    --bg-elevated:    #18181B;
    --bg-overlay:     #1F1F24;
    --bg-hover:       #27272A;
    --bg-glass:       rgba(15,15,18,0.72);

    /* Borders — almost invisible, depth through shadow not lines */
    --border-subtle:  rgba(255,255,255,0.035);
    --border-default: rgba(255,255,255,0.065);
    --border-strong:  rgba(255,255,255,0.11);
    --border-focus:   rgba(99,114,243,0.45);

    /* Typography */
    --text-primary:   #FAFAFA;
    --text-secondary: #A1A1AA;
    --text-muted:     #52525B;
    --text-disabled:  #3F3F46;

    /* Accents — restrained, max 2 in any one view */
    --accent-primary: #6172F3;   /* indigo — main brand, like Linear */
    --accent-blue:    #6172F3;
    --accent-violet:  #8B5CF6;
    --accent-green:   #22C55E;
    --accent-red:     #EF4444;
    --accent-amber:   #F59E0B;
    --accent-teal:    #14B8A6;

    /* Legacy compat aliases */
    --accent-primary-glow: rgba(97,114,243,0.18);
    --accent-green-glow:   rgba(34,197,94,0.12);
    --accent-red-glow:     rgba(239,68,68,0.10);

    /* Radius */
    --radius-xs:  4px;
    --radius-sm:  6px;
    --radius-md:  10px;
    --radius-lg:  14px;
    --radius-xl:  20px;

    /* Shadows — depth without borders */
    --shadow-xs:  0 1px 2px rgba(0,0,0,0.5);
    --shadow-sm:  0 2px 8px rgba(0,0,0,0.45), 0 1px 2px rgba(0,0,0,0.3);
    --shadow-md:  0 4px 20px rgba(0,0,0,0.5),  0 1px 3px rgba(0,0,0,0.4);
    --shadow-lg:  0 12px 48px rgba(0,0,0,0.6), 0 4px 12px rgba(0,0,0,0.4);
    --shadow-glow: 0 0 24px rgba(97,114,243,0.15), 0 4px 20px rgba(0,0,0,0.5);

    /* Timing */
    --ease-out:   cubic-bezier(0.16, 1, 0.3, 1);
    --ease-in:    cubic-bezier(0.4, 0, 1, 1);
    --transition: 120ms cubic-bezier(0.16, 1, 0.3, 1);
    --transition-slow: 200ms cubic-bezier(0.16, 1, 0.3, 1);
}

/* ── Base ──────────────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

.stApp {
    background: var(--bg-base);
    /* Cinematic ambient — barely visible, just sets atmosphere */
    background-image:
        radial-gradient(ellipse 80% 50% at 15% -10%,  rgba(97,114,243,0.055) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 85% 110%,  rgba(139,92,246,0.04)  0%, transparent 55%);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: var(--text-primary);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* ── Page entrance — fast, barely perceptible ──────────────────────────────── */
@keyframes pageIn {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulseGreen {
    0%, 100% { box-shadow: 0 0 0 0 rgba(34,197,94,0.4); }
    60%      { box-shadow: 0 0 0 4px rgba(34,197,94,0);  }
}
@keyframes countUp {
    from { opacity: 0; transform: translateY(3px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes shimmer {
    0%   { background-position: -200% 0; }
    100% { background-position:  200% 0; }
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 5rem;
    padding-left: 2.5rem;
    padding-right: 2.5rem;
    max-width: 1440px;
    animation: pageIn 0.22s var(--ease-out) both;
}

/* ══════════════════════════════════════════════════════════════════════════════
   SIDEBAR — atmospheric, glass, minimal
   ══════════════════════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {
    background: var(--bg-glass) !important;
    backdrop-filter: blur(24px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
    border-right: 1px solid var(--border-subtle) !important;
    box-shadow: 1px 0 0 var(--border-subtle), 4px 0 20px rgba(0,0,0,0.3) !important;
}

/* Nav separators — invisible, only the label shows */
[data-testid="stSidebarNavSeparator"] {
    padding: 4px 12px 2px !important;
    margin-top: 10px !important;
}
[data-testid="stSidebarNavSeparator"] span,
[data-testid="stSidebarNavSeparator"] div,
[data-testid="stSidebarNavSeparator"] p {
    font-size: 8.5px !important;
    font-weight: 600 !important;
    letter-spacing: 1.8px !important;
    text-transform: uppercase !important;
    color: var(--text-disabled) !important;
    font-family: 'Inter', sans-serif !important;
}

/* Nav links — Linear style: just text, no boxes */
[data-testid="stSidebarNavLink"] a {
    border-radius: var(--radius-sm) !important;
    padding: 7px 12px !important;
    margin: 1px 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: var(--text-muted) !important;
    transition: background var(--transition), color var(--transition) !important;
    letter-spacing: -0.1px !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stSidebarNavLink"] a:hover {
    background: rgba(255,255,255,0.04) !important;
    color: var(--text-secondary) !important;
}
[data-testid="stSidebarNavLink"] a[aria-current="page"] {
    background: rgba(97,114,243,0.1) !important;
    color: #A5B4FC !important;  /* indigo-300 — bright but not garish */
    font-weight: 600 !important;
}

/* ══════════════════════════════════════════════════════════════════════════════
   METRIC CARDS — floating, no heavy border
   ══════════════════════════════════════════════════════════════════════════════ */
div[data-testid="metric-container"] {
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 18px 20px 16px;
    position: relative;
    overflow: hidden;
    transition: transform var(--transition), box-shadow var(--transition-slow), border-color var(--transition);
    box-shadow: var(--shadow-xs);
}
div[data-testid="metric-container"]::before {
    /* Subtle top-edge highlight — glass feel */
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent);
}
div[data-testid="metric-container"]:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
    border-color: var(--border-default);
}
div[data-testid="metric-container"] label {
    font-size: 10px !important;
    font-weight: 500 !important;
    letter-spacing: 0.8px !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
    font-family: 'Inter', sans-serif !important;
}
div[data-testid="metric-container"] [data-testid="metric-value"] {
    font-size: 24px !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-variant-numeric: tabular-nums !important;
    letter-spacing: -1px !important;
    animation: countUp 0.18s var(--ease-out) both !important;
    line-height: 1.2 !important;
}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 11px !important;
    font-weight: 600 !important;
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: 0 !important;
}

/* ══════════════════════════════════════════════════════════════════════════════
   BUTTONS — magnetic, refined
   ══════════════════════════════════════════════════════════════════════════════ */
.stButton > button {
    background: var(--bg-elevated) !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: var(--radius-md) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    padding: 7px 16px !important;
    letter-spacing: -0.1px !important;
    transition: all var(--transition) !important;
    height: auto !important;
    line-height: 1.5 !important;
    box-shadow: var(--shadow-xs), inset 0 1px 0 rgba(255,255,255,0.04) !important;
}
.stButton > button:hover {
    background: var(--bg-overlay) !important;
    color: var(--text-primary) !important;
    border-color: var(--border-strong) !important;
    transform: translateY(-1px) !important;
    box-shadow: var(--shadow-sm) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
    box-shadow: var(--shadow-xs) !important;
}

/* Primary — clean indigo, no gradient glitter */
.stButton > button[kind="primary"] {
    background: var(--accent-primary) !important;
    border: 1px solid rgba(97,114,243,0.4) !important;
    color: #fff !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 8px rgba(97,114,243,0.3), var(--shadow-xs),
                inset 0 1px 0 rgba(255,255,255,0.12) !important;
}
.stButton > button[kind="primary"]:hover {
    background: #6E7EF4 !important;
    box-shadow: 0 2px 16px rgba(97,114,243,0.4), var(--shadow-sm) !important;
    transform: translateY(-1px) !important;
}

/* Secondary — ghost */
.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    border-color: var(--border-subtle) !important;
    box-shadow: none !important;
}
.stButton > button[kind="secondary"]:hover {
    color: var(--text-secondary) !important;
    background: rgba(255,255,255,0.03) !important;
    border-color: var(--border-default) !important;
    box-shadow: none !important;
}

/* ══════════════════════════════════════════════════════════════════════════════
   PAGE HEADERS — editorial, breathing
   ══════════════════════════════════════════════════════════════════════════════ */
.page-header {
    margin-bottom: 2.2rem;
    padding-bottom: 1.4rem;
    border-bottom: 1px solid var(--border-subtle);
}
.page-title {
    font-family: 'Syne', 'Inter', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -1px;
    margin-bottom: 0.35rem;
    line-height: 1.15;
}
.page-subtitle {
    font-size: 0.82rem;
    color: var(--text-muted);
    font-weight: 400;
    letter-spacing: 0.1px;
    line-height: 1.5;
}

/* ══════════════════════════════════════════════════════════════════════════════
   CARDS — depth without borders, glass aesthetic
   ══════════════════════════════════════════════════════════════════════════════ */
.card {
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 20px 22px;
    margin-bottom: 10px;
    position: relative;
    overflow: hidden;
    transition: transform var(--transition), box-shadow var(--transition-slow), border-color var(--transition);
    box-shadow: var(--shadow-xs), inset 0 1px 0 rgba(255,255,255,0.03);
}
.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent 10%, rgba(255,255,255,0.055) 50%, transparent 90%);
    pointer-events: none;
}
.card:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
    border-color: var(--border-default);
}

/* Accent stripe variants */
.card-accent  { border-left: 2px solid var(--accent-primary) !important; }
.card-success { border-left: 2px solid var(--accent-green) !important; }
.card-danger  { border-left: 2px solid var(--accent-red) !important; }
.card-warning { border-left: 2px solid var(--accent-amber) !important; }

/* ══════════════════════════════════════════════════════════════════════════════
   TABS — linear style, ultra clean
   ══════════════════════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border-subtle) !important;
    gap: 0 !important;
    padding: 0 0 0 2px !important;
    margin-bottom: 1.5rem !important;
}
.stTabs [data-baseweb="tab"] {
    color: var(--text-muted) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 12.5px !important;
    padding: 9px 16px !important;
    border-radius: 0 !important;
    border-bottom: 1.5px solid transparent !important;
    margin-bottom: -1px !important;
    transition: color var(--transition) !important;
    background: transparent !important;
    letter-spacing: -0.1px !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-secondary) !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    border-bottom: 1.5px solid var(--accent-primary) !important;
    background: transparent !important;
}

/* ══════════════════════════════════════════════════════════════════════════════
   INPUTS — Raycast style
   ══════════════════════════════════════════════════════════════════════════════ */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    letter-spacing: -0.1px !important;
    transition: border-color var(--transition), box-shadow var(--transition) !important;
    box-shadow: inset 0 1px 2px rgba(0,0,0,0.3) !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: rgba(97,114,243,0.5) !important;
    box-shadow: 0 0 0 3px rgba(97,114,243,0.07), inset 0 1px 2px rgba(0,0,0,0.2) !important;
    outline: none !important;
    background: var(--bg-elevated) !important;
}
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
}

/* ── Expanders ─────────────────────────────────────────────────────────────── */
div[data-testid="stExpander"] {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-lg) !important;
    box-shadow: var(--shadow-xs) !important;
    transition: border-color var(--transition) !important;
}
div[data-testid="stExpander"]:hover {
    border-color: var(--border-default) !important;
}
div[data-testid="stExpander"] summary {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    color: var(--text-secondary) !important;
    font-size: 13px !important;
    letter-spacing: -0.1px !important;
}

/* ── Alerts — minimal, no heavy color blocks ────────────────────────────────── */
.stAlert {
    border-radius: var(--radius-md) !important;
    border-left-width: 2px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
}
[data-testid="stSuccess"]  { background: rgba(34,197,94,0.05) !important;  border-color: rgba(34,197,94,0.4) !important; }
[data-testid="stWarning"]  { background: rgba(245,158,11,0.05) !important; border-color: rgba(245,158,11,0.4) !important; }
[data-testid="stError"]    { background: rgba(239,68,68,0.05) !important;  border-color: rgba(239,68,68,0.4) !important; }
[data-testid="stInfo"]     { background: rgba(97,114,243,0.05) !important; border-color: rgba(97,114,243,0.4) !important; }

/* ── Dividers — barely visible ──────────────────────────────────────────────── */
hr {
    border: none !important;
    height: 1px !important;
    background: var(--border-subtle) !important;
    margin: 2rem 0 !important;
}

/* ── Scrollbar — Vercel style ──────────────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.07);
    border-radius: 2px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.12); }

/* ── Spinner ────────────────────────────────────────────────────────────────── */
.stSpinner > div { border-top-color: var(--accent-primary) !important; }

/* ── Progress bars ──────────────────────────────────────────────────────────── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--accent-primary), var(--accent-violet)) !important;
    border-radius: 2px !important;
}
.stProgress > div > div {
    background: var(--bg-overlay) !important;
    border-radius: 2px !important;
    height: 3px !important;
}

/* ── Typography ─────────────────────────────────────────────────────────────── */
h1, h2, h3, h4, h5 {
    font-family: 'Syne', 'Inter', sans-serif !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.5px !important;
    font-weight: 700 !important;
}
h2 { font-size: 1.2rem !important;  letter-spacing: -0.5px !important; }
h3 { font-size: 1.0rem !important;  letter-spacing: -0.3px !important; }
p, li, span, div { font-family: 'Inter', sans-serif; }

.stCaption, small {
    color: var(--text-muted) !important;
    font-size: 11.5px !important;
    font-family: 'Inter', sans-serif !important;
}

/* Numbers → monospace everywhere */
[data-testid="metric-value"],
[data-testid="stMetricDelta"],
.mono { font-family: 'JetBrains Mono', monospace !important; font-variant-numeric: tabular-nums !important; }

/* ── Toast — floating, premium ─────────────────────────────────────────────── */
div[data-testid="stToast"] {
    background: var(--bg-overlay) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: var(--radius-lg) !important;
    font-family: 'Inter', sans-serif !important;
    color: var(--text-primary) !important;
    box-shadow: var(--shadow-lg) !important;
    backdrop-filter: blur(16px) !important;
    font-size: 13px !important;
}

/* ── Radio / Checkbox ───────────────────────────────────────────────────────── */
.stRadio > div, .stCheckbox > div { gap: 6px !important; }
.stRadio label, .stCheckbox label {
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    color: var(--text-secondary) !important;
    letter-spacing: -0.1px !important;
}

/* ── Slider ─────────────────────────────────────────────────────────────────── */
.stSlider [data-testid="stThumbValue"],
.stSlider [data-testid="StyledThumbValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    background: var(--bg-overlay) !important;
    color: var(--text-secondary) !important;
    border-radius: var(--radius-sm) !important;
}

/* ── DataFrames ─────────────────────────────────────────────────────────────── */
.stDataFrame {
    border-radius: var(--radius-lg) !important;
    border: 1px solid var(--border-subtle) !important;
    overflow: hidden !important;
    box-shadow: var(--shadow-xs) !important;
}
.stDataFrame [data-testid="stDataFrameResizable"] { background: var(--bg-elevated) !important; }
.stDataFrame tbody tr:hover td { background: rgba(97,114,243,0.04) !important; }
.stDataFrame thead tr th {
    font-family: 'Inter', sans-serif !important;
    font-size: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.6px !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
    background: var(--bg-elevated) !important;
}

/* ══════════════════════════════════════════════════════════════════════════════
   BULL MONKEY COMPONENT LIBRARY
   ══════════════════════════════════════════════════════════════════════════════ */

/* ── Logo mark ──────────────────────────────────────────────────────────────── */
.y-logo-mark {
    display: inline-flex; align-items: center; justify-content: center;
    width: 30px; height: 30px;
    background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-violet) 100%);
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(97,114,243,0.3);
}

/* ── Sidebar header ─────────────────────────────────────────────────────────── */
.y-sidebar-header {
    padding: 18px 14px 14px;
    border-bottom: 1px solid var(--border-subtle);
    margin-bottom: 8px;
    display: flex; align-items: center; gap: 10px;
}
.y-wordmark {
    font-family: 'Syne', 'Inter', sans-serif;
    font-size: 15px;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.5px;
    line-height: 1;
}
.y-tagline {
    font-size: 8px;
    font-weight: 500;
    letter-spacing: 1.5px;
    color: var(--text-disabled);
    text-transform: uppercase;
    margin-top: 2px;
}

/* ── User badge ─────────────────────────────────────────────────────────────── */
.y-user-badge {
    padding: 8px 12px;
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    margin-bottom: 10px;
}

/* ── Section label ──────────────────────────────────────────────────────────── */
.y-section-label {
    font-size: 9.5px;
    font-weight: 600;
    color: var(--text-disabled);
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin-bottom: 14px;
    font-family: 'Inter', sans-serif;
}

/* ── Badges ─────────────────────────────────────────────────────────────────── */
.badge {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 2px 7px;
    border-radius: 20px;
    font-size: 10px; font-weight: 600;
    letter-spacing: 0.3px;
    font-family: 'Inter', sans-serif;
}
.badge-blue   { background: rgba(97,114,243,0.1);  color: #A5B4FC; border: 1px solid rgba(97,114,243,0.18); }
.badge-green  { background: rgba(34,197,94,0.09);  color: #86EFAC; border: 1px solid rgba(34,197,94,0.15); }
.badge-red    { background: rgba(239,68,68,0.09);  color: #FCA5A5; border: 1px solid rgba(239,68,68,0.15); }
.badge-amber  { background: rgba(245,158,11,0.09); color: #FCD34D; border: 1px solid rgba(245,158,11,0.15); }
.badge-violet { background: rgba(139,92,246,0.09); color: #C4B5FD; border: 1px solid rgba(139,92,246,0.15); }
.badge-muted  { background: var(--bg-overlay); color: var(--text-muted); border: 1px solid var(--border-subtle); }

/* ── Live indicator ─────────────────────────────────────────────────────────── */
.live-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(34,197,94,0.07);
    border: 1px solid rgba(34,197,94,0.15);
    color: #86EFAC;
    font-size: 9.5px; font-weight: 600;
    padding: 3px 9px; border-radius: 20px;
    letter-spacing: 0.8px; text-transform: uppercase;
    font-family: 'Inter', sans-serif;
}
.live-badge::before {
    content: '';
    width: 5px; height: 5px;
    background: var(--accent-green);
    border-radius: 50%;
    animation: pulseGreen 2s ease-in-out infinite;
}

/* ── Tier labels ────────────────────────────────────────────────────────────── */
.tier1 { color: #86EFAC !important; font-weight: 600; }
.tier2 { color: #FCD34D !important; font-weight: 600; }
.tier3 { color: #FCA5A5 !important; font-weight: 600; }

/* ── Ticker chip ────────────────────────────────────────────────────────────── */
.ticker-chip {
    display: inline-flex; align-items: center;
    background: rgba(97,114,243,0.08);
    border: 1px solid rgba(97,114,243,0.14);
    color: #A5B4FC;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10.5px; font-weight: 600;
    padding: 2px 7px;
    border-radius: var(--radius-sm);
    letter-spacing: 0.3px;
}

/* ── Data row ───────────────────────────────────────────────────────────────── */
.data-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 9px 0;
    border-bottom: 1px solid var(--border-subtle);
    font-size: 13px;
}
.data-row:last-child { border-bottom: none; }
.data-row .label { color: var(--text-muted); font-weight: 400; font-family: 'Inter', sans-serif; }
.data-row .value {
    color: var(--text-primary);
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
    font-size: 13px;
}

/* ── Feature card ───────────────────────────────────────────────────────────── */
.feature-card {
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 14px 16px; margin-bottom: 8px;
    display: flex; align-items: center; gap: 14px;
    transition: all var(--transition);
    box-shadow: var(--shadow-xs);
}
.feature-card:hover {
    border-color: var(--border-default);
    box-shadow: var(--shadow-sm);
    transform: translateY(-1px);
}
.feature-icon {
    font-size: 17px; width: 34px; height: 34px;
    background: var(--bg-overlay);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.feature-name { font-size: 12.5px; font-weight: 600; color: var(--text-primary); font-family: 'Inter', sans-serif; letter-spacing: -0.1px; }
.feature-desc { font-size: 11px; color: var(--text-muted); margin-top: 1px; font-family: 'Inter', sans-serif; }

/* ── Step number ────────────────────────────────────────────────────────────── */
.step-num {
    background: rgba(97,114,243,0.15);
    color: #A5B4FC;
    border: 1px solid rgba(97,114,243,0.2);
    border-radius: 50%;
    width: 22px; height: 22px;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 11px;
    flex-shrink: 0; font-family: 'Inter', sans-serif;
}

/* ── Price change ───────────────────────────────────────────────────────────── */
.change-positive { color: #86EFAC !important; font-family: 'JetBrains Mono', monospace; font-weight: 600; }
.change-negative { color: #FCA5A5 !important; font-family: 'JetBrains Mono', monospace; font-weight: 600; }
.change-neutral  { color: var(--text-muted) !important; font-family: 'JetBrains Mono', monospace; }

/* ── Score pill ─────────────────────────────────────────────────────────────── */
.stat-pill {
    display: inline-block;
    background: var(--bg-overlay);
    border: 1px solid var(--border-subtle);
    color: var(--text-secondary);
    font-family: 'JetBrains Mono', monospace;
    font-size: 10.5px; font-weight: 600;
    padding: 2px 8px; border-radius: 20px;
}

/* ── Page header block ──────────────────────────────────────────────────────── */
.y-page-header {
    display: flex; align-items: flex-start; justify-content: space-between;
    margin-bottom: 2rem; padding-bottom: 1.4rem;
    border-bottom: 1px solid var(--border-subtle);
}
.y-page-header .title {
    font-family: 'Syne', 'Inter', sans-serif;
    font-size: 1.7rem; font-weight: 800;
    color: var(--text-primary); letter-spacing: -0.8px; line-height: 1.15;
}
.y-page-header .subtitle {
    font-size: 0.8rem; color: var(--text-muted);
    margin-top: 4px; font-weight: 400; letter-spacing: 0.1px;
}

/* ══════════════════════════════════════════════════════════════════════════════
   PLOTLY — clean modebar, invisible chrome
   ══════════════════════════════════════════════════════════════════════════════ */
.js-plotly-plot .plotly .modebar {
    background: var(--bg-overlay) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
    box-shadow: var(--shadow-sm) !important;
}
.js-plotly-plot .plotly .modebar-btn path { fill: var(--text-muted) !important; }
.js-plotly-plot .plotly .modebar-btn:hover path { fill: var(--text-secondary) !important; }

/* ══════════════════════════════════════════════════════════════════════════════
   HIDE STREAMLIT CHROME
   ══════════════════════════════════════════════════════════════════════════════ */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; height: 0 !important; }
.stDeployButton { display: none !important; }

/* Chat messages */
[data-testid="stChatMessage"] {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-lg) !important;
    margin-bottom: 8px !important;
}
[data-testid="stChatInput"] > div {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: var(--radius-lg) !important;
}
[data-testid="stChatInput"] textarea {
    font-family: 'Inter', sans-serif !important;
    font-size: 13.5px !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: var(--bg-elevated) !important;
    border: 1px dashed var(--border-default) !important;
    border-radius: var(--radius-lg) !important;
}

/* ── Light Mode Token Overrides ────────────────────────────────────────────── */
/* Applied via data-theme="light" on <body> — toggled by Streamlit JS injector */
[data-theme="light"] {
    --bg-base:        #F8F8FA;
    --bg-surface:     #F2F2F5;
    --bg-elevated:    #FFFFFF;
    --bg-overlay:     #EEEEF2;
    --bg-hover:       #E4E4E9;
    --bg-glass:       rgba(248,248,250,0.80);

    --border-subtle:  rgba(0,0,0,0.055);
    --border-default: rgba(0,0,0,0.10);
    --border-strong:  rgba(0,0,0,0.16);

    --text-primary:   #111114;
    --text-secondary: #3F3F46;
    --text-muted:     #71717A;
    --text-disabled:  #A1A1AA;

    --shadow-xs:  0 1px 2px rgba(0,0,0,0.08);
    --shadow-sm:  0 2px 8px rgba(0,0,0,0.10), 0 1px 2px rgba(0,0,0,0.06);
    --shadow-md:  0 4px 20px rgba(0,0,0,0.12), 0 1px 3px rgba(0,0,0,0.08);
    --shadow-lg:  0 12px 48px rgba(0,0,0,0.14), 0 4px 12px rgba(0,0,0,0.08);
    --shadow-glow: 0 0 24px rgba(97,114,243,0.12), 0 4px 20px rgba(0,0,0,0.08);
}
[data-theme="light"] .stApp {
    background: var(--bg-base);
    background-image:
        radial-gradient(ellipse 80% 50% at 15% -10%, rgba(97,114,243,0.04) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 85% 110%, rgba(139,92,246,0.03) 0%, transparent 55%);
}
[data-theme="light"] section[data-testid="stSidebar"] {
    background: rgba(248,248,250,0.88) !important;
}
</style>
"""


# ── Theme injection helper ─────────────────────────────────────────────────────
def theme_js(theme: str) -> str:
    """Return a <script> snippet that sets data-theme on <body>."""
    return f"""<script>
(function() {{
    var t = "{theme}";
    document.body.setAttribute("data-theme", t);
    var mo = new MutationObserver(function() {{
        if (document.body.getAttribute("data-theme") !== t)
            document.body.setAttribute("data-theme", t);
    }});
    mo.observe(document.body, {{attributes: true, attributeFilter: ["data-theme"]}});
}})();
</script>"""
