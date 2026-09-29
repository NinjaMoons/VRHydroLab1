#!/usr/bin/env python3

"""Finalize and archive one already running LR7 job without restarting it."""

import gzip
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

job = Path(sys.argv[1]).resolve()
evidence = Path(sys.argv[2]).resolve()
case = job / "case"
status_path = job / "status.json"
fast_finish = Path(__file__).resolve().parents[1]
pvpython = Path("/home/pavel/openfoam-lab/tools/ParaView-6.1.1-MPI-Linux-Python3.12-x86_64/bin/pvpython")
postprocess = fast_finish / "LR8" / "postprocess_nozzle.py"

while True:
    state = json.loads(status_path.read_text(encoding="utf-8"))
    if state.get("state") in {"done", "failed"}:
        break
    time.sleep(10)

if state.get("state") != "done":
    raise RuntimeError("LR7 job failed: " + str(state.get("error", "unknown error")))
if not (case / "log.foamRun").read_text(errors="replace").rstrip().endswith("End"):
    raise RuntimeError("LR7 solver log does not end with End")

result_dir = job / "result"
if not (result_dir / "pressure.png").exists():
    (case / "nozzle.foam").touch()
    with (job / "log.postprocess").open("w", encoding="utf-8") as log:
        completed = subprocess.run(
            [str(pvpython), str(postprocess), str(case / "nozzle.foam"), str(result_dir)],
            env={**os.environ, "LIBGL_ALWAYS_SOFTWARE": "1"},
            stdout=log, stderr=subprocess.STDOUT,
        )
    if completed.returncode:
        raise RuntimeError("LR7 ParaView post-processing failed")
shutil.copyfile(result_dir / "pressure.png", job / "result.png")

state.update({"state": "done", "result": str(job / "result.png"), "resultTime": 0.015})
status_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

evidence.mkdir(parents=True, exist_ok=True)
for name in ("params.json", "analytic.json", "status.json", "log.postprocess", "result.png"):
    shutil.copy2(job / name, evidence / name)
for name in ("log.blockMesh", "log.checkMesh", "log.setFields"):
    shutil.copy2(case / name, evidence / name)
with (case / "log.foamRun").open("rb") as source, gzip.open(evidence / "log.foamRun.gz", "wb", compresslevel=6) as target:
    shutil.copyfileobj(source, target)
(evidence / "case_evidence").mkdir(exist_ok=True)
for name in ("0", "0.015", "constant", "system"):
    source = case / name
    if source.exists():
        shutil.copytree(source, evidence / "case_evidence" / name, dirs_exist_ok=True)

print("LR7_FINALIZE_OK")
print("evidence=", evidence)
