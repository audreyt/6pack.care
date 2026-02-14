#!/usr/bin/env python3
"""Shared configuration for Google Doc sync scripts/workflows."""

from __future__ import annotations

import argparse

DOC_ID = "1qmurZps5LUyFhjbM1C6DXtWrZvWXDd3rjIXpWsAABO0"
SITE_URL = "https://6pack.care"

# Files managed by the doc-sync workflow.
SYNC_FILES = ("index.md", "manifesto.md", "faq.md")

# Mapping from local filename to Google Docs tab id.
TAB_MAP: dict[str, str] = {
    "faq.md": "t.jutu46j75do3",
    "manifesto.md": "t.iphokcalvpzi",
    "index.md": "t.n06zotu1buvc",
}


def get_files_for_shell() -> str:
    """Return synchronized file list in a shell-safe, space-separated format."""
    return " ".join(SYNC_FILES)


def get_files_for_scope() -> str:
    """Return Markdown list used by workflow PR/body messages."""
    return ", ".join(f"`{name}`" for name in SYNC_FILES)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--print-files",
        action="store_true",
        help="Print space-separated list of synced markdown files",
    )
    parser.add_argument(
        "--print-scope",
        action="store_true",
        help="Print markdown-formatted list for workflow message bodies",
    )
    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    if args.print_files:
        print(get_files_for_shell())
    elif args.print_scope:
        print(get_files_for_scope())
    else:
        build_parser().print_help()
        raise SystemExit(1)
