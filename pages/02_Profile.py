import streamlit as st

st.markdown("""
<div class='page-header'>
  <div class='page-title'>👤 Investor Profile</div>
  <div class='page-subtitle'>Complete your profile to personalize all AI analysis</div>
</div>""", unsafe_allow_html=True)

# ── Step state ────────────────────────────────────────────────────────────────
if "profile_step" not in st.session_state:
    st.session_state.profile_step = 1

TOTAL_STEPS = 6
step = st.session_state.profile_step

# Progress bar
progress = (step - 1) / (TOTAL_STEPS - 1)
st.progress(progress, text=f"Step {step} of {TOTAL_STEPS}")
st.markdown("---")

p = st.session_state.get("profile", {})


# ── Step 1 — Basic Info ───────────────────────────────────────────────────────
if step == 1:
    st.subheader("Step 1 — Basic Info")
    name = st.text_input("Your name", value=p.get("nombre", ""))
    age  = st.slider("Age", 18, 80, value=p.get("edad", 30))
    stage = st.radio("Life stage", [
        "Just starting out (early career, building savings)",
        "Mid-career (established income, some investments)",
        "Pre-retirement (planning for retirement)",
        "Retired (living on savings)",
    ], index=p.get("stage_idx", 0))
    if st.button("Next →"):
        p.update({"nombre": name, "edad": age, "stage": stage,
                  "stage_idx": ["Just starting out (early career, building savings)",
                                "Mid-career (established income, some investments)",
                                "Pre-retirement (planning for retirement)",
                                "Retired (living on savings)"].index(stage)})
        st.session_state.profile = p
        st.session_state.profile_step = 2
        st.rerun()

# ── Step 2 — Risk Mindset ─────────────────────────────────────────────────────
elif step == 2:
    st.subheader("Step 2 — Risk Mindset")
    st.write("*The market drops 30% in one month. What do you realistically do?*")
    options = [
        "Sell everything and move to cash immediately",
        "Sell some positions to reduce the pain",
        "Hold tight and wait for recovery",
        "Hold and start looking for buying opportunities",
        "Aggressively add more — I love a sale",
    ]
    riesgo = st.radio("Select your reaction:", options, index=p.get("riesgo_idx", 4))
    mapping = {"Sell everything": "Very Conservative",
               "Sell some": "Conservative",
               "Hold tight": "Moderate",
               "Hold and start": "Aggressive",
               "Aggressively": "Very Aggressive"}
    label = next((v for k, v in mapping.items() if riesgo.startswith(k)), "Moderate")
    col1, col2 = st.columns(2)
    if col1.button("← Back"):
        st.session_state.profile_step = 1; st.rerun()
    if col2.button("Next →"):
        p.update({"riesgo": label, "riesgo_raw": riesgo, "riesgo_idx": options.index(riesgo)})
        st.session_state.profile = p
        st.session_state.profile_step = 3; st.rerun()

# ── Step 3 — Experience & Knowledge ──────────────────────────────────────────
elif step == 3:
    st.subheader("Step 3 — Experience & Knowledge")
    exp_opts = [
        "Less than 1 year (I'm just getting started)",
        "1-3 years (I have some experience)",
        "3-7 years (I've seen a couple of market cycles)",
        "7-15 years (I'm experienced)",
        "More than 15 years (I'm a seasoned investor)",
    ]
    exp = st.radio("How long have you been actively investing?",
                   exp_opts, index=p.get("exp_idx", 0))

    st.write("")
    instruments = st.multiselect(
        "Which instruments have you personally invested in?",
        ["Individual stocks", "ETFs / Index funds", "Crypto / Digital assets",
         "Options / Derivatives", "Bonds / Fixed income", "Real estate"],
        default=p.get("instruments", ["Individual stocks", "ETFs / Index funds"]),
    )
    decision_opts = [
        "I follow a professional advisor or newsletter",
        "Mainly fundamental analysis (earnings, valuation, growth)",
        "Mainly technical analysis (charts, momentum, patterns)",
        "A mix of fundamental + technical",
        "Quantitative / systematic approach",
        "Gut feeling based on what I know",
    ]
    decision = st.radio("How do you typically make investment decisions?",
                        decision_opts, index=p.get("decision_idx", 1))
    col1, col2 = st.columns(2)
    if col1.button("← Back"):
        st.session_state.profile_step = 2; st.rerun()
    if col2.button("Next →"):
        p.update({"experiencia": exp, "exp_idx": exp_opts.index(exp),
                  "instruments": instruments,
                  "decision": decision, "decision_idx": decision_opts.index(decision)})
        st.session_state.profile = p
        st.session_state.profile_step = 4; st.rerun()

# ── Step 4 — Preferences ──────────────────────────────────────────────────────
elif step == 4:
    st.subheader("Step 4 — Investment Preferences")
    markets = st.multiselect(
        "Which markets do you want to invest in?",
        ["US (NYSE / NASDAQ)", "México (BMV)", "Asia / Emerging Markets", "Global (no preference)"],
        default=p.get("markets", ["US (NYSE / NASDAQ)", "Global (no preference)"]),
    )
    style_opts = [
        "Passive / Index investing",
        "Dividend growth (income + appreciation)",
        "Value investing (buy undervalued companies)",
        "Growth investing (high-growth companies)",
        "Momentum / Trend following",
        "Mixed / No strong preference",
    ]
    estilo = st.radio("Which investment style resonates most?",
                      style_opts, index=p.get("estilo_idx", 5))
    esg_opts = [
        "Not important — I focus purely on returns",
        "Slightly important",
        "Moderately important",
        "Very important — ESG is a primary filter",
    ]
    esg = st.radio("How important is ESG / ethical investing?",
                   esg_opts, index=p.get("esg_idx", 0))
    objetivo_opts = ["Growth", "Income", "Balanced", "Speculation", "Capital preservation"]
    objetivo = st.selectbox("Primary investment objective:",
                            objetivo_opts, index=p.get("obj_idx", 0))
    col1, col2 = st.columns(2)
    if col1.button("← Back"):
        st.session_state.profile_step = 3; st.rerun()
    if col2.button("Next →"):
        p.update({"markets": markets, "estilo": estilo, "estilo_idx": style_opts.index(estilo),
                  "esg": esg, "esg_idx": esg_opts.index(esg),
                  "objetivo": objetivo, "obj_idx": objetivo_opts.index(objetivo)})
        st.session_state.profile = p
        st.session_state.profile_step = 5; st.rerun()

# ── Step 5 — Financial Situation ──────────────────────────────────────────────
elif step == 5:
    st.subheader("Step 5 — Financial Situation")
    horizon = st.radio("Investment time horizon:", [
        "Short-term (< 1 year)", "Medium-term (1-5 years)",
        "Long-term (5-15 years)", "Very long-term (15+ years)",
    ], index=p.get("horizon_idx", 2))
    portfolio_size = st.select_slider("Approximate portfolio size:", options=[
        "< $10k", "$10k – $50k", "$50k – $200k", "$200k – $1M", "$1M+",
    ], value=p.get("portfolio_size", "$50k – $200k"))
    check_freq = st.radio("How often do you check your portfolio?", [
        "Multiple times a day", "Daily", "Weekly", "Monthly",
    ], index=p.get("freq_idx", 1))
    col1, col2 = st.columns(2)
    if col1.button("← Back"):
        st.session_state.profile_step = 4; st.rerun()
    if col2.button("Next →"):
        p.update({"horizon": horizon, "horizon_idx": ["Short-term (< 1 year)", "Medium-term (1-5 years)",
                  "Long-term (5-15 years)", "Very long-term (15+ years)"].index(horizon),
                  "portfolio_size": portfolio_size,
                  "check_freq": check_freq, "freq_idx": ["Multiple times a day","Daily","Weekly","Monthly"].index(check_freq)})
        st.session_state.profile = p
        st.session_state.profile_step = 6; st.rerun()

# ── Step 6 — Review ────────────────────────────────────────────────────────────
elif step == 6:
    st.subheader("Step 6 — Review Your Profile")
    if p:
        rows = {
            "Name":        p.get("nombre", "—"),
            "Age":         str(p.get("edad", "—")),
            "Life Stage":  p.get("stage", "—"),
            "Risk Profile":p.get("riesgo", "—"),
            "Experience":  p.get("experiencia", "—"),
            "Style":       p.get("estilo", "—"),
            "Objective":   p.get("objetivo", "—"),
            "Markets":     ", ".join(p.get("markets", [])),
            "ESG":         p.get("esg", "—"),
            "Time Horizon":p.get("horizon", "—"),
            "Portfolio Size": p.get("portfolio_size", "—"),
        }
        for k, v in rows.items():
            c1, c2 = st.columns([1, 2])
            c1.write(f"**{k}**")
            c2.write(v)
    else:
        st.warning("Please complete the previous steps first.")

    col1, col2 = st.columns(2)
    if col1.button("← Go back"):
        st.session_state.profile_step = 5; st.rerun()
    if col2.button("✅ Save Profile", type="primary"):
        st.session_state.profile = p
        st.success("Profile saved! All AI analyses will now be personalized for you.")
        st.session_state.profile_step = 1
