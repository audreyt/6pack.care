#!/usr/bin/env python3
"""Shared configuration for Google Doc sync scripts/workflows."""

from __future__ import annotations

import argparse

DOC_ID = "1qmurZps5LUyFhjbM1C6DXtWrZvWXDd3rjIXpWsAABO0"
DOC_ID_TW = "1RPe4yOtWcixia8ludAU0DDLTMcbV1zSKP2isxD_ljIo"
SITE_URL = "https://6pack.care"

# Files managed by the doc-sync workflow.
SYNC_FILES = (
    "index.md", "manifesto.md", "faq.md",
    "1.md", "2.md", "3.md", "4.md", "5.md", "6.md",
    "tw-index.md", "tw-manifesto.md", "tw-faq.md",
    "tw-1.md", "tw-2.md", "tw-3.md", "tw-4.md", "tw-5.md", "tw-6.md",
)

# Mapping from local filename to Google Docs tab id.
TAB_MAP: dict[str, str] = {
    "faq.md": "t.jutu46j75do3",
    "manifesto.md": "t.iphokcalvpzi",
    "index.md": "t.n06zotu1buvc",
    "1.md": "t.wvx7cq952sj5",
    "2.md": "t.w4pue0hgeutw",
    "3.md": "t.a0wddqpxtuk7",
    "4.md": "t.8b7he5x870mo",
    "5.md": "t.keauzhwx9sq",
    "6.md": "t.rk66ffskrbnk",
    "tw-index.md": "t.0",
    "tw-manifesto.md": "t.pstem4cg1bvo",
    "tw-1.md": "t.mzhiy338dord",
    "tw-2.md": "t.nv6d0g7hrqd0",
    "tw-3.md": "t.tl7fjs4m0x99",
    "tw-4.md": "t.ee73sjuyra3m",
    "tw-5.md": "t.5vty71f16vz6",
    "tw-6.md": "t.aozqqajhyyft",
    "tw-faq.md": "t.au4rn9sutt1y",
}

# Per-file doc ID override (files not listed default to DOC_ID).
FILE_DOC_ID: dict[str, str] = {f: DOC_ID_TW for f in (
    "tw-index.md", "tw-manifesto.md", "tw-faq.md",
    "tw-1.md", "tw-2.md", "tw-3.md", "tw-4.md", "tw-5.md", "tw-6.md",
)}

# Partial-tab sync: only manage content from the first heading whose
# text starts with the given prefix.  Files not listed sync the full tab.
CONTENT_START: dict[str, str] = {
    "1.md": "Pack 1",
    "2.md": "Pack 2",
    "3.md": "Pack 3",
    "4.md": "Pack 4",
    "5.md": "Pack 5",
    "6.md": "Pack 6",
}


def doc_id_for(filename: str) -> str:
    """Return the Google Doc ID that owns *filename*."""
    return FILE_DOC_ID.get(filename, DOC_ID)


def validate_sync_config() -> None:
    """Ensure SYNC_FILES and TAB_MAP keys are consistent."""
    seen: set[str] = set()
    duplicates = []
    for filename in SYNC_FILES:
        if filename in seen:
            duplicates.append(filename)
        seen.add(filename)

    if duplicates:
        raise SystemExit(
            "doc-sync config invalid: duplicate filenames in SYNC_FILES: "
            f"{', '.join(sorted(set(duplicates)))}"
        )

    sync_files = set(SYNC_FILES)
    mapped_files = set(TAB_MAP.keys())
    missing_in_map = [name for name in SYNC_FILES if name not in mapped_files]
    extra_in_map = sorted(mapped_files - sync_files)

    if missing_in_map or extra_in_map:
        details = []
        if missing_in_map:
            details.append(
                "files missing tab mappings: " + ", ".join(missing_in_map)
            )
        if extra_in_map:
            details.append("tabs mapped to unknown files: " + ", ".join(extra_in_map))
        raise SystemExit(
            "doc-sync config invalid: "
            + "; ".join(details)
        )

    extra_start = sorted(set(CONTENT_START.keys()) - sync_files)
    if extra_start:
        raise SystemExit(
            "doc-sync config invalid: CONTENT_START references unknown files: "
            + ", ".join(extra_start)
        )

    extra_doc_id = sorted(set(FILE_DOC_ID.keys()) - sync_files)
    if extra_doc_id:
        raise SystemExit(
            "doc-sync config invalid: FILE_DOC_ID references unknown files: "
            + ", ".join(extra_doc_id)
        )


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
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate doc sync configuration and exit",
    )
    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    if args.check:
        validate_sync_config()
        print("doc-sync config OK")
    elif args.print_files:
        print(get_files_for_shell())
    elif args.print_scope:
        print(get_files_for_scope())
    else:
        build_parser().print_help()
        raise SystemExit(1)
