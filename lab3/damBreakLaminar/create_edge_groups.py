#!/usr/bin/env python

"""Create only the five remaining edge groups in the current SALOME study."""

import salome
from salome.geom import geomBuilder


salome.salome_init()
geompy = geomBuilder.New()

study_object = salome.myStudy.FindObject("Glue_1")
if study_object is None:
    raise RuntimeError("Glue_1 was not found in the current study")

glue = study_object.GetObject()
all_edges = geompy.SubShapeAll(glue, geompy.ShapeType["EDGE"])


def create_group(name, length, expected_count):
    if salome.myStudy.FindObject(name) is not None:
        raise RuntimeError(f"{name} already exists; the script was not rerun")
    selected = [
        edge
        for edge in all_edges
        if abs(geompy.BasicProperties(edge)[0] - length) < 1.0e-8
    ]
    if len(selected) != expected_count:
        raise RuntimeError(
            f"{name}: expected {expected_count} edges, found {len(selected)}"
        )
    group = geompy.CreateGroup(glue, geompy.ShapeType["EDGE"])
    geompy.UnionList(group, selected)
    geompy.addToStudyInFather(glue, group, name)
    print(f"{name}: {len(selected)} edges")


create_group("Edges_X_left_23", 2.0, 6)
create_group("Edges_X_barrier_2", 0.16438, 4)
create_group("Edges_X_right_19", 1.83562, 6)
create_group("Edges_Y_lower_4", 0.32876, 8)
create_group("Edges_Y_upper_42", 3.67124, 8)

salome.sg.updateObjBrowser()
