"""
THRESHOLD — VTU Academic Tracker
Run: streamlit run app.py
"""
import streamlit as st
from datetime import datetime, timedelta, timezone

# ── PAGE CONFIG (must be FIRST Streamlit call) ───────────────────────────────
st.set_page_config(
    page_title="THRESHOLD",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from utils.database      import init_db, _num
from utils.auth          import (
    init_auth_db, is_logged_in, current_user,
    verify_user, register_user, logout, login, update_theme,
)
from utils.styles        import inject_css
from utils.calendar_data import sem_to_cal_key

# ── TIME ─────────────────────────────────────────────────────────────────────
IST = timezone(timedelta(hours=5, minutes=30))
def today_ist(): return datetime.now(IST).date()
def now_ist():   return datetime.now(IST)

# ── INIT ─────────────────────────────────────────────────────────────────────
init_db()
init_auth_db()

# ── SESSION STATE ─────────────────────────────────────────────────────────────
for key, default in [("page", "home"), ("sub_id", None), ("auth_tab", "login")]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── THEME ─────────────────────────────────────────────────────────────────────
user = current_user()
dark = True if user is None else (user.get("theme", "dark") == "dark")
inject_css(dark)

# ══════════════════════════════════════════════════════════════════════════════
# AUTH PAGES (Login / Register)
# ══════════════════════════════════════════════════════════════════════════════
if not is_logged_in():
    # Hero
    st.markdown(
        """<div class="hero-wrap" style="min-height:40vh;">
            <div class="hero-badge">B.M.S. College of Engineering · VTU</div>
            <div class="hero-title">THRESHOLD</div>
            <div class="hero-sub">Plan · Track · Achieve</div>
        </div>""",
        unsafe_allow_html=True,
    )

    col = st.columns([1, 1.4, 1])[1]
    with col:
        tab_login, tab_reg = st.tabs(["🔑 Login", "✨ Register"])

        # ── LOGIN ──────────────────────────────────────────────────────────────
        with tab_login:
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            st.markdown('<div class="auth-title">Welcome back</div>', unsafe_allow_html=True)
            st.markdown('<div class="auth-sub">Sign in to your THRESHOLD account</div>', unsafe_allow_html=True)

            with st.form("login_form"):
                un = st.text_input("Username", placeholder="your_username")
                pw = st.text_input("Password", type="password", placeholder="••••••••")
                if st.form_submit_button("Sign In →", use_container_width=True):
                    u = verify_user(un, pw)
                    if u:
                        login(u)
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
            st.markdown("</div>", unsafe_allow_html=True)

        # ── REGISTER ───────────────────────────────────────────────────────────
        with tab_reg:
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            st.markdown('<div class="auth-title">Create account</div>', unsafe_allow_html=True)
            st.markdown('<div class="auth-sub">Join THRESHOLD — it\'s free</div>', unsafe_allow_html=True)

            with st.form("reg_form"):
                r1, r2 = st.columns(2)
                rn   = r1.text_input("Full Name",  placeholder="Enter your name")
                rdep = r2.text_input("Department", placeholder="e.g. Computer Science")
                run  = st.text_input("Username",   placeholder="Choose a unique username")
                rpw  = st.text_input("Password",   type="password", placeholder="Min 6 characters")
                rpw2 = st.text_input("Confirm Password", type="password", placeholder="Repeat password")
                rsem = st.selectbox("Current Semester", [1,2,3,4,5,6,7,8])

                if st.form_submit_button("Create Account →", use_container_width=True):
                    if not run or not rpw:
                        st.error("Username and password are required.")
                    elif len(rpw) < 6:
                        st.error("Password must be at least 6 characters.")
                    elif rpw != rpw2:
                        st.error("Passwords do not match.")
                    else:
                        ok = register_user(run, rpw, rn, rdep, rsem)
                        if ok:
                            u = verify_user(run, rpw)
                            login(u)
                            st.rerun()
                        else:
                            st.error("Username already taken. Choose another.")
            st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP (authenticated)
# ══════════════════════════════════════════════════════════════════════════════
from pages import (
    dashboard, calendar_page, sgpa_page, bunk_page,
    profile_page, subject_detail, analytics_page, export_page,
)

user    = current_user()
u_name  = user.get("name") or user.get("username", "Student")
u_sem   = int(_num(user.get("current_sem", 1)))
user_id = user["id"]
now     = now_ist()
today   = today_ist()

# ── TOP NAVIGATION ─────────────────────────────────────────────────────────
st.markdown('<div class="topbar">', unsafe_allow_html=True)
nc = st.columns([2.5, 1, 1, 1, 1, 1, 1, 0.7, 0.7])

with nc[0]:
    st.markdown(
        f'<span class="topbar-logo">🎓 THRESHOLD</span>'
        f'<span style="font-size:.7rem;opacity:.4;margin-left:12px;">'
        f'📅 {now.strftime("%d %b %Y")} &nbsp;|&nbsp; '
        f'🕐 {now.strftime("%I:%M %p")} IST</span>',
        unsafe_allow_html=True,
    )

nav = [
    ("🏠", "Dashboard",  "dashboard"),
    ("📅", "Calendar",   "calendar"),
    ("📈", "SGPA/CGPA",  "sgpa"),
    ("🚫", "Bunk",       "bunk"),
    ("📊", "Analytics",  "analytics"),
    ("📄", "Export",     "export"),
]
for i, (icon, label, pg) in enumerate(nav):
    with nc[i + 1]:
        if st.button(f"{icon} {label}", use_container_width=True, key=f"nav_{pg}"):
            st.session_state.page = pg
            st.rerun()

# Theme toggle
with nc[7]:
    theme_icon = "☀️" if dark else "🌙"
    if st.button(theme_icon, use_container_width=True, key="theme_toggle"):
        new_theme = "light" if dark else "dark"
        update_theme(user_id, new_theme)
        st.session_state.user["theme"] = new_theme
        st.rerun()

# Logout
with nc[8]:
    if st.button("🚪", use_container_width=True, key="logout_btn", help="Logout"):
        logout()
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# ── PAGE ROUTING ──────────────────────────────────────────────────────────────
st.markdown('<div style="padding:0 20px 80px;">', unsafe_allow_html=True)

page = st.session_state.page

if   page == "dashboard": dashboard.render(u_name, u_sem, today)
elif page == "calendar":  calendar_page.render(u_sem, today)
elif page == "sgpa":      sgpa_page.render(u_sem)
elif page == "bunk":      bunk_page.render(u_sem)
elif page == "analytics": analytics_page.render(u_sem, dark)
elif page == "export":    export_page.render(user, u_sem)
elif page == "profile":   profile_page.render(user, user_id)
elif page == "detail":    subject_detail.render()
else:
    st.session_state.page = "dashboard"
    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)
