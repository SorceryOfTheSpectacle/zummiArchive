#!/usr/bin/env python3
"""
Generate downloadable TXT, MD, and PDF versions of the Zummi Archive,
plus browse.md — the Jekyll browsing page with ToC and per-block anchors.
Run from repo root: python3 analysis/generate_downloads.py
Output: downloads/zummi-archive.txt, .md, .pdf  and  browse.md
"""

import html
import re
from pathlib import Path

ARCHIVE = Path("archived/2014-04-23_EverySingleOneOfZummiPosts_from_pastebin")
DOWNLOADS = Path("downloads")

TITLE = "Zummi Archive"
SUBTITLE = "Every Single One of Zummi's Posts"
COMPILED = "Compiled by OilofOregano — Pastebin, 2014-04-23"

ABOUT = (
    "This archive preserves the posts of Zummi, founder of r/sorceryofthespectacle (SotS).\n\n"
    "SotS is a community that resists being described -- which is itself part of the point. "
    "It was founded by Zummi as a response to r/DigitalCartel's failed ARG promise, with "
    "raisondecalcul as co-admin from the beginning, and takes its name from Guy Debord's "
    "Society of the Spectacle. At its core is Debord's concept of the spectacle: a "
    "'self-mutating proteum of semantics' in which media, commodification and technology "
    "combine to substitute representation for lived experience. In the community's own "
    "framing, 'sorcery is the intentional manipulation of the spectacle' -- using the "
    "system's own spectacular mechanisms against itself.\n\n"
    "The sub draws on a deliberately eclectic range of sources: critical theory (Debord, "
    "Ranciere, Deleuze & Guattari), the CCRU lineage (Nick Land, Mark Fisher, Reza "
    "Negarestani), Platonic and Gnostic philosophy, Western occultism (Stolen Lightning, "
    "SSOTBME), and concepts like Academocculture (the overlap between academic theory and "
    "occultism) and APS (Abstract Phase Space -- the cognitive structures through which we "
    "model and navigate reality). A recurring preoccupation is the Kali Yuga framing: "
    "whether the cascading failures of contemporary institutions are error, strategy, or "
    "structurally inevitable. One long-standing member described it as 'the sugary sweet "
    "spot between critical theory, conspiracy theory and accidentally summoning an Elder "
    "Thing while you munch your favourite breakfast cereal.'\n\n"
    "What the sub is -- in the words of a moderator -- is simply 'a premise: that we are "
    "aware of the spectacle. Discussion goes from there.' It is not a school of thought "
    "with a doctrine but a space of ongoing inquiry, multi-vocal and irony-laden, where "
    "the question 'what is this?' recurs on an almost predictable schedule and the "
    "impossibility of answering it neatly is part of the experience.\n\n"
    "Zummi was the community's founder and its most prolific voice. Over several years of "
    "posts he developed a recognisable intellectual project: tracing the alphabet as the "
    "origin of externalized memory and therefore of culture itself; reading the history of "
    "philosophy as a progression from myth (body, image, oral culture) toward logos (text, "
    "abstraction, literacy); identifying cybernetics and social media as the unconscious "
    "rediscovery and inversion of archaic magical structures. At the centre of it was always "
    "the question of what the spectacle does to consciousness, and whether there is any exit.\n\n"
    "Zummi eventually stepped back from moderation and publicly distanced himself from the "
    "subreddit, expressing exhaustion with the medium and doubt about whether anything he "
    "had built there was genuinely useful. The posts below document that whole arc: the "
    "theorising, the community-building, the burnout, and the departure. The community has "
    "continued after his departure, and Zummi has since published a paperback book.\n\n"
    "ARCHIVE PROVENANCE: The post collection was originally compiled by OilofOregano for a "
    "Reddit thread and posted to Pastebin on 2014-04-23. Pastebin later deleted it due to "
    "profanity in the original posts. It is mirrored here from an Internet Archive capture "
    "in the interest of preservation. Zummi's spelling, punctuation, capitalisation, and "
    "formatting are reproduced exactly as written.\n\n"
    "Online: https://sorceryofthespectacle.github.io/zummiArchive/\n"
    "Source: https://github.com/SorceryOfTheSpectacle/zummiArchive"
)

VERBATIM_NOTE = (
    "The following text is preserved verbatim from the original pastebin. "
    "Spelling, punctuation, capitalisation, and formatting are reproduced exactly as written. "
    "Each paragraph block is numbered [N] for reference. Blocks of 500+ characters are "
    "listed in the Table of Contents."
)

# Markdown version of the about section (used in .md output header)
ABOUT_MD = """\
# Zummi Archive

*Every Single One of Zummi's Posts — compiled by OilofOregano, Pastebin 2014-04-23*

## About This Archive

This archive preserves the posts of **Zummi**, founder of r/sorceryofthespectacle (SotS).

*r/sorceryofthespectacle* (SotS) is a community for philosophical discussion of what the subreddit itself calls **Academocculture** — the overlap of critical theory, occultism, and the study of media and power. Its starting point is Guy Debord's *Society of the Spectacle*: the idea that contemporary culture is a "self-mutating proteum of semantics" that combines agency-robbing fantasy with instantaneous technological dissemination. The "sorcery" in the name is not merely metaphorical — the community treats the spectacle as a genuinely magical phenomenon, drawing on works like Daniel O'Keefe's *Stolen Lightning* (a social theory of magic) and the CCRU lineage (Nick Land, Reza Negarestani) alongside Debord, Rancière, Deleuze & Guattari, and Platonic and Gnostic philosophy. A recurring preoccupation is the Kali Yuga framing: whether the cascading failures of contemporary institutions are error, strategy, or built into the structure of things.

Zummi was the community's founder and its most prolific voice. Over several years of posts he developed a recognisable intellectual project: tracing the alphabet as the origin of externalized memory and therefore of culture itself; reading the history of philosophy as a progression from myth (body, image, oral culture) toward logos (text, abstraction, literacy); identifying cybernetics and social media as the unconscious rediscovery and inversion of archaic magical structures. At the centre of it was always the question of what the spectacle does to consciousness, and whether there is any exit.

Zummi eventually stepped back from moderation and publicly distanced himself from the subreddit, expressing exhaustion with the medium and doubt about whether anything he had built there was genuinely useful. The posts below document that whole arc: the theorising, the community-building, the burnout, and the departure.

**Archive provenance:** Originally compiled by [OilofOregano](https://www.reddit.com/user/OilofOregano) and posted to Pastebin on 2014-04-23. Pastebin later deleted it due to profanity. Mirrored here from an [Internet Archive capture](http://web.archive.org/web/20190606033621/https://pastebin.com/dtNG4LKg) in the interest of preservation. Zummi's spelling, punctuation, capitalisation, and formatting are reproduced exactly as written.

- Online: <https://sorceryofthespectacle.github.io/zummiArchive/>
- Source: <https://github.com/SorceryOfTheSpectacle/zummiArchive>

---\
"""

# Blocks at or above this character length get a ToC entry.
TOC_MIN_CHARS = 500


def load_blocks() -> list[str]:
    """Split archive on blank lines; return non-empty stripped blocks."""
    text = ARCHIVE.read_text(encoding="utf-8", errors="replace")
    return [b.strip() for b in text.split("\n\n") if b.strip()]


def strip_markdown(text: str) -> str:
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # [text](url) -> text
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = re.sub(r'\*+([^\*]+)\*+', r'\1', text)           # *bold* / **bold**
    text = re.sub(r'`([^`]+)`', r'\1', text)                # `code`
    return text


def toc_title(block: str, max_len: int = 72) -> str:
    """First line of a block, truncated, as a ToC label."""
    first = block.split("\n")[0].strip()
    first = strip_markdown(first)
    if len(first) > max_len:
        first = first[:max_len].rstrip() + "..."
    return first


def normalise_for_pdf(text: str) -> str:
    """Replace Unicode characters that ReportLab built-in fonts can't render."""
    replacements = {
        '—': '--',  # em dash
        '–': '-',   # en dash
        '‘': "'",   # left single quote
        '’': "'",   # right single quote
        '“': '"',   # left double quote
        '”': '"',   # right double quote
        '…': '...',  # ellipsis
        '\xf6': 'o',     # o-umlaut
        '\xe9': 'e',     # e-acute
        '\xe8': 'e',     # e-grave
        '\xe0': 'a',     # a-grave
        '\xe2': 'a',     # a-circumflex
        '\xfb': 'u',     # u-circumflex
        '\xee': 'i',     # i-circumflex
        '\xe7': 'c',     # c-cedilla
        '\xfc': 'u',     # u-umlaut
        '\xe4': 'a',     # a-umlaut
        '\xdf': 'ss',    # sharp s
        '´': "'",   # acute accent
        ' ': ' ',   # non-breaking space
        '•': '*',   # bullet
        '→': '->',  # right arrow
        'α': 'alpha',
        'β': 'beta',
        'γ': 'gamma',
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text.encode('latin-1', errors='replace').decode('latin-1')


# ---------------------------------------------------------------------------
# MD
# ---------------------------------------------------------------------------

def generate_md(blocks: list[str]) -> None:
    toc_entries = [(i, toc_title(b)) for i, b in enumerate(blocks, 1)
                   if len(b) >= TOC_MIN_CHARS]

    parts = [ABOUT_MD, ""]

    # ToC
    parts.append("## Table of Contents")
    parts.append(f"*{len(toc_entries)} blocks of 500+ characters "
                 f"(of {len(blocks)} total). Block numbers shown as `[N]` in the text.*\n")
    for num, title in toc_entries:
        parts.append(f"- `[{num}]` {title}")

    parts += ["", "---", "", "## Archive Content", ""]
    parts.append(f"*{VERBATIM_NOTE}*\n")

    # Content — original text verbatim; block numbers as HTML comments so
    # they're invisible when rendered but present in the raw file.
    for i, block in enumerate(blocks, 1):
        parts.append(f"<!-- [{i}] -->")
        parts.append(block)
        parts.append("")

    out = DOWNLOADS / "zummi-archive.md"
    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"  {out}  ({out.stat().st_size:,} bytes)")


# ---------------------------------------------------------------------------
# TXT
# ---------------------------------------------------------------------------

def generate_txt(blocks: list[str]) -> None:
    sep72 = "-" * 72

    parts = [
        TITLE,
        "=" * len(TITLE),
        "",
        SUBTITLE,
        COMPILED,
        "",
        sep72,
        "",
        "ABOUT THIS ARCHIVE",
        "",
        ABOUT,
        "",
        sep72,
        "",
        "TABLE OF CONTENTS",
        "(blocks >= 500 characters)",
        "",
    ]

    # ToC
    for i, block in enumerate(blocks, 1):
        if len(block) >= TOC_MIN_CHARS:
            title = toc_title(strip_markdown(block))
            parts.append(f"  [{i:3d}]  {title}")

    parts += [
        "",
        sep72,
        "",
        "ARCHIVE CONTENT",
        "",
        VERBATIM_NOTE,
        "",
    ]

    # Content
    for i, block in enumerate(blocks, 1):
        parts.append(f"[{i}]")
        parts.append(strip_markdown(block))
        parts.append("")

    out = DOWNLOADS / "zummi-archive.txt"
    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"  {out}  ({out.stat().st_size:,} bytes)")


# ---------------------------------------------------------------------------
# PDF
# ---------------------------------------------------------------------------

def generate_pdf(blocks: list[str]) -> None:
    from reportlab.lib.colors import Color, HexColor
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import (HRFlowable, PageBreak, Paragraph,
                                    SimpleDocTemplate, Spacer)
    from reportlab.platypus.tableofcontents import TableOfContents

    grey = HexColor('#888888')
    light_grey = HexColor('#bbbbbb')

    out = DOWNLOADS / "zummi-archive.pdf"

    doc = SimpleDocTemplate(
        str(out),
        pagesize=A4,
        leftMargin=3 * cm,
        rightMargin=3 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
        title=TITLE,
        author="Zummi",
        subject="Archive of Zummi's posts from r/sorceryofthespectacle",
    )

    styles = getSampleStyleSheet()

    s_title = ParagraphStyle("ZTitle", parent=styles["Title"],
                              fontSize=26, spaceAfter=10, alignment=TA_CENTER)
    s_sub = ParagraphStyle("ZSub", parent=styles["Normal"],
                            fontSize=11, spaceAfter=4, alignment=TA_CENTER,
                            textColor=grey)
    s_h2 = ParagraphStyle("ZH2", parent=styles["Heading2"],
                           fontSize=13, spaceBefore=20, spaceAfter=8)
    s_body = ParagraphStyle("ZBody", parent=styles["Normal"],
                             fontSize=10, leading=15, spaceAfter=6,
                             alignment=TA_JUSTIFY)
    s_note = ParagraphStyle("ZNote", parent=s_body,
                             fontSize=9, textColor=grey)
    # Label style: small grey number shown before each block
    s_label = ParagraphStyle("ZLabel", parent=styles["Normal"],
                              fontSize=7.5, textColor=grey,
                              spaceBefore=10, spaceAfter=2,
                              leading=10)
    # ToC entry style
    s_toc = ParagraphStyle("ZToc", parent=styles["Normal"],
                            fontSize=9, leading=13, spaceAfter=2)
    s_toc_head = ParagraphStyle("ZTocHead", parent=s_h2,
                                 fontSize=13, spaceBefore=0, spaceAfter=12)

    def e(s: str) -> str:
        return html.escape(normalise_for_pdf(s))

    def thin_rule():
        return HRFlowable(width="100%", thickness=0.3,
                          color=light_grey, spaceAfter=4, spaceBefore=0)

    story = []

    # ---- Title page ----
    story.append(Spacer(1, 3 * cm))
    story.append(Paragraph(e(TITLE), s_title))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(e(SUBTITLE), s_sub))
    story.append(Paragraph(e(COMPILED), s_sub))
    story.append(Spacer(1, 1.5 * cm))
    story.append(HRFlowable(width="100%", thickness=0.5, spaceAfter=6))
    story.append(PageBreak())

    # ---- About section ----
    story.append(Paragraph("About This Archive", s_h2))
    for para in ABOUT.split("\n\n"):
        story.append(Paragraph(e(para.replace("\n", " ")), s_body))
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=0.5, spaceAfter=6))
    story.append(PageBreak())

    # ---- Table of Contents ----
    toc_entries = [(i, toc_title(strip_markdown(b)))
                   for i, b in enumerate(blocks, 1)
                   if len(b) >= TOC_MIN_CHARS]

    story.append(Paragraph("Table of Contents", s_toc_head))
    story.append(Paragraph(
        f"<i>Listing {len(toc_entries)} blocks of 500+ characters "
        f"(out of {len(blocks)} total blocks). "
        f"Block numbers [N] are shown in the text.</i>",
        s_note,
    ))
    story.append(Spacer(1, 0.3 * cm))
    for num, title in toc_entries:
        story.append(Paragraph(
            f'<font color="#888888">[{num}]</font>  {e(title)}',
            s_toc,
        ))
    story.append(PageBreak())

    # ---- Archive content ----
    story.append(Paragraph("Archive Content", s_h2))
    story.append(Paragraph(f"<i>{e(VERBATIM_NOTE)}</i>", s_note))
    story.append(Spacer(1, 0.5 * cm))

    for i, block in enumerate(blocks, 1):
        clean = strip_markdown(block)

        # Separator rule before each block (skip first)
        if i > 1:
            story.append(thin_rule())

        # Block number label
        story.append(Paragraph(f"[{i}]", s_label))

        # Content — preserve internal newlines as separate paragraphs
        paras = [p.strip().replace("\n", " ") for p in clean.split("\n\n") if p.strip()]
        if not paras:
            paras = [clean.replace("\n", " ").strip()]
        for p in paras:
            if p:
                story.append(Paragraph(e(p), s_body))

    doc.build(story)
    print(f"  {out}  ({out.stat().st_size:,} bytes)")


# ---------------------------------------------------------------------------
# Web (browse.md)
# ---------------------------------------------------------------------------

def generate_web(blocks: list[str]) -> None:
    """Generate browse.md — Jekyll page with collapsible ToC and per-block anchors."""
    import html as html_mod

    toc_entries = [
        (i, toc_title(b, max_len=80))
        for i, b in enumerate(blocks, 1)
        if len(b) >= TOC_MIN_CHARS
    ]

    lines = [
        '---',
        'title: Browse Archive',
        'layout: page',
        '---',
        '',
        '[← About & Downloads]({{ "/" | relative_url }})',
        '',
        (f'*{len(blocks)} numbered blocks — '
         f'{len(toc_entries)} substantial (≥ 500 chars) listed below.*'),
        '',
        '<details>',
        f'<summary>Table of Contents — {len(toc_entries)} entries</summary>',
        '<div markdown="0" style="max-height:55vh;overflow-y:scroll;'
        'padding:0.4em 0 0.4em 0.6em">',
    ]

    for num, title in toc_entries:
        safe = html_mod.escape(title)
        lines.append(
            f'<p style="margin:0.1em 0;font-size:0.85em">'
            f'<a href="#b{num}">[{num}]</a> {safe}</p>'
        )

    lines += [
        '</div>',
        '</details>',
        '',
        '---',
        '',
        f'*{VERBATIM_NOTE}*',
        '',
    ]

    for i, block in enumerate(blocks, 1):
        lines.append(f'<a id="b{i}"></a>')
        lines.append('')
        lines.append(block)
        lines.append('')

    out = Path('browse.md')
    out.write_text('\n'.join(lines), encoding='utf-8')
    print(f'  {out}  ({out.stat().st_size:,} bytes)')


# ---------------------------------------------------------------------------

def main() -> None:
    DOWNLOADS.mkdir(exist_ok=True)
    blocks = load_blocks()
    print(f"Loaded {len(blocks)} blocks from archive.")
    print("Generating downloads...")
    generate_md(blocks)
    generate_txt(blocks)
    generate_pdf(blocks)
    generate_web(blocks)
    print("Done.")


if __name__ == "__main__":
    main()
