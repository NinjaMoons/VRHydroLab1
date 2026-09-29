#!/usr/bin/env python

"""Build the Lab 3 geometry and its structured hexahedral mesh in SALOME."""

import sys

import salome

salome.salome_init()
sys.path.insert(0, "/media/sf_OpenFOAM_Labs/lab3/damBreakLaminar")

sys.modules.pop("solid", None)
import solid

import SMESH
from salome.geom import geomBuilder
from salome.smesh import smeshBuilder


geompy = geomBuilder.New()
smesh = smeshBuilder.New()
Glue_1 = solid.Glue_1


def edge_group_by_length(name, target_length, expected_count):
    """Create a GEOM group containing all edges of the requested length."""
    all_edges = geompy.SubShapeAll(Glue_1, geompy.ShapeType["EDGE"])
    selected = [
        edge
        for edge in all_edges
        if abs(geompy.BasicProperties(edge)[0] - target_length) < 1.0e-8
    ]
    if len(selected) != expected_count:
        raise RuntimeError(
            f"{name}: expected {expected_count} edges of length {target_length}, "
            f"found {len(selected)}"
        )
    group = geompy.CreateGroup(Glue_1, geompy.ShapeType["EDGE"])
    geompy.UnionList(group, selected)
    geompy.addToStudyInFather(Glue_1, group, name)
    return group


# Edge groups are identified by the exact dimensions from blockMeshDict.
Edges_Z_1cell = edge_group_by_length("Edges_Z_1cell", 0.1, 12)
Edges_X_left_23 = edge_group_by_length("Edges_X_left_23", 2.0, 6)
Edges_X_right_19 = edge_group_by_length("Edges_X_right_19", 1.83562, 6)
Edges_Y_upper_42 = edge_group_by_length("Edges_Y_upper_42", 3.67124, 8)
Edges_X_barrier_2 = edge_group_by_length("Edges_X_barrier_2", 0.16438, 4)
Edges_Y_barrier_4 = edge_group_by_length("Edges_Y_barrier_4", 0.32876, 8)


Mesh_1 = smesh.Mesh(Glue_1, "Mesh_1")

# Global structured-hexahedral algorithms and default edge discretisation.
Regular_1D = Mesh_1.Segment()
Number_of_Segments_15 = Regular_1D.NumberOfSegments(15, None, [])
Quadrangle_2D = Mesh_1.Quadrangle(algo=smeshBuilder.QUADRANGLE)
Hexahedron_3D = Mesh_1.Hexahedron(algo=smeshBuilder.Hexa)


def set_local_segments(group, number, name):
    algorithm = Mesh_1.Segment(geom=group)
    hypothesis = algorithm.NumberOfSegments(number, None, [])
    smesh.SetName(algorithm.GetAlgorithm(), f"Wire_{name}")
    smesh.SetName(hypothesis, f"Segments_{number}_{name}")
    return algorithm.GetSubMesh()


SubMesh_Z_1 = set_local_segments(Edges_Z_1cell, 1, "Z")
SubMesh_X_left_23 = set_local_segments(Edges_X_left_23, 23, "X_left")
SubMesh_X_right_19 = set_local_segments(Edges_X_right_19, 19, "X_right")
SubMesh_Y_upper_42 = set_local_segments(Edges_Y_upper_42, 42, "Y_upper")
SubMesh_X_barrier_2 = set_local_segments(Edges_X_barrier_2, 2, "X_barrier")
SubMesh_Y_barrier_4 = set_local_segments(Edges_Y_barrier_4, 4, "Y_barrier")

if not Mesh_1.Compute():
    Mesh_1.CheckCompute()
    raise RuntimeError("Mesh_1 computation failed")

print("Mesh_1 computed successfully")
print("Nodes:", Mesh_1.NbNodes())
print("Hexahedra:", Mesh_1.NbHexas())

if salome.sg.hasDesktop():
    salome.sg.updateObjBrowser()
