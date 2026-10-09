import streamlit as st

import database as db
import ui
from careers import CAREER_NAMES, EDUCATION_LEVELS, LEARNING_AREAS, SOFT_SKILL_OPTIONS, TECHNICAL_SKILL_OPTIONS
from demo import load_demo_profile
from recommendations import refresh_saved_recommendations
from utils import validate_profile


def _defaults(profile: dict | None, key: str, options: list[str]) -> list[str]:
    return [v for v in (profile or {}).get(key, []) if v in options]


def render() -> None:
    pid = ui.active_profile_id()
    profile = db.get_profile(pid) if pid else None
    ui.page_header("Your Profile", "Tell us about your background and goals. Nothing sensitive is needed - no passwords or ID numbers.")
    sid = pid if profile else "new"

    if profile is None:
        st.info("Create a profile to begin, or explore the app with a clearly labelled fictional demo profile.")
        if st.button("Load fictional demo profile", key="load_demo"):
            ui.flash("Demo profile loaded. All data in it is fictional.")
            ui.set_active_profile(load_demo_profile())
    elif profile["is_demo"]:
        st.warning("This is the fictional demo profile. Create your own profile for real guidance.")

    with st.form(f"profile_form_{sid}"):
        name = st.text_input("Display name *", value=profile["display_name"] if profile else "", max_chars=50,
                             key=f"pf_name_{sid}", help="A name or nickname; 2-50 characters.")
        c1, c2 = st.columns(2)
        edu_index = EDUCATION_LEVELS.index(profile["education_level"]) if profile and profile["education_level"] in EDUCATION_LEVELS else 2
        education = c1.selectbox("Education level *", EDUCATION_LEVELS, index=edu_index, key=f"pf_edu_{sid}")
        field = c2.text_input("Field of study *", value=profile["field_of_study"] if profile else "", max_chars=80,
                              key=f"pf_field_{sid}")
        tech = st.multiselect("Technical skills", TECHNICAL_SKILL_OPTIONS, default=_defaults(profile, "technical_skills", TECHNICAL_SKILL_OPTIONS),
                              key=f"pf_tech_{sid}")
        soft = st.multiselect("Soft skills", SOFT_SKILL_OPTIONS, default=_defaults(profile, "soft_skills", SOFT_SKILL_OPTIONS),
                              key=f"pf_soft_{sid}")
        interests = st.multiselect("Career interests", CAREER_NAMES, default=_defaults(profile, "career_interests", CAREER_NAMES),
                                   key=f"pf_int_{sid}", help="Careers you are curious about. Adds a small, transparent bonus to their match score.")
        areas = st.multiselect("Preferred learning areas", LEARNING_AREAS, default=_defaults(profile, "learning_areas", LEARNING_AREAS),
                               key=f"pf_area_{sid}")
        goal = st.text_area("Current career goal", value=profile["career_goal"] if profile else "", max_chars=250,
                            key=f"pf_goal_{sid}", placeholder="e.g. Become a junior data analyst within a year")
        submitted = st.form_submit_button("Save profile" if profile else "Create profile")

    if submitted:
        data = {"display_name": name, "education_level": education, "field_of_study": field, "technical_skills": tech,
                "soft_skills": soft, "career_interests": interests, "learning_areas": areas, "career_goal": goal}
        errors = validate_profile(data)
        if errors:
            for err in errors:
                st.error(err)
        else:
            try:
                if profile:
                    db.update_profile(profile["id"], data)
                    refresh_saved_recommendations(profile["id"])
                    ui.flash("Profile updated.")
                    st.rerun()
                else:
                    new_id = db.create_profile(data)
                    ui.flash("Profile created. Next, complete your skill assessment.")
                    ui.set_active_profile(new_id)
            except db.DatabaseError as exc:
                st.error(f"Could not save your profile: {exc}")

    if profile:
        with st.expander("Danger zone: delete this profile"):
            st.caption("Deletes the profile, its assessment, recommendations and roadmap progress permanently.")
            confirm = st.checkbox("I understand this cannot be undone", key=f"del_confirm_{profile['id']}")
            if st.button("Delete profile", disabled=not confirm, key=f"del_btn_{profile['id']}"):
                db.delete_profile(profile["id"])
                ui.flash("Profile deleted.", "info")
                ui.set_active_profile(None)
