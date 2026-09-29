#!/usr/bin/env pvpython

"""Render the real LR6 pressure evolution as reproducible LR8 animation frames."""

import os
import sys

from paraview.simple import (
    CellDatatoPointData, ColorBy, CreateView, GetColorTransferFunction,
    GetScalarBar, OpenFOAMReader, Render, ResetSession, SaveScreenshot, Show,
)

case_file = os.path.abspath(sys.argv[1])
frame_dir = os.path.abspath(sys.argv[2])
os.makedirs(frame_dir, exist_ok=True)

ResetSession()
reader = OpenFOAMReader(registrationName="LR6 nozzle animation", FileName=case_file)
reader.MeshRegions = ["internalMesh"]
reader.CellArrays = ["p"]
reader.UpdatePipeline()
times = list(reader.TimestepValues or [])
if not times:
    raise RuntimeError("No time layers in LR6 case")

points = CellDatatoPointData(registrationName="Cell data to point data", Input=reader)
view = CreateView("RenderView")
view.ViewSize = [1000, 333]
view.UseColorPaletteForBackground = 0
view.Background = [1.0, 1.0, 1.0]
view.Background2 = [1.0, 1.0, 1.0]
view.BackgroundColorMode = "Single Color"
view.OrientationAxesVisibility = 0
view.CameraParallelProjection = 1

display = Show(points, view, "UnstructuredGridRepresentation")
display.Representation = "Surface"
ColorBy(display, ("POINTS", "p"))
lut = GetColorTransferFunction("p")
lut.ApplyPreset("Cool to Warm", True)
lut.RescaleTransferFunction(19000.0, 201000.0)
display.SetScalarBarVisibility(view, True)
bar = GetScalarBar(lut, view)
bar.TitleColor = [0.0, 0.0, 0.0]
bar.LabelColor = [0.0, 0.0, 0.0]

reader.UpdatePipeline(times[0])
points.UpdatePipeline(times[0])
view.ViewTime = times[0]
view.ResetCamera()
Render(view)

for index, time_value in enumerate(times):
    reader.UpdatePipeline(time_value)
    points.UpdatePipeline(time_value)
    view.ViewTime = time_value
    view.ViewSize = [1000, 333]
    Render(view)
    SaveScreenshot(os.path.join(frame_dir, f"frame_{index:03d}.png"), view)

print("LR8_ANIMATION_FRAMES_OK")
print("frames=", len(times))
print("first_time=", min(times), "last_time=", max(times))

