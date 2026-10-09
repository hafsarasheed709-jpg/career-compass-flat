import streamlit as st

import database as db
import ui
from careers import CAREER_NAMES, CAREERS
from recommendations import recommend
from roadmap import build_roadmap, flatten_tasks, progress

PRIORITY_ICON = {"High priority": "🔴", "Medium priority": "🟠", "Strengthen": "🟢", "Core": "🔵"}


def default_career(profile: dict, scores: dict) -> str:
    intent = st.session_state.get("roadmap_intent")
    if intent:
        return intent["career"]
    if scores:
        return recommend(scores, profile["career_interests"])[0]["career"]
    return CAREER_NAMES[0]


def render() -> None:
    ui.page_header("Learning Roadmap", "Follow the modules in order and tick tasks as you finish them. Progress is saved automatically.")
    profile = ui.require_profile()
    if profile is None:
        return
    pid = profile["id"]
    scores = db.get_assessment(pid)
    if not scores:
        st.info("Tip: complete the skill assessment to see which modules are your highest priority.")

    intent_n = st.session_state.get("roadmap_intent", {}).get("n", 0)
    default = default_career(profile, scores)
    career = st.selectbox("Career path", CAREER_NAMES, index=CAREER_NAMES.index(default), key=f"rm_career_{intent_n}")
    st.caption(CAREERS[career]["overview"])

    modules = build_roadmap(career, scores or None)
    db.ensure_roadmap_tasks(pid, career, flatten_tasks(career))
    tasks = db.get_roadmap_tasks(pid, career)
    by_key = {t["task_key"]: t for t in tasks}
    done, total, fraction = progress(tasks)
    st.progress(fraction, text=f"{done} of {total} tasks complete ({fraction * 100:.0f}%)")

    for mod in modules:
        mod_tasks = [by_key[t["key"]] for t in mod["tasks"] if t["key"] in by_key]
        m_done = sum(1 for t in mod_tasks if t["completed"])
        icon = PRIORITY_ICON.get(mod["priority"], "")
        label = f"{icon} Module {mod['index']}: {mod['module']} — {m_done}/{len(mod_tasks)} · {mod['priority']}"
        with st.expander(label, expanded=m_done < len(mod_tasks) and mod["index"] <= 2):
            st.caption(f"Builds your “{mod['skill']}” skill.")
            for task in mod_tasks:
                checked = st.checkbox(f"**{task['task_type']}** — {task['title']}", value=task["completed"],
                                      key=f"task_{task['id']}")
                if checked != task["completed"]:
                    db.set_task_completed(pid, task["id"], checked)
                    st.rerun()

    st.subheader("Suggested portfolio projects")
    for proj in CAREERS[career]["projects"]:
        st.markdown(f"- {proj}")
    st.caption("Tools: " + ", ".join(CAREERS[career]["tools"]))
