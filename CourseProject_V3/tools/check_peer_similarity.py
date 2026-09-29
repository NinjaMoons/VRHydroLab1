#!/usr/bin/env python3
"""Find exact long phrase overlap between V2 prose and extracted peer reports."""

import argparse
import json
import re
from pathlib import Path


def words(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"https?://\S+", " ", text)
    return re.findall(r"[A-Za-zА-Яа-яЁё0-9]+", text.lower())


def ngrams(tokens, size):
    return {" ".join(tokens[index:index + size]) for index in range(len(tokens) - size + 1)}


parser = argparse.ArgumentParser()
parser.add_argument("--report", type=Path, required=True)
parser.add_argument("--inventory", type=Path, default=Path("/tmp/cpv3_peer_inventory.json"))
parser.add_argument("--representatives", type=Path, default=Path("/tmp/cpv3_peer_representatives.json"))
parser.add_argument("--words", type=int, default=20)
args = parser.parse_args()

report_text = args.report.read_text(encoding="utf-8")
if "# 1 " in report_text:
    report_text = report_text[report_text.index("# 1 "):]
if "# Список использованных источников" in report_text:
    report_text = report_text[:report_text.index("# Список использованных источников")]
report_set = ngrams(words(report_text), args.words)
inventory = {item["path"]: item for item in json.loads(args.inventory.read_text(encoding="utf-8"))}
representatives = json.loads(args.representatives.read_text(encoding="utf-8"))
matches = []
for representative in representatives:
    peer = inventory[representative["path"]]
    overlap = sorted(report_set & ngrams(words(peer["text"]), args.words))
    if overlap:
        matches.append({
            "student": representative["student_folder"],
            "count": len(overlap),
            "examples": overlap[:3],
        })

print(json.dumps({
    "status": "PASS" if not matches else "REVIEW",
    "window_words": args.words,
    "reports_checked": len(representatives),
    "matches": matches,
}, ensure_ascii=False, indent=2))
