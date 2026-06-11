#!/usr/bin/env python3
"""Build ONE combined PDF folding together every skill view.

Sections:
  1. Title page + summary + installation history
  2. Part I  — Skills by Category (functional grouping)
  3. Part II — Skills A-Z (full alphabetical listing)

Reuses the category rules from generate_skills_by_category.py so the two
documents never drift. Pure-Python via reportlab.
"""
from __future__ import annotations

import re
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_skills_by_category import (  # noqa: E402
    parse_frontmatter, clean, categorize, RULES, DEFAULT,
)

from reportlab.lib import colors  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # noqa: E402
from reportlab.lib.units import mm  # noqa: E402
from reportlab.platypus import (  # noqa: E402
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)

SKILLS_DIR = Path(".claude/skills")
OUT = Path("INSTALLED_SKILLS_COMBINED.pdf")
MAX_LEN = 200

RISK_COLORS = {
    "safe": colors.HexColor("#1a7f37"),
    "none": colors.HexColor("#57606a"),
    "unknown": colors.HexColor("#9a6700"),
    "critical": colors.HexColor("#cf222e"),
    "high": colors.HexColor("#cf222e"),
}


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
    return uniq


# ---- styles ----
styles = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=styles["Title"], fontSize=26, spaceAfter=6)
PART = ParagraphStyle("PART", parent=styles["Title"], fontSize=22,
                      textColor=colors.HexColor("#0969da"), spaceAfter=4, alignment=1)
SUB = ParagraphStyle("SUB", parent=styles["Normal"], fontSize=11,
                     textColor=colors.HexColor("#57606a"), spaceAfter=2)
SEC = ParagraphStyle("SEC", parent=styles["Heading1"], fontSize=15,
                     textColor=colors.HexColor("#0969da"), spaceBefore=8, spaceAfter=4)
NAME = ParagraphStyle("NAME", fontName="Helvetica-Bold", fontSize=8.5, leading=10.5)
DESC = ParagraphStyle("DESC", fontName="Helvetica", fontSize=8.5, leading=10.5)
RISK = ParagraphStyle("RISK", fontName="Helvetica", fontSize=8, leading=10, alignment=1)


def skill_table(rows, with_risk: bool):
    """Build a paginating table flowable for a list of (name, desc, risk)."""
    if with_risk:
        header = [Paragraph("<b>Skill</b>", DESC), Paragraph("<b>Description</b>", DESC),
                  Paragraph("<b>Risk</b>", RISK)]
        widths = [42 * mm, 113 * mm, 16 * mm]
    else:
        header = [Paragraph("<b>Skill</b>", DESC), Paragraph("<b>Description</b>", DESC)]
        widths = [44 * mm, 127 * mm]
    data = [header]
    sty = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f6f8fa")),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#eaeef2")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]
    for i, row in enumerate(rows, start=1):
        name, desc = row[0], row[1]
        cells = [Paragraph(esc(name), NAME), Paragraph(esc(desc), DESC)]
        if with_risk:
            risk = row[2]
            rc = RISK_COLORS.get(risk.lower(), colors.HexColor("#57606a"))
            cells.append(Paragraph(esc(risk), RISK))
            sty.append(("TEXTCOLOR", (2, i), (2, i), rc))
        data.append(cells)
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle(sty))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#57606a"))
    canvas.drawString(18 * mm, 10 * mm, "Installed Skills — Combined Catalog")
    canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def main():
    uniq = collect()
    today = datetime.date.today().isoformat()

    doc = SimpleDocTemplate(
        str(OUT), pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm, topMargin=18 * mm, bottomMargin=18 * mm,
        title="Installed Skills — Combined Catalog", author="skill repository",
    )
    flow = []

    # ===== title page =====
    flow.append(Spacer(1, 38 * mm))
    flow.append(Paragraph("Installed Skills", H1))
    flow.append(Paragraph("Combined Catalog — by category and alphabetical", SUB))
    flow.append(Spacer(1, 8 * mm))
    meta = [
        ["Total skills", str(len(uniq))],
        ["Source", "antigravity-awesome-skills (catalog v12.3.0) + ui-ux-pro-max"],
        ["Install path", ".claude/skills/"],
        ["Generated", today],
        ["Contents", "Installation history · Part I: by category · Part II: A–Z"],
    ]
    mt = Table(meta, colWidths=[34 * mm, 137 * mm])
    mt.setStyle(TableStyle([
        ("FONT", (0, 0), (0, -1), "Helvetica-Bold", 10),
        ("FONT", (1, 0), (1, -1), "Helvetica", 10),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, colors.HexColor("#d0d7de")),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    flow.append(mt)
    flow.append(Spacer(1, 10 * mm))

    flow.append(Paragraph("Installation History", SEC))
    hist = [
        [Paragraph("<b>Session</b>", DESC), Paragraph("<b>Commit</b>", DESC),
         Paragraph("<b>What was installed</b>", DESC)],
        [Paragraph("1", DESC), Paragraph("<font face='Courier'>ce5f832</font>", DESC),
         Paragraph("<b>ui-ux-pro-max</b> — UI/UX Pro Max design intelligence "
                   "(50+ styles, 97 palettes, 57 font pairings, 99 UX guidelines, 25 chart types, 9 stacks).", DESC)],
        [Paragraph("2", DESC), Paragraph("<font face='Courier'>e0d93e2</font>", DESC),
         Paragraph("<b>antigravity-awesome-skills</b> library — the full catalog (v12.3.0); "
                   "added the remaining skills and updated ui-ux-pro-max.", DESC)],
    ]
    ht = Table(hist, colWidths=[18 * mm, 24 * mm, 129 * mm])
    ht.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f6f8fa")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d0d7de")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    flow.append(ht)
    flow.append(PageBreak())

    # ===== Part I: by category =====
    cats: dict[str, list] = {}
    for name, desc, risk in uniq:
        cats.setdefault(categorize(name, desc), []).append((name, desc, risk))
    for c in cats:
        cats[c].sort(key=lambda r: r[0].lower())
    cat_order = [c for c, _ in RULES if c in cats]
    if DEFAULT in cats:
        cat_order.append(DEFAULT)

    flow.append(Spacer(1, 4 * mm))
    flow.append(Paragraph("Part I", PART))
    flow.append(Paragraph("Skills by Category", SUB))
    flow.append(Spacer(1, 6 * mm))
    ov = [[Paragraph("<b>Category</b>", DESC), Paragraph("<b>Skills</b>", RISK)]]
    for c in cat_order:
        ov.append([Paragraph(esc(c), DESC), Paragraph(str(len(cats[c])), RISK)])
    ov.append([Paragraph("<b>Total</b>", DESC), Paragraph(f"<b>{len(uniq)}</b>", RISK)])
    ovt = Table(ov, colWidths=[140 * mm, 31 * mm])
    ovt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f6f8fa")),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#eaeef2")),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ]))
    flow.append(ovt)
    flow.append(PageBreak())

    for c in cat_order:
        flow.append(Paragraph(f"{esc(c)} &nbsp;<font size=9 color='#57606a'>({len(cats[c])})</font>", SEC))
        flow.append(skill_table(cats[c], with_risk=True))
        flow.append(Spacer(1, 4 * mm))

    # ===== Part II: alphabetical =====
    flow.append(PageBreak())
    flow.append(Spacer(1, 4 * mm))
    flow.append(Paragraph("Part II", PART))
    flow.append(Paragraph("Skills A–Z", SUB))
    flow.append(Spacer(1, 6 * mm))

    alpha = sorted(uniq, key=lambda r: r[0].lower())
    groups: dict[str, list] = {}
    for name, desc, risk in alpha:
        ch = name[0].upper()
        groups.setdefault(ch if ch.isalpha() else "#", []).append((name, desc, risk))
    letter_order = (["#"] if "#" in groups else []) + [c for c in map(chr, range(65, 91)) if c in groups]
    for key in letter_order:
        flow.append(Paragraph(f"{key} &nbsp;<font size=9 color='#57606a'>({len(groups[key])})</font>", SEC))
        flow.append(skill_table(groups[key], with_risk=True))
        flow.append(Spacer(1, 4 * mm))

    doc.build(flow, onFirstPage=footer, onLaterPages=footer)
    print(f"Wrote {OUT} ({OUT.stat().st_size // 1024} KB) — {len(uniq)} skills, "
          f"{len(cat_order)} categories.")


if __name__ == "__main__":
    main()
