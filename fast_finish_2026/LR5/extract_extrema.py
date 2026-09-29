#!/usr/bin/env pvpython

"""Read min/max T and velocity magnitude from an existing OpenFOAM result."""

import os
import sys

from paraview import servermanager
from paraview.simple import MergeBlocks, OpenFOAMReader, ResetSession


case_file = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "buoyantCavity.foam")

ResetSession()
reader = OpenFOAMReader(registrationName="LR5 buoyant cavity", FileName=case_file)
reader.MeshRegions = ["internalMesh"]
reader.CellArrays = ["U", "T"]
reader.UpdatePipeline()

times = list(reader.TimestepValues or [])
if not times:
    raise RuntimeError("No result times found")

final_time = max(times)
reader.UpdatePipeline(final_time)
merged = MergeBlocks(registrationName="Merged internal mesh", Input=reader)
merged.UpdatePipeline(final_time)
data = servermanager.Fetch(merged)

temperature = data.GetCellData().GetArray("T")
velocity = data.GetCellData().GetArray("U")
if temperature is None or velocity is None:
    raise RuntimeError("Required cell arrays T and U were not read")

print("LR5_EXTREMA_OK")
print("case=", case_file)
print("available_times=", times)
print("final_time=", final_time)
print("cells=", data.GetNumberOfCells())
print("T_range_K=", temperature.GetRange())
print("U_magnitude_range_m_s=", velocity.GetRange(-1))
