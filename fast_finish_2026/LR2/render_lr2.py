#!/usr/bin/env pvpython

"""Create reproducible ParaView figures and centreline data for LR2."""

import csv
import math
import os
import sys

from paraview import servermanager
from paraview.simple import (
    Calculator, CellDatatoPointData, ColorBy, Contour, CreateView,
    GetColorTransferFunction, GetScalarBar, Glyph, Hide, OpenFOAMReader, PlotOverLine,
    Render, ResetSession, SaveScreenshot, Show, Slice, StreamTracer, Tube,
)


root = os.path.abspath(sys.argv[1])
output = os.path.abspath(sys.argv[2])
os.makedirs(output, exist_ok=True)


def load_case(relative, requested_time=None):
    case_file = os.path.join(root, relative)
    reader = OpenFOAMReader(registrationName=os.path.basename(case_file), FileName=case_file)
    reader.MeshRegions = ["internalMesh"]
    reader.CellArrays = ["U", "p"]
    reader.UpdatePipeline()
    times = list(reader.TimestepValues or [])
    if not times:
        raise RuntimeError("No times in " + case_file)
    time_value = max(times) if requested_time is None else min(times, key=lambda t: abs(t-requested_time))
    reader.UpdatePipeline(time_value)
    points = CellDatatoPointData(registrationName="Cell data to point data", Input=reader)
    points.PassCellData = 1
    points.UpdatePipeline(time_value)
    return reader, points, time_value, times


def new_view(time_value):
    view = CreateView("RenderView")
    view.ViewSize = [900, 900]
    view.UseColorPaletteForBackground = 0
    view.Background = [1.0, 1.0, 1.0]
    view.Background2 = [1.0, 1.0, 1.0]
    view.BackgroundColorMode = "Single Color"
    view.OrientationAxesVisibility = 1
    view.ViewTime = time_value
    view.CameraPosition = [0.05, 0.05, 0.5]
    view.CameraFocalPoint = [0.05, 0.05, 0.0]
    view.CameraViewUp = [0.0, 1.0, 0.0]
    view.CameraParallelProjection = 1
    return view


def style_scalar_bar(lut, view):
    bar = GetScalarBar(lut, view)
    bar.TitleColor = [0.0, 0.0, 0.0]
    bar.LabelColor = [0.0, 0.0, 0.0]


def save_mesh(relative, filename, requested_time=None):
    ResetSession()
    _, points, time_value, _ = load_case(relative, requested_time)
    view = new_view(time_value)
    display = Show(points, view, "UnstructuredGridRepresentation")
    display.Representation = "Surface With Edges"
    ColorBy(display, None)
    display.DiffuseColor = [0.82, 0.87, 0.94]
    view.ResetCamera()
    Render(view)
    SaveScreenshot(os.path.join(output, filename), view, ImageResolution=[900, 900])
    return time_value


def save_field(relative, filename, requested_time=None, pressure=False):
    ResetSession()
    _, points, time_value, _ = load_case(relative, requested_time)
    view = new_view(time_value)
    display = Show(points, view, "UnstructuredGridRepresentation")
    display.Representation = "Surface"
    array = "p" if pressure else "U"
    spec = ("POINTS", "p") if pressure else ("POINTS", "U", "Magnitude")
    ColorBy(display, spec)
    lut = GetColorTransferFunction(array)
    lut.ApplyPreset("Cool to Warm", True)
    display.RescaleTransferFunctionToDataRange(True, False)
    display.SetScalarBarVisibility(view, True)
    style_scalar_bar(lut, view)
    view.ResetCamera()
    Render(view)
    SaveScreenshot(os.path.join(output, filename), view, ImageResolution=[900, 900])
    return time_value


def save_base_specials():
    ResetSession()
    _, points, time_value, _ = load_case("cavityBase/cavityBase.foam")
    view = new_view(time_value)
    display = Show(points, view, "UnstructuredGridRepresentation")
    display.Representation = "Surface"
    ColorBy(display, ("POINTS", "p"))
    pressure_lut = GetColorTransferFunction("p")
    pressure_lut.ApplyPreset("Cool to Warm", True)
    display.RescaleTransferFunctionToDataRange(True, False)
    display.SetScalarBarVisibility(view, True)
    style_scalar_bar(pressure_lut, view)
    view.ResetCamera()
    Render(view)
    SaveScreenshot(os.path.join(output, "base_pressure.png"), view, ImageResolution=[900, 900])

    pressure_slice = Slice(registrationName="Mid-plane pressure slice", Input=points)
    pressure_slice.SliceType = "Plane"
    pressure_slice.SliceType.Origin = [0.05, 0.05, 0.005]
    pressure_slice.SliceType.Normal = [0.0, 0.0, 1.0]
    pressure_slice.UpdatePipeline(time_value)
    contour = Contour(registrationName="Ten pressure contours", Input=pressure_slice)
    contour.ContourBy = ["POINTS", "p"]
    bounds = points.PointData.GetArray("p").GetRange()
    contour.Isosurfaces = [bounds[0] + (bounds[1]-bounds[0])*i/11 for i in range(1, 11)]
    contour.UpdatePipeline(time_value)
    contour_display = Show(contour, view, "GeometryRepresentation")
    ColorBy(contour_display, None)
    contour_display.DiffuseColor = [0.05, 0.05, 0.05]
    contour_display.LineWidth = 4.0
    display.Opacity = 0.45
    Render(view)
    SaveScreenshot(os.path.join(output, "base_pressure_contours.png"), view, ImageResolution=[900, 900])

    Hide(contour, view)
    display.Opacity = 0.20
    glyph = Glyph(registrationName="Velocity vectors", Input=points, GlyphType="Arrow")
    glyph.OrientationArray = ["POINTS", "U"]
    glyph.ScaleArray = ["POINTS", "U"]
    glyph.ScaleFactor = 0.005
    glyph.GlyphMode = "Every Nth Point"
    glyph.Stride = 4
    glyph.UpdatePipeline(time_value)
    glyph_display = Show(glyph, view, "GeometryRepresentation")
    ColorBy(glyph_display, ("POINTS", "U", "Magnitude"))
    glyph_display.RescaleTransferFunctionToDataRange(True, False)
    Render(view)
    SaveScreenshot(os.path.join(output, "base_velocity_glyphs.png"), view, ImageResolution=[900, 900])

    Hide(glyph, view)
    tracer = StreamTracer(registrationName="Cavity streamlines", Input=points, SeedType="Line")
    tracer.Vectors = ["POINTS", "U"]
    tracer.SeedType.Point1 = [0.005, 0.005, 0.005]
    tracer.SeedType.Point2 = [0.095, 0.095, 0.005]
    tracer.SeedType.Resolution = 90
    tracer.IntegrationDirection = "BOTH"
    tracer.MaximumStreamlineLength = 1.0
    tracer.UpdatePipeline(time_value)
    tube = Tube(registrationName="Streamline tubes", Input=tracer)
    tube.Radius = 0.00035
    tube.NumberofSides = 8
    tube.UpdatePipeline(time_value)
    tube_display = Show(tube, view, "GeometryRepresentation")
    ColorBy(tube_display, ("POINTS", "U", "Magnitude"))
    tube_display.RescaleTransferFunctionToDataRange(True, False)
    Render(view)
    SaveScreenshot(os.path.join(output, "base_streamlines.png"), view, ImageResolution=[900, 900])


def save_streamlines(relative, filename):
    ResetSession()
    _, points, time_value, _ = load_case(relative)
    view = new_view(time_value)
    display = Show(points, view, "UnstructuredGridRepresentation")
    display.Representation = "Surface"
    ColorBy(display, ("POINTS", "U", "Magnitude"))
    lut = GetColorTransferFunction("U")
    lut.ApplyPreset("Cool to Warm", True)
    display.RescaleTransferFunctionToDataRange(True, False)
    display.SetScalarBarVisibility(view, True)
    style_scalar_bar(lut, view)
    display.Opacity = 0.22
    view.ResetCamera()
    tracer = StreamTracer(registrationName="Streamlines", Input=points, SeedType="Line")
    tracer.Vectors = ["POINTS", "U"]
    tracer.SeedType.Point1 = [0.005, 0.005, 0.005]
    tracer.SeedType.Point2 = [0.095, 0.095, 0.005]
    tracer.SeedType.Resolution = 100
    tracer.IntegrationDirection = "BOTH"
    tracer.MaximumStreamlineLength = 1.0
    tracer.UpdatePipeline(time_value)
    tube = Tube(registrationName="Streamline tubes", Input=tracer)
    tube.Radius = 0.0003
    tube.NumberofSides = 8
    tube.UpdatePipeline(time_value)
    tube_display = Show(tube, view, "GeometryRepresentation")
    ColorBy(tube_display, ("POINTS", "U", "Magnitude"))
    tube_display.RescaleTransferFunctionToDataRange(True, False)
    Render(view)
    SaveScreenshot(os.path.join(output, filename), view, ImageResolution=[900, 900])


def export_profile(relative, label):
    ResetSession()
    _, points, time_value, _ = load_case(relative)
    line = PlotOverLine(registrationName=label, Input=points)
    line.Point1 = [0.05, 0.0, 0.005]
    line.Point2 = [0.05, 0.1, 0.005]
    line.Resolution = 200
    line.UpdatePipeline(time_value)
    data = servermanager.Fetch(line)
    u = data.GetPointData().GetArray("U")
    result = []
    for index in range(data.GetNumberOfPoints()):
        x, y, z = data.GetPoint(index)
        result.append((y, u.GetTuple(index)[0]))
    return time_value, result


base_time = save_mesh("cavityBase/cavityBase.foam", "base_mesh.png")
save_base_specials()
fine_time = save_mesh("cavityFine/cavityFine.foam", "fine_mesh.png")
save_mesh("cavityGrade/cavityGrade.foam", "graded_mesh.png")
save_field("cavityHighRe/cavityHighRe.foam", "highRe_velocity.png")
save_streamlines("cavityHighRe/cavityHighRe.foam", "highRe_streamlines.png")
save_field("cavityRAS/cavityRAS.foam", "ras_velocity.png")
save_field("cavityRAS/cavityRAS.foam", "ras_pressure.png", pressure=True)
save_field("cavityClipped/cavityClipped.foam", "clipped_t0_5.png", requested_time=0.5)
save_field("cavityClipped/cavityClipped.foam", "clipped_t0_6.png", requested_time=0.6)

base_profile_time, base_profile = export_profile("cavityBase/cavityBase.foam", "coarse")
fine_profile_time, fine_profile = export_profile("cavityFine/cavityFine.foam", "fine")
profile_csv = os.path.join(output, "ux_profile_coarse_fine.csv")
with open(profile_csv, "w", newline="", encoding="utf-8") as stream:
    writer = csv.writer(stream)
    writer.writerow(("mesh", "time_s", "y_m", "Ux_m_s"))
    for label, time_value, values in (("20x20", base_profile_time, base_profile),
                                      ("40x40", fine_profile_time, fine_profile)):
        for y, ux in values:
            writer.writerow((label, time_value, y, ux))

print("LR2_RENDER_OK")
print("base_time=", base_time)
print("fine_time=", fine_time)
print("profile=", profile_csv)
