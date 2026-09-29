#!/usr/bin/env python3

"""Generate the parameterised Variant 3 geometry and one-layer SALOME mesh."""

import argparse
import json
import os
import sys

import salome

salome.salome_init()

import SMESH
from salome.geom import geomBuilder
from salome.smesh import smeshBuilder


HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJECT, "scripts"))

from geometry import derived_values, load_settings


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--settings",
        default=os.environ.get("CPV3_SETTINGS", os.path.join(PROJECT, "settings.json")),
    )
    parser.add_argument(
        "--output-dir",
        default=os.environ.get("CPV3_OUTPUT_DIR", HERE),
    )
    return parser.parse_args()


def close(value, target, tolerance=1.0e-5):
    return abs(value - target) <= tolerance


def rectangle_face(geompy, xmin, ymin, xmax, ymax):
    vertices = [
        geompy.MakeVertex(xmin, ymin, 0.0),
        geompy.MakeVertex(xmax, ymin, 0.0),
        geompy.MakeVertex(xmax, ymax, 0.0),
        geompy.MakeVertex(xmin, ymax, 0.0),
    ]
    edges = [
        geompy.MakeLineTwoPnt(vertices[index], vertices[(index + 1) % 4])
        for index in range(4)
    ]
    return geompy.MakeFaceWires(edges, True)


def geometry_group(geompy, parent, shape_type, name, selected):
    if not selected:
        raise RuntimeError("geometry group %s is empty" % name)
    group = geompy.CreateGroup(parent, shape_type)
    geompy.UnionList(group, selected)
    geompy.addToStudyInFather(parent, group, name)
    return group


def classify_planar_edges(geompy, face, L, H):
    categories = {"inlet": [], "outlet": [], "walls": [], "obstacles": []}
    for edge in geompy.SubShapeAll(face, geompy.ShapeType["EDGE"]):
        xmin, xmax, ymin, ymax, _zmin, _zmax = geompy.BoundingBox(edge)
        if close(xmin, 0.0) and close(xmax, 0.0):
            categories["inlet"].append(edge)
        elif close(xmin, L) and close(xmax, L):
            categories["outlet"].append(edge)
        elif (close(ymin, 0.0) and close(ymax, 0.0)) or (
            close(ymin, H) and close(ymax, H)
        ):
            categories["walls"].append(edge)
        else:
            categories["obstacles"].append(edge)
    expected = {"inlet": 1, "outlet": 1, "walls": 2, "obstacles": 28}
    for name, count in expected.items():
        if len(categories[name]) != count:
            raise RuntimeError(
                "%s: expected %d planar edges, found %d"
                % (name, count, len(categories[name]))
            )
    return categories


def classify_solid_faces(geompy, solid, L, H, thickness):
    categories = {
        "inlet": [],
        "outlet": [],
        "walls": [],
        "obstacles": [],
        "frontAndBack": [],
    }
    for face in geompy.SubShapeAll(solid, geompy.ShapeType["FACE"]):
        xmin, xmax, ymin, ymax, zmin, zmax = geompy.BoundingBox(face)
        if (close(zmin, 0.0) and close(zmax, 0.0)) or (
            close(zmin, thickness) and close(zmax, thickness)
        ):
            categories["frontAndBack"].append(face)
        elif close(xmin, 0.0) and close(xmax, 0.0):
            categories["inlet"].append(face)
        elif close(xmin, L) and close(xmax, L):
            categories["outlet"].append(face)
        elif (close(ymin, 0.0) and close(ymax, 0.0)) or (
            close(ymin, H) and close(ymax, H)
        ):
            categories["walls"].append(face)
        else:
            categories["obstacles"].append(face)
    expected = {
        "inlet": 1,
        "outlet": 1,
        "walls": 2,
        "obstacles": 28,
        "frontAndBack": 2,
    }
    for name, count in expected.items():
        if len(categories[name]) != count:
            raise RuntimeError(
                "%s: expected %d solid faces, found %d"
                % (name, count, len(categories[name]))
            )
    return categories


def classify_mesh_faces(mesh, L, H, thickness):
    categories = {
        "inlet": [],
        "outlet": [],
        "walls": [],
        "obstacles": [],
        "frontAndBack": [],
    }
    tolerance = 1.0e-6

    def all_close(values, target):
        return all(abs(value - target) <= tolerance for value in values)

    for face_id in mesh.GetElementsByType(SMESH.FACE):
        points = [mesh.GetNodeXYZ(node_id) for node_id in mesh.GetElemNodes(face_id)]
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        zs = [point[2] for point in points]
        if all_close(zs, 0.0) or all_close(zs, thickness):
            categories["frontAndBack"].append(face_id)
        elif all_close(xs, 0.0):
            categories["inlet"].append(face_id)
        elif all_close(xs, L):
            categories["outlet"].append(face_id)
        elif all_close(ys, 0.0) or all_close(ys, H):
            categories["walls"].append(face_id)
        else:
            categories["obstacles"].append(face_id)
    for name, identifiers in categories.items():
        if not identifiers:
            raise RuntimeError("mesh boundary group %s is empty" % name)
    return categories


def main():
    arguments = parse_arguments()
    settings = load_settings(arguments.settings)
    derived = derived_values(settings)
    geometry = settings["geometryMm"]
    mesh_settings = settings["mesh"]
    L = float(geometry["L"])
    H = float(geometry["H"])
    a = float(geometry["a"])
    thickness = float(mesh_settings["thicknessMm"])
    max_size = float(mesh_settings["maxSizeMm"])
    min_size = float(mesh_settings["minSizeMm"])
    obstacle_size = float(mesh_settings["obstacleSizeMm"])

    output_dir = os.path.abspath(arguments.output_dir)
    os.makedirs(output_dir, exist_ok=True)
    unv_path = os.path.join(output_dir, "Mesh.unv")
    hdf_path = os.path.join(output_dir, "CourseProject_V3.hdf")
    statistics_path = os.path.join(output_dir, "mesh_summary.json")

    geompy = geomBuilder.New()
    smesh = smeshBuilder.New()
    oz = geompy.MakeVectorDXDYDZ(0.0, 0.0, 1.0)

    channel = rectangle_face(geompy, 0.0, 0.0, L, H)
    obstacle_faces = []
    for obstacle in derived["obstacles"]:
        half = a / 2.0
        face = rectangle_face(
            geompy,
            obstacle["x"] - half,
            obstacle["y"] - half,
            obstacle["x"] + half,
            obstacle["y"] + half,
        )
        obstacle_faces.append(face)

    fluid_face = geompy.MakeCutList(channel, obstacle_faces, True)
    solid = geompy.MakePrismVecH(fluid_face, oz, thickness)
    geompy.addToStudy(fluid_face, "Fluid_domain_2D")
    geompy.addToStudy(solid, "Fluid_domain_3D")

    planar_edges = classify_planar_edges(geompy, fluid_face, L, H)
    edge_groups = {
        name: geometry_group(
            geompy,
            fluid_face,
            geompy.ShapeType["EDGE"],
            name + "_edges",
            selected,
        )
        for name, selected in planar_edges.items()
    }

    solid_faces = classify_solid_faces(geompy, solid, L, H, thickness)
    for name, selected in solid_faces.items():
        geometry_group(
            geompy,
            solid,
            geompy.ShapeType["FACE"],
            name,
            selected,
        )

    mesh = smesh.Mesh(fluid_face, "Variant3_mesh")
    netgen = mesh.Triangle(algo=smeshBuilder.NETGEN_1D2D)
    parameters = netgen.Parameters()
    parameters.SetMaxSize(max_size)
    parameters.SetMinSize(min_size)
    parameters.SetSecondOrder(0)
    parameters.SetOptimize(1)
    parameters.SetFineness(2)
    parameters.SetGrowthRate(0.2)
    parameters.SetNbSegPerEdge(1)
    parameters.SetQuadAllowed(1 if mesh_settings.get("quadAllowed", False) else 0)
    parameters.SetUseSurfaceCurvature(1)
    parameters.SetFuseEdges(1)
    parameters.SetLocalSizeOnShape(edge_groups["obstacles"], obstacle_size)

    if not mesh.Compute():
        mesh.CheckCompute()
        raise RuntimeError("SALOME failed to compute the 2D mesh")
    triangles_2d = mesh.NbTriangles()
    quadrangles_2d = mesh.NbQuadrangles()
    faces_2d = triangles_2d + quadrangles_2d
    if faces_2d <= 0:
        raise RuntimeError("SALOME generated no 2D faces")

    mesh.ExtrusionSweepObject2D(mesh, [0.0, 0.0, thickness], 1, MakeGroups=False)
    if mesh.NbVolumes() != faces_2d:
        raise RuntimeError(
            "expected one volume per 2D face: faces=%d volumes=%d"
            % (faces_2d, mesh.NbVolumes())
        )

    boundary_faces = classify_mesh_faces(mesh, L, H, thickness)
    groups = []
    for name in ("inlet", "outlet", "walls", "obstacles", "frontAndBack"):
        groups.append(mesh.MakeGroupByIds(name, SMESH.FACE, boundary_faces[name]))

    mesh.ExportUNV(unv_path)
    salome.myStudy.SaveAs(hdf_path, False, False)

    mesh_info = mesh.GetMeshInfo()
    summary = {
        "settings": os.path.abspath(arguments.settings),
        "nodes": mesh.NbNodes(),
        "edges": mesh.NbEdges(),
        "faces": mesh.NbFaces(),
        "trianglesPerPlane": triangles_2d,
        "quadranglesPerPlane": quadrangles_2d,
        "volumes": mesh.NbVolumes(),
        "pentas": mesh_info[SMESH.Entity_Penta],
        "hexas": mesh_info[SMESH.Entity_Hexa],
        "groups": {group.GetName(): group.Size() for group in groups},
        "files": {
            "unv": {"path": unv_path, "bytes": os.path.getsize(unv_path)},
            "hdf": {"path": hdf_path, "bytes": os.path.getsize(hdf_path)},
        },
    }
    with open(statistics_path, "w", encoding="utf-8") as stream:
        json.dump(summary, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")

    print("COURSEPROJECT_V3_SALOME_OK")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
