import math
import streamlit as st
import pandas as pd
import sqlite3
from utils.database import (
    DB_NAME, save_marks, save_weights, save_attendance,
    update_planned_classes, delete_subject, get_subject_by_id, _num,
)
from utils.calculations import (
    internal_from_values, GRADE_CUTOFFS, GP_MAP,
    required_see, required_cie, bunk_calc,
)


def render():
    if st.button("← Back"):
        st.session_state.page = "dashboard"
        st.rerun()

    sid = st.session_state.sub_id
    row = get_subject_by_id(sid)

    st.markdown(
        f"<div style='margin-top:16px;'>"
        f"<h1 style='font-size:1.8rem;font-weight:900;margin:0'>{row['name']}</h1>"
        f"<p style='opacity:.45;margin:4px 0 20px;'>"
        f"{int(row['credits'])} Credits · Semester {int(row['semester'])}</p></div>",
        unsafe_allow_html=True,
    )

    t1, t2, t3 = st.tabs(["📊 Marks & Predict", "📅 Attendance", "⚙️ Settings"])

    # ── MARKS ─────────────────────────────────────────────────────────────────
    with t1:
        st.markdown('<div class="glass" style="margin-top:12px;">', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        cie1 = c1.number_input("CIE 1 (/40)", 0, 40, int(row["cie1"]))
        cie2 = c2.number_input("CIE 2 (/40)", 0, 40, int(row["cie2"]))
        cie3 = c3.number_input("CIE 3 (/40)", 0, 40, int(row["cie3"]))

        c4, c5, c6 = st.columns(3)
        q = c4.number_input("Quiz Score", 0.0, 100.0, float(row["quiz_score"]))
        a = c5.number_input("AAT Score",  0.0, 100.0, float(row["aat_score"]))
        l = c6.number_input("Lab Score",  0.0, 100.0, float(row["lab_score"]))

        c7, c8, c9 = st.columns(3)
        qm = c7.number_input("Quiz Max", 1.0, 100.0, float(row["quiz_max"] or 10))
        am = c8.number_input("AAT Max",  1.0, 100.0, float(row["aat_max"]  or 10))
        lm = c9.number_input("Lab Max",  1.0, 100.0, float(row["lab_max"]  or 25))

        e1, e2 = st.columns(2)
        ex = e1.number_input("Extra Score", 0.0, 100.0, float(row["extra_score"]))
        em = e2.number_input("Extra Max",   1.0, 100.0, float(row["extra_max"] or 50))

        if st.button("💾 Save Marks", use_container_width=True):
            save_marks(sid, (cie1, cie2, cie3, q, a, l, qm, am, lm, ex, em, sid))
            # Re-fetch weights so we don't overwrite them
            fresh = get_subject_by_id(sid)
            save_weights(sid, fresh["cie_weight"], fresh["lab_weight"],
                         fresh["quiz_weight"], fresh["aat_weight"],
                         fresh["extra_weight"], ex, em)
            st.success("✅ Marks saved!")
            st.rerun()

        cm, exact = internal_from_values(
            cie1, cie2, cie3, q, a, l, ex, qm, am, lm, em,
            row["cie_max"], row["cie_weight"], row["lab_weight"],
            row["quiz_weight"], row["aat_weight"], row["extra_weight"],
        )
        st.progress(cm / 50)
        mc = "#1db954" if cm >= 40 else ("#ffa726" if cm >= 25 else "#ff5252")
        st.markdown(
            f"<h3 style='text-align:center;color:{mc}'>{cm}/50 "
            f"<span style='font-size:.6em;opacity:.5'>({exact:.1f} exact)</span></h3>",
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown("### 🎯 Grade Prediction")
        cA, cB = st.columns(2)
        gr   = cA.selectbox("Target Grade", list(GRADE_CUTOFFS.keys()))
        see  = cB.number_input("Assumed SEE /100", 0, 100, 90)
        mode = st.selectbox(
            "Plan for CIE",
            ["none", "cie1", "cie2", "cie3", "cie2_3_equal", "all_equal"],
            format_func=lambda x: x.upper().replace("_", " "),
        )
        if mode != "none":
            rq = required_cie(row, cie1, cie2, cie3, q, a, l, ex, qm, am, lm, em,
                              see, GRADE_CUTOFFS[gr], mode)
            if rq is None:
                st.error("❌ Impossible with current weights.")
            else:
                st.success(f"✅ Need **{rq}/40** in selected CIE(s) for **{gr}**.")

        st.markdown("#### SEE Score Required per Grade")
        tbl = []
        for g, cut in GRADE_CUTOFFS.items():
            r = required_see(exact, cut)
            tbl.append([g, GP_MAP.get(g, 0), cut, f"{r}/100" if r is not None else "❌ Impossible"])
        st.table(pd.DataFrame(tbl, columns=["Grade", "GP", "Min Total", "Required SEE"]))
        st.markdown("</div>", unsafe_allow_html=True)

    # ── ATTENDANCE ────────────────────────────────────────────────────────────
    with t2:
        st.markdown('<div class="glass" style="margin-top:12px;">', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        cond = c1.number_input("Classes Conducted", 0, 500, int(row["total_classes"]))
        att  = c2.number_input("Classes Attended",  0, 500, int(row["attended_classes"]))
        c3, c4 = st.columns(2)
        plan = c3.number_input(
            "Planned Total", 0, 500,
            int(row["default_total_classes"] or 10 * row["credits"])
        )
        targ = c4.selectbox("Target %", [85, 75, 65], index=1)

        if att > cond:
            st.error("⚠️ Attended classes cannot exceed conducted!")
        else:
            if st.button("💾 Save Attendance", use_container_width=True):
                save_attendance(sid, att, cond)
                update_planned_classes(sid, plan)
                st.success("✅ Saved!")
                st.rerun()

            rem, cur, fin = bunk_calc(row["credits"], cond, att, targ, plan)
            ac = "#1db954" if cur >= 75 else "#ff5252"
            st.markdown(
                f"<h3 style='text-align:center;color:{ac}'>{cur}% Current</h3>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<p style='text-align:center;opacity:.5'>Projected final: {fin}%</p>",
                unsafe_allow_html=True,
            )

            bw = min(cur, 100)
            st.markdown(
                f'<div style="background:rgba(255,255,255,.06);border-radius:100px;'
                f'height:8px;margin:12px 0;overflow:hidden;">'
                f'<div style="width:{bw}%;height:100%;background:{ac};border-radius:100px;"></div>'
                f"</div>",
                unsafe_allow_html=True,
            )

            if rem < 0:
                st.error(f"❌ Need **{abs(rem)}** more classes to reach {targ}%.")
            else:
                st.success(f"✅ Can bunk **{rem}** more classes and stay above {targ}%.")

            if cur < targ:
                needed = math.ceil((targ / 100 * plan) - att)
                st.warning(f"⚡ Attend **{needed}** more of the remaining classes to recover.")

        st.markdown("</div>", unsafe_allow_html=True)

    # ── SETTINGS ──────────────────────────────────────────────────────────────
    with t3:
        st.markdown('<div class="glass" style="margin-top:12px;">', unsafe_allow_html=True)
        st.markdown("### ⚖️ Component Weights (must total 50)")

        cols = st.columns(5)
        cw = cols[0].number_input("CIE",   0.0, 50.0, float(row["cie_weight"]))
        lw = cols[1].number_input("Lab",   0.0, 50.0, float(row["lab_weight"]))
        qw = cols[2].number_input("Quiz",  0.0, 50.0, float(row["quiz_weight"]))
        aw = cols[3].number_input("AAT",   0.0, 50.0, float(row["aat_weight"]))
        ew = cols[4].number_input("Extra", 0.0, 50.0, float(row["extra_weight"]))

        tw = cw + lw + qw + aw + ew
        wc = "#1db954" if abs(tw - 50) < 0.1 else "#ff5252"
        st.markdown(f"<p style='color:{wc};font-weight:700;'>Total: {tw} / 50</p>", unsafe_allow_html=True)

        if abs(tw - 50) > 0.1:
            st.error("❌ Weights must sum to exactly 50.")
        else:
            if st.button("💾 Save Weights", use_container_width=True):
                save_weights(sid, cw, lw, qw, aw, ew, row["extra_score"], row["extra_max"])
                st.success("✅ Weights saved!")
                st.rerun()

        st.markdown("---")
        st.markdown("### ⚠️ Danger Zone")
        if st.button("🗑️ Delete This Subject", type="primary"):
            delete_subject(sid)
            st.session_state.page = "dashboard"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
