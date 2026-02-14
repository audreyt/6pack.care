#!/usr/bin/env python3
"""Push markdown file(s) to Google Doc tabs via the Docs API.

Reads YAML front matter for the page title (→ HEADING_1), parses the
markdown body into headings / paragraphs / lists with inline formatting,
then clears the target tab and rebuilds it via a single batchUpdate.

Auth: expects GOOGLE_REFRESH_TOKEN, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
in the environment (e.g. from GitHub Secrets).
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from doc_sync_config import DOC_ID, SITE_URL, TAB_MAP, SYNC_FILES, CONTENT_START, validate_sync_config

HEADING_STYLE = {
    1: "HEADING_1",
    2: "HEADING_2",
    3: "HEADING_3",
    4: "HEADING_4",
    5: "HEADING_5",
    6: "HEADING_6",
}

# ── Data types ───────────────────────────────────────────────────────


@dataclass
class Span:
    text: str
    bold: bool = False
    italic: bool = False
    link: Optional[str] = None


@dataclass
class Block:
    heading_level: int = 0  # 0 = paragraph, 1‑6 = heading
    spans: list[Span] = field(default_factory=list)
    is_list_item: bool = False
    list_ordered: bool = False
    is_separator: bool = False  # blank line / ---


# ── URL helpers ──────────────────────────────────────────────────────


def _normalise_url(url: str, page_path: str = "/faq/") -> str:
    """Convert relative markdown links to absolute 6pack.care URLs."""
    if url.startswith(("http://", "https://")):
        return url
    if url.startswith("#"):
        return f"{SITE_URL}{page_path}{url}"
    if url.startswith("../"):
        return f"{SITE_URL}/{url[3:]}"
    if url.startswith("/"):
        return f"{SITE_URL}{url}"
    return url


# ── Inline markdown parser ───────────────────────────────────────────


def _parse_inline(text: str, page_path: str = "/faq/") -> list[Span]:
    """Parse **bold**, *italic*, and [text](url) into Spans."""
    spans: list[Span] = []
    pos = 0
    buf = ""
    bold = False
    italic = False

    while pos < len(text):
        ch = text[pos]

        # **bold toggle**
        if text[pos : pos + 2] == "**":
            if buf:
                spans.append(Span(buf, bold=bold, italic=italic))
                buf = ""
            bold = not bold
            pos += 2
            continue

        # *italic toggle* (single *, not **)
        if ch == "*" and text[pos : pos + 2] != "**":
            if buf:
                spans.append(Span(buf, bold=bold, italic=italic))
                buf = ""
            italic = not italic
            pos += 1
            continue

        # [link text](url)
        if ch == "[":
            bracket = text.find("]", pos + 1)
            if bracket != -1 and text[bracket : bracket + 2] == "](":
                paren = text.find(")", bracket + 2)
                if paren != -1:
                    if buf:
                        spans.append(Span(buf, bold=bold, italic=italic))
                        buf = ""
                    link_text = text[pos + 1 : bracket]
                    link_url = _normalise_url(text[bracket + 2 : paren], page_path)
                    spans.append(Span(link_text, bold=bold, italic=italic, link=link_url))
                    pos = paren + 1
                    continue

        buf += ch
        pos += 1

    if buf:
        spans.append(Span(buf, bold=bold, italic=italic))

    return spans or [Span(text)]


# ── Front-matter parser ─────────────────────────────────────────────


def _parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text

    fm: dict[str, str] = {}
    for line in parts[1].strip().splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip().strip("\"'")

    return fm, parts[2].strip()


# ── Markdown → Block list ───────────────────────────────────────────

_H4_RE = re.compile(r"<h4[^>]*>(.*?)</h4>", re.DOTALL)
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")
_NUM_LIST_RE = re.compile(r"^(\d+)\.\s+(.+)$")


def _strip_html_blocks(body: str) -> str:
    """Remove multi-line HTML block elements (<div>…</div>) that can't
    be represented in Google Docs.  Tracks nesting depth so nested divs
    are handled correctly."""
    lines = body.split("\n")
    result: list[str] = []
    depth = 0
    for line in lines:
        stripped = line.strip()
        opens = len(re.findall(r"<div\b", stripped))
        closes = len(re.findall(r"</div>", stripped))
        if depth > 0 or opens > 0:
            depth += opens - closes
            if depth < 0:
                depth = 0
            continue
        result.append(line)
    return "\n".join(result)


def parse_markdown(text: str, filename: str = "faq.md") -> tuple[str, list[Block]]:
    """Return (title_from_frontmatter, blocks)."""
    fm, body = _parse_front_matter(text)
    title = fm.get("title", "")
    # derive page_path from permalink or filename
    permalink = fm.get("permalink", "")
    if not permalink:
        permalink = "/" + Path(filename).stem + "/"
    page_path = permalink.rstrip("/") + "/"

    # strip multi-line HTML blocks (audio sections, etc.)
    body = _strip_html_blocks(body)

    blocks: list[Block] = []
    para_lines: list[str] = []

    def flush():
        if para_lines:
            joined = " ".join(para_lines)
            blocks.append(Block(spans=_parse_inline(joined, page_path)))
            para_lines.clear()

    for line in body.split("\n"):
        stripped = line.strip()

        # blank line
        if not stripped:
            flush()
            if blocks and not blocks[-1].is_separator:
                blocks.append(Block(is_separator=True))
            continue

        # skip HTML block elements (can't be represented in Google Docs)
        if stripped.startswith("<") and not _H4_RE.match(stripped):
            continue

        # horizontal rule
        if stripped == "---":
            flush()
            if blocks and not blocks[-1].is_separator:
                blocks.append(Block(is_separator=True))
            continue

        # HTML <h4> (FAQ questions)
        m = _H4_RE.match(stripped)
        if m:
            flush()
            plain = re.sub(r"<[^>]+>", "", m.group(1)).strip()
            blocks.append(Block(heading_level=4, spans=_parse_inline(plain, page_path)))
            continue

        # markdown heading
        m = _HEADING_RE.match(stripped)
        if m:
            flush()
            level = len(m.group(1))
            blocks.append(Block(heading_level=level, spans=_parse_inline(m.group(2), page_path)))
            continue

        # numbered list
        m = _NUM_LIST_RE.match(stripped)
        if m:
            flush()
            blocks.append(
                Block(spans=_parse_inline(m.group(2), page_path), is_list_item=True, list_ordered=True)
            )
            continue

        # bullet list
        if stripped.startswith("- "):
            flush()
            blocks.append(Block(spans=_parse_inline(stripped[2:], page_path), is_list_item=True))
            continue

        # indented continuation of a list item (e.g., multi-line bullets)
        if line != line.lstrip() and blocks and blocks[-1].is_list_item and not para_lines:
            blocks[-1].spans.append(Span("\n"))
            blocks[-1].spans.extend(_parse_inline(stripped, page_path))
            continue

        # regular text — accumulate
        para_lines.append(stripped)

    flush()

    # trim trailing separators
    while blocks and blocks[-1].is_separator:
        blocks.pop()

    return title, blocks


# ── Block list → Docs API requests ──────────────────────────────────


def _build_requests(
    title: str,
    blocks: list[Block],
    tab_id: str,
    end_index: int,
    insert_at: int = 1,
) -> tuple[list[dict], str]:
    """Return (requests, assembled_text).

    *insert_at* is the document index where new content is placed.
    For full-tab sync this is 1 (right after the section break).
    For partial-tab sync it is the startIndex of the boundary heading,
    so everything before it is preserved.
    """
    requests: list[dict] = []

    # 1. clear managed range
    if end_index > insert_at + 1:
        requests.append(
            {
                "deleteContentRange": {
                    "range": {
                        "startIndex": insert_at,
                        "endIndex": end_index - 1,
                        "tabId": tab_id,
                    }
                }
            }
        )

    # 2. assemble text and collect formatting metadata
    parts: list[str] = []
    para_styles: list[tuple[int, int, str]] = []
    text_styles: list[tuple[int, int, Span]] = []
    bullet_ranges: list[tuple[int, int, bool]] = []

    cursor = 0

    # title → HEADING_1
    if title:
        start = cursor
        parts.append(title + "\n")
        cursor += len(title) + 1
        para_styles.append((start, cursor, "HEADING_1"))
        # blank line after title
        parts.append("\n")
        cursor += 1

    for block in blocks:
        if block.is_separator:
            parts.append("\n")
            cursor += 1
            continue

        block_start = cursor

        for span in block.spans:
            span_start = cursor
            parts.append(span.text)
            cursor += len(span.text)
            if span.bold or span.italic or span.link:
                text_styles.append((span_start, cursor, span))

        parts.append("\n")
        cursor += 1
        block_end = cursor

        if block.heading_level > 0:
            para_styles.append(
                (block_start, block_end, HEADING_STYLE[block.heading_level])
            )

        if block.is_list_item:
            bullet_ranges.append((block_start, block_end, block.list_ordered))

    full_text = "".join(parts)

    # 3. insert all text
    requests.append(
        {
            "insertText": {
                "location": {"index": insert_at, "tabId": tab_id},
                "text": full_text,
            }
        }
    )

    # 4. reset bold/italic on entire range — inserted text inherits
    #    the heading style from the character at the insertion point,
    #    so everything becomes bold unless we clear it first.
    if full_text:
        requests.append(
            {
                "updateTextStyle": {
                    "range": {
                        "startIndex": insert_at,
                        "endIndex": insert_at + len(full_text),
                        "tabId": tab_id,
                    },
                    "textStyle": {"bold": False, "italic": False},
                    "fields": "bold,italic",
                }
            }
        )

    # 5. paragraph styles (headings)
    for start, end, style in para_styles:
        requests.append(
            {
                "updateParagraphStyle": {
                    "range": {
                        "startIndex": start + insert_at,
                        "endIndex": end + insert_at,
                        "tabId": tab_id,
                    },
                    "paragraphStyle": {"namedStyleType": style},
                    "fields": "namedStyleType",
                }
            }
        )

    # 6. text styles (bold, italic, links)
    for start, end, span in text_styles:
        if start >= end:
            continue
        style: dict = {}
        fields: list[str] = []
        if span.bold:
            style["bold"] = True
            fields.append("bold")
        if span.italic:
            style["italic"] = True
            fields.append("italic")
        if span.link:
            style["link"] = {"url": span.link}
            fields.append("link")
        if fields:
            requests.append(
                {
                    "updateTextStyle": {
                        "range": {
                            "startIndex": start + insert_at,
                            "endIndex": end + insert_at,
                            "tabId": tab_id,
                        },
                        "textStyle": style,
                        "fields": ",".join(fields),
                    }
                }
            )

    # 7. bullets — merge consecutive same-type items into one range
    merged: list[tuple[int, int, bool]] = []
    for start, end, ordered in bullet_ranges:
        if merged and merged[-1][2] == ordered and start == merged[-1][1]:
            merged[-1] = (merged[-1][0], end, ordered)
        else:
            merged.append((start, end, ordered))

    for start, end, ordered in merged:
        preset = (
            "NUMBERED_DECIMAL_ALPHA_ROMAN"
            if ordered
            else "BULLET_DISC_CIRCLE_SQUARE"
        )
        requests.append(
            {
                "createParagraphBullets": {
                    "range": {
                        "startIndex": start + insert_at,
                        "endIndex": end + insert_at,
                        "tabId": tab_id,
                    },
                    "bulletPreset": preset,
                }
            }
        )

    return requests, full_text


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


def _validate_paths(files: list[str]) -> list[Path]:
    paths = [Path(path) for path in files]
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


def _find_content_start(body: dict, prefix: str) -> Optional[int]:
    """Return the startIndex of the first heading whose text starts with *prefix*.

    Scans the structural elements in the tab body for a paragraph styled
    as any heading level whose plain text begins with the given prefix.
    Returns ``None`` if no match is found.
    """
    for elem in body.get("content", []):
        para = elem.get("paragraph")
        if not para:
            continue
        named = para.get("paragraphStyle", {}).get("namedStyleType", "")
        if named not in HEADING_STYLE.values():
            continue
        text = "".join(
            el.get("textRun", {}).get("content", "")
            for el in para.get("elements", [])
        ).strip()
        if text.startswith(prefix):
            return elem["startIndex"]
    return None


# ── Main ─────────────────────────────────────────────────────────────


def main() -> None:
    validate_sync_config()
    md_files = sys.argv[1:] if len(sys.argv) > 1 else list(SYNC_FILES)
    md_paths = _validate_paths(md_files)

    creds = _credentials()
    service = build("docs", "v1", credentials=creds)

    doc = service.documents().get(
        documentId=DOC_ID,
        includeTabsContent=True,
    ).execute()

    for md_path in md_paths:
        filename = md_path.name
        tab_id = TAB_MAP.get(filename)
        if not tab_id:
            _warn_no_tab_mapping(filename)
            continue

        tab = _find_tab(doc["tabs"], tab_id)
        if not tab:
            _warn_tab_not_found(filename, tab_id)
            continue

        body = tab["documentTab"]["body"]
        end_index = body["content"][-1]["endIndex"]

        # Determine where managed content starts in the tab.
        content_prefix = CONTENT_START.get(filename)
        if content_prefix:
            boundary = _find_content_start(body, content_prefix)
            offset = boundary if boundary is not None else end_index - 1
        else:
            offset = 1  # full-tab sync (after section break)

        md_text = md_path.read_text(encoding="utf-8")
        title, blocks = parse_markdown(md_text, filename=filename)
        requests, full_text = _build_requests(
            title, blocks, tab_id, end_index, insert_at=offset,
        )

        result = service.documents().batchUpdate(
            documentId=DOC_ID,
            body={"requests": requests},
        ).execute()

        rev = result.get("writeControl", {}).get("requiredRevisionId", "?")
        print(
            f"{filename} → tab {tab_id}: "
            f"{len(blocks)} blocks, {len(requests)} requests, rev {rev[:12]}…"
        )


if __name__ == "__main__":
    main()
