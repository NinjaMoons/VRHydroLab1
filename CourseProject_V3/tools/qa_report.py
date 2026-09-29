#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--report", type=Path, default=ROOT / "docs" / "REPORT_MASTER.md")
args = parser.parse_args()
REPORT = args.report.resolve()
text = REPORT.read_text(encoding="utf-8")
errors = []

markers = ("UNVERIFIED", "TODO", "PENDING", "PLACEHOLDER", "FIXME", "TBD", "XXX", "ВСТАВИТЬ")
for marker in markers:
    if marker in text:
        errors.append(f"forbidden marker: {marker}")
for foreign in (
    "Володин", "Гаджиламаммаев", "Горькова", "Емельянов", "Зайцева",
    "Каргин", "Клинюшин", "Лях", "Макарцева", "Молчанова", "Нагорная",
    "Панин", "Пимахин", "Попович", "Пяткин", "Ревина", "Сарычев",
    "Синтюрин", "Старков", "Табасный", "Телекаев", "Тимершина",
    "Цветкова", "Шамов",
):
    if foreign in text:
        errors.append(f"foreign trace: {foreign}")
for variant in ("№1", "№2", "№6", "№7", "№8", "№10", "№15", "№16", "№19", "№22", "№24", "№25", "№26"):
    if f"вариант {variant}" in text.lower():
        errors.append(f"wrong variant trace: {variant}")
for medium in ("воздух", " air "):
    if medium in text.lower():
        errors.append(f"wrong medium trace: {medium.strip()}")

images = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)
figure_numbers = [int(v) for v in re.findall(r"\*\*Рисунок (\d+) —", text)]
table_numbers = [int(v) for v in re.findall(r"\*\*Таблица (\d+) —", text)]
listing_numbers = [int(v) for v in re.findall(r"\*\*Листинг (\d+) —", text)]

for label, values in (("figures", figure_numbers), ("tables", table_numbers), ("listings", listing_numbers)):
    expected = list(range(1, len(values) + 1))
    if values != expected:
        errors.append(f"{label} numbering: {values}")

if len(images) != len(figure_numbers):
    errors.append(f"images/captions mismatch: {len(images)}/{len(figure_numbers)}")

image_info = []
for rel in images:
    path = (REPORT.parent / rel).resolve()
    if not path.is_file():
        errors.append(f"missing image: {rel}")
        continue
    with Image.open(path) as img:
        image_info.append((rel, img.format, img.size))

if text.count("```") % 2:
    errors.append("unbalanced code fences")

lines = text.splitlines()
for index, line in enumerate(lines):
    if not line.startswith("|") or index + 1 >= len(lines):
        continue
    if not re.match(r"^\|(?:\s*:?-+:?\s*\|)+$", lines[index + 1]):
        continue
    width = len(re.split(r"(?<!\\)\|", line)) - 2
    row = index + 2
    while row < len(lines) and lines[row].startswith("|"):
        current = len(re.split(r"(?<!\\)\|", lines[row])) - 2
        if current != width:
            errors.append(f"table row width at line {row + 1}: {current}!={width}")
        row += 1

references = re.findall(r"(?m)^\d+\. .+$", text[text.index("# Список использованных источников"):text.index("# Приложение А")])
cited = set()
for group in re.findall(r"\[([0-9, –-]+)\]", text[:text.index("# Список использованных источников")]):
    for part in group.split(","):
        part = part.strip()
        match = re.fullmatch(r"(\d+)[–-](\d+)", part)
        if match:
            cited.update(range(int(match.group(1)), int(match.group(2)) + 1))
        elif part.isdigit():
            cited.add(int(part))
reference_ids = set(range(1, len(references) + 1))
if cited != reference_ids:
    errors.append(f"citation coverage cited={sorted(cited)} refs={sorted(reference_ids)}")

baseline = json.loads((ROOT / "runs/baseline_v3_u0p1/results/summary.json").read_text(encoding="utf-8"))
speed = json.loads((ROOT / "runs/speed_v3_u0p15/results/summary.json").read_text(encoding="utf-8"))
geometry = json.loads((ROOT / "runs/geometry_v3_changed/results/summary.json").read_text(encoding="utf-8"))
required_values = (
    str(baseline["mesh"]["salome"]["cells"]),
    f'{baseline["velocity"]["cellMaximumMagnitudeMps"]:.8f}',
    f'{baseline["pressure"]["dropPa"]:.9f}',
    f'{speed["velocity"]["cellMaximumMagnitudeMps"]:.8f}',
    f'{speed["pressure"]["dropPa"]:.9f}',
    str(geometry["mesh"]["salome"]["cells"]),
    f'{geometry["velocity"]["cellMaximumMagnitudeMps"]:.8f}',
)
for value in required_values:
    if value not in text:
        errors.append(f"source value absent from report: {value}")

print(json.dumps({
    "status": "PASS" if not errors else "FAIL",
    "errors": errors,
    "words": len(text.split()),
    "figures": len(figure_numbers),
    "tables": len(table_numbers),
    "listings": len(listing_numbers),
    "references": len(references),
    "appendices": len(re.findall(r"(?m)^# Приложение [А-Я] —", text)),
    "citations": sorted(cited),
    "images": image_info,
}, ensure_ascii=False, indent=2))
raise SystemExit(1 if errors else 0)
