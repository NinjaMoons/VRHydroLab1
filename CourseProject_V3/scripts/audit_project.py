#!/usr/bin/env python3

"""Fail-fast audit of saved CourseProject_V3 evidence."""

from __future__ import annotations

import json
import struct
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
FULL_RUNS = ("baseline_v3_u0p1", "speed_v3_u0p15", "geometry_v3_changed")


def image_info(path: Path) -> dict:
    with path.open("rb") as stream:
        header = stream.read(24)
    if len(header) == 24 and header[:8] == b"\x89PNG\r\n\x1a\n":
        width, height = struct.unpack(">II", header[16:24])
        image_format = "PNG"
    elif header[:3] == b"\xff\xd8\xff":
        width = height = None
        image_format = "JPEG"
    else:
        raise RuntimeError(f"Unsupported image: {path}")
    return {"path": str(path.relative_to(PROJECT)), "format": image_format, "bytes": path.stat().st_size, "width": width, "height": height}


def main() -> None:
    checks = []
    for relative in (
        "settings.json", "salome/generate_mesh.py", "salome/final/CourseProject_V3.hdf",
        "salome/final/Mesh.unv", "app/server.js", "scripts/run_pipeline.py",
        "postprocessing/render_results.py", "docs/REPORT_DRAFT.md", "docs/DEFENSE_CHEATSHEET.md",
    ):
        path = PROJECT / relative
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"Missing artifact: {relative}")
        checks.append({"artifact": relative, "bytes": path.stat().st_size})

    run_checks = []
    for name in FULL_RUNS:
        directory = PROJECT / "runs" / name
        summary = json.loads((directory / "summary.json").read_text(encoding="utf-8"))
        check_mesh = (directory / "logs" / "checkMesh.log").read_text(encoding="utf-8", errors="replace")
        solver = (directory / "logs" / "solver_transient.log").read_text(encoding="utf-8", errors="replace")
        accepted = (
            "Mesh OK." in check_mesh
            and solver.rstrip().endswith("End")
            and summary["mesh"]["openfoam"]["meshOK"]
            and summary["solver"]["completed"]
            and summary["flow"]["imbalancePercent"] < 1.0
        )
        if not accepted:
            raise RuntimeError(f"Run acceptance failed: {name}")
        images = [image_info(directory / "screenshots" / filename) for filename in ("mesh.png", "velocity.png", "pressure.png", "streamlines.png", "obstacles_zoom.png")]
        run_checks.append({"run": name, "accepted": accepted, "cells": summary["mesh"]["salome"]["cells"], "Re_a": summary["dimensionless"]["Re_a"], "images": images})

    evidence_names = ("app_default.jpg", "app_changed.jpg", "app_running.jpg", "app_complete.jpg", "openfoam_mesh.png", "velocity.png", "pressure.png", "streamlines.png", "obstacles_zoom.png")
    evidence = [image_info(PROJECT / "screenshots" / name) for name in evidence_names]
    payload = {
        "status": "PASS_WITH_GUI_EVIDENCE_PENDING",
        "verifiedFullRuns": run_checks,
        "verifiedProjectArtifacts": checks,
        "verifiedScreenshots": evidence,
        "remainingGuiEvidence": ["screenshots/salome_geometry.png", "screenshots/salome_mesh.png", "screenshots/salome_groups.png"],
    }
    output = PROJECT / "validation" / "final_audit.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
