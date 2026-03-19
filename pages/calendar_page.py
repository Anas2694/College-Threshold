import streamlit as st
from utils.calendar_data import CALENDAR, EVENT_COLORS, EVENT_LABELS, sem_to_cal_key


def render(u_sem, today):
    st.markdown(
        "<div style='margin-top:24px;'>"
        "<h1 style='font-size:2rem;font-weight:900;'>📅 Academic Calendar</h1>"
        "<p style='opacity:.5;'>BMSCE · Even Semester 2025-26</p></div>",
        unsafe_allow_html=True,
    )

    opts    = ["II & IV Sem", "VI Sem", "VIII Sem"]
    def_idx = {"II & IV Sem": 0, "VI Sem": 1, "VIII Sem": 2}.get(sem_to_cal_key(u_sem), 0)
    sel     = st.selectbox("Semester", opts, index=def_idx)
    events  = CALENDAR.get(sel, [])

    f1, f2    = st.columns(2)
    show_past = f1.checkbox("Show past events", value=False)
    ftype     = f2.selectbox("Filter by type", ["All", "exam", "warning", "info", "event"])

    st.markdown("<br>", unsafe_allow_html=True)
    shown = 0

    for e in sorted(events, key=lambda x: x["date"]):
        d     = e["date"]
        delta = (d - today).days

        if not show_past and delta < -1:
            continue
        if ftype != "All" and e.get("type") != ftype:
            continue

        shown += 1
        col   = EVENT_COLORS.get(e.get("type", "info"), "#7c8ff5")
        label = EVENT_LABELS.get(e.get("type", "info"), e.get("type", ""))
        end_s = f" → {e['end'].strftime('%d %b %Y')}" if "end" in e else ""

        if   delta == 0: badge = "🔴 TODAY"
        elif delta == 1: badge = "🟡 TOMORROW"
        elif delta <  0: badge = f"✓ {abs(delta)}d ago"
        else:            badge = f"⏳ In {delta} days"

        cls = "today" if delta == 0 else ("past" if delta < 0 else ("warning" if delta <= 7 else "upcoming"))

        st.markdown(
            f'<div class="cal-event {cls}" style="border-color:{col}">'
            f'<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
            f"<div>"
            f'<div class="cal-event-date">{d.strftime("%A, %d %B %Y")}{end_s}</div>'
            f'<div class="cal-event-name">{e["name"]}</div>'
            f'<span class="pill" style="border-color:{col};color:{col};'
            f'font-size:.65rem;padding:3px 10px;margin-top:4px;">{label}</span>'
            f"</div>"
            f'<div class="cal-event-days" style="color:{col};white-space:nowrap;margin-left:12px;">{badge}</div>'
            f"</div></div>",
            unsafe_allow_html=True,
        )

    if shown == 0:
        st.info("No events match the selected filter.")
