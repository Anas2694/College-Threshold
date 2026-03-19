import streamlit as st
from utils.database import get_subjects, get_past, _num
from utils.calculations import calc_sgpa, calc_cgpa
from utils.export import (
    generate_pdf_report, marks_csv, attendance_csv, sgpa_csv, REPORTLAB_OK,
)


def render(user: dict, u_sem: int):
    st.markdown(
        "<div style='margin-top:24px;'>"
        "<h1 style='font-size:2rem;font-weight:900;'>📄 Export</h1>"
        "<p style='opacity:.5;'>Download your academic data as PDF or CSV</p></div>",
        unsafe_allow_html=True,
    )

    df      = get_subjects(u_sem)
    past_df = get_past()

    if df.empty:
        st.info("No subjects found. Add subjects from the Dashboard first.")
        return

    sgpa_val, sgpa_rows = calc_sgpa(df)
    total_cr = sum(int(_num(r.get("credits", 0))) for _, r in df.iterrows())
    cgpa_val = calc_cgpa(past_df, sgpa_val, total_cr)

    u_name = user.get("name", "Student")
    u_dept = user.get("dept", "")

    # ── PDF Report ─────────────────────────────────────────────────────────────
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### 📋 Full Academic Report (PDF)")
    st.markdown(
        "<p style='opacity:.5;font-size:.85rem;'>"
        "Includes marks, attendance, SGPA/CGPA, and past semester record.</p>",
        unsafe_allow_html=True,
    )

    if REPORTLAB_OK:
        if st.button("⬇️ Download PDF Report", use_container_width=True):
            try:
                pdf_bytes = generate_pdf_report(
                    u_name, u_dept, u_sem, df, sgpa_rows,
                    sgpa_val, cgpa_val, past_df,
                )
                st.download_button(
                    label="📥 Click to Save PDF",
                    data=pdf_bytes,
                    file_name=f"THRESHOLD_Report_Sem{u_sem}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"PDF generation failed: {e}")
    else:
        st.warning("ReportLab not installed. Run: `pip install reportlab`")
        if st.button("Install ReportLab", use_container_width=True):
            import subprocess, sys
            subprocess.run([sys.executable, "-m", "pip", "install", "reportlab"])
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # ── CSV Downloads ──────────────────────────────────────────────────────────
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### 📊 CSV Downloads")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("**Marks Summary**")
        st.markdown("<p style='opacity:.5;font-size:.8rem;'>All CIE/Quiz/Lab/SEE scores with grades</p>", unsafe_allow_html=True)
        try:
            csv_data = marks_csv(df, sgpa_rows)
            st.download_button(
                "⬇️ marks_summary.csv", csv_data,
                file_name=f"marks_sem{u_sem}.csv",
                mime="text/csv", use_container_width=True,
            )
        except Exception as e:
            st.error(str(e))

    with c2:
        st.markdown("**Attendance Report**")
        st.markdown("<p style='opacity:.5;font-size:.8rem;'>Per-subject attendance breakdown</p>", unsafe_allow_html=True)
        try:
            csv_data = attendance_csv(df)
            st.download_button(
                "⬇️ attendance.csv", csv_data,
                file_name=f"attendance_sem{u_sem}.csv",
                mime="text/csv", use_container_width=True,
            )
        except Exception as e:
            st.error(str(e))

    with c3:
        st.markdown("**SGPA / CGPA Record**")
        st.markdown("<p style='opacity:.5;font-size:.8rem;'>All semesters + current SGPA</p>", unsafe_allow_html=True)
        try:
            csv_data = sgpa_csv(past_df, sgpa_val, u_sem, cgpa_val)
            st.download_button(
                "⬇️ sgpa_record.csv", csv_data,
                file_name="sgpa_cgpa_record.csv",
                mime="text/csv", use_container_width=True,
            )
        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Preview ────────────────────────────────────────────────────────────────
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### 👁️ Data Preview")
    import pandas as pd
    tbl = [
        {
            "Subject":      r["subject"],
            "Credits":      r["credits"],
            "Internal /50": r["internal"],
            "SEE /100":     int(r["see"]) if r["see"] >= 0 else "—",
            "Total /100":   r["total"],
            "Grade":        r["grade"],
            "GP":           r["gp"],
        }
        for r in sgpa_rows
    ]
    st.dataframe(pd.DataFrame(tbl), use_container_width=True, hide_index=True)
    st.markdown(
        f"<div style='display:flex;gap:20px;margin-top:12px;'>"
        f"<span class='pill pill-green'>⭐ SGPA: {sgpa_val}</span>"
        f"<span class='pill pill-blue'>🎓 CGPA: {cgpa_val}</span>"
        f"<span class='pill pill-blue'>📚 {len(df)} Subjects</span>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)
