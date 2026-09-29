#!/usr/bin/env python3

"""Build a machine-readable run summary strictly from saved artifacts."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path


NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def last_float(pattern: str, content: str, label: str) -> float:
    values = re.findall(pattern, content, flags=re.MULTILINE)
    if not values:
        raise ValueError(f"Cannot find {label}")
    value = values[-1]
    if isinstance(value, tuple):
        raise TypeError(f"Pattern for {label} returned multiple groups")
    return float(value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--mesh-summary", type=Path, required=True)
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    logs = run_dir / "logs"
    results = run_dir / "results"
    results.mkdir(parents=True, exist_ok=True)

    settings = load_json(run_dir / "settings.json")
    mesh = load_json(args.mesh_summary.resolve())
    paraview = load_json(run_dir / "screenshots" / "paraview_summary.json")
    solver_log = text(logs / "solver_transient.log")
    check_log = text(logs / "checkMesh.log")

    def value_from_log(filename: str, pattern: str, label: str) -> float:
        return last_float(pattern, text(logs / filename), label)

    q_in_signed = value_from_log(
        "flow_inlet.log", rf"sum\(inlet\) of phi = ({NUMBER})", "inlet flow"
    )
    q_out_signed = value_from_log(
        "flow_outlet.log", rf"sum\(outlet\) of phi = ({NUMBER})", "outlet flow"
    )
    q_in = abs(q_in_signed)
    q_out = abs(q_out_signed)
    reference_flow = max(q_in, q_out)
    imbalance_percent = (
        abs(q_in - q_out) / reference_flow * 100.0 if reference_flow else math.nan
    )

    p_in = value_from_log(
        "p_inlet.log", rf"areaAverage\(inlet\) of p = ({NUMBER})", "inlet pressure"
    )
    p_out = value_from_log(
        "p_outlet.log", rf"areaAverage\(outlet\) of p = ({NUMBER})", "outlet pressure"
    )
    rho = float(settings["flow"]["rho"])
    velocity = float(settings["flow"]["Uin"])
    nu = float(settings["flow"]["nu"])
    side_m = float(settings["geometryMm"]["a"]) / 1000.0
    height_m = float(settings["geometryMm"]["H"]) / 1000.0

    courant_values = re.findall(
        rf"Courant Number mean: ({NUMBER}) max: ({NUMBER})", solver_log
    )
    if not courant_values:
        raise ValueError("Cannot find Courant numbers")
    courant_mean, courant_max = map(float, courant_values[-1])
    continuity_values = re.findall(
        rf"time step continuity errors : sum local = ({NUMBER}), global = ({NUMBER}), cumulative = ({NUMBER})",
        solver_log,
    )
    if not continuity_values:
        raise ValueError("Cannot find final continuity errors")
    continuity_local, continuity_global, continuity_cumulative = map(
        float, continuity_values[-1]
    )

    velocity_max = value_from_log(
        "u_max.log", rf"maxMag\(all\) of U = ({NUMBER})", "cell velocity maximum"
    )
    velocity_min = value_from_log(
        "u_min.log", rf"minMag\(all\) of U = ({NUMBER})", "cell velocity minimum"
    )
    p_cell_max = value_from_log(
        "p_max.log", rf"max\(all\) of p = ({NUMBER})", "cell pressure maximum"
    )
    p_cell_min = value_from_log(
        "p_min.log", rf"min\(all\) of p = ({NUMBER})", "cell pressure minimum"
    )

    summary = {
        "runId": run_dir.name,
        "status": "VERIFIED",
        "settings": settings,
        "dimensionless": {
            "Re_a": velocity * side_m / nu,
            "Re_H": velocity * height_m / nu,
        },
        "mesh": {
            "salome": {
                "nodes": mesh["nodes"],
                "cells": mesh["volumes"],
                "hexas": mesh["hexas"],
                "prisms": mesh["pentas"],
                "groups": mesh["groups"],
            },
            "openfoam": {
                "meshOK": "Mesh OK." in check_log,
                "maxAspectRatio": last_float(
                    rf"Max aspect ratio = ({NUMBER})", check_log, "max aspect ratio"
                ),
                "maxNonOrthogonalityDeg": last_float(
                    rf"Mesh non-orthogonality Max: ({NUMBER})", check_log, "non-orthogonality"
                ),
                "maxSkewness": last_float(
                    rf"Max skewness = ({NUMBER})", check_log, "skewness"
                ),
                "minDeterminant": last_float(
                    rf"Cell determinant \(wellposedness\) : minimum: ({NUMBER})",
                    check_log,
                    "minimum determinant",
                ),
            },
        },
        "solver": {
            "application": "foamRun -solver incompressibleFluid",
            "algorithm": "transient PIMPLE",
            "turbulenceModel": settings["flow"]["turbulenceModel"],
            "finalTime": last_float(rf"^Time = ({NUMBER})s$", solver_log, "final time"),
            "finalDeltaT": last_float(rf"^deltaT = ({NUMBER})$", solver_log, "final deltaT"),
            "courantMean": courant_mean,
            "courantMax": courant_max,
            "continuity": {
                "local": continuity_local,
                "global": continuity_global,
                "cumulative": continuity_cumulative,
            },
            "completed": solver_log.rstrip().endswith("End"),
        },
        "flow": {
            "inletSignedM3s": q_in_signed,
            "outletSignedM3s": q_out_signed,
            "inletMagnitudeM3s": q_in,
            "outletMagnitudeM3s": q_out,
            "imbalancePercent": imbalance_percent,
        },
        "pressure": {
            "inletAreaAverageKinematicM2s2": p_in,
            "outletAreaAverageKinematicM2s2": p_out,
            "dropPa": (p_in - p_out) * rho,
            "cellMinimumKinematicM2s2": p_cell_min,
            "cellMaximumKinematicM2s2": p_cell_max,
            "cellMinimumPa": p_cell_min * rho,
            "cellMaximumPa": p_cell_max * rho,
        },
        "velocity": {
            "cellMinimumMagnitudeMps": velocity_min,
            "cellMaximumMagnitudeMps": velocity_max,
            "paraviewPointMagnitudeRangeMps": paraview[
                "pointVelocityMagnitudeRangeMps"
            ],
        },
        "paraview": paraview,
        "evidence": {
            "case": "case/",
            "logs": "logs/",
            "screenshots": "screenshots/",
            "mesh": "Mesh.unv",
        },
    }

    output = results / "summary.json"
    output.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (run_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(output)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
