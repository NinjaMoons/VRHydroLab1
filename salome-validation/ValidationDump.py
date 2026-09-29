#!/usr/bin/env python

###
### This file is generated automatically by SALOME v9.16.0 with dump python functionality
###

import sys
import salome

salome.salome_init()
import salome_notebook
notebook = salome_notebook.NoteBook()
sys.path.insert(0, r'/media/sf_OpenFOAM_Labs/salome-validation')

###
### GEOM component
###

import GEOM
from salome.geom import geomBuilder
import math
import SALOMEDS


geompy = geomBuilder.New()

ValidationBox = geompy.MakeBoxDXDYDZ(1, 1, 0.1)
[geomObj_1,geomObj_2,geomObj_3,geomObj_4,geomObj_5,geomObj_6] = geompy.SubShapeAllSortedCentres(ValidationBox, geompy.ShapeType["FACE"])
boundary_1 = geompy.CreateGroup(ValidationBox, geompy.ShapeType["FACE"])
geompy.UnionList(boundary_1, [geomObj_1])
boundary_2 = geompy.CreateGroup(ValidationBox, geompy.ShapeType["FACE"])
geompy.UnionList(boundary_2, [geomObj_2])
boundary_3 = geompy.CreateGroup(ValidationBox, geompy.ShapeType["FACE"])
geompy.UnionList(boundary_3, [geomObj_3])
boundary_4 = geompy.CreateGroup(ValidationBox, geompy.ShapeType["FACE"])
geompy.UnionList(boundary_4, [geomObj_4])
boundary_5 = geompy.CreateGroup(ValidationBox, geompy.ShapeType["FACE"])
geompy.UnionList(boundary_5, [geomObj_5])
boundary_6 = geompy.CreateGroup(ValidationBox, geompy.ShapeType["FACE"])
geompy.UnionList(boundary_6, [geomObj_6])
geompy.addToStudy( ValidationBox, 'ValidationBox' )
geompy.addToStudyInFather( ValidationBox, boundary_1, 'boundary_1' )
geompy.addToStudyInFather( ValidationBox, boundary_2, 'boundary_2' )
geompy.addToStudyInFather( ValidationBox, boundary_3, 'boundary_3' )
geompy.addToStudyInFather( ValidationBox, boundary_4, 'boundary_4' )
geompy.addToStudyInFather( ValidationBox, boundary_5, 'boundary_5' )
geompy.addToStudyInFather( ValidationBox, boundary_6, 'boundary_6' )

###
### SMESH component
###

import  SMESH, SALOMEDS
from salome.smesh import smeshBuilder

smesh = smeshBuilder.New()
#smesh.SetEnablePublish( False ) # Set to False to avoid publish in study if not needed or in some particular situations:
                                 # multiples meshes built in parallel, complex and numerous mesh edition (performance)

ValidationMesh = smesh.Mesh(ValidationBox,'ValidationMesh')
Regular_1D_1 = ValidationMesh.Segment()
NumberOfSegments_4_0 = Regular_1D_1.NumberOfSegments(4,None,[])
Quadrangle_2D_2 = ValidationMesh.Quadrangle(algo=smeshBuilder.QUADRANGLE)
Hexa_3D_3 = ValidationMesh.Hexahedron(algo=smeshBuilder.Hexa)
isDone = ValidationMesh.Compute()
ValidationMesh.CheckCompute()
boundary_1_1 = ValidationMesh.GroupOnGeom(boundary_1,'boundary_1',SMESH.FACE)
boundary_2_1 = ValidationMesh.GroupOnGeom(boundary_2,'boundary_2',SMESH.FACE)
boundary_3_1 = ValidationMesh.GroupOnGeom(boundary_3,'boundary_3',SMESH.FACE)
boundary_4_1 = ValidationMesh.GroupOnGeom(boundary_4,'boundary_4',SMESH.FACE)
boundary_5_1 = ValidationMesh.GroupOnGeom(boundary_5,'boundary_5',SMESH.FACE)
boundary_6_1 = ValidationMesh.GroupOnGeom(boundary_6,'boundary_6',SMESH.FACE)
try:
  ValidationMesh.ExportUNV( r'/media/sf_OpenFOAM_Labs/salome-validation/ValidationMesh.unv', 1 )
  pass
except:
  print('ExportUNV() failed. Invalid file name?')


## Set names of Mesh objects
smesh.SetName(NumberOfSegments_4_0, 'NumberOfSegments=4,[],0:1:1:1')
smesh.SetName(boundary_4_1, 'boundary_4')
smesh.SetName(boundary_5_1, 'boundary_5')
smesh.SetName(ValidationMesh.GetMesh(), 'ValidationMesh')
smesh.SetName(boundary_1_1, 'boundary_1')
smesh.SetName(boundary_2_1, 'boundary_2')
smesh.SetName(boundary_6_1, 'boundary_6')
smesh.SetName(Hexa_3D_3.GetAlgorithm(), 'Hexa_3D_3')
smesh.SetName(boundary_3_1, 'boundary_3')
smesh.SetName(Regular_1D_1.GetAlgorithm(), 'Regular_1D_1')
smesh.SetName(Quadrangle_2D_2.GetAlgorithm(), 'Quadrangle_2D_2')


if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()
