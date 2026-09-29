#!/usr/bin/env python

"""Rebuild the LR3 SALOME study, verify its mesh, and export durable artifacts."""

import os
import sys

import salome


CASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CASE_DIR)

# Importing this module rebuilds geometry, mesh hypotheses and named boundaries.
import mesh1_withBoundary as lab3


mesh = lab3.Mesh_1
group_names = ("leftWall", "rightWall", "lowerWall", "atmosphere", "frontAndBack")
groups = {group.GetName(): group for group in mesh.GetGroups()}
missing = sorted(set(group_names) - set(groups))
if missing:
    raise RuntimeError("Missing mesh boundary groups: " + ", ".join(missing))

nodes = mesh.NbNodes()
hexas = mesh.NbHexas()
if nodes != 4222 or hexas != 2016:
    raise RuntimeError(
        "Unexpected mesh size: nodes=%d, hexas=%d; expected 4222 and 2016"
        % (nodes, hexas)
    )

unv_path = os.path.join(CASE_DIR, "Mesh_1.unv")
hdf_path = os.path.join(CASE_DIR, "Lab3-final.hdf")
dump_path = os.path.join(CASE_DIR, "Lab3-final-dump.py")

mesh.ExportUNV(unv_path)
salome.myStudy.SaveAs(hdf_path, False, False)
dump_ok = salome.myStudy.DumpStudy(CASE_DIR, "Lab3-final-dump", True, False)

print("LAB3_SALOME_EXPORT_OK")
print("nodes=", nodes)
print("hexas=", hexas)
for name in group_names:
    print("group_%s=%d" % (name, groups[name].Size()))
print("unv=", unv_path, os.path.getsize(unv_path))
print("hdf=", hdf_path, os.path.getsize(hdf_path))
print("dump=", dump_path, dump_ok, os.path.getsize(dump_path))

