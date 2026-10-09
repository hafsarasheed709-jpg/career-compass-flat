import streamlit as st

import ui
from recommendations import METHODOLOGY


def render() -> None:
    ui.page_header("Help & About", "What Career Compass AI does - and what it does not.")
    st.markdown(
        """
**Career Compass AI** helps students and fresh graduates assess their skills, compare career paths,
find skill gaps, follow a learning roadmap and track progress.

### How to use it
1. **Profile** - create a profile (or load the fictional demo).
2. **Skill Assessment** - rate nine skills from 1 to 5.
3. **Career Explorer** - search careers and see your gaps.
4. **Learning Roadmap** - tick tasks; progress is saved.
5. **Analytics** and **Career Report** - interactive charts, PDF and CSV downloads.
"""
    )
    st.subheader("How recommendations work")
    st.write(METHODOLOGY)
    st.info("This app does **not** use machine learning. No suitable, documented dataset is bundled, so a "
            "transparent rule-based engine is used instead.")
    st.subheader("Privacy")
    st.write("Only the information you type is stored, in a local SQLite database. No passwords, ID numbers or "
             "payment details are collected. On shared deployments anyone can see every profile in the selector, "
             "so avoid real names.")
    st.subheader("Limitations")
    st.markdown("- Ratings are self-assessments and may be biased.\n- Career requirements are editorial estimates.\n"
                "- Results are guidance, not predictions of job success.\n- Demo data is fictional.")
