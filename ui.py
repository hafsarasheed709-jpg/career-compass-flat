"""Streamlit UI helpers shared by all views (styling, state, empty states)."""
from __future__ import annotations

import html

import streamlit as st

import database as db

CSS = """
<style>
:root { --navy:#0B1F3A; --blue:#2F6FED; --sky:#EAF1FF; --grey:#5B6B82; }
.block-container { padding-top: 2rem; max-width: 1200px; }
h1, h2, h3 { color: var(--navy); letter-spacing: -0.01em; }
[data-testid="stSidebar"] { background: var(--navy); }
[data-testid="stSidebar"] * { color: #E8EEF9; }
[data-testid="stSidebar"] [data-baseweb="select"] * { color: var(--navy); }
.cc-card { background:#fff; border:1px solid #D9E3F5; border-left:4px solid var(--blue); border-radius:10px;
           padding:14px 16px; box-shadow:0 1px 3px rgba(11,31,58,.06); }
.cc-card .label { color:var(--grey); font-size:.78rem; text-transform:uppercase; letter-spacing:.04em; }
.cc-card .value { color:var(--navy); font-size:1.7rem; font-weight:700; line-height:1.2; }
.cc-card .sub { color:var(--grey); font-size:.8rem; }
.cc-badge { display:inline-block; background:var(--sky); color:var(--blue); border-radius:999px;
            padding:2px 10px; font-size:.75rem; font-weight:600; margin-right:6px; }
.cc-banner { background:var(--sky); border-radius:10px; padding:14px 18px; color:var(--navy); }
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def metric_card(label: str, value: str, sub: str = "", help_text: str = "") -> None:
    title = f' title="{html.escape(help_text, quote=True)}"' if help_text else ""
    st.markdown(
        f'<div class="cc-card"{title}><div class="label">{html.escape(label)}</div>'
        f'<div class="value">{html.escape(value)}</div><div class="sub">{html.escape(sub)}</div></div>',
        unsafe_allow_html=True,
    )


def badge(text: str) -> str:
    return f'<span class="cc-badge">{html.escape(text)}</span>'


def page_header(title: str, subtitle: str = "") -> None:
    st.title(title)
    if subtitle:
        st.caption(subtitle)


def navigate(page: str) -> None:
    """Switch page on the next run (safe to call from a button handler)."""
    st.session_state["pending_page"] = page
    st.rerun()


def active_profile_id() -> int | None:
    return st.session_state.get("active_profile_id")


def set_active_profile(profile_id: int | None) -> None:
    st.session_state["pending_profile_id"] = profile_id
    st.rerun()


def empty_state(message: str, button_label: str | None = None, target: str | None = None) -> None:
    st.markdown(f'<div class="cc-banner">{html.escape(message)}</div>', unsafe_allow_html=True)
    if button_label and target and st.button(button_label, key=f"empty_{target}"):
        navigate(target)


def require_profile() -> dict | None:
    """Return the active profile or show a friendly empty state."""
    pid = active_profile_id()
    profile = db.get_profile(pid) if pid else None
    if profile is None:
        empty_state("No profile selected yet. Create your profile (or load the fictional demo) to get started.",
                    "Create profile", "Profile")
    return profile


def require_assessment(profile: dict) -> dict | None:
    scores = db.get_assessment(profile["id"])
    if not scores:
        empty_state("You have not completed the skill assessment yet. It takes about two minutes.",
                    "Start assessment", "Skill Assessment")
        return None
    return scores


def flash(message: str, kind: str = "success") -> None:
    """Queue a message that survives the next st.rerun()."""
    st.session_state["flash"] = (kind, message)


def show_flash() -> None:
    item = st.session_state.pop("flash", None)
    if item:
        kind, message = item
        getattr(st, kind if kind in ("success", "info", "warning", "error") else "info")(message)
