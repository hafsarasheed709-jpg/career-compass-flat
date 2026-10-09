"""Skill assessment logic: validation, summaries and CSV export."""
from __future__ import annotations

import pandas as pd

from careers import LEVEL_LABELS, SKILLS


def validate_scores(scores: dict) -> list[str]:
    errors = []
    for skill in SKILLS:
        if skill not in scores:
            errors.append(f"Missing rating for '{skill}'.")
            continue
        value = scores[skill]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or int(value) != value:
            errors.append(f"Rating for '{skill}' must be a whole number.")
        elif not 1 <= int(value) <= 5:
            errors.append(f"Rating for '{skill}' must be between 1 and 5.")
    unknown = set(scores) - set(SKILLS)
    if unknown:
        errors.append("Unknown skills: " + ", ".join(sorted(unknown)))
    return errors


def level_label(score: float) -> str:
    return LEVEL_LABELS[min(5, max(1, round(score)))]


def scores_to_df(scores: dict) -> pd.DataFrame:
    rows = [{"Skill": s, "Score": int(scores[s]), "Level": level_label(scores[s])} for s in SKILLS if s in scores]
    return pd.DataFrame(rows, columns=["Skill", "Score", "Level"])


def summarize(scores: dict) -> dict:
    """Average, strengths (>=4) and improvement areas (<=2), lowest first."""
    if not scores:
        return {"average": 0.0, "assessed": 0, "strengths": [], "improve": []}
    ordered = sorted(scores.items(), key=lambda kv: (kv[1], kv[0]))
    return {
        "average": round(sum(scores.values()) / len(scores), 2),
        "assessed": len(scores),
        "strengths": [s for s, v in reversed(ordered) if v >= 4],
        "improve": [s for s, v in ordered if v <= 2],
    }


def assessment_csv(scores: dict) -> bytes:
    return scores_to_df(scores).to_csv(index=False).encode("utf-8")
