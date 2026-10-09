import streamlit as st

import database as db
import ui
from assessment import summarize
from careers import SKILLS
from charts import career_comparison_chart, skill_bar_chart
from recommendations import recommend, skill_gaps


def render() -> None:
    profile = ui.require_profile()
    if profile is None:
        ui.page_header("Dashboard", "Your career development overview.")
        return
    pid = profile["id"]
    ui.page_header(f"Welcome, {profile['display_name']}", f"{profile['education_level']} · {profile['field_of_study']}")
    if profile["is_demo"]:
        st.warning("You are viewing fictional demonstration data.")
    if profile["career_goal"]:
        st.markdown(f"**Career goal:** {profile['career_goal']}")

    scores = db.get_assessment(pid)
    if not scores:
        ui.empty_state("Complete your skill assessment to unlock career matches, skill gaps and roadmaps.",
                       "Start assessment", "Skill Assessment")
        return

    recs = recommend(scores, profile["career_interests"])
    summary = summarize(scores)
    rows = db.roadmap_progress(pid)
    done, total = sum(r["done"] for r in rows), sum(r["total"] for r in rows)
    pct = 100 * done / total if total else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        ui.metric_card("Skills assessed", f"{summary['assessed']}/{len(SKILLS)}", f"Average {summary['average']:.1f} / 5")
    with c2:
        ui.metric_card("Top career match", f"{recs[0]['match']:.0f}%", recs[0]["career"], "Rule-based skill coverage score")
    with c3:
        ui.metric_card("Learning progress", f"{pct:.0f}%", f"{done} of {total} tasks" if total else "No roadmap started")
    with c4:
        gaps = recs[0]["gaps"]
        ui.metric_card("Skill gaps (top career)", str(len(gaps)), "Skills below the required level")

    st.write("")
    left, right = st.columns(2)
    left.plotly_chart(skill_bar_chart(scores))
    right.plotly_chart(career_comparison_chart(recs))

    a, b = st.columns(2)
    with a:
        st.subheader("Top recommended careers")
        for i, r in enumerate(recs[:3], 1):
            st.markdown(f"**{i}. {r['career']}** — {r['match']:.1f}% · {r['label']}")
            st.progress(min(r["match"] / 100, 1.0))
        if st.button("Explore careers", key="dash_explore"):
            ui.navigate("Career Explorer")
    with b:
        st.subheader(f"Skill-gap summary: {recs[0]['career']}")
        if gaps:
            for g in skill_gaps(recs[0]["career"], scores)[:3]:
                if g["gap"] > 0:
                    st.markdown(f"- **{g['skill']}**: {g['current']} → {g['required']} (gap {g['gap']})")
        else:
            st.success("You meet every requirement for this career.")

    st.subheader("Recent activity")
    items = [f"Profile last updated {profile['updated_at']} UTC"]
    stamp = db.get_assessment_updated_at(pid)
    if stamp:
        items.append(f"Skill assessment saved {stamp} UTC")
    for t in db.recent_completed_tasks(pid):
        items.append(f"Completed “{t['title']}” ({t['career']}) on {t['completed_at']} UTC")
    for line in items:
        st.markdown(f"- {line}")
