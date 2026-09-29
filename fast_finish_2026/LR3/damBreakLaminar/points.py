import salome

salome.salome_init()

from salome.geom import geomBuilder

geompy = geomBuilder.New()

coordinates = (
    (0, 0, 0),
    (2, 0, 0),
    (2.16438, 0, 0),
    (4, 0, 0),
    (0, 0.32876, 0),
    (2, 0.32876, 0),
    (2.16438, 0.32876, 0),
    (4, 0.32876, 0),
    (0, 4, 0),
    (2, 4, 0),
    (2.16438, 4, 0),
    (4, 4, 0),
)

for number, (x, y, z) in enumerate(coordinates, start=1):
    vertex = geompy.MakeVertex(x, y, z)
    geompy.addToStudy(vertex, f"Vertex_{number}")

if salome.sg.hasDesktop():
    salome.sg.updateObjBrowser()
    salome.sg.FitAll()
