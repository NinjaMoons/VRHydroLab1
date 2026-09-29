#!/usr/bin/env pvpython

"""Reproducible ParaView post-processing for LR6/LR8 nozzle results."""

import csv
import math
import os
import sys

from paraview import servermanager
from paraview.simple import (
    Calculator, CellDatatoPointData, ColorBy, CreateView,
    GetColorTransferFunction, GetScalarBar, OpenFOAMReader, PlotOverLine, Render,
    ResetSession, SaveScreenshot, Show,
)

case_file = os.path.abspath(sys.argv[1])
output_dir = os.path.abspath(sys.argv[2])
os.makedirs(output_dir, exist_ok=True)

ResetSession()
reader = OpenFOAMReader(registrationName="LR6 nozzle", FileName=case_file)
reader.MeshRegions = ["internalMesh"]
reader.CellArrays = ["U", "T", "p"]
reader.UpdatePipeline()
times = list(reader.TimestepValues or [])
if not times:
    raise RuntimeError("No nozzle result times")
final_time = max(times)
reader.UpdatePipeline(final_time)
points = CellDatatoPointData(registrationName="Cell data to point data", Input=reader)
points.PassCellData = 1
points.UpdatePipeline(final_time)
mach = Calculator(registrationName="Mach number", Input=points)
mach.ResultArrayName = "Mach"
mach.Function = "mag(U)/sqrt(1.4*287*T)"
mach.UpdatePipeline(final_time)

view = CreateView("RenderView")
view.ViewSize = [1500, 500]
view.UseColorPaletteForBackground = 0
view.Background = [1.0, 1.0, 1.0]
view.Background2 = [1.0, 1.0, 1.0]
view.BackgroundColorMode = "Single Color"
view.OrientationAxesVisibility = 1
view.ViewTime = final_time
view.CameraPosition = [-0.518, 0.098, 2.5]
view.CameraFocalPoint = [-0.518, 0.098, 0.0]
view.CameraViewUp = [0.0, 1.0, 0.0]
view.CameraParallelProjection = 1
display = Show(mach, view, "UnstructuredGridRepresentation")
display.Representation = "Surface With Edges"
display.ColorArrayName = [None, ""]
display.DiffuseColor = [0.82, 0.87, 0.94]
view.ResetCamera()
# ResetCamera leaves excessive horizontal margins for this very slender 2-D
# domain.  This fixed scale keeps the complete nozzle in frame and makes the
# mesh/field screenshots useful in the report.
view.CameraParallelScale = 0.235
Render(view)
view.ViewSize = [1500, 500]
SaveScreenshot(os.path.join(output_dir, "mesh.png"), view)

for filename, array_spec, lut_name in (
    ("pressure.png", ("POINTS", "p"), "p"),
    ("temperature.png", ("POINTS", "T"), "T"),
    ("velocity.png", ("POINTS", "U", "Magnitude"), "U"),
    ("mach.png", ("POINTS", "Mach"), "Mach"),
):
    display.Representation = "Surface"
    ColorBy(display, array_spec)
    lut = GetColorTransferFunction(lut_name)
    lut.ApplyPreset("Cool to Warm", True)
    display.RescaleTransferFunctionToDataRange(True, False)
    display.SetScalarBarVisibility(view, True)
    scalar_bar = GetScalarBar(lut, view)
    scalar_bar.TitleColor = [0.0, 0.0, 0.0]
    scalar_bar.LabelColor = [0.0, 0.0, 0.0]
    Render(view)
    view.ViewSize = [1500, 500]
    SaveScreenshot(os.path.join(output_dir, filename), view)
    display.SetScalarBarVisibility(view, False)

line = PlotOverLine(registrationName="Nozzle centreline", Input=mach)
line.Point1 = [-1.1880, 0.001, 0.0]
line.Point2 = [0.1523, 0.001, 0.0]
line.Resolution = 600
line.UpdatePipeline(final_time)
data = servermanager.Fetch(line)
point_data = data.GetPointData()
arrays = {name: point_data.GetArray(name) for name in ("U", "T", "p", "Mach")}
missing = [name for name, array in arrays.items() if array is None]
if missing:
    raise RuntimeError("Missing centreline arrays: " + ", ".join(missing))

csv_path = os.path.join(output_dir, "centerline.csv")
with open(csv_path, "w", newline="", encoding="utf-8") as stream:
    writer = csv.writer(stream)
    writer.writerow(("x_m", "y_m", "z_m", "Ux_m_s", "Uy_m_s", "U_mag_m_s", "T_K", "p_Pa", "Mach"))
    for index in range(data.GetNumberOfPoints()):
        x, y, z = data.GetPoint(index)
        u = arrays["U"].GetTuple(index)
        umag = math.sqrt(sum(component * component for component in u))
        writer.writerow((x, y, z, u[0], u[1], umag,
                         arrays["T"].GetTuple1(index), arrays["p"].GetTuple1(index),
                         arrays["Mach"].GetTuple1(index)))

print("LR8_POSTPROCESS_OK")
print("time=", final_time)
print("times=", times)
print("centerline=", csv_path)
print("points=", data.GetNumberOfPoints())
