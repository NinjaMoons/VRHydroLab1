#!/usr/bin/env python3

"""Plot LR8 centreline data and compare characteristic sections with theory."""

import csv
import math
import os
import sys

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-lr8")
import matplotlib.pyplot as plt


input_csv = os.path.abspath(sys.argv[1])
output_dir = os.path.abspath(sys.argv[2])
os.makedirs(output_dir, exist_ok=True)

with open(input_csv, encoding="utf-8") as stream:
    rows = [{key: float(value) for key, value in row.items()}
            for row in csv.DictReader(stream)]

x = [row["x_m"] for row in rows]
velocity = [row["U_mag_m_s"] for row in rows]
temperature = [row["T_K"] for row in rows]
pressure = [row["p_Pa"] for row in rows]
mach = [row["Mach"] for row in rows]

plt.style.use("seaborn-v0_8-whitegrid")
fig, ax_velocity = plt.subplots(figsize=(12, 5.5), constrained_layout=True)
ax_temperature = ax_velocity.twinx()
line_velocity = ax_velocity.plot(x, velocity, color="#1261a0", linewidth=2,
                                 label="Скорость |U|")
line_temperature = ax_temperature.plot(x, temperature, color="#d1495b", linewidth=2,
                                       label="Температура T")
ax_velocity.axvline(0.0, color="#555555", linestyle="--", linewidth=1,
                    label="Критическое сечение")
ax_velocity.set_xlabel("Координата вдоль сопла x, м")
ax_velocity.set_ylabel("Скорость |U|, м/с", color="#1261a0")
ax_temperature.set_ylabel("Температура T, K", color="#d1495b")
lines = line_velocity + line_temperature + [ax_velocity.lines[-1]]
ax_velocity.legend(lines, [item.get_label() for item in lines], loc="best")
ax_velocity.set_title("LR8: распределение скорости и температуры по оси сопла")
fig.savefig(os.path.join(output_dir, "velocity_temperature_plot.png"), dpi=180)
plt.close(fig)

fig, ax_pressure = plt.subplots(figsize=(12, 5.5), constrained_layout=True)
ax_mach = ax_pressure.twinx()
line_pressure = ax_pressure.plot(x, [value / 1000 for value in pressure],
                                 color="#3a7d44", linewidth=2, label="Давление p")
line_mach = ax_mach.plot(x, mach, color="#7b2cbf", linewidth=2, label="Число Маха")
ax_pressure.axvline(0.0, color="#555555", linestyle="--", linewidth=1,
                    label="Критическое сечение")
ax_pressure.set_xlabel("Координата вдоль сопла x, м")
ax_pressure.set_ylabel("Давление p, кПа", color="#3a7d44")
ax_mach.set_ylabel("Число Маха M", color="#7b2cbf")
lines = line_pressure + line_mach + [ax_pressure.lines[-1]]
ax_pressure.legend(lines, [item.get_label() for item in lines], loc="best")
ax_pressure.set_title("LR8: распределение давления и числа Маха по оси сопла")
fig.savefig(os.path.join(output_dir, "pressure_mach_plot.png"), dpi=180)
plt.close(fig)

# Values computed by LR6/calc_nozzle.py for the same input data.
theory = {
    "Вход": (-1.188030, 32.149, 1799.4855, 199800.0, 0.03781),
    "Критическое сечение": (0.0, 776.338, 1500.0, 105656.358, 1.0),
    "Выход": (0.152328, 1457.832, 742.1233, 9000.0, 2.6697),
}

comparison_path = os.path.join(output_dir, "section_comparison.csv")
with open(comparison_path, "w", newline="", encoding="utf-8") as stream:
    writer = csv.writer(stream)
    writer.writerow(("section", "x_target_m", "x_sample_m",
                     "U_cfd_m_s", "U_theory_m_s", "T_cfd_K", "T_theory_K",
                     "p_cfd_Pa", "p_theory_Pa", "Mach_cfd", "Mach_theory"))
    for section, (target_x, u_ref, t_ref, p_ref, mach_ref) in theory.items():
        row = min(rows, key=lambda item: abs(item["x_m"] - target_x))
        writer.writerow((section, target_x, row["x_m"], row["U_mag_m_s"], u_ref,
                         row["T_K"], t_ref, row["p_Pa"], p_ref,
                         row["Mach"], mach_ref))

print("LR8_PLOTS_OK")
print("rows=", len(rows))
print("comparison=", comparison_path)
