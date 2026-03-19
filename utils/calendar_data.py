from datetime import date

# ── EVENT COLOUR MAP ─────────────────────────────────────────────────────────
EVENT_COLORS = {
    "exam":    "#ff5252",
    "warning": "#ffa726",
    "info":    "#7c8ff5",
    "event":   "#1db954",
}

EVENT_LABELS = {
    "exam":    "🔴 Exam",
    "warning": "🟡 Important",
    "info":    "🔵 Info",
    "event":   "🟢 Event",
}

# ── BMSCE EVEN SEMESTER 2025-26 ──────────────────────────────────────────────
CALENDAR = {
    "VI Sem": [
        {"name": "Course Registration & Commencement",   "date": date(2026, 1, 19), "type": "info"},
        {"name": "Quiz #1 / AAT #1",                     "date": date(2026, 2,  1), "type": "warning"},
        {"name": "CIE Test I",                           "date": date(2026, 2, 19), "end": date(2026, 2, 21), "type": "exam"},
        {"name": "Announce CIE I Marks",                 "date": date(2026, 2, 25), "type": "info"},
        {"name": "First Student Feedback (T-L-P)",       "date": date(2026, 2, 25), "end": date(2026, 2, 27), "type": "info"},
        {"name": "First Proctor-Parent Meeting",         "date": date(2026, 2, 28), "type": "info"},
        {"name": "UTSAV",                                "date": date(2026, 4, 17), "end": date(2026, 4, 19), "type": "event"},
        {"name": "Quiz #2 / AAT #2",                     "date": date(2026, 4,  1), "type": "warning"},
        {"name": "CIE Test II",                          "date": date(2026, 4,  6), "end": date(2026, 4,  8), "type": "exam"},
        {"name": "Announce CIE II Marks",                "date": date(2026, 4, 13), "type": "info"},
        {"name": "Second Student Feedback (T-L-P)",      "date": date(2026, 4, 13), "end": date(2026, 4, 15), "type": "info"},
        {"name": "Second Proctor-Parent Meeting",        "date": date(2026, 4, 25), "type": "info"},
        {"name": "Course Withdrawal",                    "date": date(2026, 5,  4), "type": "warning"},
        {"name": "CIE Test III",                         "date": date(2026, 5,  7), "end": date(2026, 5,  9), "type": "exam"},
        {"name": "Announce CIE III Marks",               "date": date(2026, 5, 12), "type": "info"},
        {"name": "Third Student Feedback (T-L-P)",       "date": date(2026, 5, 10), "end": date(2026, 5, 12), "type": "info"},
        {"name": "Last Working Day",                     "date": date(2026, 5, 12), "type": "warning"},
        {"name": "Submit Final CIE to COE",              "date": date(2026, 5, 14), "type": "warning"},
        {"name": "Issue Hall Ticket for SEE",            "date": date(2026, 5, 18), "type": "info"},
        {"name": "SEE Lab / Project / SMR / Theory",     "date": date(2026, 5, 20), "end": date(2026, 6,  3), "type": "exam"},
        {"name": "VI Sem SEE Results",                   "date": date(2026, 6,  8), "type": "info"},
    ],
    "II & IV Sem": [
        {"name": "Course Registration & Commencement",   "date": date(2026, 2, 23), "type": "info"},
        {"name": "Quiz #1 / AAT #1",                     "date": date(2026, 3, 15), "type": "warning"},
        {"name": "CIE Test I",                           "date": date(2026, 4,  6), "end": date(2026, 4,  8), "type": "exam"},
        {"name": "Announce CIE I Marks",                 "date": date(2026, 4, 13), "type": "info"},
        {"name": "First Student Feedback (T-L-P)",       "date": date(2026, 4, 13), "end": date(2026, 4, 15), "type": "info"},
        {"name": "First Proctor-Parent Meeting",         "date": date(2026, 4, 25), "type": "info"},
        {"name": "UTSAV",                                "date": date(2026, 4, 17), "end": date(2026, 4, 19), "type": "event"},
        {"name": "Quiz #2 / AAT #2",                     "date": date(2026, 5,  1), "type": "warning"},
        {"name": "CIE Test II",                          "date": date(2026, 5, 18), "end": date(2026, 5, 20), "type": "exam"},
        {"name": "Announce CIE II Marks",                "date": date(2026, 5, 23), "type": "info"},
        {"name": "Second Student Feedback (T-L-P)",      "date": date(2026, 5, 25), "end": date(2026, 5, 27), "type": "info"},
        {"name": "Second Proctor-Parent Meeting",        "date": date(2026, 5, 30), "type": "info"},
        {"name": "Course Withdrawal (IV Sem only)",      "date": date(2026, 6, 11), "type": "warning"},
        {"name": "CIE Test III",                         "date": date(2026, 6, 18), "end": date(2026, 6, 20), "type": "exam"},
        {"name": "Announce CIE III Marks",               "date": date(2026, 6, 23), "type": "info"},
        {"name": "Last Working Day",                     "date": date(2026, 6, 23), "type": "warning"},
        {"name": "Submit Final CIE to COE",              "date": date(2026, 6, 23), "type": "warning"},
        {"name": "Issue Hall Ticket for SEE",            "date": date(2026, 6, 25), "type": "info"},
        {"name": "SEE Lab / Project / SMR / Theory",     "date": date(2026, 6, 29), "end": date(2026, 7, 13), "type": "exam"},
        {"name": "II & IV Sem SEE Results",              "date": date(2026, 7, 17), "type": "info"},
    ],
    "VIII Sem": [
        {"name": "Course Registration & Commencement",   "date": date(2026, 1, 19), "type": "info"},
        {"name": "Quiz #1 / AAT #1",                     "date": date(2026, 2,  1), "type": "warning"},
        {"name": "CIE Test I",                           "date": date(2026, 2, 19), "end": date(2026, 2, 21), "type": "exam"},
        {"name": "Announce CIE I Marks",                 "date": date(2026, 2, 25), "type": "info"},
        {"name": "First Proctor-Parent Meeting",         "date": date(2026, 2, 28), "type": "info"},
        {"name": "Open House / Project Exhibition",      "date": date(2026, 2, 28), "type": "event"},
        {"name": "CIE Test II",                          "date": date(2026, 4,  6), "end": date(2026, 4,  8), "type": "exam"},
        {"name": "CIE Test III",                         "date": date(2026, 5,  7), "end": date(2026, 5,  9), "type": "exam"},
        {"name": "Farewell to Final Year Students",      "date": date(2026, 5, 11), "type": "event"},
        {"name": "Last Working Day",                     "date": date(2026, 5, 12), "type": "warning"},
        {"name": "Issue Hall Ticket for SEE",            "date": date(2026, 5, 14), "type": "info"},
        {"name": "SEE Lab / Project / SMR / Theory",     "date": date(2026, 5, 18), "end": date(2026, 5, 25), "type": "exam"},
        {"name": "VIII Sem SEE Results",                 "date": date(2026, 5, 29), "type": "info"},
    ],
}


def sem_to_cal_key(sem_number):
    """Map semester number to calendar key."""
    if sem_number in [2, 4]: return "II & IV Sem"
    if sem_number == 6:      return "VI Sem"
    if sem_number == 8:      return "VIII Sem"
    return "II & IV Sem"


def get_upcoming_events(cal_key, today, n=3):
    """Return next n upcoming events sorted by date."""
    events = CALENDAR.get(cal_key, [])
    upcoming = [
        {**e, "delta": (e["date"] - today).days}
        for e in events
        if (e["date"] - today).days >= 0
    ]
    return sorted(upcoming, key=lambda x: x["delta"])[:n]
