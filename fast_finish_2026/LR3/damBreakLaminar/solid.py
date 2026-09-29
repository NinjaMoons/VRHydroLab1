#!/usr/bin/env python

###
### This file is generated automatically by SALOME v9.16.0 with dump python functionality
###

import sys
import salome

salome.salome_init()
import salome_notebook
notebook = salome_notebook.NoteBook()
sys.path.insert(0, r'/media/sf_OpenFOAM_Labs/lab3/damBreakLaminar')

###
### GEOM component
###

import GEOM
from salome.geom import geomBuilder
import math
import SALOMEDS


geompy = geomBuilder.New()

O = geompy.MakeVertex(0, 0, 0)
OX = geompy.MakeVectorDXDYDZ(1, 0, 0)
OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)
Vertex_1 = geompy.MakeVertex(0, 0, 0)
Vertex_1_1 = geompy.MakeVertex(0, 0, 0)
Vertex_2 = geompy.MakeVertex(2, 0, 0)
Vertex_3 = geompy.MakeVertex(2.16438, 0, 0)
Vertex_4 = geompy.MakeVertex(4, 0, 0)
Vertex_5 = geompy.MakeVertex(0, 0.32876, 0)
Vertex_6 = geompy.MakeVertex(2, 0.32876, 0)
Vertex_7 = geompy.MakeVertex(2.16438, 0.32876, 0)
Vertex_8 = geompy.MakeVertex(4, 0.32876, 0)
Vertex_9 = geompy.MakeVertex(0, 4, 0)
Vertex_10 = geompy.MakeVertex(2, 4, 0)
Vertex_11 = geompy.MakeVertex(2.16438, 4, 0)
Vertex_12 = geompy.MakeVertex(4, 4, 0)
Line_1 = geompy.MakeLineTwoPnt(Vertex_1, Vertex_2)
Line_2 = geompy.MakeLineTwoPnt(Vertex_3, Vertex_4)
Line_3 = geompy.MakeLineTwoPnt(Vertex_5, Vertex_6)
Line_4 = geompy.MakeLineTwoPnt(Vertex_6, Vertex_7)
Line_5 = geompy.MakeLineTwoPnt(Vertex_7, Vertex_8)
Line_6 = geompy.MakeLineTwoPnt(Vertex_9, Vertex_10)
Line_7 = geompy.MakeLineTwoPnt(Vertex_10, Vertex_11)
Line_8 = geompy.MakeLineTwoPnt(Vertex_11, Vertex_12)
Line_9 = geompy.MakeLineTwoPnt(Vertex_1_1, Vertex_5)
Line_10 = geompy.MakeLineTwoPnt(Vertex_2, Vertex_6)
Line_11 = geompy.MakeLineTwoPnt(Vertex_3, Vertex_7)
Line_12 = geompy.MakeLineTwoPnt(Vertex_4, Vertex_8)
Line_13 = geompy.MakeLineTwoPnt(Vertex_5, Vertex_9)
Line_14 = geompy.MakeLineTwoPnt(Vertex_6, Vertex_10)
Line_15 = geompy.MakeLineTwoPnt(Vertex_7, Vertex_11)
Line_16 = geompy.MakeLineTwoPnt(Vertex_8, Vertex_12)
Face_1 = geompy.MakeFaceWires([Line_1, Line_3, Line_9, Line_10], True)
Face_2 = geompy.MakeFaceWires([Line_2, Line_5, Line_11, Line_12], True)
Face_3 = geompy.MakeFaceWires([Line_3, Line_6, Line_13, Line_14], True)
Face_4 = geompy.MakeFaceWires([Line_4, Line_7, Line_14, Line_15], True)
Face_5 = geompy.MakeFaceWires([Line_5, Line_8, Line_15, Line_16], True)
Compound_1 = geompy.MakeCompound([Face_1, Face_2, Face_3, Face_4, Face_5])
Extrusion_1 = geompy.MakePrismVecH(Compound_1, OZ, 0.1)
Glue_1 = geompy.MakeGlueFaces(Extrusion_1, 1e-07)
geompy.addToStudy( O, 'O' )
geompy.addToStudy( OX, 'OX' )
geompy.addToStudy( OY, 'OY' )
geompy.addToStudy( OZ, 'OZ' )
geompy.addToStudy( Vertex_1, 'Vertex_1' )
geompy.addToStudy( Vertex_1_1, 'Vertex_1' )
geompy.addToStudy( Vertex_2, 'Vertex_2' )
geompy.addToStudy( Vertex_3, 'Vertex_3' )
geompy.addToStudy( Vertex_4, 'Vertex_4' )
geompy.addToStudy( Vertex_5, 'Vertex_5' )
geompy.addToStudy( Vertex_6, 'Vertex_6' )
geompy.addToStudy( Vertex_7, 'Vertex_7' )
geompy.addToStudy( Vertex_8, 'Vertex_8' )
geompy.addToStudy( Vertex_9, 'Vertex_9' )
geompy.addToStudy( Vertex_10, 'Vertex_10' )
geompy.addToStudy( Vertex_11, 'Vertex_11' )
geompy.addToStudy( Vertex_12, 'Vertex_12' )
geompy.addToStudy( Line_1, 'Line_1' )
geompy.addToStudy( Line_2, 'Line_2' )
geompy.addToStudy( Line_3, 'Line_3' )
geompy.addToStudy( Line_4, 'Line_4' )
geompy.addToStudy( Line_5, 'Line_5' )
geompy.addToStudy( Line_6, 'Line_6' )
geompy.addToStudy( Line_7, 'Line_7' )
geompy.addToStudy( Line_8, 'Line_8' )
geompy.addToStudy( Line_9, 'Line_9' )
geompy.addToStudy( Line_10, 'Line_10' )
geompy.addToStudy( Line_11, 'Line_11' )
geompy.addToStudy( Line_12, 'Line_12' )
geompy.addToStudy( Line_13, 'Line_13' )
geompy.addToStudy( Line_14, 'Line_14' )
geompy.addToStudy( Line_15, 'Line_15' )
geompy.addToStudy( Line_16, 'Line_16' )
geompy.addToStudy( Face_1, 'Face_1' )
geompy.addToStudy( Face_2, 'Face_2' )
geompy.addToStudy( Face_3, 'Face_3' )
geompy.addToStudy( Face_4, 'Face_4' )
geompy.addToStudy( Face_5, 'Face_5' )
geompy.addToStudy( Compound_1, 'Compound_1' )
geompy.addToStudy( Extrusion_1, 'Extrusion_1' )
geompy.addToStudy( Glue_1, 'Glue_1' )


if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()
