"""Plotly figure builders. Every chart is built from real application data."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from careers import CAREERS, SKILLS
from recommendations import skill_gaps

NAVY, BLUE, SKY, GREY = "#0B1F3A", "#2F6FED", "#9DBBF5", "#8A97AB"
_LAYOUT = dict(template="plotly_white", font=dict(family="Inter, Arial, sans-serif", color=NAVY),
               margin=dict(l=10, r=10, t=50, b=10), title_font_size=16)


def _finish(fig: go.Figure, height: int = 380) -> go.Figure:
    fig.update_layout(height=height, **_LAYOUT)
    return fig


def skill_bar_chart(scores: dict) -> go.Figure:
    df = pd.DataFrame({"Skill": list(SKILLS), "Rating": [scores.get(s, 0) for s in SKILLS]})
    fig = px.bar(df, x="Rating", y="Skill", orientation="h", range_x=[0, 5], text="Rating",
                 color="Rating", color_continuous_scale=[SKY, BLUE, NAVY], range_color=[1, 5],
                 title="Skill assessment (1 = beginner, 5 = expert)")
    fig.update_yaxes(autorange="reversed", title=None)
    fig.update_xaxes(title="Self-rating", dtick=1)
    fig.update_coloraxes(showscale=False)
    fig.update_traces(hovertemplate="%{y}: %{x}/5<extra></extra>")
    return _finish(fig)


def career_comparison_chart(recs: list[dict]) -> go.Figure:
    df = pd.DataFrame(recs)[["career", "skill_score", "interest_bonus", "match"]]
    fig = go.Figure()
    fig.add_bar(y=df["career"], x=df["skill_score"], name="Skill match", orientation="h", marker_color=BLUE)
    fig.add_bar(y=df["career"], x=df["interest_bonus"], name="Interest bonus", orientation="h", marker_color=SKY)
    fig.update_layout(barmode="stack", title="Career match comparison (%)", xaxis=dict(range=[0, 100], title="Match score (%)"),
                      yaxis=dict(autorange="reversed", title=None), legend=dict(orientation="h", y=-0.2))
    return _finish(fig)


def skill_gap_chart(career: str, scores: dict) -> go.Figure:
    gaps = skill_gaps(career, scores)
    skills = [g["skill"] for g in gaps]
    fig = go.Figure()
    fig.add_bar(x=skills, y=[g["current"] for g in gaps], name="Your rating", marker_color=BLUE)
    fig.add_bar(x=skills, y=[g["required"] for g in gaps], name=f"Required for {career}", marker_color=SKY)
    fig.update_layout(barmode="group", title=f"Skill gap: you vs {career}", yaxis=dict(range=[0, 5], dtick=1, title="Level"),
                      xaxis_title=None, legend=dict(orientation="h", y=-0.35))
    return _finish(fig, 420)


def career_radar_chart(career: str, scores: dict) -> go.Figure:
    req = CAREERS[career]["required_skills"]
    names = list(req)
    closed = names + names[:1]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=[req[n][0] for n in closed], theta=closed, name="Required", fill="toself",
                                  line_color=SKY))
    fig.add_trace(go.Scatterpolar(r=[scores.get(n, 0) for n in closed], theta=closed, name="You", fill="toself",
                                  line_color=BLUE))
    fig.update_layout(title=f"Career match overview: {career}", polar=dict(radialaxis=dict(range=[0, 5], dtick=1)),
                      legend=dict(orientation="h", y=-0.1))
    return _finish(fig, 440)


def progress_chart(progress_rows: list[dict]) -> go.Figure:
    df = pd.DataFrame(progress_rows)
    df["Completed (%)"] = (100 * df["done"] / df["total"]).round(1)
    df["Label"] = df["done"].astype(str) + "/" + df["total"].astype(str) + " tasks"
    fig = px.bar(df, x="career", y="Completed (%)", text="Label", range_y=[0, 100],
                 title="Learning roadmap progress", color_discrete_sequence=[BLUE])
    fig.update_xaxes(title=None)
    return _finish(fig, 340)
