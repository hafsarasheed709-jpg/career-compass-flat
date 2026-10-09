import pandas as pd
import streamlit as st

import database as db
import ui
from careers import CAREERS, CATEGORIES
from charts import skill_gap_chart
from recommendations import recommend, skill_gaps


def _matches(name: str, info: dict, query: str) -> bool:
    haystack = " ".join([name, info["overview"], " ".join(info["tools"]), " ".join(info["required_skills"])]).lower()
    return all(word in haystack for word in query.lower().split())


def render() -> None:
    ui.page_header("Career Explorer", "Search, filter and compare career paths. Match scores use your saved assessment.")
    pid = ui.active_profile_id()
    profile = db.get_profile(pid) if pid else None
    scores = db.get_assessment(pid) if profile else {}
    match_by_career = {}
    if scores:
        match_by_career = {r["career"]: r for r in recommend(scores, profile["career_interests"])}
    elif profile:
        st.info("Complete the skill assessment to see personalised match scores and skill gaps.")
    else:
        st.info("Create a profile to see personalised matches. You can still browse every career below.")

    f1, f2, f3 = st.columns([2, 2, 1])
    query = f1.text_input("Search careers, skills or tools", placeholder="e.g. SQL, dashboard, Streamlit", key="ce_query")
    cats = f2.multiselect("Category", CATEGORIES, key="ce_cats")
    sort_by = f3.selectbox("Sort by", ["Best match", "Name"], key="ce_sort") if match_by_career else "Name"

    names = [n for n, info in CAREERS.items() if _matches(n, info, query) and (not cats or info["category"] in cats)]
    if match_by_career and sort_by == "Best match":
        names.sort(key=lambda n: (-match_by_career[n]["match"], n))
    else:
        names.sort()
    if not names:
        st.warning("No careers match your search. Try fewer keywords or clear the category filter.")
        return

    for name in names:
        info = CAREERS[name]
        match = match_by_career.get(name)
        header = f"{name} — {match['match']:.0f}% · {match['label']}" if match else name
        with st.expander(header, expanded=len(names) == 1):
            st.markdown(ui.badge(info["category"]), unsafe_allow_html=True)
            st.write(info["overview"])
            tab_skills, tab_projects, tab_tools, tab_path = st.tabs(["Required skills & gaps", "Projects", "Tools", "Roadmap preview"])
            with tab_skills:
                if scores:
                    df = pd.DataFrame(skill_gaps(name, scores))[["skill", "current", "required", "gap", "weight"]]
                    df.columns = ["Skill", "Your rating", "Required", "Gap", "Importance (1-3)"]
                    st.dataframe(df, hide_index=True)
                    st.plotly_chart(skill_gap_chart(name, scores), key=f"gap_{name}")
                else:
                    df = pd.DataFrame([{"Skill": s, "Required level": r, "Importance (1-3)": w}
                                       for s, (r, w) in info["required_skills"].items()])
                    st.dataframe(df, hide_index=True)
            with tab_projects:
                for p in info["projects"]:
                    st.markdown(f"- {p}")
            with tab_tools:
                st.write(", ".join(info["tools"]))
            with tab_path:
                for i, mod in enumerate(info["roadmap"], 1):
                    st.markdown(f"{i}. **{mod['module']}** ({len(mod['tasks'])} tasks)")
            if profile and st.button(f"Open {name} roadmap", key=f"open_rm_{name}"):
                n = st.session_state.get("roadmap_intent", {}).get("n", 0) + 1
                st.session_state["roadmap_intent"] = {"career": name, "n": n}
                ui.navigate("Learning Roadmap")
