#!/usr/bin/env python3

"""Parameterize and run an isolated copy of the verified LR6 nozzle case."""

import importlib.util
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

job = Path(sys.argv[1]).resolve()
root = Path(__file__).resolve().parents[2]
template = root / "LR6" / "nozzleShockFluidFresh"
calc_path = root / "LR6" / "calc_nozzle.py"
postprocess_path = root / "LR8" / "postprocess_nozzle.py"
params = json.loads((job / "params.json").read_text(encoding="utf-8"))
case = job / "case"
status_file = job / "status.json"

spec = importlib.util.spec_from_file_location("calc_nozzle", calc_path)
calc_module = importlib.util.module_from_spec(spec); spec.loader.exec_module(calc_module)

def status(state, **extra): status_file.write_text(json.dumps({"state": state, "job": job.name, **extra}, ensure_ascii=False, indent=2), encoding="utf-8")
def ignore_generated(directory, names):
    ignored = {n for n in names if n.startswith(("log.", "processor")) or n.endswith((".foam", ".orig")) or n in {"core", "postProcessing"}}
    ignored.update(n for n in names if n != "0" and re.fullmatch(r"\d+(?:\.\d+)?", n))
    if Path(directory).name == "constant" and "polyMesh" in names: ignored.add("polyMesh")
    return ignored
def replace_one(text, pattern, replacement, label, flags=0):
    value, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    if count != 1: raise RuntimeError("Не удалось обновить " + label)
    return value

try:
    status("preparing")
    data = calc_module.calculate(params["pInput"], params["tInput"], params["pOutput"], params["massFlow"], params["alpha"], params["beta"])
    shutil.copytree(template, case, ignore=ignore_generated)
    (job / "analytic.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    x0 = -data["geometry"]["length_convergent_m"]; x2 = data["geometry"]["length_divergent_m"]
    r0 = data["inlet"]["diameter_m"] / 2; rt = data["throat"]["diameter_m"] / 2; r2 = data["outlet"]["diameter_m"] / 2; z = 0.002
    vertices = f"""vertices
(
    ({x0:.9g} 0 {-z:g}) (0 0 {-z:g}) ({x2:.9g} 0 {-z:g})
    ({x0:.9g} {r0:.9g} {-z:g}) (0 {rt:.9g} {-z:g}) ({x2:.9g} {r2:.9g} {-z:g})
    ({x0:.9g} 0 {z:g}) (0 0 {z:g}) ({x2:.9g} 0 {z:g})
    ({x0:.9g} {r0:.9g} {z:g}) (0 {rt:.9g} {z:g}) ({x2:.9g} {r2:.9g} {z:g})
);"""
    mesh_path = case / "system" / "blockMeshDict"; mesh_text = mesh_path.read_text(); mesh_text = replace_one(mesh_text, r"vertices\s*\(.*?\n\);", vertices, "vertices", re.S); mesh_path.write_text(mesh_text)
    header = "FoamFile { format ascii; class %s; location \"0\"; object %s; }\n"
    patches = """axis { type symmetryPlane; }
    wall { type %s; }
    frontAndBack { type empty; }"""
    (case / "0" / "U").write_text((header % ("volVectorField", "U")) + """
dimensions [0 1 -1 0 0 0 0];
internalField uniform (0 0 0);
boundaryField {
    inlet { type zeroGradient; }
    outlet { type zeroGradient; }
    %s
}
""" % (patches % "slip"))
    (case / "0" / "T").write_text((header % ("volScalarField", "T")) + f"""
dimensions [0 0 0 1 0 0 0];
internalField uniform {params['tInput']:.9g};
boundaryField {{
    inlet {{ type fixedValue; value uniform {params['tInput']:.9g}; }}
    outlet {{ type zeroGradient; }}
    {patches % "zeroGradient"}
}}
""")
    (case / "0" / "p").write_text((header % ("volScalarField", "p")) + f"""
dimensions [1 -1 -2 0 0 0 0];
internalField uniform {params['pOutput']:.9g};
boundaryField {{
    inlet {{ type fixedValue; value uniform {params['pInput']:.9g}; }}
    outlet {{ type zeroGradient; }}
    {patches % "zeroGradient"}
}}
""")
    sf = case / "system" / "setFieldsDict"; txt = sf.read_text(); txt = replace_one(txt, r"(defaultValues\s*\{.*?T\s+)[^;]+;", rf"\g<1>{params['tInput']:.9g};", "setFields default T", re.S); txt = replace_one(txt, r"(defaultValues\s*\{.*?p\s+)[^;]+;", rf"\g<1>{params['pOutput']:.9g};", "setFields default p", re.S); txt = replace_one(txt, r"(values\s*\{.*?p\s+)[^;]+;", rf"\g<1>{params['pInput']:.9g};", "setFields inlet p", re.S); sf.write_text(txt)
    shim = Path(__file__).resolve().parent / "bin"
    status("meshing", case=str(case), analytic=str(job / "analytic.json"))
    commands = "blockMesh > log.blockMesh 2>&1 && checkMesh -allGeometry -allTopology > log.checkMesh 2>&1 && setFields > log.setFields 2>&1"
    prepare_only = os.environ.get("LR7_PREPARE_ONLY") == "1"
    if not prepare_only:
        commands += " && foamRun > log.foamRun 2>&1"
    shell = f"export PATH={shlex.quote(str(shim))}:$PATH; source /home/pavel/openfoam-lab/of-root/activate-of13.sh >/dev/null 2>&1; cd {shlex.quote(str(case))}; {commands}"
    completed = subprocess.run(["/bin/bash", "-lc", shell], check=False)
    mesh_log = (case / "log.checkMesh").read_text(errors="replace") if (case / "log.checkMesh").exists() else ""
    run_log = (case / "log.foamRun").read_text(errors="replace") if (case / "log.foamRun").exists() else ""
    if completed.returncode or "Mesh OK." not in mesh_log: raise RuntimeError("OpenFOAM не подтвердил Mesh OK")
    if prepare_only:
        status("prepared", case=str(case), analytic=str(job / "analytic.json"))
    else:
        if not run_log.rstrip().endswith("End"): raise RuntimeError("OpenFOAM solver не завершился строкой End")
        (case / "nozzle.foam").touch()
        status("postprocessing", case=str(case), analytic=str(job / "analytic.json"), resultTime=0.015)
        result_dir = job / "result"
        pvpython = Path("/home/pavel/openfoam-lab/tools/ParaView-6.1.1-MPI-Linux-Python3.12-x86_64/bin/pvpython")
        with (job / "log.postprocess").open("w", encoding="utf-8") as log:
            post = subprocess.run([str(pvpython), str(postprocess_path), str(case / "nozzle.foam"), str(result_dir)],
                                  env={**os.environ, "LIBGL_ALWAYS_SOFTWARE": "1"}, stdout=log, stderr=subprocess.STDOUT)
        if post.returncode or not (result_dir / "pressure.png").exists():
            raise RuntimeError("ParaView post-processing не создал pressure.png")
        shutil.copyfile(result_dir / "pressure.png", job / "result.png")
        status("done", case=str(case), analytic=str(job / "analytic.json"), result=str(job / "result.png"), resultTime=0.015)
except Exception as error:
    status("failed", error=str(error), case=str(case)); raise
