#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fetch markdown tabs from the published Google Doc via curl and regenerate local files."""

from __future__ import annotations

import argparse
import subprocess
import re
from pathlib import Path
from typing import Dict, Iterable, List, Set
from urllib.parse import parse_qs, unquote, urlparse

from bs4 import BeautifulSoup, NavigableString, Tag

DEFAULT_DOC_URL = "https://docs.google.com/document/d/e/2PACX-1vTvWQ1BT8cUYdjPNCTFt-LL0tm_zv1KpvJyIzdS7NuHIbIdjFrwD243eMGie5O2um-iEuAGRRRLZ6PQ/pub"
PACK_PATTERN = re.compile(r"^Pack ([1-6]):\s*(.+)$")


def _run_curl(url: str) -> str:
    try:
        result = subprocess.run(
            ["curl", "-fsSL", url],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise SystemExit("curl is required but was not found in PATH") from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip() if exc.stderr else ""
        raise SystemExit(f"curl failed with exit code {exc.returncode}: {stderr}") from exc
    return result.stdout


def detect_locale(tab_name: str) -> str:
    return "zh-tw" if tab_name.startswith("tw") else "en"


def inline_text(node, bold_classes: Set[str]) -> str:
    if isinstance(node, NavigableString):
        return str(node)
    result: List[str] = []
    for child in node.children:
        if isinstance(child, NavigableString):
            result.append(str(child))
        else:
            name = child.name.lower()
            style = child.get("style", "")
            style_lower = style.lower().replace(" ", "")
            is_bold_style = any(token in style_lower for token in ("font-weight:bold", "font-weight:600", "font-weight:700", "font-weight:800", "font-weight:900"))
            classes = set(child.get("class", []))
            if name in {"strong", "b"} or is_bold_style or classes & bold_classes:
                result.append("**" + inline_text(child, bold_classes) + "**")
            elif name in {"em", "i"}:
                result.append("*" + inline_text(child, bold_classes) + "*")
            elif name == "a":
                href = _clean_href(child.get("href", "").strip())
                text = inline_text(child, bold_classes).strip() or href
                result.append(f"[{text}]({href})" if href else text)
            elif name == "br":
                result.append("\n")
            else:
                result.append(inline_text(child, bold_classes))
    text = "".join(result)
    text = re.sub(r"[\t\f\v]+", " ", text)
    text = re.sub(r" *\n *", "\\n", text)
    return text


def render_section(nodes: Iterable, locale: str, bold_classes: Set[str], skip_first_h1: bool = False) -> str:
    lines: List[str] = []
    state = {"pack": False, "seen_h1": False}

    def ensure_blank() -> None:
        if lines and lines[-1] != "":
            lines.append("")

    def finish_pack() -> None:
        if state["pack"]:
            ensure_blank()
            state["pack"] = False

    for node in nodes:
        if isinstance(node, NavigableString):
            continue
        name = getattr(node, "name", "").lower()
        
        # Check if this node contains text that indicates start of next chapter
        node_text = node.get_text(strip=True)
        if node_text and (node_text.startswith("Chapter 8:") or node_text.startswith("# Chapter 8:") or 
                         node_text.startswith("ch8:") or node_text.startswith("**ch8:") or
                         node_text.startswith("**ch9:") or node_text.startswith("Chapter 9:")):
            # Stop processing this section
            break
            
        if name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            finish_pack()
            level = int(name[1])
            # Skip the first H1 if requested (chapter files have title in front matter)
            if skip_first_h1 and level == 1 and not state["seen_h1"]:
                state["seen_h1"] = True
                continue
            ensure_blank()
            heading = node.get_text(strip=True)
            lines.append("#" * level + " " + heading)
            ensure_blank()
        elif name in {"p", "li"}:
            text = inline_text(node, bold_classes).strip()
            if not text:
                continue
            match = PACK_PATTERN.match(text) if locale == "en" else None
            if locale == "en" and match:
                num, remainder = match.groups()
                title_part, body_part = remainder, ""
                if " — " in remainder:
                    title_part, body_part = remainder.split(" — ", 1)
                title_part = title_part.strip()
                body_part = body_part.strip()
                if num == "1":
                    label = f"**[Pack {num}: {title_part}](/1)**"
                else:
                    label = f"**Pack {num}: {title_part}**"
                if num == "4" and "kami" in body_part:
                    body_part = body_part.replace(" an local ", " a local ")
                    body_part = body_part.replace("kami", "**kami**", 1)
                bullet = f"- {label}"
                if body_part:
                    bullet += f" — {body_part}"
                if not state["pack"]:
                    ensure_blank()
                lines.append(bullet)
                state["pack"] = True
                continue
            finish_pack()
            ensure_blank()
            if locale == "en" and text.startswith("At the heart of our work is the 6-Pack"):
                text = text.replace("At the heart of our work is the 6-Pack", "At the heart of our work is the **6-Pack", 1)
            lines.append(text)
            ensure_blank()
        elif name in {"ul", "ol"}:
            finish_pack()
            bullet = "-" if name == "ul" else "1."
            ensure_blank()
            for li in node.find_all("li", recursive=False):
                text = inline_text(li, bold_classes).strip()
                if text:
                    lines.append(f"{bullet} {text}")
            ensure_blank()
        else:
            finish_pack()
            html_block = node.decode().strip()
            if html_block:
                ensure_blank()
                lines.append(html_block)
                ensure_blank()

    finish_pack()
    cleaned: List[str] = []
    for line in lines:
        if line == "":
            if cleaned and cleaned[-1] == "":
                continue
            if not cleaned:
                continue
            cleaned.append("")
        else:
            cleaned.append(line.rstrip())
    if cleaned and cleaned[-1] == "":
        cleaned.pop()
    return "\n".join(cleaned).strip() + "\n"


def extract_front_matter(path: Path) -> str:
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                return "---" + parts[1] + "---\n\n"
    return ""


def _clean_href(href: str) -> str:
    if not href:
        return href

    parsed = urlparse(href)
    if "google.com" in parsed.netloc and parsed.path == "/url":
        target = parse_qs(parsed.query).get("q")
        if target:
            href = unquote(target[0])
            parsed = urlparse(href)

    if parsed.scheme in {"http", "https"} and parsed.netloc.endswith("6pack.care"):
        path = parsed.path or "/"
        href = path if path.startswith("/") else f"/{path}"
        if parsed.query:
            href = f"{href}?{parsed.query}"

    return href


def gather_sections(contents: Tag) -> Dict[str, List]:
    sections: Dict[str, List] = {}
    seen: set[str] = set()
    markers: List[Tag] = []
    for tag in contents.find_all(True):
        text = tag.get_text(strip=True)
        if text.endswith(".md") and text not in seen:
            markers.append(tag)
            seen.add(text)
    for marker in markers:
        name = marker.get_text(strip=True)
        nodes: List[Tag] = []
        for sibling in marker.next_siblings:
            if isinstance(sibling, NavigableString):
                continue
            if not hasattr(sibling, "get_text"):
                continue
            text = sibling.get_text(strip=True)
            if text.lower().endswith(".md") or text.strip().lower() == "manifesto":
                break
            nodes.append(sibling)
        sections[name] = nodes
    return sections


def extract_bold_classes(contents: Tag) -> Set[str]:
    bold: Set[str] = set()
    for style_tag in contents.find_all("style"):
        css = style_tag.string or ""
        for match in re.finditer(r"\.([a-zA-Z0-9_-]+)\s*\{[^}]*font-weight\s*:\s*([^;}]*)", css):
            cls, weight = match.groups()
            weight_clean = weight.strip().lower()
            if any(token in weight_clean for token in ("bold", "600", "700", "800", "900")):
                bold.add(cls)
    return bold


def regenerate_markdown(doc_url: str) -> List[str]:
    html = _run_curl(doc_url)
    soup = BeautifulSoup(html, "lxml")
    contents = soup.find("div", id="contents")
    if contents is None:
        raise SystemExit("Could not locate contents div in published document")

    sections = gather_sections(contents)
    if not sections:
        raise SystemExit("No .md tabs found in document")

    bold_classes = extract_bold_classes(contents)

    updated: List[str] = []
    for tab, nodes in sections.items():
        # Map chapter names to numbered files
        chapter_mapping = {
            "ch1: attentiveness.md": "1.md",
            "ch2: responsibility.md": "2.md", 
            "ch3: competence.md": "3.md",
            "ch4: responsiveness.md": "4.md",
            "ch5: solidarity.md": "5.md",
            "ch6: symbiosis.md": "6.md",
            "ch7: faq.md": "7.md"
        }
        
        target_name = chapter_mapping.get(tab, tab)
        target = Path(target_name)
        locale = detect_locale(tab)
        # Skip first H1 for chapter files (they have title in front matter)
        is_chapter = target_name in chapter_mapping.values() or target_name.startswith("tw-") and target_name[3:] in chapter_mapping.values()
        content = render_section(nodes, locale, bold_classes, skip_first_h1=is_chapter)
        front = extract_front_matter(target)
        target.write_text(front + content, encoding="utf-8")
        updated.append(target_name)
    return updated


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--doc-url", default=DEFAULT_DOC_URL, help="Published Google Doc URL")
    args = parser.parse_args()

    updated = regenerate_markdown(args.doc_url)
    if updated:
        print("Updated:", ", ".join(sorted(updated)))
    else:
        print("No markdown tabs updated")


if __name__ == "__main__":
    main()
