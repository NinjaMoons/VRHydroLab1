#!/usr/bin/env python3
"""Select one representative PDF per peer and extract report-level structure."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from pypdf import PdfReader


def student_key(path: Path) -> str:
    parts = path.parts
    return parts[parts.index("Черновик") + 1]


def normal(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def likely_heading(line: str) -> bool:
    line = normal(line)
    if not 3 <= len(line) <= 115:
        return False
    if re.match(r"^\d+(?:\.\d+){0,2}\s+[А-ЯA-Z]", line):
        return True
    if re.match(r"^(ВВЕДЕНИЕ|ЗАКЛЮЧЕНИЕ|АННОТАЦИЯ|СОДЕРЖАНИЕ|СПИСОК |ПРИЛОЖЕНИЕ )", line.upper()):
        return True
    return False


def extract_pdf(path: Path):
    reader = PdfReader(str(path))
    pages = [(page.extract_text() or "") for page in reader.pages]
    joined = "\n".join(pages)
    first = "\n".join(pages[:6])
    headings = []
    for page_number, page in enumerate(pages, 1):
        for line in page.splitlines():
            line = normal(line)
            if likely_heading(line) and line not in [item[1] for item in headings]:
                headings.append((page_number, line))
    topic_lines = []
    for line in first.splitlines():
        line = normal(line)
        if any(term in line.casefold() for term in ("тема", "вариант", "выполнил", "студент", "расчет", "расчёт", "разработка приложения")):
            if 3 < len(line) < 180:
                topic_lines.append(line)
    variants = sorted(set(re.findall(r"вариант(?:а|у|ом|е)?\s*(?:№|N)?\s*(\d{1,2})", joined, re.I)))
    media_snippets = []
    for match in re.finditer(r".{0,80}(?:рабочая среда|вода|воды|воздух).{0,100}", joined, re.I | re.S):
        snippet = normal(match.group(0))
        if snippet not in media_snippets:
            media_snippets.append(snippet)
        if len(media_snippets) == 5:
            break
    return {
        "pages": len(pages),
        "words": len(re.findall(r"[\wА-Яа-яЁё-]+", joined)),
        "headings": headings,
        "topic_lines": topic_lines[:18],
        "variants": variants,
        "media_snippets": media_snippets,
        "figures": max([int(x) for x in re.findall(r"рисунок\s+(\d+)", joined, re.I)] or [0]),
        "tables": max([int(x) for x in re.findall(r"таблиц[аы]\s+(\d+)", joined, re.I)] or [0]),
        "listings": max([int(x) for x in re.findall(r"листинг\s+(\d+)", joined, re.I)] or [0]),
        "stack": [term for term in (
            "SALOME", "OpenFOAM", "ParaView", "Python", "Node.js", "JavaScript",
            "HTML", "CSS", "Flask", "Django", "FastAPI", "PyQt", "Tkinter",
            "React", "Vue", "C#", "WPF", "MATLAB", "FreeCAD",
        ) if re.search(rf"(?<![\w.]){re.escape(term)}(?![\w.])", joined, re.I)],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("inventory", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    records = json.loads(args.inventory.read_text(encoding="utf-8"))
    groups = defaultdict(list)
    for record in records:
        path = Path(record["path"])
        if path.suffix.lower() != ".pdf":
            continue
        groups[student_key(path)].append(record)
    selected = []
    for student, candidates in sorted(groups.items()):
        # The most text-complete PDF is the representative; ties prefer explicit student filenames.
        representative = max(
            candidates,
            key=lambda item: (
                item.get("words", 0),
                student.replace(" ", "").casefold() in Path(item["path"]).name.replace(" ", "").casefold(),
                Path(item["path"]).stat().st_mtime,
            ),
        )
        path = Path(representative["path"])
        data = extract_pdf(path)
        data.update({"student_folder": student, "path": str(path)})
        selected.append(data)
    args.output.write_text(json.dumps(selected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"unique_reports={len(selected)}")
    for item in selected:
        print(
            f"{item['student_folder']} | {item['pages']} p | {item['words']} w | "
            f"fig {item['figures']} | tab {item['tables']} | list {item['listings']} | "
            f"variants {item['variants']} | {Path(item['path']).name}"
        )


if __name__ == "__main__":
    main()
