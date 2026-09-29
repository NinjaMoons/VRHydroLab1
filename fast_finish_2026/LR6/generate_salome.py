#!/usr/bin/env python

"""Build and export the parameter-derived LR6 nozzle mesh in SALOME."""

import os
import sys

import salome

salome.salome_init()
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import SMESH
from salome.geom import geomBuilder
from salome.smesh import smeshBuilder

from calc_nozzle import calculate


result = calculate(200000.0, 1800.0, 9000.0, 1.5, 14.0, 28.0)
inlet_r = 500.0 * result["inlet"]["diameter_m"]
throat_r = 500.0 * result["throat"]["diameter_m"]
outlet_r = 500.0 * result["outlet"]["diameter_m"]
x_inlet = -1000.0 * result["geometry"]["length_convergent_m"]
x_throat = 0.0
x_outlet = 1000.0 * result["geometry"]["length_divergent_m"]
depth = 4.0

geompy = geomBuilder.New()
smesh = smeshBuilder.New()
oz = geompy.MakeVectorDXDYDZ(0, 0, 1)


def quad_face(coords):
    vertices = [geompy.MakeVertex(x, y, 0.0) for x, y in coords]
    edges = [
        geompy.MakeLineTwoPnt(vertices[index], vertices[(index + 1) % 4])
        for index in range(4)
    ]
    return geompy.MakeFaceWires(edges, True)


left_face = quad_face(((x_inlet, 0), (x_throat, 0),
                       (x_throat, throat_r), (x_inlet, inlet_r)))
right_face = quad_face(((x_throat, 0), (x_outlet, 0),
                        (x_outlet, outlet_r), (x_throat, throat_r)))
base = geompy.MakeCompound([left_face, right_face])
extrusion = geompy.MakePrismVecH(base, oz, depth)
geometry = geompy.MakeGlueFaces(extrusion, 1.0e-5)
geompy.addToStudy(geometry, "Nozzle_geometry")

tol = 2.0e-5


def close(a, b):
    return abs(a - b) < tol


def face_group(name, predicate, expected):
    faces = geompy.SubShapeAll(geometry, geompy.ShapeType["FACE"])
    selected = [face for face in faces if predicate(geompy.BoundingBox(face))]
    if len(selected) != expected:
        raise RuntimeError("%s: expected %d faces, found %d" %
                           (name, expected, len(selected)))
    group = geompy.CreateGroup(geometry, geompy.ShapeType["FACE"])
    geompy.UnionList(group, selected)
    geompy.addToStudyInFather(geometry, group, name)
    return group


def box_values(box):
    return tuple(box)


inlet_geom = face_group(
    "inlet", lambda b: close(box_values(b)[0], x_inlet) and close(box_values(b)[1], x_inlet), 1)
outlet_geom = face_group(
    "outlet", lambda b: close(box_values(b)[0], x_outlet) and close(box_values(b)[1], x_outlet), 1)
axis_geom = face_group(
    "axis", lambda b: close(box_values(b)[2], 0.0) and close(box_values(b)[3], 0.0), 2)
front_back_geom = face_group(
    "frontAndBack",
    lambda b: ((close(box_values(b)[4], 0.0) and close(box_values(b)[5], 0.0)) or
               (close(box_values(b)[4], depth) and close(box_values(b)[5], depth))),
    4,
)


def is_wall(box):
    xmin, xmax, ymin, ymax, zmin, zmax = box_values(box)
    spans_depth = close(zmin, 0.0) and close(zmax, depth)
    is_end = (close(xmin, x_inlet) and close(xmax, x_inlet)) or \
             (close(xmin, x_outlet) and close(xmax, x_outlet))
    is_axis = close(ymin, 0.0) and close(ymax, 0.0)
    is_cross_section = close(xmin, xmax)
    return spans_depth and not is_end and not is_axis and not is_cross_section


wall_geom = face_group("wall", is_wall, 2)

edges = geompy.SubShapeAll(geometry, geompy.ShapeType["EDGE"])


def edge_group(name, predicate, expected):
    selected = [edge for edge in edges if predicate(geompy.BoundingBox(edge))]
    if len(selected) != expected:
        raise RuntimeError("%s: expected %d edges, found %d" %
                           (name, expected, len(selected)))
    group = geompy.CreateGroup(geometry, geompy.ShapeType["EDGE"])
    geompy.UnionList(group, selected)
    geompy.addToStudyInFather(geometry, group, name)
    return group


def is_depth_edge(box):
    xmin, xmax, ymin, ymax, zmin, zmax = box_values(box)
    return close(xmin, xmax) and close(ymin, ymax) and close(zmin, 0.0) and close(zmax, depth)


def is_left_axial(box):
    xmin, xmax, ymin, ymax, zmin, zmax = box_values(box)
    return close(xmin, x_inlet) and close(xmax, x_throat) and close(zmin, zmax)


def is_right_axial(box):
    xmin, xmax, ymin, ymax, zmin, zmax = box_values(box)
    return close(xmin, x_throat) and close(xmax, x_outlet) and close(zmin, zmax)


def is_radial(box):
    xmin, xmax, ymin, ymax, zmin, zmax = box_values(box)
    return close(xmin, xmax) and not close(ymin, ymax) and close(zmin, zmax)


depth_edges = edge_group("Edges_depth_1", is_depth_edge, 6)
left_edges = edge_group("Edges_convergent_120", is_left_axial, 4)
right_edges = edge_group("Edges_divergent_80", is_right_axial, 4)
radial_edges = edge_group("Edges_radial_40", is_radial, 6)

mesh = smesh.Mesh(geometry, "Nozzle_mesh")
mesh.Segment().NumberOfSegments(15)
mesh.Quadrangle(algo=smeshBuilder.QUADRANGLE)
mesh.Hexahedron(algo=smeshBuilder.Hexa)


def local_segments(group, number):
    mesh.Segment(geom=group).NumberOfSegments(number, None, [])


local_segments(depth_edges, 1)
local_segments(left_edges, 120)
local_segments(right_edges, 80)
local_segments(radial_edges, 40)

if not mesh.Compute():
    mesh.CheckCompute()
    raise RuntimeError("SALOME failed to compute nozzle mesh")

groups = (
    mesh.GroupOnGeom(inlet_geom, "inlet", SMESH.FACE),
    mesh.GroupOnGeom(outlet_geom, "outlet", SMESH.FACE),
    mesh.GroupOnGeom(axis_geom, "axis", SMESH.FACE),
    mesh.GroupOnGeom(wall_geom, "wall", SMESH.FACE),
    mesh.GroupOnGeom(front_back_geom, "frontAndBack", SMESH.FACE),
)

if not mesh.Compute():
    raise RuntimeError("SALOME failed to recompute mesh boundary groups")

unv_path = os.path.join(HERE, "Mesh.unv")
hdf_path = os.path.join(HERE, "LR6-nozzle.hdf")
mesh.ExportUNV(unv_path)
salome.myStudy.SaveAs(hdf_path, False, False)

print("LR6_SALOME_EXPORT_OK")
print("nodes=", mesh.NbNodes())
print("hexas=", mesh.NbHexas())
for group in groups:
    print("group_%s=%d" % (group.GetName(), group.Size()))
print("unv=", unv_path, os.path.getsize(unv_path))
print("hdf=", hdf_path, os.path.getsize(hdf_path))
