"""Minimal Markdown -> PDF for the project's briefs.

Handles what BRIEF.md actually uses: headings, paragraphs, bullet and task
lists, pipe tables, blockquotes, rules, and inline bold/italic/code. Not a
general Markdown implementation.

    python tools/md2pdf.py paper/BRIEF.md paper/BRIEF.pdf
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (HRFlowable, KeepTogether, ListFlowable, ListItem,
                                PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

ACCENT = colors.HexColor("#1a3a5c")
MUTED = colors.HexColor("#5a6672")
RULE = colors.HexColor("#d5dbe1")
CODEBG = colors.HexColor("#f2f4f6")


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(s: str) -> str:
    """Markdown inline -> reportlab mini-HTML. Escape first, then add tags."""
    s = esc(s)
    s = re.sub(r"`([^`]+)`",
               r'<font face="Courier" size="8.5" backColor="#f2f4f6">\1</font>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<link href="\2" color="#1a55a0">\1</link>', s)
    s = s.replace("→", "&#8594;").replace("←", "&#8592;")
    s = s.replace("✅", "[yes]").replace("❌", "[no]").replace("⚠️", "[!]").replace("⚠", "[!]")
    s = s.replace("[ ]", "&#9744;").replace("[x]", "&#9746;")
    return s


def styles():
    ss = getSampleStyleSheet()
    base = dict(textColor=colors.HexColor("#1c2024"))   # fontName set per style
    return {
        "h1": ParagraphStyle("h1", parent=ss["Title"], fontName="Helvetica-Bold",
                             fontSize=19, leading=23, textColor=ACCENT,
                             spaceBefore=4, spaceAfter=10, alignment=TA_LEFT),
        "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=13.5, leading=17,
                             textColor=ACCENT, spaceBefore=17, spaceAfter=6),
        "h3": ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=11, leading=14,
                             textColor=colors.HexColor("#2b4d70"), spaceBefore=11, spaceAfter=4),
        "h4": ParagraphStyle("h4", fontName="Helvetica-BoldOblique", fontSize=10, leading=13,
                             spaceBefore=8, spaceAfter=3, **base),
        "p": ParagraphStyle("p", fontName="Helvetica", fontSize=9.5, leading=13.2, spaceAfter=6, **base),
        "li": ParagraphStyle("li", fontName="Helvetica", fontSize=9.5, leading=13, spaceAfter=2.5, **base),
        "quote": ParagraphStyle("quote", fontSize=9.5, leading=13.5, leftIndent=14,
                                rightIndent=10, spaceBefore=5, spaceAfter=7,
                                borderPadding=(6, 6, 6, 8), backColor=colors.HexColor("#f6f8fa"),
                                fontName="Helvetica-Oblique",
                                textColor=colors.HexColor("#22303c")),
        "th": ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=8.5, leading=11,
                             textColor=colors.white),
        "td": ParagraphStyle("td", fontName="Helvetica", fontSize=8.5, leading=11,
                             textColor=colors.HexColor("#1c2024")),
    }


def build_table(rows: list[list[str]], S, avail: float) -> Table:
    head, body = rows[0], rows[1:]
    data = [[Paragraph(inline(c), S["th"]) for c in head]]
    for r in body:
        data.append([Paragraph(inline(c), S["td"]) for c in r])
    ncol = max(len(r) for r in data)
    data = [r + [Paragraph("", S["td"])] * (ncol - len(r)) for r in data]
    # width proportional to content, so a "#" column does not get 42%
    raw = [rows[0]] + rows[1:]
    lens = []
    for c in range(ncol):
        vals = [len(re.sub(r"[*`]", "", r[c])) if c < len(r) else 0 for r in raw]
        vals.sort()
        # 85th percentile, floored, so one long cell does not dominate
        lens.append(max(4, vals[int(0.85 * (len(vals) - 1))]))
    tot = sum(lens)
    widths = [max(avail * 0.055, avail * l / tot) for l in lens]
    scale = avail / sum(widths)
    widths = [w * scale for w in widths]
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f9fb")]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
        ("BOX", (0, 0), (-1, -1), 0.5, RULE),
    ]))
    return t


def convert(src: Path, dst: Path) -> None:
    S = styles()
    md = src.read_text(encoding="utf-8").splitlines()
    doc = SimpleDocTemplate(str(dst), pagesize=LETTER,
                            leftMargin=0.72 * inch, rightMargin=0.72 * inch,
                            topMargin=0.68 * inch, bottomMargin=0.68 * inch,
                            title="Earshot — abstract brief", author="Adrian Erlikhman")
    avail = LETTER[0] - 1.44 * inch
    flow: list = []
    i = 0
    bullets: list[str] = []

    def flush_bullets():
        nonlocal bullets
        if bullets:
            flow.append(ListFlowable(
                [ListItem(Paragraph(inline(b), S["li"]), leftIndent=12) for b in bullets],
                bulletType="bullet", bulletFontSize=6, bulletOffsetY=1,
                leftIndent=13, spaceBefore=2, spaceAfter=6))
            bullets = []

    while i < len(md):
        ln = md[i].rstrip()

        if not ln.strip():
            flush_bullets(); i += 1; continue

        if re.fullmatch(r"-{3,}|\*{3,}|_{3,}", ln.strip()):
            flush_bullets()
            flow.append(Spacer(1, 3))
            flow.append(HRFlowable(width="100%", thickness=0.7, color=RULE,
                                   spaceBefore=1, spaceAfter=8))
            i += 1; continue

        m = re.match(r"^(#{1,4})\s+(.*)$", ln)
        if m:
            flush_bullets()
            lvl, txt = len(m.group(1)), m.group(2)
            flow.append(Paragraph(inline(txt), S[f"h{lvl}"]))
            i += 1; continue

        if ln.lstrip().startswith(">"):
            flush_bullets()
            buf = []
            while i < len(md) and md[i].lstrip().startswith(">"):
                buf.append(md[i].lstrip()[1:].strip()); i += 1
            flow.append(Paragraph(inline(" ".join(buf)), S["quote"]))
            continue

        # pipe table
        if ln.lstrip().startswith("|") and i + 1 < len(md) and re.match(
                r"^\s*\|[\s:|-]+\|\s*$", md[i + 1]):
            flush_bullets()
            rows = []
            def cells(s): return [c.strip() for c in s.strip().strip("|").split("|")]
            rows.append(cells(ln)); i += 2
            while i < len(md) and md[i].lstrip().startswith("|"):
                rows.append(cells(md[i])); i += 1
            flow.append(Spacer(1, 2))
            flow.append(build_table(rows, S, avail))
            flow.append(Spacer(1, 9))
            continue

        m = re.match(r"^\s*(?:[-*+]|\d+\.)\s+(.*)$", ln)
        if m:
            item = m.group(1)
            i += 1
            # absorb indented continuation lines so a wrapped list item stays one item
            while (i < len(md) and md[i].strip()
                   and re.match(r"^\s{2,}\S", md[i])
                   and not re.match(r"^\s*(?:[-*+]|\d+\.)\s", md[i])):
                item += " " + md[i].strip(); i += 1
            bullets.append(item); continue

        # paragraph: gather until blank / structural line
        buf = [ln]
        i += 1
        while i < len(md) and md[i].strip() and not re.match(
                r"^\s*(#{1,4}\s|[-*+]\s|\d+\.\s|>|\||-{3,}$)", md[i]):
            buf.append(md[i].strip()); i += 1
        flush_bullets()
        flow.append(Paragraph(inline(" ".join(buf)), S["p"]))

    flush_bullets()

    def footer(canvas, d):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(0.72 * inch, 0.42 * inch,
                          "Earshot — AI for Peace @ NeurIPS 2026 — internal brief, 12 Sept 2026")
        canvas.drawRightString(LETTER[0] - 0.72 * inch, 0.42 * inch, f"{d.page}")
        canvas.restoreState()

    doc.build(flow, onFirstPage=footer, onLaterPages=footer)
    print(f"wrote {dst}  ({dst.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    src = Path(sys.argv[1]); dst = Path(sys.argv[2] if len(sys.argv) > 2 else src.with_suffix(".pdf"))
    convert(src, dst)
