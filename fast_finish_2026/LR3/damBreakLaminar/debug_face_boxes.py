#!/usr/bin/env python

"""Print SALOME face bounding boxes for LR3 boundary-group debugging."""

import sys
import salome

salome.salome_init()
sys.path.insert(0, "/media/sf_OpenFOAM_Labs/lab3/damBreakLaminar")
import solid
from salome.geom import geomBuilder

geompy = geomBuilder.New()
faces = geompy.SubShapeAll(solid.Glue_1, geompy.ShapeType["FACE"])
print("FACE_COUNT", len(faces))
for index, face in enumerate(faces, 1):
    print(index, geompy.BoundingBox(face), geompy.BasicProperties(face))
