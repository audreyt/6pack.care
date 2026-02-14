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
from pathlib import Path

from doc_sync_config import DOC_ID, SITE_URL, TAB_MAP, SYNC_FILES, validate_sync_config

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
            raise SystemExit(f"Missing sync source file: {path}")
    return paths


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


def _run_to_md(run: dict, page_path: str) -> str:
    """Convert a single textRun to inline markdown."""
    content = run.get("content", "")
    if not content or content == "\n":
        return content

    style = run.get("textStyle", {})
    bold = style.get("bold", False)
    italic = style.get("italic", False)
    link = style.get("link", {}).get("url", "")

    text = content.rstrip("\n")

    if link:
        url = _relativise_url(link, page_path)
        text = f"[{text}]({url})"
    if bold and italic:
        text = f"***{text}***"
    elif bold:
        text = f"**{text}**"
    elif italic:
        text = f"*{text}*"

    return text


def _is_ordered(lists_meta: dict, list_id: str, nesting: int) -> bool:
    """Check whether a list nesting level is ordered."""
    props = lists_meta.get(list_id, {})
    levels = props.get("listProperties", {}).get("nestingLevel", [])
    if nesting < len(levels):
        glyph = levels[nesting].get("glyphType", "")
        return glyph in ORDERED_GLYPH_TYPES
    return False


HEADING_LEVEL = {
    "HEADING_1": 1, "HEADING_2": 2, "HEADING_3": 3,
    "HEADING_4": 4, "HEADING_5": 5, "HEADING_6": 6,
}


def tab_to_markdown(
    tab: dict,
    page_path: str,
    skip_first_h1: bool = True,
) -> str:
    """Convert a Google Doc tab to markdown text (without front matter)."""
    body = tab["documentTab"]["body"]
    lists_meta = tab.get("documentTab", {}).get("lists", {})
    content = body.get("content", [])

    lines: list[str] = []
    seen_h1 = False
    prev_kind = ""  # "heading", "list", "para", "blank"

    for elem in content:
        para = elem.get("paragraph")
        if not para:
            continue

        # ── assemble inline text ──
        parts: list[str] = []
        for el in para.get("elements", []):
            tr = el.get("textRun")
            if tr:
                parts.append(_run_to_md(tr, page_path))
        text = "".join(parts).rstrip("\n").rstrip()

        # ── classify paragraph ──
        named = para.get("paragraphStyle", {}).get("namedStyleType", "NORMAL_TEXT")
        level = HEADING_LEVEL.get(named)
        bullet = para.get("bullet")

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


# ── Main ─────────────────────────────────────────────────────────────


def main() -> None:
    validate_sync_config()
    raw_targets = sys.argv[1:] if len(sys.argv) > 1 else list(SYNC_FILES)
    target_paths = _validate_targets(raw_targets)

    creds = _credentials()
    service = build("docs", "v1", credentials=creds)

    doc = (
        service.documents()
        .get(documentId=DOC_ID, includeTabsContent=True)
        .execute()
    )

    for target in target_paths:
        filename = target.name
        tab_id = TAB_MAP.get(filename)
        if not tab_id:
            print(f"skip {filename}: no tab mapping")
            continue

        tab = _find_tab(doc["tabs"], tab_id)
        if not tab:
            print(f"skip {filename}: tab {tab_id} not found")
            continue

        page_path = "/" + Path(filename).stem + "/"
        md = tab_to_markdown(tab, page_path, skip_first_h1=True)

        front = _extract_front_matter(target)
        html_blocks = _extract_html_blocks(target)
        md = _reinject_html_blocks(md, html_blocks)
        target.write_text(front + md, encoding="utf-8")
        print(f"{filename} ← tab {tab_id}")


if __name__ == "__main__":
    main()
