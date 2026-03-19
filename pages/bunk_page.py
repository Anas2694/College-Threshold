import streamlit as st
import pandas as pd
from utils.database import get_subjects, _num
from utils.calculations import bunk_calc


def render(u_sem):
    st.markdown(
        "<div style='margin-top:24px;'>"
        "<h1 style='font-size:2rem;font-weight:900;'>🚫 Bunk Planner</h1>"
        "<p style='opacity:.5;'>Smart attendance management across all subjects</p></div>",
        unsafe_allow_html=True,
    )

    df = get_subjects(u_sem)
    if df.empty:
        st.info("No subjects yet. Add subjects from the Dashboard.")
        return

    target = st.select_slider("Target Attendance %", [65, 75, 85], value=75)
    st.markdown("<br>", unsafe_allow_html=True)

    bunk_data = []
    for _, row in df.iterrows():
        cond  = int(_num(row["total_classes"]))
        att   = int(_num(row["attended_classes"]))
        plan  = int(_num(row["default_total_classes"]) or 10 * _num(row["credits"]))
        cred  = int(_num(row["credits"]))
        rem, cur, fin = bunk_calc(cred, cond, att, target, plan)
        bunk_data.append({
            "name": row["name"], "credits": cred, "conducted": cond,
            "attended": att, "planned": plan, "cur": cur, "fin": fin, "bunks": rem,
        })

    safe  = [b for b in bunk_data if b["bunks"] > 0]
    risk  = [b for b in bunk_data if b["bunks"] <= 0]
    total_b = sum(b["bunks"] for b in safe)

    st.markdown(
        f"<div style='display:flex;gap:12px;flex-wrap:wrap;margin-bottom:20px;'>"
        f"<span class='pill pill-green'>✅ {len(safe)} subjects safe</span>"
        f"<span class='pill pill-red'>⚠️ {len(risk)} at risk</span>"
        f"<span class='pill pill-blue'>🚫 {total_b} bunks available</span></div>",
        unsafe_allow_html=True,
    )

    # ── Per-subject cards ──
    bc = st.columns(2)
    for i, b in enumerate(sorted(bunk_data, key=lambda x: x["bunks"])):
        with bc[i % 2]:
            safe_b = b["bunks"] > 0
            bg  = "rgba(29,185,84,.08)"  if safe_b else "rgba(255,82,82,.08)"
            bd  = "rgba(29,185,84,.3)"   if safe_b else "rgba(255,82,82,.3)"
            pc  = "#1db954" if b["cur"] >= 75 else "#ff5252"
            bw  = min(b["cur"], 100)
            msg = f"🚫 Bunk {b['bunks']} more" if safe_b else f"⚠️ Need {abs(b['bunks'])} more classes"
            mc  = "#1db954" if safe_b else "#ff5252"

            st.markdown(
                f'<div class="glass" style="background:{bg};border-color:{bd};padding:18px;">'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:10px;">'
                f'<div><div style="font-weight:700;">{b["name"]}</div>'
                f'<div style="font-size:.7rem;opacity:.45;">{b["credits"]} Credits · {b["conducted"]} held</div></div>'
                f'<div style="text-align:right;">'
                f'<div style="font-size:1.6rem;font-weight:800;color:{pc};line-height:1;">{b["cur"]}%</div>'
                f'<div style="font-size:.65rem;opacity:.5;">Current</div></div></div>'
                f'<div style="background:rgba(255,255,255,.06);border-radius:100px;height:6px;'
                f'margin-bottom:10px;overflow:hidden;">'
                f'<div style="width:{bw}%;height:100%;background:{pc};border-radius:100px;"></div></div>'
                f'<div style="display:flex;justify-content:space-between;font-size:.8rem;">'
                f'<span style="opacity:.55;">{b["attended"]}/{b["planned"]} planned</span>'
                f'<span style="font-weight:700;color:{mc}">{msg}</span>'
                f"</div></div>",
                unsafe_allow_html=True,
            )

    # ── Bunk Day Simulator ──
    st.markdown('<div class="sec-title" style="margin-top:24px;">Bunk Day Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("**If I bunk X days — which subjects go below target?**")

    cpd  = st.slider("Classes per day", 1, 8, 4)
    bd_  = st.slider("Days to bunk",    1, 20, 1)
    miss = cpd * bd_
    st.markdown(
        f"<p style='opacity:.5;font-size:.83rem;'>{miss} classes missed per subject</p>",
        unsafe_allow_html=True,
    )

    sim = []
    for b in bunk_data:
        na  = max(0, b["attended"] - miss)
        np_ = round((na / b["planned"] * 100) if b["planned"] > 0 else 0, 1)
        sim.append({
            "Subject":      b["name"],
            "Current %":    f"{b['cur']}%",
            "After Bunk %": f"{np_}%",
            "Status":       "✅ Safe" if np_ >= target else "❌ Below Target",
        })
    st.dataframe(pd.DataFrame(sim), use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)
