#!/usr/bin/env pvpython

"""Render the verified LR5 natural-convection case reproducibly."""

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
    StreamTracer,
    Tube,
)


case_file = os.path.abspath(sys.argv[1])
output_dir = os.path.abspath(sys.argv[2])
os.makedirs(output_dir, exist_ok=True)

ResetSession()
reader = OpenFOAMReader(registrationName="LR5 buoyant cavity", FileName=case_file)
reader.MeshRegions = ["internalMesh"]
reader.CellArrays = ["T", "U", "p", "p_rgh"]
reader.UpdatePipeline()
times = list(reader.TimestepValues or [])
if not times:
    raise RuntimeError("OpenFOAM reader returned no result times")
final_time = max(times)
reader.UpdatePipeline(final_time)

points = CellDatatoPointData(registrationName="Cell data to point data", Input=reader)
points.PassCellData = 1
points.UpdatePipeline(final_time)

view = CreateView("RenderView")
view.ViewSize = [900, 900]
view.Background = [1.0, 1.0, 1.0]
view.OrientationAxesVisibility = 1
view.ViewTime = final_time
view.CameraPosition = [0.05, 0.05, 0.4]
view.CameraFocalPoint = [0.05, 0.05, 0.0]
view.CameraViewUp = [0.0, 1.0, 0.0]
view.CameraParallelProjection = 1

display = Show(points, view, "UnstructuredGridRepresentation")
display.Representation = "Surface With Edges"
ColorBy(display, None)
display.DiffuseColor = [0.82, 0.87, 0.94]
view.ResetCamera()
Render(view)
SaveScreenshot(os.path.join(output_dir, "mesh.png"), view, ImageResolution=[900, 900])

display.Representation = "Surface"
ColorBy(display, ("POINTS", "T"))
t_lut = GetColorTransferFunction("T")
t_lut.ApplyPreset("Cool to Warm", True)
display.RescaleTransferFunctionToDataRange(True, False)
display.SetScalarBarVisibility(view, True)
Render(view)
SaveScreenshot(os.path.join(output_dir, "temperature.png"), view, ImageResolution=[900, 900])

tracer = StreamTracer(registrationName="Velocity streamlines", Input=points, SeedType="Line")
tracer.Vectors = ["POINTS", "U"]
tracer.SeedType.Point1 = [0.002, 0.002, 0.0]
tracer.SeedType.Point2 = [0.002, 0.098, 0.0]
tracer.SeedType.Resolution = 70
tracer.IntegrationDirection = "BOTH"
tracer.MaximumStreamlineLength = 0.6
tracer.UpdatePipeline(final_time)
tube = Tube(registrationName="Streamline tubes", Input=tracer)
tube.Radius = 0.00023
tube.NumberofSides = 8
tube.UpdatePipeline(final_time)
tube_display = Show(tube, view, "GeometryRepresentation")
ColorBy(tube_display, ("POINTS", "U", "Magnitude"))
tube_display.RescaleTransferFunctionToDataRange(True, False)
display.Opacity = 0.38
Render(view)
SaveScreenshot(os.path.join(output_dir, "velocity_streamlines.png"), view, ImageResolution=[900, 900])

print("LR5_RENDER_OK")
print("time=", final_time)
print("times=", times)
print("output_dir=", output_dir)
