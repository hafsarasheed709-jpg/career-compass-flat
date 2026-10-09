import streamlit as st

import database as db
import ui
from careers import CAREER_NAMES
from charts import (career_comparison_chart, career_radar_chart, progress_chart, skill_bar_chart,
                    skill_gap_chart)
from recommendations import recommend


def render() -> None:
    ui.page_header("Interactive Analytics", "Hover, zoom and click legend items to explore your data.")
    profile = ui.require_profile()
    if profile is None:
        return
    scores = ui.require_assessment(profile)
    if scores is None:
        return
    recs = recommend(scores, profile["career_interests"])

    t1, t2, t3, t4, t5 = st.tabs(["Skills", "Career comparison", "Skill gap", "Career match overview", "Learning progress"])
    with t1:
        st.plotly_chart(skill_bar_chart(scores), key="an_skills")
    with t2:
        st.plotly_chart(career_comparison_chart(recs), key="an_compare")
        st.caption("Blue = weighted skill coverage; light blue = small bonus for careers you listed as interests.")
    with t3:
        career = st.selectbox("Career", CAREER_NAMES, index=CAREER_NAMES.index(recs[0]["career"]), key="an_gap_career")
        st.plotly_chart(skill_gap_chart(career, scores), key="an_gap")
    with t4:
        career = st.selectbox("Career", CAREER_NAMES, index=CAREER_NAMES.index(recs[0]["career"]), key="an_radar_career")
        st.plotly_chart(career_radar_chart(career, scores), key="an_radar")
    with t5:
        rows = db.roadmap_progress(profile["id"])
        if rows:
            st.plotly_chart(progress_chart(rows), key="an_progress")
        else:
            ui.empty_state("No roadmap started yet. Open a roadmap and tick off your first task.", "Open roadmap", "Learning Roadmap")
