#!/usr/bin/env python3
"""Build a downloadable PDF catalog of all installed skills.

Parses every .claude/skills/**/SKILL.md, then renders a clean, paginated PDF
with a title page, installation history, and an alphabetised table of all
skills (name, short description, risk). Pure-Python via reportlab.
"""
from __future__ import annotations

import re
import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)

SKILLS_DIR = Path(".claude/skills")
OUT = Path("INSTALLED_SKILLS.pdf")
MAX_LEN = 240


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    data, key, buf = {}, None, []
    for line in text[3:end].splitlines():
        m = re.match(r"^([A-Za-z0-9_]+):\s?(.*)$", line)
        if m:
            if key is not None:
                data[key] = " ".join(buf).strip()
            key, buf = m.group(1), [m.group(2)]
        elif key is not None and line.strip():
            buf.append(line.strip())
    if key is not None:
        data[key] = " ".join(buf).strip()
    return data


def clean(val: str) -> str:
    val = val.strip()
    if len(val) >= 2 and val[0] in "\"'" and val[-1] == val[0]:
        val = val[1:-1]
    return val.strip()


def shorten(desc: str) -> str:
    desc = re.sub(r"\s+", " ", clean(desc))
    if not desc:
        return "(no description)"
    first = re.split(r"(?<=[.!?])\s", desc, maxsplit=1)[0]
    if 0 < len(first) <= MAX_LEN:
        return first.rstrip()
    return desc if len(desc) <= MAX_LEN else desc[: MAX_LEN - 1].rstrip() + "…"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def collect():
    rows = []
    for path in sorted(SKILLS_DIR.glob("**/SKILL.md")):
        fm = parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        name = clean(fm.get("name", "")) or path.parent.name
        rows.append((name, shorten(fm.get("description", "")), clean(fm.get("risk", "")) or "—"))
    seen, uniq = set(), []
    for r in rows:
        if r[0].lower() in seen:
            continue
        seen.add(r[0].lower())
        uniq.append(r)
    uniq.sort(key=lambda r: r[0].lower())
    return uniq


RISK_COLORS = {
    "safe": colors.HexColor("#1a7f37"),
    "none": colors.HexColor("#57606a"),
    "unknown": colors.HexColor("#9a6700"),
    "critical": colors.HexColor("#cf222e"),
    "high": colors.HexColor("#cf222e"),
}


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#57606a"))
    canvas.drawString(18 * mm, 10 * mm, "Installed Skills Catalog")
    canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def main():
    uniq = collect()
    today = datetime.date.today().isoformat()

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Title"], fontSize=26, spaceAfter=6)
    sub = ParagraphStyle("sub", parent=styles["Normal"], fontSize=11,
                         textColor=colors.HexColor("#57606a"), spaceAfter=2)
    letter = ParagraphStyle("letter", parent=styles["Heading1"], fontSize=15,
                            textColor=colors.HexColor("#0969da"), spaceBefore=8, spaceAfter=4)
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=11, leading=15)
    name_st = ParagraphStyle("name", fontName="Helvetica-Bold", fontSize=8.5, leading=10.5)
    desc_st = ParagraphStyle("desc", fontName="Helvetica", fontSize=8.5, leading=10.5)
    risk_st = ParagraphStyle("risk", fontName="Helvetica", fontSize=8, leading=10, alignment=1)

    doc = SimpleDocTemplate(
        str(OUT), pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm, topMargin=18 * mm, bottomMargin=18 * mm,
        title="Installed Skills Catalog", author="skill repository",
    )
    flow = []

    # ---- title page ----
    flow.append(Spacer(1, 40 * mm))
    flow.append(Paragraph("Installed Skills Catalog", h1))
    flow.append(Paragraph(f"{len(uniq)} agentic skills installed under <font face='Courier'>.claude/skills/</font>", sub))
    flow.append(Spacer(1, 8 * mm))
    meta = [
        ["Total skills", str(len(uniq))],
        ["Source", "antigravity-awesome-skills (catalog v12.3.0)"],
        ["Install path", ".claude/skills/"],
        ["Generated", today],
    ]
    mt = Table(meta, colWidths=[40 * mm, 120 * mm])
    mt.setStyle(TableStyle([
        ("FONT", (0, 0), (0, -1), "Helvetica-Bold", 10),
        ("FONT", (1, 0), (1, -1), "Helvetica", 10),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#24292f")),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, colors.HexColor("#d0d7de")),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    flow.append(mt)
    flow.append(Spacer(1, 10 * mm))

    flow.append(Paragraph("Installation History", letter))
    hist = [
        [Paragraph("<b>Session</b>", desc_st), Paragraph("<b>Commit</b>", desc_st),
         Paragraph("<b>What was installed</b>", desc_st)],
        [Paragraph("1", desc_st), Paragraph("<font face='Courier'>ce5f832</font>", desc_st),
         Paragraph("<b>ui-ux-pro-max</b> — UI/UX Pro Max design intelligence "
                   "(50+ styles, 97 palettes, 57 font pairings, 99 UX guidelines, 25 chart types, 9 stacks). Installed as a single skill.", desc_st)],
        [Paragraph("2", desc_st), Paragraph("<font face='Courier'>e0d93e2</font>", desc_st),
         Paragraph("<b>antigravity-awesome-skills</b> library — the full catalog (v12.3.0). "
                   "Added the remaining skills and updated ui-ux-pro-max to the catalog version.", desc_st)],
    ]
    ht = Table(hist, colWidths=[18 * mm, 24 * mm, 118 * mm])
    ht.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f6f8fa")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d0d7de")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    flow.append(ht)
    flow.append(PageBreak())

    # ---- skills by letter ----
    groups: dict[str, list] = {}
    for name, desc, risk in uniq:
        c = name[0].upper()
        groups.setdefault(c if c.isalpha() else "#", []).append((name, desc, risk))
    order = (["#"] if "#" in groups else []) + [c for c in map(chr, range(65, 91)) if c in groups]

    header = [Paragraph("<b>Skill</b>", desc_st), Paragraph("<b>Description</b>", desc_st),
              Paragraph("<b>Risk</b>", risk_st)]
    for key in order:
        flow.append(Paragraph(f"{key} &nbsp;<font size=9 color='#57606a'>({len(groups[key])})</font>", letter))
        data = [header]
        stycmds = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f6f8fa")),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#eaeef2")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ]
        for i, (name, desc, risk) in enumerate(groups[key], start=1):
            rc = RISK_COLORS.get(risk.lower(), colors.HexColor("#57606a"))
            data.append([
                Paragraph(esc(name), name_st),
                Paragraph(esc(desc), desc_st),
                Paragraph(esc(risk), risk_st),
            ])
            stycmds.append(("TEXTCOLOR", (2, i), (2, i), rc))
        t = Table(data, colWidths=[42 * mm, 113 * mm, 16 * mm], repeatRows=1)
        t.setStyle(TableStyle(stycmds))
        flow.append(t)
        flow.append(Spacer(1, 4 * mm))

    doc.build(flow, onFirstPage=footer, onLaterPages=footer)
    print(f"Wrote {OUT} ({OUT.stat().st_size // 1024} KB) with {len(uniq)} skills.")


if __name__ == "__main__":
    main()
