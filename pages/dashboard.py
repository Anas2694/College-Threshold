import streamlit as st
from utils.database import get_subjects, add_subject, get_past, _num
from utils.calculations import calc_internals, calc_sgpa, calc_cgpa
from utils.calendar_data import sem_to_cal_key, CALENDAR, EVENT_COLORS


def render(u_name, u_sem, today):
    df       = get_subjects(u_sem)
    cal_key  = sem_to_cal_key(u_sem)
    all_ev   = sorted(CALENDAR.get(cal_key, []), key=lambda x: x["date"])
    upcoming = [
        {**e, "delta": (e["date"] - today).days}
        for e in all_ev
        if (e["date"] - today).days >= 0
    ][:3]

    # ── Header ──
    st.markdown(
        f"<div style='margin-top:24px;'>"
        f"<h1 style='font-size:2rem;font-weight:900;margin:0'>Hey, {u_name} 👋</h1>"
        f"<p style='opacity:.45;margin:4px 0 16px;font-size:.85rem'>"
        f"Semester {u_sem} · {today.strftime('%A, %d %B %Y')} · IST</p></div>",
        unsafe_allow_html=True,
    )

    # ── Quick stats ──
    atts = []
    for _, row in df.iterrows():
        t = _num(row["total_classes"]); a = _num(row["attended_classes"])
        if t > 0: atts.append(a / t * 100)
    avg_att  = round(sum(atts) / len(atts), 1) if atts else 0
    sgpa_val, _ = calc_sgpa(df) if not df.empty else (0.0, [])

    # Next event pill
    next_pill = ""
    if upcoming:
        ne = upcoming[0]
        if   ne["delta"] == 0: next_pill = f"<span class='pill pill-red'>🔴 TODAY: {ne['name']}</span>"
        elif ne["delta"] == 1: next_pill = f"<span class='pill pill-yellow'>🟡 TOMORROW: {ne['name']}</span>"
        else:                  next_pill = f"<span class='pill pill-blue'>⏳ {ne['delta']}d → {ne['name']}</span>"

    att_pill = "pill-green" if avg_att >= 75 else "pill-red"
    st.markdown(
        f"<div style='display:flex;flex-wrap:wrap;gap:8px;margin-bottom:20px;'>"
        f"<span class='pill pill-blue'>📚 {len(df)} Subjects</span>"
        f"<span class='pill {att_pill}'>📅 {avg_att}% Avg Attendance</span>"
        f"<span class='pill pill-green'>⭐ {sgpa_val} Est. SGPA</span>"
        f"<span class='pill pill-blue'>🎓 Sem {u_sem}</span>"
        f"{next_pill}</div>",
        unsafe_allow_html=True,
    )

    left, right = st.columns([3, 2])

    # ── Subject cards ──
    with left:
        st.markdown('<div class="sec-title">My Subjects</div>', unsafe_allow_html=True)
        if df.empty:
            st.markdown(
                '<div class="glass" style="text-align:center;padding:40px;opacity:.5;">'
                "No subjects yet. Add one below ↓</div>",
                unsafe_allow_html=True,
            )
        else:
            cc = st.columns(2)
            for i, row in df.iterrows():
                with cc[i % 2]:
                    tot, _ = calc_internals(row)
                    at = _num(row["total_classes"]); aa = _num(row["attended_classes"])
                    pct = int((aa / at) * 100) if at > 0 else 0
                    ic = "#1db954" if tot >= 40 else ("#ffa726" if tot >= 25 else "#ff5252")
                    ac = "#1db954" if pct >= 75 else "#ff5252"
                    st.markdown(
                        f'<div class="sub-card">'
                        f'<div class="sub-card-name">{row["name"]}</div>'
                        f'<div class="sub-card-cred">{int(row["credits"])} Credits</div>'
                        f'<div style="display:flex;justify-content:space-between;'
                        f'position:absolute;bottom:20px;left:20px;right:20px;">'
                        f'<div><div class="sub-stat">Internal</div>'
                        f'<div class="sub-val" style="color:{ic}">{tot}'
                        f'<span style="font-size:.85rem;opacity:.5">/50</span></div></div>'
                        f'<div style="text-align:right"><div class="sub-stat">Attendance</div>'
                        f'<div class="sub-val" style="color:{ac}">{pct}'
                        f'<span style="font-size:.85rem;opacity:.5">%</span></div></div>'
                        f"</div></div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown('<div class="ghost-btn-container">', unsafe_allow_html=True)
                    if st.button("open", key=f"btn_{row['id']}"):
                        st.session_state.sub_id = int(row["id"])
                        st.session_state.page   = "detail"
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("➕ Add New Subject"):
            with st.form("add_sub"):
                an, ac = st.columns(2)
                sn = an.text_input("Subject Name")
                sc = ac.selectbox("Credits", [4, 3, 2, 1])
                if st.form_submit_button("Add Subject", use_container_width=True) and sn:
                    if add_subject(sn, sc, u_sem): st.rerun()
                    else: st.error("Name already exists.")

    # ── Right panel: upcoming events + SGPA/CGPA ──
    with right:
        st.markdown('<div class="sec-title">Upcoming Events</div>', unsafe_allow_html=True)
        if upcoming:
            for e in upcoming:
                d = e["date"]; delta = e["delta"]
                col = EVENT_COLORS.get(e.get("type", "info"), "#7c8ff5")
                lbl = "🔴 TODAY" if delta == 0 else ("🟡 TOMORROW" if delta == 1 else f"⏳ in {delta} days")
                end_s = f" → {e['end'].strftime('%d %b')}" if "end" in e else ""
                cls = "today" if delta == 0 else "upcoming"
                st.markdown(
                    f'<div class="cal-event {cls}" style="border-color:{col}">'
                    f'<div class="cal-event-date">{d.strftime("%d %B %Y")}{end_s}</div>'
                    f'<div class="cal-event-name" style="color:{col}">{e["name"]}</div>'
                    f'<div class="cal-event-days" style="color:{col}">{lbl}</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<div class="glass" style="opacity:.5;text-align:center;padding:24px;">No upcoming events</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="sec-title" style="margin-top:20px;">Performance</div>', unsafe_allow_html=True)
        past_df      = get_past()
        total_sem_cr = sum(int(_num(r.get("credits", 0))) for _, r in df.iterrows()) if not df.empty else 0
        cgpa_val     = calc_cgpa(past_df, sgpa_val, total_sem_cr)
        s_col = "#1db954" if sgpa_val >= 8 else ("#ffa726" if sgpa_val >= 6 else "#ff5252")
        c_col = "#7c8ff5" if cgpa_val >= 8 else ("#ffa726" if cgpa_val >= 6 else "#ff5252")
        st.markdown(
            f'<div class="glass" style="text-align:center;padding:28px 20px;">'
            f'<div style="display:flex;justify-content:space-around;align-items:center;">'
            f'<div><div class="cgpa-big" style="color:{s_col}">{sgpa_val}</div>'
            f'<div class="cgpa-label">Est. SGPA</div></div>'
            f'<div style="width:1px;height:60px;background:rgba(255,255,255,.1);"></div>'
            f'<div><div class="cgpa-big" style="color:{c_col}">{cgpa_val}</div>'
            f'<div class="cgpa-label">CGPA</div></div>'
            f"</div></div>",
            unsafe_allow_html=True,
        )
