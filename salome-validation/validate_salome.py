import os
import salome

salome.salome_init()
from salome.geom import geomBuilder
from salome.smesh import smeshBuilder
import GEOM
import SMESH

out_dir = os.path.dirname(os.path.abspath(__file__))
geompy = geomBuilder.New()
smesh = smeshBuilder.New()

# A small 3-D body is sufficient to exercise GEOM, SMESH, named boundaries,
# structured hexahedral meshing, study persistence, Python dump and UNV export.
box = geompy.MakeBoxDXDYDZ(1.0, 1.0, 0.1)
geompy.addToStudy(box, "ValidationBox")

faces = geompy.SubShapeAllSortedCentres(box, geompy.ShapeType["FACE"])
if len(faces) != 6:
    raise RuntimeError(f"Expected 6 box faces, got {len(faces)}")

boundary_names = ["boundary_%d" % (i + 1) for i in range(len(faces))]
geometry_groups = []
for face, name in zip(faces, boundary_names):
    group = geompy.CreateGroup(box, geompy.ShapeType["FACE"])
    geompy.UnionList(group, [face])
    geompy.addToStudyInFather(box, group, name)
    geometry_groups.append(group)

mesh = smesh.Mesh(box, "ValidationMesh")
mesh.Segment().NumberOfSegments(4)
mesh.Quadrangle()
mesh.Hexahedron()
if not mesh.Compute():
    raise RuntimeError("SMESH Compute() failed")

mesh_groups = []
for group, name in zip(geometry_groups, boundary_names):
    mesh_groups.append(mesh.GroupOnGeom(group, name, SMESH.FACE))

unv_path = os.path.join(out_dir, "ValidationMesh.unv")
hdf_path = os.path.join(out_dir, "ValidationStudy.hdf")
dump_path = os.path.join(out_dir, "ValidationDump.py")
mesh.ExportUNV(unv_path)
salome.myStudy.SaveAs(hdf_path, False, False)
dump_ok = salome.myStudy.DumpStudy(out_dir, "ValidationDump", True, False)

print("SALOME_VALIDATION_OK")
print("nodes=", mesh.NbNodes())
print("edges=", mesh.NbEdges())
print("faces=", mesh.NbFaces())
print("volumes=", mesh.NbVolumes())
print("groups=", [(g.GetName(), g.Size()) for g in mesh_groups])
print("unv=", unv_path, os.path.getsize(unv_path))
print("hdf=", hdf_path, os.path.getsize(hdf_path))
print("dump=", dump_path, dump_ok, os.path.getsize(dump_path))
