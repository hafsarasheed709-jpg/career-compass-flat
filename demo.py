"""Fictional demonstration profile (clearly labelled as demo data)."""
from __future__ import annotations


import database as db
from recommendations import refresh_saved_recommendations

SAMPLE_SCORES = {
    "Python Programming": 4, "Mathematics & Statistics": 3, "Data Analysis": 4, "SQL & Databases": 3,
    "Machine Learning": 2, "Data Visualization": 4, "Communication": 3, "Problem Solving": 4,
    "Software Development": 2,
}

DEMO_PROFILE = {
    "display_name": "Demo Student (fictional)",
    "education_level": "Undergraduate (in progress)",
    "field_of_study": "Mathematics",
    "technical_skills": ["Python", "Excel", "Pandas"],
    "soft_skills": ["Communication", "Critical thinking"],
    "career_interests": ["Data Analyst", "Machine Learning Engineer"],
    "career_goal": "Start a career in data and AI after graduation (fictional example).",
    "learning_areas": ["Data analysis", "Machine learning"],
}


def read_sample_scores() -> dict[str, int]:
    return dict(SAMPLE_SCORES)


def load_demo_profile(db_path=None) -> int:
    pid = db.create_profile(DEMO_PROFILE, is_demo=True, db_path=db_path)
    db.save_assessment(pid, read_sample_scores(), db_path)
    refresh_saved_recommendations(pid, db_path)
    return pid
