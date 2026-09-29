#!/usr/bin/env python

"""Build the Lab 3 mesh and create named OpenFOAM boundary groups."""

import sys

import salome

salome.salome_init()
sys.path.insert(0, "/media/sf_OpenFOAM_Labs/lab3/damBreakLaminar")

sys.modules.pop("mesh1", None)
import mesh1

import SMESH
from salome.geom import geomBuilder


geompy = geomBuilder.New()
Glue_1 = mesh1.Glue_1
Mesh_1 = mesh1.Mesh_1

# MakeGlueFaces(1e-7) expands reported bounding boxes by about 1e-7.
TOL = 2.0e-7


def close(a, b):
    return abs(a - b) < TOL


def make_face_group(name, predicate, expected_count):
    faces = geompy.SubShapeAll(Glue_1, geompy.ShapeType["FACE"])
    selected = [face for face in faces if predicate(geompy.BoundingBox(face))]
    if len(selected) != expected_count:
        raise RuntimeError(
            f"{name}: expected {expected_count} faces, found {len(selected)}"
        )
    group = geompy.CreateGroup(Glue_1, geompy.ShapeType["FACE"])
    geompy.UnionList(group, selected)
    geompy.addToStudyInFather(Glue_1, group, name)
    return group


def is_left(box):
    xmin, xmax, ymin, ymax, zmin, zmax = box
    return close(xmin, 0.0) and close(xmax, 0.0)


def is_right(box):
    xmin, xmax, ymin, ymax, zmin, zmax = box
    return close(xmin, 4.0) and close(xmax, 4.0)


def is_atmosphere(box):
    xmin, xmax, ymin, ymax, zmin, zmax = box
    return close(ymin, 4.0) and close(ymax, 4.0)


def is_front_or_back(box):
    xmin, xmax, ymin, ymax, zmin, zmax = box
    return (close(zmin, 0.0) and close(zmax, 0.0)) or (
        close(zmin, 0.1) and close(zmax, 0.1)
    )


def is_lower_wall(box):
    xmin, xmax, ymin, ymax, zmin, zmax = box
    bottom = close(ymin, 0.0) and close(ymax, 0.0)
    barrier_top = (
        close(ymin, 0.32876)
        and close(ymax, 0.32876)
        and close(xmin, 2.0)
        and close(xmax, 2.16438)
    )
    barrier_left = (
        close(xmin, 2.0)
        and close(xmax, 2.0)
        and close(ymin, 0.0)
        and close(ymax, 0.32876)
    )
    barrier_right = (
        close(xmin, 2.16438)
        and close(xmax, 2.16438)
        and close(ymin, 0.0)
        and close(ymax, 0.32876)
    )
    return bottom or barrier_top or barrier_left or barrier_right


leftWall_geom = make_face_group("leftWall", is_left, 2)
rightWall_geom = make_face_group("rightWall", is_right, 2)
lowerWall_geom = make_face_group("lowerWall", is_lower_wall, 5)
atmosphere_geom = make_face_group("atmosphere", is_atmosphere, 3)
frontAndBack_geom = make_face_group("frontAndBack", is_front_or_back, 10)

leftWall = Mesh_1.GroupOnGeom(leftWall_geom, "leftWall", SMESH.FACE)
rightWall = Mesh_1.GroupOnGeom(rightWall_geom, "rightWall", SMESH.FACE)
lowerWall = Mesh_1.GroupOnGeom(lowerWall_geom, "lowerWall", SMESH.FACE)
atmosphere = Mesh_1.GroupOnGeom(atmosphere_geom, "atmosphere", SMESH.FACE)
frontAndBack = Mesh_1.GroupOnGeom(frontAndBack_geom, "frontAndBack", SMESH.FACE)

if not Mesh_1.Compute():
    Mesh_1.CheckCompute()
    raise RuntimeError("Mesh_1 recomputation with boundary groups failed")

print("Boundary groups created successfully")
print("leftWall faces:", leftWall.Size())
print("rightWall faces:", rightWall.Size())
print("lowerWall faces:", lowerWall.Size())
print("atmosphere faces:", atmosphere.Size())
print("frontAndBack faces:", frontAndBack.Size())

if salome.sg.hasDesktop():
    salome.sg.updateObjBrowser()
