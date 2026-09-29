#!/usr/bin/env pvpython

"""Render the imported SALOME mesh and LR3 phase evolution."""

import os
import sys

from paraview.simple import (
    CellDatatoPointData,
    ColorBy,
    CreateView,
    GetColorTransferFunction,
    OpenFOAMReader,
    Render,
    ResetSession,
    SaveScreenshot,
    Show,
)


case_file = os.path.abspath(sys.argv[1])
output_dir = os.path.abspath(sys.argv[2])
os.makedirs(output_dir, exist_ok=True)

ResetSession()
reader = OpenFOAMReader(registrationName="LR3 dam break", FileName=case_file)
reader.SkipZeroTime = 0
reader.MeshRegions = ["internalMesh"]
reader.CellArrays = ["alpha.water", "U", "p_rgh"]
reader.UpdatePipeline()
available = list(reader.TimestepValues or [])
if not available:
    raise RuntimeError("No LR3 time values found")

points = CellDatatoPointData(registrationName="Cell data to point data", Input=reader)
points.PassCellData = 1
view = CreateView("RenderView")
view.ViewSize = [1100, 900]
view.Background = [1.0, 1.0, 1.0]
view.OrientationAxesVisibility = 1
view.CameraPosition = [0.292, 0.292, 2.2]
view.CameraFocalPoint = [0.292, 0.292, 0.0073]
view.CameraViewUp = [0.0, 1.0, 0.0]
view.CameraParallelProjection = 1

display = Show(points, view, "UnstructuredGridRepresentation")
view.ViewTime = min(available)
reader.UpdatePipeline(view.ViewTime)
points.UpdatePipeline(view.ViewTime)
display.Representation = "Surface With Edges"
display.ColorArrayName = [None, ""]
display.DiffuseColor = [0.82, 0.87, 0.94]
view.ResetCamera()
Render(view)
SaveScreenshot(os.path.join(output_dir, "mesh.png"), view, ImageResolution=[1100, 900])

display.Representation = "Surface"
ColorBy(display, ("POINTS", "alpha.water"))
lut = GetColorTransferFunction("alpha.water")
lut.ApplyPreset("Cool to Warm", True)
lut.RescaleTransferFunction(0.0, 1.0)
display.SetScalarBarVisibility(view, True)

targets = (0.25, 0.5, 0.65, 0.85)
for target in targets:
    actual = min(available, key=lambda value: abs(value - target))
    if abs(actual - target) > 1.0e-6:
        raise RuntimeError("Required time %g not present; nearest is %g" % (target, actual))
    view.ViewTime = actual
    reader.UpdatePipeline(actual)
    points.UpdatePipeline(actual)
    Render(view)
    suffix = ("%.2f" % target).rstrip("0").rstrip(".").replace(".", "_")
    SaveScreenshot(
        os.path.join(output_dir, "alpha_water_t%s.png" % suffix),
        view,
        ImageResolution=[1100, 900],
    )

print("LR3_RENDER_OK")
print("available_times=", available)
print("output_dir=", output_dir)
