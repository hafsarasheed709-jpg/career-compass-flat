import streamlit as st

import database as db
import ui
from assessment import assessment_csv, summarize, validate_scores
from careers import RATING_GUIDE, SKILLS
from charts import skill_bar_chart
from recommendations import refresh_saved_recommendations


def render() -> None:
    ui.page_header("Skill Assessment", "Rate yourself honestly from 1 to 5. You can edit and re-save at any time.")
    profile = ui.require_profile()
    if profile is None:
        return
    pid = profile["id"]
    saved = db.get_assessment(pid)
    st.caption(RATING_GUIDE)
    if not saved:
        st.info("No saved assessment yet - the sliders start at 3 (Intermediate). Adjust them and press Save.")

    with st.form(f"assessment_form_{pid}"):
        cols = st.columns(2)
        new_scores = {}
        for i, (skill, description) in enumerate(SKILLS.items()):
            new_scores[skill] = cols[i % 2].slider(skill, 1, 5, int(saved.get(skill, 3)), help=description,
                                                   key=f"slider_{pid}_{skill}")
        submitted = st.form_submit_button("Save assessment")

    if submitted:
        errors = validate_scores(new_scores)
        if errors:
            for err in errors:
                st.error(err)
        else:
            try:
                db.save_assessment(pid, new_scores)
                refresh_saved_recommendations(pid)
                ui.flash("Assessment saved and career matches updated.")
                st.rerun()
            except db.DatabaseError as exc:
                st.error(f"Could not save your assessment: {exc}")

    if not saved:
        return
    st.divider()
    summary = summarize(saved)
    st.plotly_chart(skill_bar_chart(saved))
    c1, c2 = st.columns(2)
    c1.markdown("**Strengths (4-5)**")
    c1.write(", ".join(summary["strengths"]) or "None yet - keep practising!")
    c2.markdown("**Areas to improve (1-2)**")
    c2.write(", ".join(summary["improve"]) or "None - every skill is at 3 or above.")

    d1, d2 = st.columns(2)
    d1.download_button("Export assessment (CSV)", assessment_csv(saved), "career_compass_assessment.csv", "text/csv",
                       key="dl_assessment_csv")
    with d2.expander("Reset assessment"):
        st.caption("Deletes your saved ratings and career matches. Roadmap progress is kept.")
        confirm = st.checkbox("Yes, reset my assessment", key=f"reset_confirm_{pid}")
        if st.button("Reset assessment", disabled=not confirm, key=f"reset_btn_{pid}"):
            db.reset_assessment(pid)
            for skill in SKILLS:
                st.session_state.pop(f"slider_{pid}_{skill}", None)
            st.session_state.pop(f"reset_confirm_{pid}", None)
            ui.flash("Assessment reset.", "info")
            st.rerun()
