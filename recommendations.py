"""Transparent, rule-based career recommendation engine.

This is NOT a machine-learning model. Scores are a weighted skill-coverage
measure, explained in METHODOLOGY, and must not be read as predictions of
job success.
"""
from __future__ import annotations

from careers import CAREERS

INTEREST_BONUS = 5.0

METHODOLOGY = (
    "Career matches are calculated with a transparent rule-based formula, not a trained "
    "machine-learning model. Each career lists the skills it needs, a required level (1-5) "
    "and an importance weight (1-3). For every skill, coverage = min(your rating / required "
    "level, 1). The skill score is the weighted average of coverage across the career's "
    f"skills, as a percentage. If you listed the career among your interests, {INTEREST_BONUS:.0f} "
    "points are added (maximum 100). Required levels and weights are editorial estimates based "
    "on typical entry-level roles, so treat results as guidance for exploration, not as a "
    "validated prediction of job success."
)


def match_label(score: float) -> str:
    if score >= 80:
        return "Strong match"
    if score >= 60:
        return "Good match"
    if score >= 40:
        return "Developing"
    return "Early stage"


def skill_gaps(career: str, scores: dict) -> list[dict]:
    """Per-skill comparison, largest weighted gap first."""
    rows = []
    for skill, (required, weight) in CAREERS[career]["required_skills"].items():
        current = int(scores.get(skill, 0))
        gap = max(required - current, 0)
        rows.append({
            "skill": skill, "current": current, "required": required,
            "gap": gap, "weight": weight, "priority": gap * weight,
        })
    return sorted(rows, key=lambda r: (-r["priority"], -r["gap"], r["skill"]))


def score_career(career: str, scores: dict, interests=()) -> dict:
    requirements = CAREERS[career]["required_skills"]
    total_weight = sum(w for _, w in requirements.values())
    weighted = sum(w * min(int(scores.get(s, 0)) / req, 1.0) for s, (req, w) in requirements.items())
    skill_score = 100.0 * weighted / total_weight
    bonus = INTEREST_BONUS if career in set(interests or ()) else 0.0
    match = round(min(100.0, skill_score + bonus), 1)
    return {
        "career": career, "skill_score": round(skill_score, 1), "interest_bonus": bonus,
        "match": match, "label": match_label(match),
        "gaps": [g for g in skill_gaps(career, scores) if g["gap"] > 0],
    }


def recommend(scores: dict, interests=()) -> list[dict]:
    """All careers ranked by match (ties broken alphabetically)."""
    results = [score_career(c, scores, interests) for c in CAREERS]
    return sorted(results, key=lambda r: (-r["match"], r["career"]))


def refresh_saved_recommendations(profile_id: int, db_path=None) -> list[dict]:
    """Recompute from saved data and persist; returns [] if nothing is assessed."""
    import database as db

    scores = db.get_assessment(profile_id, db_path)
    if not scores:
        db.save_recommendations(profile_id, [], db_path)
        return []
    profile = db.get_profile(profile_id, db_path)
    recs = recommend(scores, profile["career_interests"] if profile else ())
    db.save_recommendations(profile_id, recs, db_path)
    return recs
