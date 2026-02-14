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
import sys
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ── Configuration (keep in sync with sync_to_google_doc.py) ──────────

DOC_ID = "1qmurZps5LUyFhjbM1C6DXtWrZvWXDd3rjIXpWsAABO0"
SITE_URL = "https://6pack.care"

TAB_MAP: dict[str, str] = {
    "faq.md": "t.jutu46j75do3",
    "manifesto.md": "t.iphokcalvpzi",
    "index.md": "t.n06zotu1buvc",
}

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
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(TAB_MAP.keys())

    creds = _credentials()
    service = build("docs", "v1", credentials=creds)

    doc = (
        service.documents()
        .get(documentId=DOC_ID, includeTabsContent=True)
        .execute()
    )

    for filename in targets:
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

        target = Path(filename)
        front = _extract_front_matter(target)
        target.write_text(front + md, encoding="utf-8")
        print(f"{filename} ← tab {tab_id}")


if __name__ == "__main__":
    main()
