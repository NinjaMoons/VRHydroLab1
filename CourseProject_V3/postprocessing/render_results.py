#!/usr/bin/env pvpython

"""Render verified CourseProject_V3 fields with ParaView."""

import argparse
import json
import os

from paraview import servermanager
from paraview.simple import (
    Calculator,
    CellDatatoPointData,
    ColorBy,
    CreateView,
    GetColorTransferFunction,
    GetScalarBar,
    Hide,
    MergeBlocks,
    OpenFOAMReader,
    Render,
    ResetSession,
    SaveScreenshot,
    Show,
    StreamTracer,
)


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("case")
    parser.add_argument("output")
    parser.add_argument("--rho", type=float, default=998.2)
    return parser.parse_args()


def set_camera(view, focal_x, scale):
    view.CameraPosition = [focal_x, 0.0115, 1.0]
    view.CameraFocalPoint = [focal_x, 0.0115, 0.0005]
    view.CameraViewUp = [0.0, 1.0, 0.0]
    view.CameraParallelProjection = 1
    view.CameraParallelScale = scale


def scalar_bar(lut, view, title):
    bar = GetScalarBar(lut, view)
    bar.Title = title
    bar.ComponentTitle = ""
    bar.TitleColor = [0.0, 0.0, 0.0]
    bar.LabelColor = [0.0, 0.0, 0.0]
    bar.Orientation = "Vertical"
    bar.WindowLocation = "Any Location"
    bar.Position = [0.915, 0.18]
    bar.ScalarBarLength = 0.64
    bar.ScalarBarThickness = 18
    bar.TitleFontSize = 16
    bar.LabelFontSize = 14
    return bar


def main():
    args = arguments()
    case_file = os.path.abspath(args.case)
    output_dir = os.path.abspath(args.output)
    os.makedirs(output_dir, exist_ok=True)

    ResetSession()
    reader = OpenFOAMReader(registrationName="CourseProject_V3", FileName=case_file)
    reader.MeshRegions = ["internalMesh"]
    reader.CellArrays = ["U", "p", "k", "omega", "nut"]
    reader.UpdatePipeline()
    times = list(reader.TimestepValues or [])
    if not times:
        raise RuntimeError("OpenFOAMReader found no result times")
    final_time = max(times)
    reader.UpdatePipeline(final_time)

    points = CellDatatoPointData(registrationName="Cell data to point data", Input=reader)
    points.PassCellData = 1
    points.UpdatePipeline(final_time)
    pressure_pa = Calculator(registrationName="Pressure in Pa", Input=points)
    pressure_pa.ResultArrayName = "p_Pa"
    pressure_pa.Function = "p*%0.12g" % args.rho
    pressure_pa.UpdatePipeline(final_time)

    view = CreateView("RenderView")
    # The channel is long and thin.  A compact canvas and an explicit camera
    # keep it readable in the web interface without changing the result data.
    view.ViewSize = [1600, 320]
    view.UseColorPaletteForBackground = 0
    view.BackgroundColorMode = "Single Color"
    view.Background = [1.0, 1.0, 1.0]
    view.OrientationAxesVisibility = 0
    view.ViewTime = final_time

    display = Show(pressure_pa, view, "UnstructuredGridRepresentation")
    # The first render performs ParaView's automatic reset.  Apply the report
    # camera only after that reset has completed.
    Render(view)
    set_camera(view, 0.175, 0.040)
    display.Representation = "Surface With Edges"
    display.ColorArrayName = [None, ""]
    display.DiffuseColor = [0.82, 0.88, 0.95]
    display.EdgeColor = [0.18, 0.18, 0.18]
    Render(view)
    SaveScreenshot(os.path.join(output_dir, "mesh.png"), view)

    display.Representation = "Surface"
    ColorBy(display, ("POINTS", "U", "Magnitude"))
    velocity_lut = GetColorTransferFunction("U")
    velocity_lut.ApplyPreset("Cool to Warm", True)
    display.RescaleTransferFunctionToDataRange(True, False)
    display.SetScalarBarVisibility(view, True)
    scalar_bar(velocity_lut, view, "|U|, m/s")
    Render(view)
    SaveScreenshot(os.path.join(output_dir, "velocity.png"), view)
    display.SetScalarBarVisibility(view, False)

    ColorBy(display, ("POINTS", "p_Pa"))
    pressure_lut = GetColorTransferFunction("p_Pa")
    pressure_lut.ApplyPreset("Cool to Warm", True)
    display.RescaleTransferFunctionToDataRange(True, False)
    display.SetScalarBarVisibility(view, True)
    scalar_bar(pressure_lut, view, "p, Pa")
    Render(view)
    SaveScreenshot(os.path.join(output_dir, "pressure.png"), view)
    display.SetScalarBarVisibility(view, False)

    ColorBy(display, ("POINTS", "U", "Magnitude"))
    display.SetScalarBarVisibility(view, True)
    zoom_bar = scalar_bar(velocity_lut, view, "|U|, m/s")
    zoom_bar.Orientation = "Horizontal"
    zoom_bar.Position = [0.72, 0.79]
    zoom_bar.ScalarBarLength = 0.24
    zoom_bar.ScalarBarThickness = 14
    set_camera(view, 0.176, 0.0224)
    Render(view)
    SaveScreenshot(os.path.join(output_dir, "obstacles_zoom.png"), view)
    display.SetScalarBarVisibility(view, False)

    set_camera(view, 0.175, 0.040)
    ColorBy(display, ("POINTS", "p_Pa"))
    display.Opacity = 0.28
    stream = StreamTracer(registrationName="Inlet streamlines", Input=points, SeedType="Line")
    stream.SeedType.Point1 = [0.0005, 0.0007, 0.0005]
    stream.SeedType.Point2 = [0.0005, 0.0223, 0.0005]
    stream.SeedType.Resolution = 42
    stream.IntegrationDirection = "FORWARD"
    stream.MaximumStreamlineLength = 0.45
    stream.ComputeVorticity = 0
    stream.UpdatePipeline(final_time)
    stream_display = Show(stream, view, "GeometryRepresentation")
    # The new representation can also trigger camera adjustment.
    Render(view)
    set_camera(view, 0.175, 0.040)
    stream_display.LineWidth = 2.0
    ColorBy(stream_display, ("POINTS", "U", "Magnitude"))
    stream_lut = GetColorTransferFunction("U")
    stream_lut.ApplyPreset("Cool to Warm", True)
    stream_display.RescaleTransferFunctionToDataRange(True, False)
    stream_display.SetScalarBarVisibility(view, True)
    scalar_bar(stream_lut, view, "|U|, m/s")
    Render(view)
    SaveScreenshot(os.path.join(output_dir, "streamlines.png"), view)
    stream_display.SetScalarBarVisibility(view, False)

    merged = MergeBlocks(registrationName="Merged data for statistics", Input=points)
    merged.UpdatePipeline(final_time)
    data = servermanager.Fetch(merged)
    point_data = data.GetPointData()
    u_array = point_data.GetArray("U")
    p_array = point_data.GetArray("p")
    if u_array is None or p_array is None:
        raise RuntimeError("Required point arrays U/p are missing")
    summary = {
        "time": final_time,
        "timeCount": len(times),
        "points": data.GetNumberOfPoints(),
        "cells": data.GetNumberOfCells(),
        "pointVelocityMagnitudeRangeMps": list(u_array.GetRange(-1)),
        "pointKinematicPressureRangeM2s2": list(p_array.GetRange()),
        "pointPressureRangePa": [value * args.rho for value in p_array.GetRange()],
        "screenshots": [
            "mesh.png",
            "velocity.png",
            "pressure.png",
            "obstacles_zoom.png",
            "streamlines.png",
        ],
    }
    with open(os.path.join(output_dir, "paraview_summary.json"), "w", encoding="utf-8") as stream_file:
        json.dump(summary, stream_file, ensure_ascii=False, indent=2, sort_keys=True)
        stream_file.write("\n")
    print("COURSEPROJECT_V3_PARAVIEW_OK")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
