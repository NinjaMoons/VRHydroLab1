from paraview.simple import (
    ColorBy,
    FindSource,
    GetActiveSource,
    GetActiveViewOrCreate,
    GetDisplayProperties,
    Render,
    ResetCamera,
    SetActiveSource,
)

source = FindSource("cavity.foam") or GetActiveSource()
if source is None:
    raise RuntimeError("Source cavity.foam is not open")

SetActiveSource(source)
source.Createcelltopointfiltereddata = 1
source.UpdatePipeline(1.0)
view = GetActiveViewOrCreate("RenderView")
view.ViewTime = 1.0

display = GetDisplayProperties(source, view=view)
display.Representation = "Surface"
ColorBy(display, ("POINTS", "p"))
display.RescaleTransferFunctionToDataRange(True, False)
display.SetScalarBarVisibility(view, True)

view.CameraPosition = [0.05, 0.05, 1.0]
view.CameraFocalPoint = [0.05, 0.05, 0.005]
view.CameraViewUp = [0.0, 1.0, 0.0]
view.CameraParallelProjection = 1
ResetCamera(view=view)
Render(view)
