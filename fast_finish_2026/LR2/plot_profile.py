#!/usr/bin/env python3

"""Plot the LR2 centreline Ux profiles exported by ParaView."""

import csv
import os
import sys

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-lr2")
import matplotlib.pyplot as plt

input_csv = os.path.abspath(sys.argv[1])
output_png = os.path.abspath(sys.argv[2])
series = {}
with open(input_csv, encoding="utf-8") as stream:
    for row in csv.DictReader(stream):
        series.setdefault(row["mesh"], {"y": [], "ux": [], "time": row["time_s"]})
        series[row["mesh"]]["y"].append(float(row["y_m"]))
        series[row["mesh"]]["ux"].append(float(row["Ux_m_s"]))

plt.style.use("seaborn-v0_8-whitegrid")
fig, ax = plt.subplots(figsize=(7.5, 7.5), constrained_layout=True)
for mesh, data in sorted(series.items()):
    ax.plot(data["ux"], data["y"], linewidth=2, label=f"{mesh}, t={float(data['time']):g} s")
ax.axvline(0, color="#555555", linewidth=0.8)
ax.set_xlabel("Продольная скорость Ux, м/с")
ax.set_ylabel("Координата y, м")
ax.set_title("LR2: профиль Ux на центральной линии x=0,05 м")
ax.legend()
fig.savefig(output_png, dpi=180)
print("LR2_PROFILE_PLOT_OK")
print(output_png)
