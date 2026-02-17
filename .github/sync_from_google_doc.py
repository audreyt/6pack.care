#!/usr/bin/env python3
"""Pull Google Doc tabs back to local markdown files via the Docs API.

Reads each tab listed in TAB_MAP, converts structured content back to
markdown, preserves YAML front matter from existing local files, and
writes the result.

Auth: expects GOOGLE_REFRESH_TOKEN, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
in the environment (e.g. from GitHub Secrets).
"""

from __future__ import annotations

import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from doc_sync_config import SITE_URL, TAB_MAP, SYNC_FILES, CONTENT_START, doc_id_for, validate_sync_config

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ORDERED_GLYPH_TYPES = {
    "DECIMAL", "ZERO_DECIMAL", "ALPHA", "UPPER_ALPHA", "ROMAN", "UPPER_ROMAN",
}

# ── Auth ─────────────────────────────────────────────────────────────


def _credentials() -> Credentials:
    refresh = os.environ.get("GOOGLE_REFRESH_TOKEN")
    cid = os.environ.get("GOOGLE_CLIENT_ID")
    csecret = os.environ.get("GOOGLE_CLIENT_SECRET")
    if not all([refresh, cid, csecret]):
        raise SystemExit(
            "Missing env: GOOGLE_REFRESH_TOKEN, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET"
        )
    return Credentials(
        token=None,
        refresh_token=refresh,
        client_id=cid,
        client_secret=csecret,
        token_uri="https://oauth2.googleapis.com/token",
    )


# ── Helpers ──────────────────────────────────────────────────────────


def _validate_targets(targets: list[str]) -> list[Path]:
    paths = [Path(target) for target in targets]
    for path in paths:
        if not path.exists():
            raise SystemExit(f"doc-sync error: missing source file: {path}")
    return paths


def _warn_no_tab_mapping(filename: str) -> None:
    print(f"doc-sync warning: {filename}: missing tab mapping")


def _warn_tab_not_found(filename: str, tab_id: str) -> None:
    print(f"doc-sync warning: {filename}: mapped tab not found in Google Doc: {tab_id}")


def _find_tab(tabs: list[dict], target_id: str):
    for tab in tabs:
        if tab["tabProperties"]["tabId"] == target_id:
            return tab
        found = _find_tab(tab.get("childTabs", []), target_id)
        if found:
            return found
    return None


def _relativise_url(url: str, page_path: str) -> str:
    """Convert absolute 6pack.care URLs back to relative markdown links."""
    if not url.startswith(SITE_URL):
        return url
    path = url[len(SITE_URL):]
    if not path:
        return "/"
    if path.startswith(page_path + "#"):
        return path[len(page_path):]
    return path


def _extract_front_matter(path: Path) -> str:
    """Preserve existing YAML front matter from the local file."""
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                return "---" + parts[1] + "---\n\n"
    return ""


def _extract_html_blocks(path: Path) -> list[tuple[str | None, str]]:
    """Extract multi-line <div> blocks from existing file.

    Returns a list of (heading_anchor, block) tuples where
    *heading_anchor* is the nearest preceding markdown heading
    (e.g. ``"## About the Project"``), or ``None`` if the block
    appears before any heading (i.e. top of body).
    """
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    # strip front matter
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            text = parts[2]

    lines = text.split("\n")
    blocks: list[tuple[str | None, str]] = []
    depth = 0
    block_lines: list[str] = []
    last_heading: str | None = None

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # track headings
        if depth == 0 and re.match(r"^#{1,6}\s", stripped):
            last_heading = stripped

        opens = len(re.findall(r"<div\b", stripped))
        closes = len(re.findall(r"</div>", stripped))

        if depth > 0 or opens > 0:
            block_lines.append(line)
            depth += opens - closes
            if depth < 0:
                depth = 0
            if depth == 0:
                blocks.append((last_heading, "\n".join(block_lines)))
                block_lines = []
            i += 1
            continue
        i += 1

    return blocks


def _reinject_html_blocks(md: str, blocks: list[tuple[str | None, str]]) -> str:
    """Re-insert preserved HTML blocks after their heading anchors."""
    if not blocks:
        return md
    for heading, block in blocks:
        if heading is None:
            # top-of-body block — prepend with one blank line
            md = block + "\n\n" + md.lstrip("\n")
            continue
        idx = md.find(heading)
        if idx == -1:
            continue  # heading removed — drop the block
        # find end of the heading line
        eol = md.find("\n", idx)
        if eol == -1:
            eol = len(md)
        # insert after the heading line, preserving blank line spacing
        insert_at = eol + 1
        md = md[:insert_at] + "\n" + block + "\n\n" + md[insert_at:].lstrip("\n")
    return md


# ── Docs API content → markdown ──────────────────────────────────────


@dataclass
class _Span:
    """Inline text span with formatting metadata."""
    text: str
    bold: bool = False
    italic: bool = False
    link: str = ""


def _collect_spans(elements: list[dict], page_path: str, in_heading: bool = False) -> list[_Span]:
    """Extract formatted spans from paragraph elements."""
    spans: list[_Span] = []
    for el in elements:
        tr = el.get("textRun")
        if not tr:
            continue
        content = tr.get("content", "")
        if not content or content == "\n":
            continue
        style = tr.get("textStyle", {})
        bold = style.get("bold", False) and not in_heading
        italic = style.get("italic", False)
        link = style.get("link", {}).get("url", "")
        if link:
            link = _relativise_url(link, page_path)
        spans.append(_Span(
            text=content.rstrip("\n"),
            bold=bold,
            italic=italic,
            link=link,
        ))
    return spans


def _coalesce_spans(spans: list[_Span]) -> list[_Span]:
    """Merge adjacent spans with identical formatting."""
    if not spans:
        return spans
    merged: list[_Span] = [_Span(spans[0].text, spans[0].bold, spans[0].italic, spans[0].link)]
    for s in spans[1:]:
        prev = merged[-1]
        if prev.bold == s.bold and prev.italic == s.italic and prev.link == s.link:
            prev.text += s.text
        else:
            merged.append(_Span(s.text, s.bold, s.italic, s.link))
    return merged


def _needs_html_emphasis(text: str, prev_char: str, next_char: str) -> bool:
    """Check if markdown emphasis delimiters would fail around *text*.

    JS markdown-it follows CommonMark: a ``**`` opener after a non-punctuation
    char fails if the first inner char is Unicode punctuation, and a ``**``
    closer before a non-punctuation char fails if the last inner char is Unicode
    punctuation.  Fall back to HTML tags in these cases.
    """
    import unicodedata
    _PUNCT_CATS = {"Pc", "Pd", "Pe", "Pf", "Pi", "Po", "Ps", "Sc", "Sk", "Sm", "So"}

    if not text:
        return False
    first, last = text[0], text[-1]
    first_cat = unicodedata.category(first)
    last_cat = unicodedata.category(last)
    prev_cat = unicodedata.category(prev_char) if prev_char else "Zs"
    next_cat = unicodedata.category(next_char) if next_char else "Zs"

    # Opening delimiter: if inner-first is punctuation, preceding must be
    # punctuation or whitespace for the delimiter to be left-flanking.
    if first_cat in _PUNCT_CATS and prev_cat not in (_PUNCT_CATS | {"Zs"}):
        return True
    # Closing delimiter: if inner-last is punctuation, following must be
    # punctuation or whitespace for the delimiter to be right-flanking.
    if last_cat in _PUNCT_CATS and next_cat not in (_PUNCT_CATS | {"Zs"}):
        return True
    return False


def _spans_to_md(spans: list[_Span]) -> str:
    """Convert a list of formatted spans to an inline markdown string."""
    spans = _coalesce_spans(spans)
    parts: list[str] = []
    for i, s in enumerate(spans):
        text = s.text
        if s.link:
            text = f"[{text}]({s.link})"

        if s.bold or s.italic:
            # Determine surrounding chars for emphasis-safety check
            prev_char = parts[-1][-1] if parts and parts[-1] else ""
            next_char = spans[i + 1].text[0] if i + 1 < len(spans) and spans[i + 1].text else ""
            use_html = _needs_html_emphasis(s.text, prev_char, next_char)

            if s.bold and s.italic:
                text = f"<b><i>{text}</i></b>" if use_html else f"***{text}***"
            elif s.bold:
                text = f"<strong>{text}</strong>" if use_html else f"**{text}**"
            elif s.italic:
                text = f"<em>{text}</em>" if use_html else f"_{text}_"

        parts.append(text)
    return "".join(parts)


def _is_ordered(lists_meta: dict, list_id: str, nesting: int) -> bool:
    """Check whether a list nesting level is ordered."""
    props = lists_meta.get(list_id, {})
    levels = props.get("listProperties", {}).get("nestingLevels", [])
    if nesting < len(levels):
        glyph = levels[nesting].get("glyphType", "")
        if glyph in ORDERED_GLYPH_TYPES:
            return True
        # Fallback: GLYPH_TYPE_UNSPECIFIED but has a numeric format like "%0."
        if glyph in ("GLYPH_TYPE_UNSPECIFIED", "") and levels[nesting].get("glyphFormat", ""):
            fmt = levels[nesting]["glyphFormat"]
            return bool(re.match(r"^%\d", fmt))
    return False


HEADING_LEVEL = {
    "HEADING_1": 1, "HEADING_2": 2, "HEADING_3": 3,
    "HEADING_4": 4, "HEADING_5": 5, "HEADING_6": 6,
}


def tab_to_markdown(
    tab: dict,
    page_path: str,
    skip_first_h1: bool = True,
    content_start: str | None = None,
) -> str:
    """Convert a Google Doc tab to markdown text (without front matter).

    When *content_start* is given (e.g. ``"Pack 1"``), all elements
    before the first heading whose text starts with that prefix are
    skipped.  The matching heading itself is treated as the "first H1"
    and also skipped (its text lives in the YAML front-matter title).
    """
    body = tab["documentTab"]["body"]
    lists_meta = tab.get("documentTab", {}).get("lists", {})
    content = body.get("content", [])

    lines: list[str] = []
    seen_h1 = False
    capturing = content_start is None
    prev_kind = ""  # "heading", "list", "para", "blank"

    for elem in content:
        para = elem.get("paragraph")
        if not para:
            continue

        # ── classify paragraph ──
        named = para.get("paragraphStyle", {}).get("namedStyleType", "NORMAL_TEXT")
        level = HEADING_LEVEL.get(named)
        bullet = para.get("bullet")

        # ── assemble inline text via span coalescing ──
        spans = _collect_spans(para.get("elements", []), page_path, in_heading=bool(level))
        text = _spans_to_md(spans).rstrip()

        # ── partial-tab: skip until boundary heading ──
        if not capturing:
            if level and text.startswith(content_start):
                capturing = True
                seen_h1 = True  # treat boundary heading as first H1 (skip it)
            continue

        # blank paragraph
        if not text:
            if prev_kind != "blank":
                lines.append("")
                prev_kind = "blank"
            continue

        # heading
        if level:
            if skip_first_h1 and level == 1 and not seen_h1:
                seen_h1 = True
                continue
            if lines and prev_kind != "blank":
                lines.append("")
            lines.append(f"{'#' * level} {text}")
            prev_kind = "heading"
            continue

        # list item
        if bullet:
            list_id = bullet.get("listId", "")
            nesting = bullet.get("nestingLevel", 0)
            ordered = _is_ordered(lists_meta, list_id, nesting)
            indent = "  " * nesting
            prefix = "1." if ordered else "-"
            if prev_kind not in ("list", "blank") and lines:
                lines.append("")
            lines.append(f"{indent}{prefix} {text}")
            prev_kind = "list"
            continue

        # regular paragraph
        if prev_kind == "list" and lines:
            lines.append("")
        if prev_kind == "para" and lines and lines[-1] != "":
            lines.append("")
        lines.append(text)
        prev_kind = "para"

    # clean trailing blanks
    while lines and lines[-1] == "":
        lines.pop()

    return "\n".join(lines) + "\n"


_FAQ_Q_RE = re.compile(r"^####\s+(Q(\d+)\.\s+.+)$")


def _faq_postprocess(md: str) -> str:
    """Reconstruct <h4 id="faq-N"> anchors and --- separators for FAQ pages.

    Converts ``#### QN. text`` lines back to the canonical
    ``<h4 id="faq-N"><a href="#faq-N">QN.</a> text</h4>`` form
    and inserts ``---`` horizontal rules between questions.
    """
    out: list[str] = []
    seen_question = False

    for line in md.split("\n"):
        m = _FAQ_Q_RE.match(line)
        if m:
            full_text = m.group(1)
            num = m.group(2)
            # Split "QN. rest" → prefix "QN.", body "rest"
            dot_pos = full_text.index(".")
            q_prefix = full_text[:dot_pos + 1]
            q_body = full_text[dot_pos + 1:].strip()

            if seen_question:
                # Insert --- separator before the next question
                # Remove trailing blank line if present, add ---, blank, heading
                while out and out[-1] == "":
                    out.pop()
                out.append("")
                out.append("---")
                out.append("")

            faq_id = f"faq-{num}"
            out.append(
                f'<h4 id="{faq_id}"><a href="#{faq_id}">{q_prefix}</a> {q_body}</h4>'
            )
            seen_question = True
        else:
            out.append(line)

    return "\n".join(out)


# ── Main ─────────────────────────────────────────────────────────────


def main() -> None:
    validate_sync_config()
    raw_targets = sys.argv[1:] if len(sys.argv) > 1 else list(SYNC_FILES)
    target_paths = _validate_targets(raw_targets)

    creds = _credentials()
    service = build("docs", "v1", credentials=creds)

    # Group targets by doc ID so each document is fetched once.
    groups: dict[str, list[Path]] = defaultdict(list)
    for target in target_paths:
        groups[doc_id_for(target.name)].append(target)

    for did, targets in groups.items():
        doc = (
            service.documents()
            .get(documentId=did, includeTabsContent=True)
            .execute()
        )

        for target in targets:
            filename = target.name
            tab_id = TAB_MAP.get(filename)
            if not tab_id:
                _warn_no_tab_mapping(filename)
                continue

            tab = _find_tab(doc["tabs"], tab_id)
            if not tab:
                _warn_tab_not_found(filename, tab_id)
                continue

            page_path = "/" + Path(filename).stem + "/"
            md = tab_to_markdown(
                tab, page_path,
                skip_first_h1=True,
                content_start=CONTENT_START.get(filename),
            )

            front = _extract_front_matter(target)
            html_blocks = _extract_html_blocks(target)
            md = _reinject_html_blocks(md, html_blocks)
            # FAQ pages: reconstruct <h4> anchors and --- separators
            if filename in ("faq.md", "tw-faq.md"):
                md = _faq_postprocess(md)
            # Strip leading blank lines — front matter already ends with \n\n
            md = md.lstrip("\n")
            target.write_text(front + md, encoding="utf-8")
            print(f"{filename} ← tab {tab_id}")


if __name__ == "__main__":
    main()
