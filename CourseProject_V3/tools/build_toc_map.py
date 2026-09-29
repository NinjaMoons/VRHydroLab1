#!/usr/bin/env python3
"""Resolve report heading page numbers from a rendered draft PDF."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "docs" / "REPORT_MASTER.md"


def normalise(value: str) -> str:
    value = value.replace("–", "-").replace("—", "-").replace("‑", "-")
    return re.sub(r"\s+", " ", value).strip().casefold()


def headings(source):
    result = []
    for line in source.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^(#{1,2})\s+(.*)$", line)
        if not match:
            continue
        title = match.group(2).strip()
        if title in {"Пояснительная записка к курсовому проекту", "Титульный лист", "Содержание"}:
            continue
        result.append(title)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    args = parser.parse_args()

    pages = [normalise(page.extract_text() or "") for page in PdfReader(str(args.pdf)).pages]
    resolved = {}
    missing = []
    for title in headings(args.source.resolve()):
        needle = normalise(title)
        matches = [number for number, text in enumerate(pages, 1) if number != 4 and needle in text]
        if not matches:
            missing.append(title)
        else:
            resolved[title] = matches[0]
    if missing:
        raise SystemExit("Unresolved headings: " + "; ".join(missing))
    args.output.write_text(json.dumps(resolved, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.output)
    for title, page in resolved.items():
        print(f"{page:>2}  {title}")


if __name__ == "__main__":
    main()
