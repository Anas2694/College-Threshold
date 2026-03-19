import math
import numpy as np
from utils.database import _num

# ── GRADE CONSTANTS ──────────────────────────────────────────────────────────
GRADE_CUTOFFS = {"O": 90, "A+": 80, "A": 70, "B+": 60, "B": 55, "C": 50}
GP_MAP        = {"O": 10, "A+": 9,  "A": 8,  "B+": 7,  "B": 6,  "C": 5, "P": 4, "F": 0}


# ── INTERNAL MARKS ───────────────────────────────────────────────────────────
def internal_from_values(
    c1, c2, c3, quiz, aat, lab, extra,
    qm, am, lm, em, cm,
    cw, lw, qw, aw, ew
):
    """Calculate internal marks out of 50."""
    def scale(mark, max_mark):
        return (_num(mark) / (_num(max_mark) or 40)) * 10

    s1, s2, s3 = scale(c1, cm), scale(c2, cm), scale(c3, cm)
    best_two   = np.sort(np.array([s1, s2, s3]))[-2:].sum()

    cie_part   = (best_two / 20) * cw
    lab_part   = (lab  / lm) * lw if lm  > 0 else 0.0
    quiz_part  = (quiz / qm) * qw if qm  > 0 else 0.0
    aat_part   = (aat  / am) * aw if am  > 0 else 0.0
    extra_part = (extra / em) * ew if em > 0 else 0.0

    exact = min(cie_part + lab_part + quiz_part + aat_part + extra_part, 50.0)
    return round(exact), exact


def calc_internals(row):
    """Calculate internals from a DataFrame row."""
    return internal_from_values(
        _num(row.get("cie1")),        _num(row.get("cie2")),        _num(row.get("cie3")),
        _num(row.get("quiz_score")),  _num(row.get("aat_score")),   _num(row.get("lab_score")),
        _num(row.get("extra_score")),
        _num(row.get("quiz_max", 10)),_num(row.get("aat_max", 10)), _num(row.get("lab_max", 25)),
        _num(row.get("extra_max")),   _num(row.get("cie_max", 40)),
        _num(row.get("cie_weight", 20)), _num(row.get("lab_weight", 20)),
        _num(row.get("quiz_weight", 5)), _num(row.get("aat_weight", 5)),
        _num(row.get("extra_weight", 0)),
    )


# ── GRADE HELPERS ────────────────────────────────────────────────────────────
def total_to_grade(total):
    for grade, cutoff in GRADE_CUTOFFS.items():
        if total >= cutoff:
            return grade
    return "F"


def required_see(internal_exact, target_total):
    """How much SEE score needed to reach target_total?"""
    remaining = target_total - internal_exact
    if remaining <= 0:
        return 0
    see_needed = 2 * remaining
    return math.ceil(see_needed) if see_needed <= 100 else None


def required_cie(row, c1, c2, c3, q, a, l, ex, qm, am, lm, em,
                 assumed_see, target_total, mode):
    """Find minimum CIE score needed in specified mode to hit target grade."""
    see_contribution = (assumed_see / 100) * 50
    cm = _num(row.get("cie_max", 40))
    cw = _num(row.get("cie_weight", 20)); lw = _num(row.get("lab_weight", 20))
    qw = _num(row.get("quiz_weight", 5)); aw = _num(row.get("aat_weight", 5))
    ew = _num(row.get("extra_weight", 0))

    for m in range(41):
        r1, r2, r3 = c1, c2, c3
        if   mode == "cie1":         r1 = m
        elif mode == "cie2":         r2 = m
        elif mode == "cie3":         r3 = m
        elif mode == "cie2_3_equal": r2 = m; r3 = m
        elif mode == "all_equal":    r1 = m; r2 = m; r3 = m

        ir, _ = internal_from_values(r1, r2, r3, q, a, l, ex, qm, am, lm, em,
                                      cm, cw, lw, qw, aw, ew)
        if ir + see_contribution >= target_total:
            return m
    return None


# ── ATTENDANCE ───────────────────────────────────────────────────────────────
def bunk_calc(credits, conducted, attended, target_pct, planned):
    """Returns (bunks_remaining, current_pct, projected_pct)."""
    if not planned or planned <= 0:
        planned = 10 * credits
    conducted, attended = int(conducted), int(attended)
    required    = math.ceil((target_pct / 100) * planned)
    missed      = max(conducted - attended, 0)
    remaining   = (planned - required) - missed
    current_pct = (attended / conducted * 100) if conducted > 0 else 0.0
    proj_pct    = (attended / planned   * 100) if planned   > 0 else 0.0
    return remaining, round(current_pct, 1), round(proj_pct, 1)


# ── SGPA / CGPA ──────────────────────────────────────────────────────────────
def calc_sgpa(df):
    """Calculate SGPA from current semester subjects."""
    total_cr, total_gp, rows = 0, 0, []
    for _, row in df.iterrows():
        see   = _num(row.get("see_score", -1))
        _, exact = calc_internals(row)
        total_marks = min(exact + (see / 100) * 50, 100) if see >= 0 else min(exact * 2, 100)
        grade = total_to_grade(total_marks)
        gp    = GP_MAP.get(grade, 0)
        cr    = int(_num(row.get("credits", 0)))
        rows.append({
            "subject": row["name"], "credits": cr, "grade": grade, "gp": gp,
            "internal": round(exact, 1), "see": see, "total": round(total_marks, 1),
        })
        total_cr += cr
        total_gp += gp * cr
    sgpa = round(total_gp / total_cr, 2) if total_cr > 0 else 0.0
    return sgpa, rows


def calc_cgpa(past_df, current_sgpa=None, current_credits=None):
    """Calculate cumulative CGPA including past and optionally current semester."""
    total_cr, total_gp = 0, 0
    for _, r in past_df.iterrows():
        cr = int(_num(r.get("credits", 0)))
        gp = _num(r.get("grade_points", 0))
        total_cr += cr
        total_gp += gp * cr
    if current_sgpa and current_credits:
        total_gp += current_sgpa * current_credits
        total_cr += current_credits
    return round(total_gp / total_cr, 2) if total_cr > 0 else 0.0
