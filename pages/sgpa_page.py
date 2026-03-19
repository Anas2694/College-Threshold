import streamlit as st
import pandas as pd
from utils.database import (
    get_subjects, get_past, save_see,
    add_past_grade, delete_past_grade, _num,
)
from utils.calculations import calc_sgpa, calc_cgpa


def render(u_sem):
    st.markdown(
        "<div style='margin-top:24px;'>"
        "<h1 style='font-size:2rem;font-weight:900;'>📈 SGPA & CGPA Tracker</h1></div>",
        unsafe_allow_html=True,
    )

    df      = get_subjects(u_sem)
    past_df = get_past()

    t1, t2, t3 = st.tabs(["📊 Current Semester", "🗂️ Past Semesters", "🧮 What-If Calculator"])

    # ── Current Semester ──────────────────────────────────────────────────────
    with t1:
        st.markdown('<div class="glass" style="margin-top:16px;">', unsafe_allow_html=True)
        st.markdown("### Enter SEE Scores")
        st.markdown(
            "<p style='opacity:.5;font-size:.82rem'>"
            "Set SEE to -1 if exam not yet taken — marks will be estimated from internals × 2.</p>",
            unsafe_allow_html=True,
        )

        if df.empty:
            st.info("Add subjects from the Dashboard first.")
        else:
            for _, row in df.iterrows():
                sid   = int(row["id"])
                see_v = _num(row.get("see_score", -1))
                rc1, rc2, rc3 = st.columns([3, 2, 1])
                rc1.markdown(f"**{row['name']}** ({int(row['credits'])} cr)")
                new_see = rc2.number_input(
                    "SEE /100", -1.0, 100.0,
                    float(see_v) if see_v >= 0 else -1.0,
                    key=f"see_{sid}",
                )
                if rc3.button("Save", key=f"ss_{sid}"):
                    save_see(sid, new_see)
                    st.rerun()

            st.markdown("---")
            sgpa_val, sgpa_rows = calc_sgpa(df)
            s_col = "#1db954" if sgpa_val >= 8 else ("#ffa726" if sgpa_val >= 6 else "#ff5252")
            st.markdown(
                f"<div style='text-align:center;padding:20px 0;'>"
                f"<div class='cgpa-big' style='color:{s_col}'>{sgpa_val}</div>"
                f"<div class='cgpa-label'>Estimated SGPA · Semester {u_sem}</div></div>",
                unsafe_allow_html=True,
            )

            tbl = [
                {
                    "Subject":  r["subject"],
                    "Credits":  r["credits"],
                    "Internal": f"{r['internal']}/50",
                    "SEE":      f"{int(r['see'])}/100" if r["see"] >= 0 else "Est.",
                    "Total":    r["total"],
                    "Grade":    r["grade"],
                    "GP":       r["gp"],
                }
                for r in sgpa_rows
            ]
            st.dataframe(pd.DataFrame(tbl), use_container_width=True, hide_index=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Past Semesters ────────────────────────────────────────────────────────
    with t2:
        st.markdown('<div class="glass" style="margin-top:16px;">', unsafe_allow_html=True)
        st.markdown("### Past Semester Grades")

        if not past_df.empty:
            for sn in sorted(past_df["semester"].unique()):
                sd = past_df[past_df["semester"] == sn]
                tc = sd.apply(lambda r: _num(r["credits"]), axis=1).sum()
                tg = sd.apply(lambda r: _num(r["credits"]) * _num(r["grade_points"]), axis=1).sum()
                sg = round(tg / tc, 2) if tc > 0 else 0
                sc = "#1db954" if sg >= 8 else ("#ffa726" if sg >= 6 else "#ff5252")

                st.markdown(
                    f"<div style='display:flex;justify-content:space-between;margin:14px 0 6px;'>"
                    f"<b>Semester {int(sn)}</b>"
                    f"<span style='color:{sc};font-weight:800;'>SGPA: {sg}</span></div>",
                    unsafe_allow_html=True,
                )
                for _, gr in sd.iterrows():
                    dc = st.columns([3, 1, 1, 1, 1])
                    dc[0].write(gr["subject_name"])
                    dc[1].write(f"{int(gr['credits'])} cr")
                    dc[2].write(gr["grade"])
                    dc[3].write(f"GP: {gr['grade_points']}")
                    if dc[4].button("🗑️", key=f"dpg_{gr['id']}"):
                        delete_past_grade(int(gr["id"]))
                        st.rerun()
                st.markdown("<hr style='opacity:.1'>", unsafe_allow_html=True)

            tc2 = past_df.apply(lambda r: _num(r["credits"]), axis=1).sum()
            tg2 = past_df.apply(lambda r: _num(r["credits"]) * _num(r["grade_points"]), axis=1).sum()
            cgpa = round(tg2 / tc2, 2) if tc2 > 0 else 0
            cc   = "#1db954" if cgpa >= 8 else ("#ffa726" if cgpa >= 6 else "#ff5252")
            st.markdown(
                f"<div style='text-align:center;padding:20px;"
                f"background:rgba(29,185,84,.08);border-radius:16px;margin-top:12px;'>"
                f"<div class='cgpa-big' style='color:{cc}'>{cgpa}</div>"
                f"<div class='cgpa-label'>Overall CGPA (Past Semesters)</div></div>",
                unsafe_allow_html=True,
            )
        else:
            st.info("No past data yet. Add grades below.")

        st.markdown("---")
        st.markdown("### ➕ Add Past Grade")
        sem_opts = list(range(1, u_sem)) if u_sem > 1 else [1]
        with st.form("add_pg"):
            p1, p2, p3, p4 = st.columns(4)
            ps  = p1.selectbox("Semester", sem_opts)
            pn  = p2.text_input("Subject Name")
            pc  = p3.selectbox("Credits", [4, 3, 2, 1])
            pg_ = p4.selectbox("Grade", ["O", "A+", "A", "B+", "B", "C", "P", "F"])
            if st.form_submit_button("Add Grade", use_container_width=True) and pn:
                add_past_grade(ps, pn, pc, pg_)
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # ── What-If Calculator ────────────────────────────────────────────────────
    with t3:
        st.markdown('<div class="glass" style="margin-top:16px;">', unsafe_allow_html=True)
        st.markdown("### 🧮 What-If CGPA Calculator")
        st.markdown(
            "<p style='opacity:.5;font-size:.82rem'>"
            "Simulate your CGPA with a hypothetical current semester SGPA.</p>",
            unsafe_allow_html=True,
        )

        tpc = past_df.apply(lambda r: _num(r["credits"]), axis=1).sum() if not past_df.empty else 0
        tpg = past_df.apply(lambda r: _num(r["credits"]) * _num(r["grade_points"]), axis=1).sum() if not past_df.empty else 0
        st.markdown(f"Past semesters: **{tpc:.0f} credits** locked in.")

        hyp_s = st.slider("Hypothetical SGPA this semester", 0.0, 10.0, 8.0, 0.1)
        hyp_c = st.slider("Credits this semester", 0, 30, 20)

        hcgpa = round((tpg + hyp_s * hyp_c) / (tpc + hyp_c), 2) if tpc + hyp_c > 0 else hyp_s
        hc    = "#1db954" if hcgpa >= 8 else ("#ffa726" if hcgpa >= 6 else "#ff5252")
        st.markdown(
            f"<div style='text-align:center;padding:30px;'>"
            f"<div class='cgpa-big' style='color:{hc}'>{hcgpa}</div>"
            f"<div class='cgpa-label'>Projected CGPA</div></div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
