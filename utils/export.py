"""
Export utilities — PDF report and CSV download.
Uses ReportLab for PDF generation.
"""
import io
import csv
from datetime import datetime, timezone, timedelta
import pandas as pd

# ── REPORTLAB OPTIONAL IMPORT ─────────────────────────────────────────────────
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors as rl_colors
    from reportlab.lib.units import cm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table,
        TableStyle, HRFlowable,
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_OK = True
except ImportError:
    rl_colors = None
    REPORTLAB_OK = False

IST = timezone(timedelta(hours=5, minutes=30))


def _now_str():
    return datetime.now(IST).strftime("%d %B %Y, %I:%M %p IST")


def _color(hex_str: str):
    """Convert hex string to ReportLab Color. Only call when REPORTLAB_OK."""
    h = hex_str.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return rl_colors.Color(r / 255, g / 255, b / 255)


# ── CSV EXPORTS ───────────────────────────────────────────────────────────────
def marks_csv(df_subjects, sgpa_rows: list) -> bytes:
    buf = io.StringIO()
    w   = csv.writer(buf)
    w.writerow(["Subject", "Credits", "CIE1", "CIE2", "CIE3",
                "Quiz", "AAT", "Lab", "Extra", "Internal/50",
                "SEE/100", "Total/100", "Grade", "GP"])
    for row in sgpa_rows:
        matches = df_subjects[df_subjects["name"] == row["subject"]]
        if matches.empty:
            continue
        sub = matches.iloc[0]
        w.writerow([
            row["subject"], row["credits"],
            int(float(sub.get("cie1", 0))),
            int(float(sub.get("cie2", 0))),
            int(float(sub.get("cie3", 0))),
            round(float(sub.get("quiz_score", 0)), 1),
            round(float(sub.get("aat_score",  0)), 1),
            round(float(sub.get("lab_score",  0)), 1),
            round(float(sub.get("extra_score",0)), 1),
            row["internal"],
            int(row["see"]) if row["see"] >= 0 else "N/A",
            row["total"], row["grade"], row["gp"],
        ])
    return buf.getvalue().encode()


def attendance_csv(df_subjects) -> bytes:
    buf = io.StringIO()
    w   = csv.writer(buf)
    w.writerow(["Subject", "Credits", "Conducted", "Attended", "Percentage", "Planned Total"])
    for _, row in df_subjects.iterrows():
        cond = int(float(row.get("total_classes", 0)))
        att  = int(float(row.get("attended_classes", 0)))
        plan = int(float(row.get("default_total_classes", 0)))
        pct  = round(att / cond * 100, 1) if cond > 0 else 0
        w.writerow([row["name"], int(row["credits"]), cond, att, f"{pct}%", plan])
    return buf.getvalue().encode()


def sgpa_csv(past_df: pd.DataFrame, current_sgpa: float, current_sem: int, cgpa: float) -> bytes:
    buf = io.StringIO()
    w   = csv.writer(buf)
    w.writerow(["Semester", "Subject", "Credits", "Grade", "Grade Points"])
    if not past_df.empty:
        for _, r in past_df.iterrows():
            w.writerow([int(r["semester"]), r["subject_name"],
                        int(r["credits"]), r["grade"], r["grade_points"]])
    w.writerow([])
    w.writerow(["Current Semester SGPA", current_sgpa])
    w.writerow(["CGPA", cgpa])
    return buf.getvalue().encode()


# ── PDF REPORT ────────────────────────────────────────────────────────────────
def generate_pdf_report(
    user_name: str,
    user_dept: str,
    u_sem: int,
    df_subjects,
    sgpa_rows: list,
    sgpa_val: float,
    cgpa_val: float,
    past_df: pd.DataFrame,
) -> bytes:
    if not REPORTLAB_OK:
        raise ImportError("reportlab not installed. Run: pip install reportlab")

    # Colours defined here so rl_colors is guaranteed to be available
    GREEN_C = _color("1db954")
    BLUE_C  = _color("4c57f0")
    DARK_C  = _color("111111")
    GRAY_C  = rl_colors.Color(0.95, 0.95, 0.95)
    WHITE_C = rl_colors.white

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm,  bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    H1  = ParagraphStyle("H1",  fontSize=22, fontName="Helvetica-Bold",
                          textColor=DARK_C, spaceAfter=4, alignment=TA_CENTER)
    H2  = ParagraphStyle("H2",  fontSize=14, fontName="Helvetica-Bold",
                          textColor=DARK_C, spaceAfter=6, spaceBefore=12)
    SUB = ParagraphStyle("SUB", fontSize=10, fontName="Helvetica",
                          textColor=rl_colors.Color(0.4, 0.4, 0.4),
                          alignment=TA_CENTER, spaceAfter=2)

    story = []

    # ── Header ──
    story.append(Paragraph("THRESHOLD", H1))
    story.append(Paragraph("B.M.S. College of Engineering · VTU", SUB))
    story.append(Paragraph(f"Academic Report — Semester {u_sem}", SUB))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=BLUE_C))
    story.append(Spacer(1, 0.3*cm))

    # ── Student info ──
    info_data = [
        ["Student",  user_name,  "Department", user_dept],
        ["Semester", str(u_sem), "Generated",  _now_str()],
    ]
    info_table = Table(info_data, colWidths=[3*cm, 6*cm, 3*cm, 5*cm])
    info_table.setStyle(TableStyle([
        ("FONTNAME",       (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME",       (0, 0), (0, -1),  "Helvetica-Bold"),
        ("FONTNAME",       (2, 0), (2, -1),  "Helvetica-Bold"),
        ("FONTSIZE",       (0, 0), (-1, -1), 10),
        ("TEXTCOLOR",      (0, 0), (-1, -1), DARK_C),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE_C, GRAY_C]),
        ("GRID",           (0, 0), (-1, -1), 0.5, rl_colors.Color(0.85, 0.85, 0.85)),
        ("PADDING",        (0, 0), (-1, -1), 5),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.5*cm))

    # ── SGPA / CGPA summary ──
    story.append(Paragraph("Performance Summary", H2))
    perf_data = [
        ["Metric", "Value"],
        [f"Estimated SGPA (Sem {u_sem})", str(sgpa_val)],
        ["CGPA (All Semesters)",          str(cgpa_val)],
    ]
    perf_table = Table(perf_data, colWidths=[10*cm, 7*cm])
    perf_table.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0),  BLUE_C),
        ("TEXTCOLOR",      (0, 0), (-1, 0),  WHITE_C),
        ("FONTNAME",       (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTNAME",       (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",       (0, 0), (-1, -1), 11),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE_C, GRAY_C]),
        ("GRID",           (0, 0), (-1, -1), 0.5, rl_colors.Color(0.85, 0.85, 0.85)),
        ("PADDING",        (0, 0), (-1, -1), 8),
        ("ALIGN",          (1, 0), (-1, -1), "CENTER"),
    ]))
    story.append(perf_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Marks table ──
    story.append(Paragraph("Subject-wise Marks", H2))
    marks_header = ["Subject", "Cr", "CIE1", "CIE2", "CIE3",
                    "Internal", "SEE", "Total", "Grade", "GP"]
    marks_data = [marks_header]
    for row in sgpa_rows:
        matches = df_subjects[df_subjects["name"] == row["subject"]]
        if matches.empty:
            continue
        sub = matches.iloc[0]
        marks_data.append([
            row["subject"][:22],
            str(int(row["credits"])),
            str(int(float(sub.get("cie1", 0)))),
            str(int(float(sub.get("cie2", 0)))),
            str(int(float(sub.get("cie3", 0)))),
            f"{row['internal']}/50",
            f"{int(row['see'])}/100" if row["see"] >= 0 else "N/A",
            f"{row['total']}/100",
            row["grade"],
            str(row["gp"]),
        ])
    col_w = [4*cm, 1*cm, 1.3*cm, 1.3*cm, 1.3*cm, 1.8*cm, 1.5*cm, 1.8*cm, 1.3*cm, 0.9*cm]
    marks_table = Table(marks_data, colWidths=col_w)
    marks_table.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0),  DARK_C),
        ("TEXTCOLOR",      (0, 0), (-1, 0),  WHITE_C),
        ("FONTNAME",       (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTNAME",       (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",       (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE_C, GRAY_C]),
        ("GRID",           (0, 0), (-1, -1), 0.5, rl_colors.Color(0.85, 0.85, 0.85)),
        ("PADDING",        (0, 0), (-1, -1), 5),
        ("ALIGN",          (1, 0), (-1, -1), "CENTER"),
    ]))
    story.append(marks_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Attendance table ──
    story.append(Paragraph("Attendance Summary", H2))
    att_header = ["Subject", "Credits", "Conducted", "Attended", "Attendance %", "Status"]
    att_data   = [att_header]
    for _, row in df_subjects.iterrows():
        cond   = int(float(row.get("total_classes", 0)))
        att    = int(float(row.get("attended_classes", 0)))
        pct    = round(att / cond * 100, 1) if cond > 0 else 0
        status = "Safe" if pct >= 75 else "Low"
        att_data.append([
            row["name"][:22], str(int(row["credits"])),
            str(cond), str(att), f"{pct}%", status,
        ])
    att_table = Table(att_data, colWidths=[4.5*cm, 1.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
    att_table.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0),  DARK_C),
        ("TEXTCOLOR",      (0, 0), (-1, 0),  WHITE_C),
        ("FONTNAME",       (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTNAME",       (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",       (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE_C, GRAY_C]),
        ("GRID",           (0, 0), (-1, -1), 0.5, rl_colors.Color(0.85, 0.85, 0.85)),
        ("PADDING",        (0, 0), (-1, -1), 6),
        ("ALIGN",          (1, 0), (-1, -1), "CENTER"),
    ]))
    story.append(att_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Past semesters ──
    if not past_df.empty:
        story.append(Paragraph("Past Semester Record", H2))
        past_header = ["Semester", "Subject", "Credits", "Grade", "Grade Points"]
        past_data   = [past_header]
        for _, r in past_df.iterrows():
            past_data.append([
                str(int(r["semester"])), r["subject_name"],
                str(int(r["credits"])), r["grade"], str(r["grade_points"]),
            ])
        past_table = Table(past_data, colWidths=[2.5*cm, 7*cm, 2.5*cm, 2.5*cm, 2.5*cm])
        past_table.setStyle(TableStyle([
            ("BACKGROUND",     (0, 0), (-1, 0),  DARK_C),
            ("TEXTCOLOR",      (0, 0), (-1, 0),  WHITE_C),
            ("FONTNAME",       (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTNAME",       (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE",       (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE_C, GRAY_C]),
            ("GRID",           (0, 0), (-1, -1), 0.5, rl_colors.Color(0.85, 0.85, 0.85)),
            ("PADDING",        (0, 0), (-1, -1), 6),
            ("ALIGN",          (2, 0), (-1, -1), "CENTER"),
        ]))
        story.append(past_table)

    # ── Footer ──
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=rl_colors.Color(0.7, 0.7, 0.7)))
    story.append(Paragraph(
        f"Generated by THRESHOLD · {_now_str()} · For personal academic use only.",
        ParagraphStyle("footer", fontSize=8,
                       textColor=rl_colors.Color(0.5, 0.5, 0.5),
                       alignment=TA_CENTER),
    ))

    doc.build(story)
    return buf.getvalue()
