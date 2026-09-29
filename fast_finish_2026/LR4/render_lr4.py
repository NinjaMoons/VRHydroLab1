#!/usr/bin/env pvpython

"""Render verified LR4 OpenFOAM results with a reproducible ParaView pipeline."""

import os
import sys

from paraview.simple import (
    CellDatatoPointData,
    ColorBy,
    CreateView,
    GetColorTransferFunction,
    Hide,
    OpenFOAMReader,
    Render,
    ResetSession,
    SaveScreenshot,
    Show,
    StreamTracer,
    Tube,
)


case_file = os.path.abspath(sys.argv[1])
output_prefix = os.path.abspath(sys.argv[2])
label = sys.argv[3] if len(sys.argv) > 3 else os.path.basename(output_prefix)
os.makedirs(os.path.dirname(output_prefix), exist_ok=True)

ResetSession()
reader = OpenFOAMReader(registrationName=os.path.basename(case_file), FileName=case_file)
reader.MeshRegions = ["internalMesh"]
reader.CellArrays = ["U", "p"]
reader.UpdatePipeline()
times = list(reader.TimestepValues or [])
if not times:
    raise RuntimeError("OpenFOAM reader returned no time values")
final_time = max(times)
reader.UpdatePipeline(final_time)

point_data = CellDatatoPointData(registrationName="Cell data to point data", Input=reader)
point_data.PassCellData = 1
point_data.UpdatePipeline(final_time)

view = CreateView("RenderView")
view.ViewSize = [1500, 600]
view.Background = [1.0, 1.0, 1.0]
view.OrientationAxesVisibility = 1
view.ViewTime = final_time

display = Show(point_data, view, "UnstructuredGridRepresentation")
display.Representation = "Surface With Edges"
display.ColorArrayName = [None, ""]
display.DiffuseColor = [0.82, 0.87, 0.94]
view.CameraPosition = [0.2, 0.0, 1.2]
view.CameraFocalPoint = [0.2, 0.0, 0.0]
view.CameraViewUp = [0.0, 1.0, 0.0]
view.CameraParallelProjection = 1
view.ResetCamera()
Render(view)
SaveScreenshot(
    output_prefix + "_mesh.png", view, ImageResolution=[1500, 600],
    TransparentBackground=0,
)

display.Representation = "Surface"
ColorBy(display, ("POINTS", "U", "X"))
lut = GetColorTransferFunction("U")
lut.ApplyPreset("Cool to Warm", True)
display.RescaleTransferFunctionToDataRange(True, False)
display.SetScalarBarVisibility(view, True)
Render(view)
SaveScreenshot(
    output_prefix + "_velocity.png", view, ImageResolution=[1500, 600],
    TransparentBackground=0,
)

tracer = StreamTracer(registrationName="Streamlines", Input=point_data, SeedType="Line")
tracer.Vectors = ["POINTS", "U"]
tracer.SeedType.Point1 = [-0.08, -0.049, 0.0]
tracer.SeedType.Point2 = [-0.08, 0.049, 0.0]
tracer.SeedType.Resolution = 80
tracer.IntegrationDirection = "BOTH"
tracer.MaximumStreamlineLength = 0.8
tracer.UpdatePipeline(final_time)
tube = Tube(registrationName="Streamline tubes", Input=tracer)
tube.Radius = 0.00045
tube.NumberofSides = 8
tube.UpdatePipeline(final_time)
tube_display = Show(tube, view, "GeometryRepresentation")
ColorBy(tube_display, ("POINTS", "U", "Magnitude"))
tube_display.RescaleTransferFunctionToDataRange(True, False)
display.Opacity = 0.27
Render(view)
SaveScreenshot(
    output_prefix + "_streamlines.png", view, ImageResolution=[1500, 600],
    TransparentBackground=0,
)

print("LR4_RENDER_OK")
print("label=", label)
print("time=", final_time)
print("times=", times)
print("velocity=", output_prefix + "_velocity.png")
print("streamlines=", output_prefix + "_streamlines.png")
print("mesh=", output_prefix + "_mesh.png")
