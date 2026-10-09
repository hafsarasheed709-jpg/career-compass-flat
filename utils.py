"""Small, framework-independent helpers (validation, formatting)."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone

NAME_PATTERN = re.compile(r"^[A-Za-z0-9 .,'\-_()]+$")
MAX_GOAL_LENGTH = 250


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def to_json_list(values) -> str:
    return json.dumps([str(v).strip() for v in (values or []) if str(v).strip()])


def from_json_list(text) -> list[str]:
    if not text:
        return []
    try:
        data = json.loads(text)
    except (TypeError, ValueError):
        return []
    return [str(v) for v in data] if isinstance(data, list) else []


def validate_profile(data: dict) -> list[str]:
    """Return a list of human-readable errors (empty list = valid)."""
    errors: list[str] = []
    name = (data.get("display_name") or "").strip()
    if len(name) < 2 or len(name) > 50:
        errors.append("Display name must be between 2 and 50 characters.")
    elif not NAME_PATTERN.match(name):
        errors.append("Display name may only contain letters, numbers, spaces and . , ' - _ ( ).")
    if not (data.get("education_level") or "").strip():
        errors.append("Please select an education level.")
    field = (data.get("field_of_study") or "").strip()
    if len(field) < 2 or len(field) > 80:
        errors.append("Field of study must be between 2 and 80 characters.")
    goal = (data.get("career_goal") or "").strip()
    if len(goal) > MAX_GOAL_LENGTH:
        errors.append(f"Career goal must be at most {MAX_GOAL_LENGTH} characters.")
    return errors


def percent(value: float, digits: int = 0) -> str:
    return f"{value:.{digits}f}%"


def csv_safe(value) -> str:
    """Neutralise spreadsheet formula injection in exported text cells."""
    text = str(value)
    return "'" + text if text[:1] in ("=", "+", "-", "@") else text
