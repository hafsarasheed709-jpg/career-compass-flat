import pandas as pd
import streamlit as st

import database as db
import ui
from assessment import assessment_csv
from careers import CAREER_NAMES
from recommendations import recommend, skill_gaps
from report_generator import build_pdf_report
from roadmap import flatten_tasks


def render() -> None:
    ui.page_header("Career Report", "Generate a PDF with your profile, results, gaps, roadmap and next steps.")
    profile = ui.require_profile()
    if profile is None:
        return
    scores = ui.require_assessment(profile)
    if scores is None:
        return
    pid = profile["id"]
    recs = recommend(scores, profile["career_interests"])
    focus = st.selectbox("Career to detail (gaps and roadmap)", CAREER_NAMES, index=CAREER_NAMES.index(recs[0]["career"]),
                         key="report_focus")

    if st.button("Generate PDF report", key="gen_report"):
        try:
            db.ensure_roadmap_tasks(pid, focus, flatten_tasks(focus))
            tasks = db.get_roadmap_tasks(pid, focus)
            pdf = build_pdf_report(profile, scores, recs, focus, tasks, skill_gaps(focus, scores))
            st.session_state["report"] = {"pid": pid, "career": focus, "pdf": pdf}
        except Exception as exc:  # report must never crash the app
            st.error(f"Could not generate the report: {exc}")

    report = st.session_state.get("report")
    if report and report["pid"] == pid:
        st.success(f"Report ready for {report['career']}.")
        st.download_button("Download PDF report", report["pdf"], "career_compass_report.pdf", "application/pdf", key="dl_pdf")

    st.divider()
    st.subheader("Data exports")
    matches = pd.DataFrame([{"career": r["career"], "match_percent": r["match"], "label": r["label"]} for r in recs])
    c1, c2 = st.columns(2)
    c1.download_button("Assessment (CSV)", assessment_csv(scores), "career_compass_assessment.csv", "text/csv", key="rep_dl_a")
    c2.download_button("Career matches (CSV)", matches.to_csv(index=False).encode("utf-8"), "career_compass_matches.csv",
                       "text/csv", key="rep_dl_m")
