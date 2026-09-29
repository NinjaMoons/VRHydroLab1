#!/usr/bin/env python3

"""Compare the three verified validation runs without inventing metrics."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt


PROJECT = Path(__file__).resolve().parents[1]
RUN_NAMES = ("baseline_v3_u0p1", "speed_v3_u0p15", "geometry_v3_changed")


def main() -> None:
    records = []
    for name in RUN_NAMES:
        summary_path = PROJECT / "runs" / name / "results" / "summary.json"
        data = json.loads(summary_path.read_text(encoding="utf-8"))
        records.append({
            "run": name,
            "Uin_m_s": data["settings"]["flow"]["Uin"],
            "L_mm": data["settings"]["geometryMm"]["L"],
            "H_mm": data["settings"]["geometryMm"]["H"],
            "a_mm": data["settings"]["geometryMm"]["a"],
            "P_mm": data["settings"]["geometryMm"]["P"],
            "S_mm": data["settings"]["geometryMm"]["S"],
            "Y_mm": data["settings"]["geometryMm"]["Y"],
            "R_mm": data["settings"]["geometryMm"]["R"],
            "cells": data["mesh"]["salome"]["cells"],
            "points": data["paraview"]["points"],
            "Re_a": data["dimensionless"]["Re_a"],
            "Re_H": data["dimensionless"]["Re_H"],
            "Qin_m3_s": data["flow"]["inletMagnitudeM3s"],
            "Qout_m3_s": data["flow"]["outletMagnitudeM3s"],
            "imbalance_percent": data["flow"]["imbalancePercent"],
            "Umax_m_s": data["velocity"]["cellMaximumMagnitudeMps"],
            "pressure_drop_Pa": data["pressure"]["dropPa"],
            "max_Co": data["solver"]["courantMax"],
            "mesh_OK": data["mesh"]["openfoam"]["meshOK"],
            "solver_completed": data["solver"]["completed"],
        })

    csv_path = PROJECT / "validation" / "run_comparison.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

    baseline, speed, geometry = records
    output = {
        "runs": records,
        "derivedComparisons": {
            "speedFactor_B_over_A": speed["Uin_m_s"] / baseline["Uin_m_s"],
            "flowFactor_B_over_A": speed["Qout_m3_s"] / baseline["Qout_m3_s"],
            "maxVelocityFactor_B_over_A": speed["Umax_m_s"] / baseline["Umax_m_s"],
            "pressureDropFactor_B_over_A": speed["pressure_drop_Pa"] / baseline["pressure_drop_Pa"],
            "geometryCellFactor_C_over_A": geometry["cells"] / baseline["cells"],
            "geometryPressureDropFactor_C_over_A": geometry["pressure_drop_Pa"] / baseline["pressure_drop_Pa"],
        },
        "acceptance": {
            "allMeshOK": all(record["mesh_OK"] for record in records),
            "allSolverCompleted": all(record["solver_completed"] for record in records),
            "allImbalanceBelowOnePercent": all(record["imbalance_percent"] < 1.0 for record in records),
        },
    }
    json_path = PROJECT / "validation" / "run_comparison.json"
    json_path.write_text(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    labels = ["A: baseline", "B: Uin=0.15", "C: geometry"]
    figure, axes = plt.subplots(1, 3, figsize=(12, 3.8), constrained_layout=True)
    series = (
        ("Reynolds Reₐ", [record["Re_a"] for record in records], ""),
        ("Maximum velocity", [record["Umax_m_s"] for record in records], "m/s"),
        ("Pressure drop", [record["pressure_drop_Pa"] for record in records], "Pa"),
    )
    colors = ("#168b82", "#d59b32", "#667c8c")
    for axis, (title, values, unit) in zip(axes, series):
        bars = axis.bar(labels, values, color=colors)
        axis.set_title(title, fontweight="bold")
        axis.set_ylabel(unit)
        axis.spines[["top", "right"]].set_visible(False)
        axis.tick_params(axis="x", rotation=18, labelsize=8)
        for bar, value in zip(bars, values):
            axis.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{value:.3g}", ha="center", va="bottom", fontsize=8)
    figure.suptitle("Course Project V3 — verified run comparison", fontweight="bold")
    figure.savefig(PROJECT / "validation" / "run_comparison.png", dpi=180, facecolor="white")
    plt.close(figure)
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
