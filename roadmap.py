"""Personalised learning-roadmap construction."""
from __future__ import annotations

from careers import CAREERS


def task_key(module_index: int, task_index: int) -> str:
    return f"m{module_index + 1}-t{task_index + 1}"


def module_priority(skill: str, career: str, scores: dict | None) -> str:
    """Flag modules that target the learner's biggest gaps for this career."""
    if not scores or skill not in scores:
        return "Core"
    required = CAREERS[career]["required_skills"].get(skill, (3, 1))[0]
    gap = required - int(scores[skill])
    if gap >= 2:
        return "High priority"
    if gap == 1:
        return "Medium priority"
    return "Strengthen"


def build_roadmap(career: str, scores: dict | None = None) -> list[dict]:
    """Ordered modules; order follows the recommended study sequence."""
    modules = []
    for mi, mod in enumerate(CAREERS[career]["roadmap"]):
        modules.append({
            "index": mi + 1, "module": mod["module"], "skill": mod["skill"],
            "priority": module_priority(mod["skill"], career, scores),
            "tasks": [
                {"key": task_key(mi, ti), "type": ttype, "title": title}
                for ti, (ttype, title) in enumerate(mod["tasks"])
            ],
        })
    return modules


def flatten_tasks(career: str) -> list[dict]:
    rows = []
    for mod in build_roadmap(career):
        for t in mod["tasks"]:
            rows.append({"key": t["key"], "module": mod["module"], "type": t["type"], "title": t["title"]})
    return rows


def progress(tasks: list[dict]) -> tuple[int, int, float]:
    """(done, total, fraction 0-1) for rows that carry a 'completed' flag."""
    total = len(tasks)
    done = sum(1 for t in tasks if t["completed"])
    return done, total, (done / total if total else 0.0)
