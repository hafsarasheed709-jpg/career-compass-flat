"""PDF career report built with ReportLab (Platypus)."""
from __future__ import annotations

import io
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from assessment import level_label, summarize
from careers import CAREERS, SKILLS
from recommendations import METHODOLOGY

NAVY = colors.HexColor("#0B1F3A")
BLUE = colors.HexColor("#2F6FED")
LIGHT = colors.HexColor("#EAF1FF")
GREY = colors.HexColor("#5B6B82")


def _styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("t", parent=base["Title"], textColor=NAVY, fontSize=22, leading=26, alignment=0),
        "h1": ParagraphStyle("h1", parent=base["Heading1"], textColor=NAVY, fontSize=14, spaceBefore=14, spaceAfter=6, keepWithNext=1),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], textColor=BLUE, fontSize=11, spaceBefore=8, spaceAfter=4, keepWithNext=1),
        "body": ParagraphStyle("b", parent=base["BodyText"], fontSize=9.5, leading=13),
        "small": ParagraphStyle("s", parent=base["BodyText"], fontSize=8, leading=10, textColor=GREY),
        "cell": ParagraphStyle("c", parent=base["BodyText"], fontSize=8.5, leading=11),
    }


def _p(text, style) -> Paragraph:
    """Paragraph with user text escaped (ReportLab parses XML-like markup)."""
    return Paragraph(escape(str(text)), style)


def _table(data, col_widths, header=True) -> Table:
    table = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C9D6EA")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F8FF")]),
    ]
    if header:
        style += [("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                  ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")]
    table.setStyle(TableStyle(style))
    return table


def _score_bars(scores: dict, width=15.5 * cm) -> Drawing:
    row_h, label_w = 16, 5.2 * cm
    height = row_h * len(SKILLS) + 6
    drawing = Drawing(width, height)
    bar_max = width - label_w - 1.2 * cm
    for i, skill in enumerate(SKILLS):
        y = height - (i + 1) * row_h
        value = int(scores.get(skill, 0))
        drawing.add(String(0, y + 3, skill, fontName="Helvetica", fontSize=8.5, fillColor=NAVY))
        drawing.add(Rect(label_w, y + 1, bar_max, 9, fillColor=LIGHT, strokeColor=None))
        drawing.add(Rect(label_w, y + 1, bar_max * value / 5, 9, fillColor=BLUE, strokeColor=None))
        drawing.add(String(label_w + bar_max + 6, y + 3, f"{value}/5", fontName="Helvetica-Bold", fontSize=8.5, fillColor=NAVY))
    return drawing


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GREY)
    canvas.drawString(2 * cm, 1.2 * cm, "Career Compass AI - guidance report (rule-based, not a validated prediction)")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}")
    canvas.restoreState()


def next_steps(focus: str, gaps: list[dict], tasks: list[dict]) -> list[str]:
    steps = []
    for g in gaps[:3]:
        steps.append(f"Raise '{g['skill']}' from {g['current']} to {g['required']} (needed for {focus}).")
    pending = [t for t in tasks if not t["completed"]]
    if pending:
        steps.append(f"Start with the next roadmap task: {pending[0]['title']}.")
    steps.append(f"Choose one suggested project for {focus} and publish it on GitHub with a clear README.")
    steps.append("Re-run the skill assessment in 4-6 weeks to measure progress.")
    return steps


def build_pdf_report(profile: dict, scores: dict, recommendations: list[dict],
                     focus_career: str, roadmap_tasks: list[dict], gaps: list[dict]) -> bytes:
    """Return the report as PDF bytes. `recommendations` come from recommendations.recommend()."""
    s = _styles()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm,
                            bottomMargin=2 * cm, title="Career Compass AI Report", author="Career Compass AI")
    story = [_p("Career Compass AI", s["title"]),
             _p(f"Personal career report - generated {datetime.now():%d %B %Y}", s["small"]), Spacer(1, 8)]
    if profile.get("is_demo"):
        story.append(_p("Note: this report uses fictional demonstration data.", s["small"]))

    story.append(_p("1. Profile summary", s["h1"]))
    rows = [["Name", profile["display_name"]], ["Education", profile["education_level"]],
            ["Field of study", profile["field_of_study"]], ["Career goal", profile.get("career_goal") or "Not specified"],
            ["Technical skills", ", ".join(profile.get("technical_skills") or []) or "-"],
            ["Soft skills", ", ".join(profile.get("soft_skills") or []) or "-"],
            ["Career interests", ", ".join(profile.get("career_interests") or []) or "-"],
            ["Learning areas", ", ".join(profile.get("learning_areas") or []) or "-"]]
    story.append(_table([[_p(a, s["cell"]), _p(b, s["cell"])] for a, b in rows], [4 * cm, 13 * cm], header=False))

    summary = summarize(scores)
    story.append(_p("2. Skill assessment results", s["h1"]))
    story.append(_p(f"Average self-rating: {summary['average']:.2f} / 5 across {summary['assessed']} skills. "
                    f"Strengths: {', '.join(summary['strengths']) or 'none rated 4 or higher yet'}. "
                    f"Areas to improve: {', '.join(summary['improve']) or 'none rated 2 or lower'}.", s["body"]))
    story += [Spacer(1, 6), _score_bars(scores)]
    story.append(_table([["Skill", "Rating", "Level"]] +
                        [[_p(k, s["cell"]), str(scores[k]), level_label(scores[k])] for k in SKILLS if k in scores],
                        [9 * cm, 3 * cm, 5 * cm]))

    story.append(_p("3. Recommended career paths", s["h1"]))
    story.append(_table([["Rank", "Career", "Match", "Assessment"]] +
                        [[str(i + 1), _p(r["career"], s["cell"]), f"{r['match']:.1f}%", r["label"]]
                         for i, r in enumerate(recommendations)], [1.5 * cm, 8 * cm, 3 * cm, 4.5 * cm]))
    top = recommendations[0]["career"] if recommendations else focus_career
    story.append(Spacer(1, 4))
    story.append(_p(CAREERS[top]["overview"], s["body"]))

    story.append(_p("4. How matching works", s["h1"]))
    story.append(_p(METHODOLOGY, s["body"]))

    story.append(_p(f"5. Skill gaps for {focus_career}", s["h1"]))
    if gaps:
        story.append(_table([["Skill", "You", "Required", "Gap"]] +
                            [[_p(g["skill"], s["cell"]), str(g["current"]), str(g["required"]), str(g["gap"])] for g in gaps],
                            [9 * cm, 2.5 * cm, 3 * cm, 2.5 * cm]))
    else:
        story.append(_p("No gaps: your ratings meet or exceed every requirement for this career.", s["body"]))

    story.append(_p(f"6. Learning roadmap - {focus_career}", s["h1"]))
    if roadmap_tasks:
        done = sum(1 for t in roadmap_tasks if t["completed"])
        story.append(_p(f"Progress: {done} of {len(roadmap_tasks)} tasks completed "
                        f"({100 * done / len(roadmap_tasks):.0f}%).", s["body"]))
        modules: dict[str, list[dict]] = {}
        for t in roadmap_tasks:
            modules.setdefault(t["module"], []).append(t)
        for n, (name, items) in enumerate(modules.items(), 1):
            block = [_p(f"Module {n}: {name}", s["h2"]),
                     _table([[("[x]" if t["completed"] else "[ ]"), _p(t["task_type"], s["cell"]), _p(t["title"], s["cell"])]
                             for t in items], [1.2 * cm, 3.2 * cm, 12.6 * cm], header=False)]
            story.append(KeepTogether(block))
    else:
        story.append(_p("Open the Learning Roadmap page to start this career's roadmap.", s["body"]))
    story.append(_p("Suggested portfolio projects", s["h2"]))
    for proj in CAREERS[focus_career]["projects"]:
        story.append(_p(f"- {proj}", s["body"]))
    story.append(_p("Tools: " + ", ".join(CAREERS[focus_career]["tools"]), s["small"]))

    story.append(_p("7. Suggested next steps", s["h1"]))
    for i, step in enumerate(next_steps(focus_career, gaps, roadmap_tasks), 1):
        story.append(_p(f"{i}. {step}", s["body"]))

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buf.getvalue()
