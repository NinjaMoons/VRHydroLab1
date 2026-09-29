#!/usr/bin/env python3

"""Apply validated flow parameters to an isolated OpenFOAM case."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from geometry import derived_values, load_settings


NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"


def replace_all(path: Path, pattern: str, replacement: str, minimum: int = 1) -> None:
    content = path.read_text(encoding="utf-8")
    changed, count = re.subn(pattern, replacement, content)
    if count < minimum:
        raise RuntimeError(f"Expected at least {minimum} replacements in {path}, got {count}")
    path.write_text(changed, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("case", type=Path)
    parser.add_argument("settings", type=Path)
    args = parser.parse_args()
    case = args.case.resolve()
    settings = load_settings(args.settings)
    derived = derived_values(settings)
    flow = settings["flow"]

    velocity = float(flow["Uin"])
    replace_all(
        case / "0" / "U",
        rf"uniform\s+\({NUMBER}\s+0\s+0\);",
        f"uniform ({velocity:.12g} 0 0);",
        minimum=2,
    )
    for field, value in (("k", derived["kInlet"]), ("omega", derived["omegaInlet"])):
        replace_all(
            case / "0" / field,
            rf"uniform\s+{NUMBER};",
            f"uniform {value:.15g};",
            minimum=3,
        )
    replace_all(
        case / "constant" / "physicalProperties",
        rf"(?m)^nu\s+{NUMBER};",
        f"nu              {float(flow['nu']):.15g};",
    )
    (case / "derived.json").write_text(
        json.dumps(derived, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("CASE_PARAMETERS_OK")
    print(json.dumps(derived, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
