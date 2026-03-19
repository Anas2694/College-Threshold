import streamlit as st
from utils.auth import update_user, change_password, update_theme
from utils.database import _num


def render(user: dict, user_id: int):
    st.markdown(
        "<div style='margin-top:24px;'>"
        "<h1 style='font-size:2rem;font-weight:900;'>👤 Profile & Settings</h1></div>",
        unsafe_allow_html=True,
    )

    t1, t2, t3 = st.tabs(["👤 Profile", "🔐 Security", "🎨 Appearance"])

    # ── PROFILE ───────────────────────────────────────────────────────────────
    with t1:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown(f"**Username:** `{user.get('username', '')}`")
        st.markdown("<br>", unsafe_allow_html=True)
        with st.form("profile_form"):
            p1, p2 = st.columns(2)
            nm = p1.text_input("Full Name",   value=user.get("name", ""))
            dp = p2.text_input("Department",  value=user.get("dept", ""))
            sm = st.selectbox(
                "Current Semester", [1, 2, 3, 4, 5, 6, 7, 8],
                index=max(0, int(_num(user.get("current_sem", 1))) - 1),
            )
            if st.form_submit_button("💾 Save Profile", use_container_width=True):
                update_user(user_id, nm, dp, sm)
                st.session_state.user["name"]        = nm
                st.session_state.user["dept"]        = dp
                st.session_state.user["current_sem"] = sm
                st.success("✅ Profile updated!")
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ── SECURITY ──────────────────────────────────────────────────────────────
    with t2:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown("### Change Password")
        with st.form("pw_form"):
            old_pw  = st.text_input("Current Password",  type="password")
            new_pw  = st.text_input("New Password",      type="password", placeholder="Min 6 characters")
            new_pw2 = st.text_input("Confirm New Password", type="password")
            if st.form_submit_button("🔐 Update Password", use_container_width=True):
                if len(new_pw) < 6:
                    st.error("Password must be at least 6 characters.")
                elif new_pw != new_pw2:
                    st.error("Passwords do not match.")
                else:
                    ok = change_password(user_id, old_pw, new_pw)
                    if ok:
                        st.success("✅ Password updated successfully!")
                    else:
                        st.error("Current password is incorrect.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── APPEARANCE ────────────────────────────────────────────────────────────
    with t3:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown("### Theme")
        current_theme = user.get("theme", "dark")
        col1, col2 = st.columns(2)
        with col1:
            is_dark = current_theme == "dark"
            st.markdown(
                f'<div style="border:2px solid {"#7c8ff5" if is_dark else "transparent"};'
                f'border-radius:16px;padding:20px;text-align:center;cursor:pointer;background:#030308;">'
                f'<div style="font-size:2rem;">🌙</div>'
                f'<div style="color:white;font-weight:700;margin-top:8px;">Dark Mode</div>'
                f'<div style="color:rgba(255,255,255,.4);font-size:.8rem;">{"✓ Active" if is_dark else ""}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )
            if st.button("Switch to Dark", use_container_width=True, key="set_dark"):
                update_theme(user_id, "dark")
                st.session_state.user["theme"] = "dark"
                st.rerun()
        with col2:
            is_light = current_theme == "light"
            st.markdown(
                f'<div style="border:2px solid {"#4c57f0" if is_light else "transparent"};'
                f'border-radius:16px;padding:20px;text-align:center;cursor:pointer;background:#f0f2f8;">'
                f'<div style="font-size:2rem;">☀️</div>'
                f'<div style="color:#111;font-weight:700;margin-top:8px;">Light Mode</div>'
                f'<div style="color:rgba(0,0,0,.4);font-size:.8rem;">{"✓ Active" if is_light else ""}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )
            if st.button("Switch to Light", use_container_width=True, key="set_light"):
                update_theme(user_id, "light")
                st.session_state.user["theme"] = "light"
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
