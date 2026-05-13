import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from utils.config import COLOR_PRIMARY, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING

_DARK = dict(
    template="plotly_dark",
    paper_bgcolor="#09090B",   # matches --bg-base
    plot_bgcolor="#09090B",
    font=dict(color="#A1A1AA", family="'Inter', -apple-system, sans-serif", size=11),
    margin=dict(l=48, r=24, t=44, b=36),
    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", zerolinecolor="rgba(255,255,255,0.06)",
               tickfont=dict(family="'JetBrains Mono', monospace", size=10, color="#52525B")),
    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", zerolinecolor="rgba(255,255,255,0.06)",
               tickfont=dict(family="'JetBrains Mono', monospace", size=10, color="#52525B")),
    hoverlabel=dict(bgcolor="#1F1F24", bordercolor="rgba(255,255,255,0.08)",
                    font=dict(family="'Inter', sans-serif", size=12, color="#FAFAFA")),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(255,255,255,0.04)",
                font=dict(size=11, color="#A1A1AA")),
)


def price_chart(hist: pd.DataFrame, ticker: str) -> go.Figure:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.72, 0.28], vertical_spacing=0.03)
    c = hist["Close"]
    # Gradient area fill under price line
    fig.add_trace(go.Scatter(x=hist.index, y=c, mode="lines", name="Price",
        line=dict(color="#6172F3", width=2),
        fill="tozeroy",
        fillcolor="rgba(97,114,243,0.05)"), row=1, col=1)
    for w, col in [(20, "#22C55E"), (50, "#F59E0B"), (200, "#8B5CF6")]:
        if len(c) >= w:
            fig.add_trace(go.Scatter(x=hist.index, y=c.rolling(w).mean(), mode="lines",
                name=f"MA{w}", line=dict(color=col, width=1.5, dash="dot")), row=1, col=1)
    vol_col = [COLOR_SUCCESS if c2 >= o else COLOR_DANGER
               for c2, o in zip(hist["Close"], hist["Open"])]
    fig.add_trace(go.Bar(x=hist.index, y=hist["Volume"], name="Volume",
        marker_color=vol_col, opacity=0.7), row=2, col=1)
    fig.update_layout(**_DARK, title=f"{ticker} — Price & Volume",
        yaxis_title="Price ($)", yaxis2_title="Volume", height=560,
        hovermode="x unified",
        legend=dict(orientation="h", y=1.02, x=1, xanchor="right", yanchor="bottom"))
    return fig


def candlestick_chart(hist: pd.DataFrame, ticker: str) -> go.Figure:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.72, 0.28], vertical_spacing=0.03)
    fig.add_trace(go.Candlestick(x=hist.index,
        open=hist["Open"], high=hist["High"], low=hist["Low"], close=hist["Close"],
        name=ticker, increasing_line_color=COLOR_SUCCESS, decreasing_line_color=COLOR_DANGER),
        row=1, col=1)
    vol_col = [COLOR_SUCCESS if c >= o else COLOR_DANGER
               for c, o in zip(hist["Close"], hist["Open"])]
    fig.add_trace(go.Bar(x=hist.index, y=hist["Volume"], name="Volume",
        marker_color=vol_col, opacity=0.7), row=2, col=1)
    fig.update_layout(**_DARK, title=f"{ticker} — Candlestick", height=560,
        hovermode="x unified", xaxis_rangeslider_visible=False)
    return fig


def screener_bar(df) -> go.Figure:
    colors = [COLOR_SUCCESS if t == 1 else COLOR_WARNING if t == 2 else COLOR_DANGER
              for t in df["tier"]]
    fig = go.Figure(go.Bar(x=df["ticker"], y=df["composite"],
        marker_color=colors,
        text=[f"{v:.1f}" for v in df["composite"]], textposition="outside"))
    fig.update_layout(**_DARK, title="Composite Score Ranking",
        yaxis_title="Score (0–10)", yaxis_range=[0, 11], height=380)
    return fig


def radar_chart(df, top_n: int = 5) -> go.Figure:
    cats = ["Valuation", "Growth", "Quality", "Technical", "Momentum", "Sentiment"]
    keys = ["valuation", "growth", "quality", "technical", "momentum", "sentiment"]
    palette = [COLOR_PRIMARY, COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER, "#9467bd", "#17becf"]
    fig = go.Figure()
    for i, (_, row) in enumerate(df.head(top_n).iterrows()):
        vals = [row[k] for k in keys] + [row[keys[0]]]
        fig.add_trace(go.Scatterpolar(r=vals, theta=cats + [cats[0]],
            fill="toself", name=row["ticker"],
            line=dict(color=palette[i % len(palette)]), opacity=0.75))
    fig.update_layout(**_DARK, title="Score Breakdown — Top 5",
        polar=dict(bgcolor="#111", radialaxis=dict(visible=True, range=[0, 10], color="#888"),
                   angularaxis=dict(color="#888")), height=430)
    return fig


def sector_bar(sector_returns: dict) -> go.Figure:
    items = sorted(sector_returns.items(), key=lambda x: x[1], reverse=True)
    sectors = [x[0] for x in items]
    returns = [x[1] for x in items]
    colors  = [COLOR_SUCCESS if r >= 0 else COLOR_DANGER for r in returns]
    fig = go.Figure(go.Bar(x=returns, y=sectors, orientation="h",
        marker_color=colors, text=[f"{r:+.1f}%" for r in returns], textposition="outside"))
    fig.update_layout(**{**_DARK, "margin": dict(l=160, r=60, t=50, b=40)},
        title="Sector Returns", xaxis_title="Return (%)", height=430)
    return fig


def multi_line(data: dict, title: str, normalize: bool = False, height: int = 420) -> go.Figure:
    palette = [COLOR_PRIMARY, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING,
               "#9467bd", "#17becf", "#e377c2", "#bcbd22"]
    fig = go.Figure()
    for i, (name, hist) in enumerate(data.items()):
        y = hist["Close"]
        if normalize and len(y):
            y = y / y.iloc[0] * 100
        fig.add_trace(go.Scatter(x=hist.index, y=y, mode="lines", name=name,
            line=dict(color=palette[i % len(palette)], width=2)))
    fig.update_layout(**_DARK, title=title, height=height,
        yaxis_title="Indexed (100 = start)" if normalize else "Price ($)",
        hovermode="x unified")
    return fig


def correlation_heatmap(corr: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Heatmap(z=corr.values, x=corr.columns, y=corr.index,
        colorscale="RdYlGn", zmin=-1, zmax=1,
        text=corr.round(2).values, texttemplate="%{text}",
        colorbar=dict(title="Corr")))
    fig.update_layout(**_DARK, title="Return Correlation Heatmap", height=380)
    return fig


def portfolio_pie(holdings: list) -> go.Figure:
    labels = [h["ticker"] for h in holdings]
    values = [h.get("current_value", 0) for h in holdings]
    fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.42,
        textinfo="label+percent",
        marker=dict(line=dict(color="#0a0a0a", width=2))))
    fig.update_layout(**_DARK, title="Portfolio Allocation", height=400)
    return fig


def financials_bar(data_dict: dict, title: str) -> go.Figure:
    palette = [COLOR_PRIMARY, COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER]
    fig = go.Figure()
    for i, (label, vals) in enumerate(data_dict.items()):
        fig.add_trace(go.Bar(name=label, x=list(vals.keys()),
            y=[v / 1e9 if abs(v) > 1e6 else v for v in vals.values()],
            marker_color=palette[i % len(palette)]))
    fig.update_layout(**_DARK, title=title, yaxis_title="$ Billions",
        barmode="group", height=360)
    return fig


def scatter_peer(df, x_col: str, y_col: str, size_col: str, label_col: str) -> go.Figure:
    sizes = df[size_col].fillna(0)
    sizes = (sizes / sizes.max() * 40 + 8) if sizes.max() > 0 else [12] * len(df)
    fig = go.Figure(go.Scatter(
        x=df[x_col], y=df[y_col], mode="markers+text",
        text=df[label_col], textposition="top center",
        marker=dict(size=list(sizes), color=COLOR_PRIMARY, opacity=0.8,
                    line=dict(color="white", width=1)),
        hovertemplate=f"<b>%{{text}}</b><br>{x_col}: %{{x:.2f}}<br>{y_col}: %{{y:.2f}}<extra></extra>"))
    fig.update_layout(**_DARK, title=f"{y_col} vs {x_col}",
        xaxis_title=x_col, yaxis_title=y_col, height=440)
    return fig


def backtest_chart(dates, portfolio_vals: list, benchmark_vals: list, ticker: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=portfolio_vals, mode="lines", name="Strategy",
        line=dict(color=COLOR_SUCCESS, width=2)))
    fig.add_trace(go.Scatter(x=dates, y=benchmark_vals, mode="lines", name="Buy & Hold",
        line=dict(color=COLOR_PRIMARY, width=2, dash="dot")))
    fig.update_layout(**_DARK, title=f"Strategy vs Buy & Hold — {ticker}",
        yaxis_title="Portfolio Value ($)", hovermode="x unified", height=420)
    return fig


def sparkline(series: list, color: str = COLOR_PRIMARY, height: int = 55) -> go.Figure:
    """Tiny inline line chart with no axes."""
    if not series or len(series) < 2:
        return go.Figure()
    y = series
    up = y[-1] >= y[0]
    c  = COLOR_SUCCESS if up else COLOR_DANGER
    rgb = (34, 197, 94) if up else (239, 68, 68)
    fig = go.Figure(go.Scatter(
        x=list(range(len(y))), y=y, mode="lines",
        line=dict(color=c, width=2),
        fill="tozeroy",
        fillcolor=f"rgba({rgb[0]},{rgb[1]},{rgb[2]},0.08)",
    ))
    fig.update_layout(
        height=height, margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False, fixedrange=True),
        yaxis=dict(visible=False, fixedrange=True),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )
    return fig


def portfolio_history_chart(df: pd.DataFrame) -> go.Figure:
    """Line chart of portfolio value over time."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["value"],
        mode="lines", name="Portfolio Value",
        line=dict(color=COLOR_PRIMARY, width=2.5),
        fill="tozeroy",
        fillcolor="rgba(31,119,180,0.08)",
        hovertemplate="<b>%{x|%b %d, %Y}</b><br>$%{y:,.2f}<extra></extra>",
    ))
    # Mark all-time high
    if len(df) > 1:
        ath_idx = df["value"].idxmax()
        fig.add_trace(go.Scatter(
            x=[df.loc[ath_idx, "date"]], y=[df.loc[ath_idx, "value"]],
            mode="markers", name="All-Time High",
            marker=dict(color=COLOR_SUCCESS, size=10, symbol="star"),
            hovertemplate="<b>ATH</b><br>$%{y:,.2f}<extra></extra>",
        ))
    fig.update_layout(
        **_DARK, title="Portfolio Value Over Time",
        yaxis_title="Total Value ($)",
        hovermode="x unified", height=380,
    )
    return fig
