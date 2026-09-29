#!/usr/bin/env pvpython

"""Render the exact LR3 t=0 phase field from an isolated zero-time case."""

import os
import sys
from paraview.simple import (
    CellDatatoPointData, ColorBy, CreateView, GetColorTransferFunction,
    OpenFOAMReader, Render, ResetSession, SaveScreenshot, Show,
)

case_file = os.path.abspath(sys.argv[1])
output_file = os.path.abspath(sys.argv[2])
ResetSession()
reader = OpenFOAMReader(registrationName="LR3 initial", FileName=case_file)
reader.SkipZeroTime = 0
reader.MeshRegions = ["internalMesh"]
reader.CellArrays = ["alpha.water"]
reader.UpdatePipeline(0.0001)
points = CellDatatoPointData(Input=reader)
points.PassCellData = 1
points.UpdatePipeline(0.0001)
view = CreateView("RenderView")
view.ViewSize = [1100, 900]
view.Background = [1.0, 1.0, 1.0]
view.OrientationAxesVisibility = 1
view.ViewTime = 0.0001
view.CameraPosition = [0.292, 0.292, 2.2]
view.CameraFocalPoint = [0.292, 0.292, 0.0073]
view.CameraViewUp = [0.0, 1.0, 0.0]
view.CameraParallelProjection = 1
display = Show(points, view, "UnstructuredGridRepresentation")
display.Representation = "Surface"
ColorBy(display, ("POINTS", "alpha.water"))
lut = GetColorTransferFunction("alpha.water")
lut.ApplyPreset("Cool to Warm", True)
lut.RescaleTransferFunction(0.0, 1.0)
display.SetScalarBarVisibility(view, True)
view.ResetCamera()
Render(view)
SaveScreenshot(output_file, view, ImageResolution=[1100, 900])
print("LR3_INITIAL_RENDER_OK", output_file)
