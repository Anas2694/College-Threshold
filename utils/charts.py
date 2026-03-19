"""
Chart generation using Plotly — dark/light theme aware.
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


# ── THEME HELPERS ─────────────────────────────────────────────────────────────
def _base_layout(dark: bool, title: str = "") -> dict:
    bg   = "rgba(0,0,0,0)"
    grid = "rgba(255,255,255,0.06)" if dark else "rgba(0,0,0,0.06)"
    text = "#ffffff" if dark else "#111111"
    return dict(
        title=dict(text=title, font=dict(size=14, color=text)),
        paper_bgcolor=bg,
        plot_bgcolor=bg,
        font=dict(family="Inter", color=text),
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(gridcolor=grid, showgrid=True, zeroline=False),
        yaxis=dict(gridcolor=grid, showgrid=True, zeroline=False),
    )


GREEN  = "#1db954"
BLUE   = "#7c8ff5"
ORANGE = "#ffa726"
RED    = "#ff5252"
PURPLE = "#b39ddb"


# ── SGPA TREND ────────────────────────────────────────────────────────────────
def sgpa_trend_chart(past_df: pd.DataFrame, current_sgpa: float, current_sem: int, dark: bool = True):
    """Line chart of SGPA per semester."""
    sems, sgpas = [], []

    if not past_df.empty:
        for sn in sorted(past_df["semester"].unique()):
            sd = past_df[past_df["semester"] == sn]
            tc = sd["credits"].astype(float).sum()
            tg = (sd["credits"].astype(float) * sd["grade_points"].astype(float)).sum()
            sems.append(int(sn))
            sgpas.append(round(tg / tc, 2) if tc > 0 else 0.0)

    sems.append(current_sem)
    sgpas.append(current_sgpa)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sems, y=sgpas,
        mode="lines+markers+text",
        text=[str(s) for s in sgpas],
        textposition="top center",
        line=dict(color=BLUE, width=3),
        marker=dict(size=10, color=BLUE, line=dict(color="white", width=2)),
        fill="tozeroy",
        fillcolor="rgba(124,143,245,0.08)",
        name="SGPA",
    ))
    fig.add_hline(y=8, line_dash="dot", line_color=GREEN,
                  annotation_text="Distinction (8+)", annotation_position="right")
    fig.add_hline(y=6, line_dash="dot", line_color=ORANGE,
                  annotation_text="Pass (6+)", annotation_position="right")

    layout = _base_layout(dark, "SGPA Trend")
    layout["xaxis"].update(tickvals=sems, ticktext=[f"Sem {s}" for s in sems])
    layout["yaxis"].update(range=[0, 10.5])
    fig.update_layout(**layout)
    return fig


# ── SUBJECT PERFORMANCE ───────────────────────────────────────────────────────
def subject_performance_chart(subjects: list[dict], dark: bool = True):
    """
    subjects = [{'name': str, 'internal': float, 'attendance': float}, ...]
    Grouped bar chart.
    """
    if not subjects:
        return None

    names     = [s["name"] for s in subjects]
    internals = [s["internal"] for s in subjects]
    attends   = [s["attendance"] for s in subjects]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Internal /50",
        x=names, y=internals,
        marker_color=BLUE,
        text=[f"{v}/50" for v in internals],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        name="Attendance %",
        x=names, y=attends,
        marker_color=GREEN,
        text=[f"{v}%" for v in attends],
        textposition="outside",
    ))

    layout = _base_layout(dark, "Subject Performance Overview")
    layout["barmode"] = "group"
    layout["yaxis"].update(range=[0, 110])
    layout["legend"] = dict(orientation="h", y=1.1)
    fig.update_layout(**layout)
    return fig


# ── ATTENDANCE PIE ────────────────────────────────────────────────────────────
def attendance_pie_chart(subjects: list[dict], dark: bool = True):
    """Donut chart of per-subject attendance."""
    if not subjects:
        return None

    names  = [s["name"] for s in subjects]
    values = [max(s["attendance"], 0) for s in subjects]
    colors = [GREEN if v >= 75 else (ORANGE if v >= 65 else RED) for v in values]

    fig = go.Figure(go.Pie(
        labels=names, values=values,
        hole=0.55,
        marker=dict(colors=colors, line=dict(color="rgba(0,0,0,0)", width=2)),
        textinfo="label+percent",
        textfont_size=12,
    ))
    layout = _base_layout(dark, "Attendance Distribution")
    layout.pop("xaxis", None); layout.pop("yaxis", None)
    fig.update_layout(**layout)
    return fig


# ── GRADE RADAR ───────────────────────────────────────────────────────────────
def grade_radar_chart(subjects: list[dict], dark: bool = True):
    """Radar/spider chart of subject marks (scaled 0-100)."""
    if not subjects:
        return None

    names  = [s["name"] for s in subjects]
    totals = [min(s.get("total", s["internal"] * 2), 100) for s in subjects]
    names_closed  = names + [names[0]]
    totals_closed = totals + [totals[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=totals_closed, theta=names_closed,
        fill="toself",
        line=dict(color=BLUE, width=2),
        fillcolor="rgba(124,143,245,0.15)",
        name="Performance",
    ))
    # Reference rings
    for cutoff, label, color in [(90, "O", "#ffd700"), (70, "A", GREEN), (50, "C", ORANGE)]:
        fig.add_trace(go.Scatterpolar(
            r=[cutoff] * len(names_closed), theta=names_closed,
            mode="lines",
            line=dict(color=color, width=1, dash="dot"),
            name=label,
            showlegend=True,
        ))

    text_col = "white" if dark else "#111"
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(range=[0, 100], visible=True,
                            gridcolor="rgba(255,255,255,0.1)" if dark else "rgba(0,0,0,0.1)",
                            tickfont=dict(color=text_col)),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.1)" if dark else "rgba(0,0,0,0.1)",
                             tickfont=dict(color=text_col)),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color=text_col),
        title=dict(text="Grade Radar", font=dict(size=14, color=text_col)),
        margin=dict(l=30, r=30, t=50, b=30),
        legend=dict(orientation="h", y=-0.1),
    )
    return fig


# ── CIE PROGRESS ─────────────────────────────────────────────────────────────
def cie_progress_chart(cie1: float, cie2: float, cie3: float, cie_max: float = 40, dark: bool = True):
    """Bar chart showing CIE scores with best-two highlighted."""
    scores = [cie1, cie2, cie3]
    sorted_idx = sorted(range(3), key=lambda i: scores[i], reverse=True)
    colors = [GREEN if i in sorted_idx[:2] else BLUE for i in range(3)]

    fig = go.Figure(go.Bar(
        x=["CIE 1", "CIE 2", "CIE 3"],
        y=scores,
        marker_color=colors,
        text=[f"{s}/{cie_max:.0f}" for s in scores],
        textposition="outside",
    ))
    fig.add_hline(y=cie_max * 0.6, line_dash="dot", line_color=ORANGE,
                  annotation_text="60% threshold")

    layout = _base_layout(dark, "CIE Scores (green = best two used)")
    layout["yaxis"].update(range=[0, cie_max * 1.2])
    fig.update_layout(**layout)
    return fig


# ── BUNK BUDGET ───────────────────────────────────────────────────────────────
def bunk_budget_chart(subjects: list[dict], dark: bool = True):
    """Horizontal bar chart of bunk budgets per subject."""
    if not subjects:
        return None

    names  = [s["name"]  for s in subjects]
    bunks  = [s["bunks"] for s in subjects]
    colors = [GREEN if b > 5 else (ORANGE if b > 0 else RED) for b in bunks]

    fig = go.Figure(go.Bar(
        x=bunks, y=names,
        orientation="h",
        marker_color=colors,
        text=[f"{b} bunks" for b in bunks],
        textposition="outside",
    ))
    fig.add_vline(x=0, line_color="rgba(255,255,255,0.3)")

    layout = _base_layout(dark, "Bunk Budget per Subject")
    layout["xaxis"].update(title="Classes you can miss")
    fig.update_layout(**layout)
    return fig
