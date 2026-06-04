#!/usr/bin/env python3
"""
compare_versions.py — diff the pastebin archive against an alternate source.

Usage:
    python3 analysis/compare_versions.py <other_file>

<other_file> can be:
  - A plain .txt file (the wiki page text copy-pasted)
  - An .html file (the raw Reddit wiki page HTML saved with "Save Page As")

The script normalises both versions (strip HTML tags, decode entities, collapse
whitespace) and reports any substantive text differences.

Run from repo root. Never modifies any file.
"""

import re
import sys
import html
import difflib
from pathlib import Path

ARCHIVE_PATH = Path(__file__).parent.parent / "archived" / \
    "2014-04-23_EverySingleOneOfZummiPosts_from_pastebin"


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------

def strip_html(text: str) -> str:
    """Remove HTML tags, decode entities, clean up."""
    # Decode HTML entities first (e.g. &amp; &lt; &#39;)
    text = html.unescape(text)
    # Remove script / style blocks entirely
    text = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # Remove all remaining tags
    text = re.sub(r'<[^>]+>', ' ', text)
    return text


def normalise(text: str) -> str:
    """Canonical form: no HTML, consistent line endings, collapsed blank lines."""
    text = strip_html(text)
    # Normalise line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Collapse runs of spaces/tabs within a line (but preserve newlines)
    lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in text.split('\n')]
    # Collapse runs of more than 2 consecutive blank lines → 2
    result_lines: list[str] = []
    blank_run = 0
    for line in lines:
        if line == '':
            blank_run += 1
            if blank_run <= 2:
                result_lines.append('')
        else:
            blank_run = 0
            result_lines.append(line)
    return '\n'.join(result_lines).strip()


def load(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='replace')


# ---------------------------------------------------------------------------
# Heuristic: try to extract just the archive body from the wiki HTML
# ---------------------------------------------------------------------------

def extract_wiki_body(raw: str) -> str:
    """
    If the input looks like a full Reddit wiki HTML page, try to extract only
    the wiki content div so we're not comparing nav/footer noise.
    Falls back to the full normalised text if no landmark found.
    """
    # Reddit's wiki content lives inside .wiki-page-content or .md
    # Try a few landmarks in order
    for pattern in [
        r'<div[^>]+class="[^"]*wiki-page-content[^"]*"[^>]*>(.*?)</div>',
        r'<div[^>]+class="[^"]*usertext-body[^"]*"[^>]*>(.*?)</div>',
        r'<div[^>]+id="wiki_content"[^>]*>(.*)',
    ]:
        m = re.search(pattern, raw, re.DOTALL | re.IGNORECASE)
        if m:
            return m.group(1)
    # If this looks like HTML but we couldn't find a landmark, strip tags globally
    if '<html' in raw.lower() or '<!doctype' in raw.lower():
        # Try to strip anything before the first <h1> or <p> inside <body>
        body_m = re.search(r'<body[^>]*>(.*)', raw, re.DOTALL | re.IGNORECASE)
        if body_m:
            return body_m.group(1)
    # Already plain text — return as-is
    return raw


# ---------------------------------------------------------------------------
# Diff helpers
# ---------------------------------------------------------------------------

def para_split(text: str) -> list[str]:
    """Split normalised text into paragraphs (blank-line separated)."""
    blocks = re.split(r'\n{2,}', text)
    return [b.strip() for b in blocks if b.strip()]


def unified_diff(a_lines: list[str], b_lines: list[str],
                 name_a: str = 'pastebin', name_b: str = 'wiki') -> str:
    return '\n'.join(difflib.unified_diff(
        a_lines, b_lines,
        fromfile=name_a, tofile=name_b,
        lineterm=''
    ))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 analysis/compare_versions.py <wiki_file>", file=sys.stderr)
        sys.exit(1)

    other_path = Path(sys.argv[1])
    if not other_path.exists():
        print(f"File not found: {other_path}", file=sys.stderr)
        sys.exit(1)

    if not ARCHIVE_PATH.exists():
        print(f"Archive not found: {ARCHIVE_PATH}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading pastebin archive:  {ARCHIVE_PATH.name}")
    print(f"Loading comparison source: {other_path.name}")
    print()

    raw_pastebin = load(ARCHIVE_PATH)
    raw_other    = load(other_path)

    # If other file is HTML, try to extract body first
    if other_path.suffix.lower() in ('.html', '.htm') or \
            ('<html' in raw_other[:200].lower()) or \
            ('<!doctype' in raw_other[:100].lower()):
        print("Detected HTML input — extracting wiki body section.")
        raw_other = extract_wiki_body(raw_other)
    print()

    norm_pastebin = normalise(raw_pastebin)
    norm_other    = normalise(raw_other)

    paras_p = para_split(norm_pastebin)
    paras_o = para_split(norm_other)

    print(f"Pastebin paragraphs: {len(paras_p)}")
    print(f"Other paragraphs:    {len(paras_o)}")
    print()

    # ---- Character-level statistics ----------------------------------------
    chars_p = len(norm_pastebin)
    chars_o = len(norm_other)
    print(f"Pastebin chars (normalised): {chars_p:,}")
    print(f"Other    chars (normalised): {chars_o:,}")
    delta = chars_o - chars_p
    print(f"Delta: {delta:+,} chars")
    print()

    # ---- Quick identity check -----------------------------------------------
    if norm_pastebin == norm_other:
        print("RESULT: Texts are IDENTICAL after normalisation. No differences found.")
        return

    # ---- Diff at paragraph level --------------------------------------------
    sm = difflib.SequenceMatcher(None, paras_p, paras_o, autojunk=False)
    ratio = sm.ratio()
    print(f"Similarity ratio (paragraph level): {ratio:.4f}  ({ratio*100:.1f}%)")
    print()

    opcodes = sm.get_opcodes()
    changed = [(tag, i1, i2, j1, j2) for tag, i1, i2, j1, j2 in opcodes if tag != 'equal']

    if not changed:
        print("RESULT: Paragraphs are identical. Any difference is whitespace/formatting only.")
        return

    print(f"Changed paragraph groups: {len(changed)}")
    print()

    # Show each changed block
    for tag, i1, i2, j1, j2 in changed:
        print(f"--- {tag.upper()} ---")
        if tag in ('replace', 'delete'):
            for idx in range(i1, i2):
                preview = paras_p[idx]
                if len(preview) > 200:
                    preview = preview[:200] + '…'
                print(f"  PASTEBIN [{idx}]: {preview!r}")
        if tag in ('replace', 'insert'):
            for idx in range(j1, j2):
                preview = paras_o[idx]
                if len(preview) > 200:
                    preview = preview[:200] + '…'
                print(f"  OTHER    [{idx}]: {preview!r}")
        print()

    # ---- Full unified diff on lines (for saving) ----------------------------
    diff_path = Path(__file__).parent / "version_diff.txt"
    diff_text = unified_diff(
        norm_pastebin.splitlines(),
        norm_other.splitlines(),
        name_a=f'pastebin/{ARCHIVE_PATH.name}',
        name_b=str(other_path),
    )
    if diff_text.strip():
        diff_path.write_text(diff_text, encoding='utf-8')
        print(f"Full unified diff written to: {diff_path}")
    else:
        print("No line-level diff to write.")


if __name__ == '__main__':
    main()
