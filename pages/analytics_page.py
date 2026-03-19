import streamlit as st
from utils.database import get_subjects, get_past, _num
from utils.calculations import calc_internals, calc_sgpa, bunk_calc
from utils.charts import (
    sgpa_trend_chart, subject_performance_chart,
    attendance_pie_chart, grade_radar_chart, bunk_budget_chart,
)


def render(u_sem: int, dark: bool = True):
    st.markdown(
        "<div style='margin-top:24px;'>"
        "<h1 style='font-size:2rem;font-weight:900;'>📊 Analytics</h1>"
        "<p style='opacity:.5;'>Visual breakdown of your academic performance</p></div>",
        unsafe_allow_html=True,
    )

    df      = get_subjects(u_sem)
    past_df = get_past()

    if df.empty:
        st.info("No subjects yet. Add subjects from the Dashboard to see analytics.")
        return

    # Build subject data list
    subjects_data = []
    for _, row in df.iterrows():
        _, exact = calc_internals(row)
        cond = int(_num(row["total_classes"]))
        att  = int(_num(row["attended_classes"]))
        plan = int(_num(row["default_total_classes"]) or 10 * _num(row["credits"]))
        pct  = round(att / cond * 100, 1) if cond > 0 else 0.0
        rem, _, _ = bunk_calc(int(_num(row["credits"])), cond, att, 75, plan)
        see = _num(row.get("see_score", -1))
        total = min(exact + (see / 100) * 50, 100) if see >= 0 else min(exact * 2, 100)
        subjects_data.append({
            "name": row["name"],
            "internal": round(exact, 1),
            "attendance": pct,
            "bunks": rem,
            "total": round(total, 1),
            "credits": int(_num(row["credits"])),
        })

    sgpa_val, _ = calc_sgpa(df)

    # ── Row 1: SGPA Trend + Radar ──
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        fig = sgpa_trend_chart(past_df, sgpa_val, u_sem, dark)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        fig = grade_radar_chart(subjects_data, dark)
        if fig:
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Row 2: Subject Performance ──
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    fig = subject_performance_chart(subjects_data, dark)
    if fig:
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Row 3: Attendance Pie + Bunk Budget ──
    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        fig = attendance_pie_chart(subjects_data, dark)
        if fig:
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        fig = bunk_budget_chart(subjects_data, dark)
        if fig:
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Summary Table ──
    st.markdown('<div class="sec-title">Quick Summary</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    import pandas as pd
    tbl = []
    for s in subjects_data:
        att_status = "✅" if s["attendance"] >= 75 else ("⚠️" if s["attendance"] >= 65 else "❌")
        int_status = "✅" if s["internal"] >= 40 else ("⚠️" if s["internal"] >= 25 else "❌")
        tbl.append({
            "Subject":      s["name"],
            "Internal /50": f"{s['internal']} {int_status}",
            "Attendance":   f"{s['attendance']}% {att_status}",
            "Bunks Left":   s["bunks"] if s["bunks"] > 0 else f"⚠️ {abs(s['bunks'])} short",
            "Est. Total":   f"{s['total']}/100",
        })
    st.dataframe(pd.DataFrame(tbl), use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)
