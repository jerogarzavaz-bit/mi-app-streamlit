"""
Morning Brief utility — HTML email template generator + SMTP sender.
Users configure email + Gmail App Password in Settings.
"""
import smtplib
import streamlit as st
from datetime import date, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# ── Email config helpers ───────────────────────────────────────────────────────

def get_email_config() -> dict:
    """Read email settings from session_state (stored under api_keys for simplicity)."""
    keys = st.session_state.get("api_keys", {})
    return {
        "to_email":      keys.get("brief_email", ""),
        "smtp_host":     keys.get("brief_smtp_host", "smtp.gmail.com"),
        "smtp_port":     int(keys.get("brief_smtp_port", 587)),
        "smtp_user":     keys.get("brief_smtp_user", ""),
        "smtp_password": keys.get("brief_smtp_password", ""),
        "send_time":     keys.get("brief_send_time", "07:00"),
        "enabled":       bool(keys.get("brief_enabled", False)),
    }


def is_email_configured() -> bool:
    cfg = get_email_config()
    return bool(cfg["to_email"] and cfg["smtp_user"] and cfg["smtp_password"])


def should_send_today(username: str) -> bool:
    """Return True if the brief should be auto-sent right now."""
    cfg = get_email_config()
    if not cfg["enabled"] or not is_email_configured():
        return False
    last_sent = st.session_state.get(f"_brief_last_sent_{username}", "")
    if last_sent == date.today().isoformat():
        return False
    try:
        now   = datetime.now()
        h, m  = cfg["send_time"].split(":")
        sched = now.replace(hour=int(h), minute=int(m), second=0, microsecond=0)
        return now >= sched
    except Exception:
        return False


# ── HTML Email template ────────────────────────────────────────────────────────

def build_brief_html(
    ai_text: str,
    market_data: dict,
    portfolio_news: list,
    insider_txns: list,
    earnings: list,
    macro_events: list,
    username: str = "",
) -> str:
    today_label = date.today().strftime("%A, %B %d, %Y")

    # Market snapshot rows
    mkt_rows = ""
    for name, d in market_data.items():
        pct   = d.get("change_pct", 0)
        price = d.get("price", 0)
        color = "#22c55e" if pct >= 0 else "#ef4444"
        arrow = "▲" if pct >= 0 else "▼"
        fmt   = f"${price:,.2f}" if name in ("Gold", "Oil WTI") else \
                f"{price:.2f}%" if "Yield" in name else f"{price:,.2f}"
        mkt_rows += f"""
        <tr>
          <td style="padding:8px 16px;color:#c8d8f0;font-weight:600;font-size:13px;">{name}</td>
          <td style="padding:8px 16px;color:#e8edf8;font-size:13px;text-align:right;">{fmt}</td>
          <td style="padding:8px 16px;color:{color};font-weight:700;font-size:13px;text-align:right;">{arrow} {abs(pct):.2f}%</td>
        </tr>"""

    # Portfolio news rows
    port_news_html = ""
    if portfolio_news:
        for n in portfolio_news[:6]:
            port_news_html += f"""
            <tr>
              <td style="padding:6px 16px;width:60px;">
                <span style="background:rgba(31,119,180,0.2);color:#7eb8e8;font-size:10px;font-weight:700;padding:2px 7px;border-radius:10px;">{n.get('ticker','')}</span>
              </td>
              <td style="padding:6px 16px;">
                <a href="{n.get('url','#')}" style="color:#7eb8e8;text-decoration:none;font-size:13px;">{n.get('title','')}</a>
                <div style="color:#4a6a8a;font-size:11px;margin-top:2px;">{n.get('source','')} · {n.get('date','')}</div>
              </td>
            </tr>"""

    # Insider transactions
    insider_html = ""
    if insider_txns:
        for t in insider_txns[:5]:
            insider_html += f"""
            <tr>
              <td style="padding:6px 16px;color:#7eb8e8;font-weight:700;font-size:12px;">{t.get('ticker','')}</td>
              <td style="padding:6px 16px;color:#c8d8f0;font-size:12px;">{t.get('filer','')}</td>
              <td style="padding:6px 16px;color:#4a6a8a;font-size:12px;">{t.get('date','')}</td>
              <td style="padding:6px 16px;">
                <a href="{t.get('edgar_url','#')}" style="color:#4a90d9;font-size:11px;">View →</a>
              </td>
            </tr>"""
    else:
        insider_html = """<tr><td colspan="4" style="padding:12px 16px;color:#3a5a7a;font-size:12px;text-align:center;">No insider filings in the last 30 days for your holdings.</td></tr>"""

    # Earnings
    earnings_html = ""
    if earnings:
        for e in earnings[:5]:
            earnings_html += f"""
            <tr>
              <td style="padding:6px 16px;color:#7eb8e8;font-weight:700;font-size:13px;">{e.get('ticker','')}</td>
              <td style="padding:6px 16px;color:#c8d8f0;font-size:13px;">{e.get('date','')}</td>
              <td style="padding:6px 16px;color:#4a6a8a;font-size:12px;">{e.get('eps_est') or '—'}</td>
            </tr>"""
    else:
        earnings_html = """<tr><td colspan="3" style="padding:12px 16px;color:#3a5a7a;font-size:12px;text-align:center;">No upcoming earnings found for your holdings.</td></tr>"""

    # Macro events
    macro_html = ""
    for ev in macro_events[:5]:
        macro_html += f"""
        <tr>
          <td style="padding:6px 16px;color:#c8d8f0;font-size:13px;">{ev.get('name','')}</td>
          <td style="padding:6px 16px;color:#4a6a8a;font-size:12px;">{ev.get('date','')}</td>
        </tr>"""

    # AI text — convert basic markdown to HTML
    ai_html = ai_text.replace("\n\n", "</p><p style='margin:8px 0;color:#c8d8f0;font-size:13px;line-height:1.7;'>")
    ai_html = ai_html.replace("\n", "<br>")
    ai_html = ai_html.replace("**", "<strong>").replace("**", "</strong>")

    greeting = f"Good morning{', ' + username if username else ''}!"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Morning Brief — {today_label}</title>
</head>
<body style="margin:0;padding:0;background:#060810;font-family:-apple-system,BlinkMacSystemFont,'Inter',sans-serif;">

  <!-- Wrapper -->
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#060810;padding:32px 16px;">
    <tr><td align="center">
    <table width="640" cellpadding="0" cellspacing="0" style="max-width:640px;width:100%;">

      <!-- Header -->
      <tr><td style="background:linear-gradient(135deg,#0d0f1a 0%,#111520 100%);border:1px solid rgba(31,119,180,0.25);border-radius:16px 16px 0 0;padding:32px 36px;text-align:center;">
        <div style="font-size:28px;font-weight:800;background:linear-gradient(135deg,#e8edf8 30%,#7eb8e8 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:-0.5px;margin-bottom:6px;">
          📊 Morning Brief
        </div>
        <div style="font-size:12px;color:#4a90d9;letter-spacing:2px;font-weight:600;text-transform:uppercase;">{today_label}</div>
        <div style="font-size:13px;color:#4a6a8a;margin-top:8px;">🐵 The Bull Monkey · Powered by Claude AI</div>
        <div style="margin-top:16px;font-size:16px;color:#8aadcc;font-weight:600;">{greeting}</div>
      </td></tr>

      <!-- AI Insights -->
      <tr><td style="background:#0e1018;border-left:1px solid rgba(31,119,180,0.2);border-right:1px solid rgba(31,119,180,0.2);padding:28px 36px;">
        <div style="font-size:10px;font-weight:700;color:#4a6a8a;letter-spacing:2px;text-transform:uppercase;margin-bottom:14px;">🤖 AI Market Intelligence</div>
        <div style="background:linear-gradient(135deg,rgba(31,119,180,0.08),rgba(124,58,237,0.05));border:1px solid rgba(31,119,180,0.18);border-radius:12px;padding:20px 22px;border-left:3px solid #1f77b4;">
          <p style="margin:0;color:#c8d8f0;font-size:13px;line-height:1.7;">{ai_html}</p>
        </div>
      </td></tr>

      <!-- Market Snapshot -->
      <tr><td style="background:#0e1018;border-left:1px solid rgba(31,119,180,0.2);border-right:1px solid rgba(31,119,180,0.2);padding:4px 36px 24px;">
        <div style="font-size:10px;font-weight:700;color:#4a6a8a;letter-spacing:2px;text-transform:uppercase;margin-bottom:12px;">📈 Market Snapshot</div>
        <table width="100%" style="background:rgba(17,21,32,0.8);border:1px solid rgba(31,119,180,0.15);border-radius:10px;overflow:hidden;" cellpadding="0" cellspacing="0">
          {mkt_rows}
        </table>
      </td></tr>

      <!-- Portfolio News -->
      {"" if not portfolio_news else f"""
      <tr><td style="background:#0e1018;border-left:1px solid rgba(31,119,180,0.2);border-right:1px solid rgba(31,119,180,0.2);padding:4px 36px 24px;">
        <div style="font-size:10px;font-weight:700;color:#4a6a8a;letter-spacing:2px;text-transform:uppercase;margin-bottom:12px;">💼 Your Portfolio — Latest News</div>
        <table width="100%" style="background:rgba(17,21,32,0.8);border:1px solid rgba(31,119,180,0.15);border-radius:10px;" cellpadding="0" cellspacing="0">
          {port_news_html}
        </table>
      </td></tr>"""}

      <!-- Insider Transactions -->
      <tr><td style="background:#0e1018;border-left:1px solid rgba(31,119,180,0.2);border-right:1px solid rgba(31,119,180,0.2);padding:4px 36px 24px;">
        <div style="font-size:10px;font-weight:700;color:#4a6a8a;letter-spacing:2px;text-transform:uppercase;margin-bottom:12px;">🏦 Insider Activity (SEC Form 4)</div>
        <table width="100%" style="background:rgba(17,21,32,0.8);border:1px solid rgba(31,119,180,0.15);border-radius:10px;" cellpadding="0" cellspacing="0">
          <tr style="background:rgba(31,119,180,0.1);">
            <th style="padding:8px 16px;color:#4a6a8a;font-size:10px;text-align:left;font-weight:600;">Ticker</th>
            <th style="padding:8px 16px;color:#4a6a8a;font-size:10px;text-align:left;font-weight:600;">Filer</th>
            <th style="padding:8px 16px;color:#4a6a8a;font-size:10px;text-align:left;font-weight:600;">Date</th>
            <th style="padding:8px 16px;color:#4a6a8a;font-size:10px;text-align:left;font-weight:600;">Link</th>
          </tr>
          {insider_html}
        </table>
      </td></tr>

      <!-- Upcoming Earnings -->
      <tr><td style="background:#0e1018;border-left:1px solid rgba(31,119,180,0.2);border-right:1px solid rgba(31,119,180,0.2);padding:4px 36px 24px;">
        <div style="font-size:10px;font-weight:700;color:#4a6a8a;letter-spacing:2px;text-transform:uppercase;margin-bottom:12px;">📅 Upcoming Earnings — Your Portfolio</div>
        <table width="100%" style="background:rgba(17,21,32,0.8);border:1px solid rgba(31,119,180,0.15);border-radius:10px;" cellpadding="0" cellspacing="0">
          <tr style="background:rgba(31,119,180,0.1);">
            <th style="padding:8px 16px;color:#4a6a8a;font-size:10px;text-align:left;font-weight:600;">Ticker</th>
            <th style="padding:8px 16px;color:#4a6a8a;font-size:10px;text-align:left;font-weight:600;">Earnings Date</th>
            <th style="padding:8px 16px;color:#4a6a8a;font-size:10px;text-align:left;font-weight:600;">EPS Est.</th>
          </tr>
          {earnings_html}
        </table>
      </td></tr>

      <!-- Macro Events -->
      {"" if not macro_events else f"""
      <tr><td style="background:#0e1018;border-left:1px solid rgba(31,119,180,0.2);border-right:1px solid rgba(31,119,180,0.2);padding:4px 36px 24px;">
        <div style="font-size:10px;font-weight:700;color:#4a6a8a;letter-spacing:2px;text-transform:uppercase;margin-bottom:12px;">🌐 Macro Events This Week</div>
        <table width="100%" style="background:rgba(17,21,32,0.8);border:1px solid rgba(31,119,180,0.15);border-radius:10px;" cellpadding="0" cellspacing="0">
          {macro_html}
        </table>
      </td></tr>"""}

      <!-- Footer -->
      <tr><td style="background:#080a10;border:1px solid rgba(31,119,180,0.2);border-top:none;border-radius:0 0 16px 16px;padding:20px 36px;text-align:center;">
        <div style="color:#2a3a5a;font-size:11px;">
          The Bull Monkey · Powered by Claude AI &amp; yfinance · © {date.today().year}<br>
          <span style="color:#1a2a4a;">This brief is generated automatically for your account.</span>
        </div>
      </td></tr>

    </table>
    </td></tr>
  </table>
</body>
</html>"""


# ── SMTP sending ───────────────────────────────────────────────────────────────

def send_brief_email(html: str, subject: str = "") -> tuple[bool, str]:
    """
    Send the morning brief email via SMTP.
    Uses Gmail App Password by default.
    Returns (success: bool, error_message: str).
    """
    cfg = get_email_config()
    if not is_email_configured():
        return False, "Email not configured. Go to Settings → Morning Brief."

    if not subject:
        subject = f"📊 Morning Brief — {date.today().strftime('%A, %B %d')}"

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = cfg["smtp_user"]
        msg["To"]      = cfg["to_email"]
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"]) as server:
            server.starttls()
            server.login(cfg["smtp_user"], cfg["smtp_password"])
            server.sendmail(cfg["smtp_user"], cfg["to_email"], msg.as_string())
        return True, ""
    except smtplib.SMTPAuthenticationError:
        return False, "SMTP authentication failed. Check your App Password."
    except smtplib.SMTPException as e:
        return False, f"SMTP error: {e}"
    except Exception as e:
        return False, f"Error: {e}"
