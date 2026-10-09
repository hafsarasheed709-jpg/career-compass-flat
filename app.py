"""Career Compass AI - Streamlit entry point.  Run:  streamlit run app.py"""
import streamlit as st

st.set_page_config(page_title="Career Compass AI", page_icon="🧭", layout="wide")

import database as db  # noqa: E402
import ui  # noqa: E402
import view_analytics as analytics  # noqa: E402
import view_career_explorer as career_explorer  # noqa: E402
import view_career_report as career_report  # noqa: E402
import view_dashboard as dashboard  # noqa: E402
import view_help_about as help_about  # noqa: E402
import view_learning_roadmap as learning_roadmap  # noqa: E402
import view_profile as profile  # noqa: E402
import view_skill_assessment as skill_assessment  # noqa: E402

PAGES = {
    "Dashboard": dashboard.render,
    "Profile": profile.render,
    "Skill Assessment": skill_assessment.render,
    "Career Explorer": career_explorer.render,
    "Learning Roadmap": learning_roadmap.render,
    "Analytics": analytics.render,
    "Career Report": career_report.render,
    "Help & About": help_about.render,
}


def main() -> None:
    try:
        db.init_db()
        profiles = db.list_profiles()
    except db.DatabaseError as exc:
        st.error(f"The database could not be opened: {exc}")
        st.stop()

    ui.inject_css()

    # Apply programmatic changes BEFORE the widgets that own these keys are created.
    if "pending_page" in st.session_state:
        st.session_state["nav_page"] = st.session_state.pop("pending_page")
    if "pending_profile_id" in st.session_state:
        st.session_state["active_profile_id"] = st.session_state.pop("pending_profile_id")
        st.session_state["nav_page"] = "Dashboard"
    ids = [p["id"] for p in profiles]
    if "active_profile_id" not in st.session_state or st.session_state["active_profile_id"] not in ids + [None]:
        st.session_state["active_profile_id"] = ids[0] if ids else None
    st.session_state.setdefault("nav_page", "Dashboard")

    names = {p["id"]: p["display_name"] + (" [demo]" if p["is_demo"] else "") for p in profiles}
    with st.sidebar:
        st.markdown("## 🧭 Career Compass AI")
        st.caption("Smart career & skill development")
        st.selectbox("Active profile", [None] + ids, key="active_profile_id",
                     format_func=lambda i: "➕ New profile" if i is None else names[i])
        st.radio("Navigate", list(PAGES), key="nav_page", label_visibility="collapsed")
        st.caption("Rule-based guidance, not a validated prediction.")

    ui.show_flash()
    PAGES[st.session_state["nav_page"]]()


main()
