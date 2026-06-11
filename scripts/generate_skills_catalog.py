#!/usr/bin/env python3
"""Generate a clean, structured catalog of all installed skills.

Parses the YAML frontmatter of every .claude/skills/**/SKILL.md, extracts the
name + description, trims each description to a short one-liner, and writes a
grouped, alphabetised markdown document with a summary and table of contents.
"""
from __future__ import annotations

import os
import re
import datetime
from pathlib import Path

SKILLS_DIR = Path(".claude/skills")
OUT = Path("INSTALLED_SKILLS.md")
MAX_LEN = 180  # max chars for a "short" description


def parse_frontmatter(text: str) -> dict:
    """Return a dict of the top-level YAML frontmatter keys (string values)."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]
    data: dict[str, str] = {}
    key = None
    buf: list[str] = []
    for line in block.splitlines():
        m = re.match(r"^([A-Za-z0-9_]+):\s?(.*)$", line)
        if m:
            if key is not None:
                data[key] = " ".join(buf).strip()
            key, val = m.group(1), m.group(2)
            buf = [val]
        elif key is not None and line.strip():
            buf.append(line.strip())
    if key is not None:
        data[key] = " ".join(buf).strip()
    return data


def clean(val: str) -> str:
    val = val.strip()
    # strip matching surrounding quotes
    if len(val) >= 2 and val[0] in "\"'" and val[-1] == val[0]:
        val = val[1:-1]
    return val.strip()


def shorten(desc: str) -> str:
    desc = clean(desc)
    desc = re.sub(r"\s+", " ", desc)
    if not desc:
        return "_(no description)_"
    # prefer the first sentence if it is reasonably sized
    first = re.split(r"(?<=[.!?])\s", desc, maxsplit=1)[0]
    if 0 < len(first) <= MAX_LEN:
        return first.rstrip()
    if len(desc) <= MAX_LEN:
        return desc
    return desc[: MAX_LEN - 1].rstrip() + "…"


def md_escape(s: str) -> str:
    return s.replace("|", "\\|")


def main() -> None:
    rows: list[tuple[str, str, str]] = []  # (name, short_desc, risk)
    for path in sorted(SKILLS_DIR.glob("**/SKILL.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(text)
        name = clean(fm.get("name", "")) or path.parent.name
        desc = shorten(fm.get("description", ""))
        risk = clean(fm.get("risk", "")) or "—"
        rows.append((name, desc, risk))

    # de-dup by name, keep first
    seen: set[str] = set()
    uniq: list[tuple[str, str, str]] = []
    for r in rows:
        if r[0].lower() in seen:
            continue
        seen.add(r[0].lower())
        uniq.append(r)
    uniq.sort(key=lambda r: r[0].lower())

    # group by first character (digits grouped under "#")
    groups: dict[str, list[tuple[str, str, str]]] = {}
    for name, desc, risk in uniq:
        c = name[0].upper()
        key = c if c.isalpha() else "#"
        groups.setdefault(key, []).append((name, desc, risk))

    order = (["#"] if "#" in groups else []) + [c for c in map(chr, range(65, 91)) if c in groups]

    today = datetime.date.today().isoformat()
    lines: list[str] = []
    lines.append("# Installed Skills Catalog")
    lines.append("")
    lines.append(
        f"A structured reference for every agentic skill installed in this repository "
        f"under `.claude/skills/`."
    )
    lines.append("")
    lines.append("| | |")
    lines.append("|---|---|")
    lines.append(f"| **Total skills** | {len(uniq)} |")
    lines.append("| **Source** | [antigravity-awesome-skills](https://github.com/sickn33/antigravity-awesome-skills) (catalog v12.3.0) |")
    lines.append(f"| **Install path** | `.claude/skills/` |")
    lines.append(f"| **Generated** | {today} |")
    lines.append("")
    lines.append("> Skills are invoked via the Skill tool or `@skill-name`. The `Risk` column reflects each skill's self-declared `risk` label (`safe`, `unknown`, etc.).")
    lines.append("")

    # installation history (provenance across sessions)
    lines.append("## Installation History")
    lines.append("")
    lines.append("Skills in this repository were installed across multiple sessions:")
    lines.append("")
    lines.append("| Session | Commit | What was installed |")
    lines.append("|---|---|---|")
    lines.append(
        "| 1 | `ce5f832` | **`ui-ux-pro-max`** — UI/UX Pro Max design intelligence "
        "(50+ styles, 97 color palettes, 57 font pairings, 99 UX guidelines, 25 chart "
        "types across 9 stacks). Installed as a single skill. |"
    )
    lines.append(
        "| 2 | `e0d93e2` | **antigravity-awesome-skills** library — the full catalog "
        "(v12.3.0). Added the remaining skills and updated `ui-ux-pro-max` to the "
        "catalog version. |"
    )
    lines.append("")
    lines.append(
        "Every skill from both sessions is included in the alphabetical listing below "
        f"(**{len(uniq)}** skills total)."
    )
    lines.append("")

    # table of contents
    lines.append("## Index")
    lines.append("")
    toc = []
    for key in order:
        anchor = "section-" + ("digit" if key == "#" else key.lower())
        toc.append(f"[{key}](#{anchor}) ({len(groups[key])})")
    lines.append(" · ".join(toc))
    lines.append("")

    for key in order:
        anchor = "section-" + ("digit" if key == "#" else key.lower())
        lines.append(f'<a id="{anchor}"></a>')
        lines.append(f"## {key}")
        lines.append("")
        lines.append("| Skill | Description | Risk |")
        lines.append("|---|---|---|")
        for name, desc, risk in groups[key]:
            lines.append(f"| `{md_escape(name)}` | {md_escape(desc)} | {md_escape(risk)} |")
        lines.append("")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} with {len(uniq)} skills across {len(order)} groups.")


if __name__ == "__main__":
    main()
