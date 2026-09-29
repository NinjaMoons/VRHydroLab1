#!/usr/bin/env python3

"""Create an isolated LR5 case, apply validated parameters and run OpenFOAM."""

import json
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


job_dir = Path(sys.argv[1]).resolve()
side = float(sys.argv[2])
cold = float(sys.argv[3])
hot = float(sys.argv[4])
template = Path(__file__).resolve().parent.parent / "buoyantCavity"
case = job_dir / "case"
status_path = job_dir / "status.json"


def status(state, **extra):
    payload = {"state": state, "job": job_dir.name, **extra}
    status_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def ignore_generated(directory, names):
    ignored = {name for name in names if name.startswith("log.") or name.endswith(".foam")}
    ignored.update(
        name for name in names
        if name != "0" and re.fullmatch(r"\d+(?:\.\d+)?", name)
    )
    if Path(directory).name == "constant" and "polyMesh" in names:
        ignored.add("polyMesh")
    ignored.update({"validation", "Allrun", "Allclean", "README"} & set(names))
    return ignored


try:
    status("preparing")
    shutil.copytree(template, case, ignore=ignore_generated)

    half_depth = 5.0
    vertices = f"""vertices
(
    (0 0 -{half_depth:g})
    ({side:g} 0 -{half_depth:g})
    ({side:g} {side:g} -{half_depth:g})
    (0 {side:g} -{half_depth:g})
    (0 0 {half_depth:g})
    ({side:g} 0 {half_depth:g})
    ({side:g} {side:g} {half_depth:g})
    (0 {side:g} {half_depth:g})
);"""
    mesh_path = case / "system" / "blockMeshDict"
    mesh_text = mesh_path.read_text(encoding="utf-8")
    mesh_text, count = re.subn(r"vertices\s*\(.*?\n\);", vertices, mesh_text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError("Не найден блок vertices в blockMeshDict")
    nxy = max(10, round(side / 2.5))
    mesh_text, count = re.subn(
        r"(hex\s*\([^\n]+\)\s*)\([^\n]+\)(\s*simpleGrading)",
        rf"\1({nxy} {nxy} 5)\2", mesh_text, count=1,
    )
    if count != 1:
        raise RuntimeError("Не найден размер cells в blockMeshDict")
    mesh_path.write_text(mesh_text, encoding="utf-8")

    t_path = case / "0" / "T"
    t_text = t_path.read_text(encoding="utf-8")
    mean = 0.5 * (hot + cold)
    t_text, count0 = re.subn(r"internalField\s+uniform\s+[^;]+;", f"internalField   uniform {mean:g};", t_text, count=1)
    t_text, count1 = re.subn(r"(hot\s*\{.*?value\s+uniform\s+)[^;]+;", rf"\g<1>{hot:g};", t_text, count=1, flags=re.S)
    t_text, count2 = re.subn(r"(cold\s*\{.*?value\s+uniform\s+)[^;]+;", rf"\g<1>{cold:g};", t_text, count=1, flags=re.S)
    if (count0, count1, count2) != (1, 1, 1):
        raise RuntimeError("Не удалось однозначно обновить поле T")
    t_path.write_text(t_text, encoding="utf-8")

    status("meshing", case=str(case))
    shim_dir = Path(__file__).resolve().parent / "bin"
    shell = (
        f"export PATH={shlex.quote(str(shim_dir))}:$PATH; "
        "source /home/pavel/openfoam-lab/of-root/activate-of13.sh; "
        f"cd {shlex.quote(str(case))}; "
        "blockMesh > log.blockMesh 2>&1; "
        "checkMesh -allGeometry -allTopology > log.checkMesh 2>&1; "
        "foamRun > log.foamRun 2>&1"
    )
    completed = subprocess.run(["/bin/bash", "-lc", shell], check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"OpenFOAM завершился с кодом {completed.returncode}")
    solver_log = (case / "log.foamRun").read_text(encoding="utf-8", errors="replace")
    mesh_log = (case / "log.checkMesh").read_text(encoding="utf-8", errors="replace")
    if "Mesh OK." not in mesh_log or not solver_log.rstrip().endswith("End"):
        raise RuntimeError("Расчёт завершён без подтверждающих маркеров Mesh OK/End")
    (case / "buoyantCavity.foam").touch()
    status("done", case=str(case), resultTime=500)
except Exception as error:
    status("failed", error=str(error), case=str(case))
    raise
