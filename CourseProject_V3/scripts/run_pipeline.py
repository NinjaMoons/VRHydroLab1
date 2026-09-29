#!/usr/bin/env python3

"""Run the Variant 3 pipeline sequentially in /tmp and persist verified artifacts."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
OPENFOAM_ROOT = Path("/home/pavel/openfoam-lab/of-root")
SALOME = Path("/home/pavel/openfoam-lab/tools/SALOME-9.16.0/run_salome.sh")
PVPYTHON = Path(
    "/home/pavel/openfoam-lab/tools/ParaView-6.1.1-MPI-Linux-Python3.12-x86_64/bin/pvpython"
)
TEMP_ROOT = Path("/tmp/CourseProject_V3/jobs")


def write_json(path: Path, value: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


class Pipeline:
    def __init__(self, run_dir: Path, stop_after: str | None = None):
        self.run_dir = run_dir.resolve()
        self.run_id = self.run_dir.name
        self.settings = self.run_dir / "settings.json"
        self.temp = TEMP_ROOT / self.run_id
        self.mesh = self.temp / "mesh"
        self.case = self.temp / "case"
        self.images = self.temp / "screenshots"
        self.logs = self.temp / "logs"
        self.pipeline_log = self.run_dir / "logs" / "pipeline.log"
        self.stop_after = stop_after
        self.current_stage_key = "validate"
        (self.run_dir / "logs").mkdir(parents=True, exist_ok=True)

    def status(self, state: str, stage: str, stage_key: str, **extra) -> None:
        self.current_stage_key = stage_key
        payload = {
            "state": state,
            "stage": stage,
            "stageKey": stage_key,
            "runId": self.run_id,
            "updatedAt": datetime.now(timezone.utc).isoformat(),
        }
        payload.update(extra)
        write_json(self.run_dir / "status.json", payload)

    def note(self, message: str) -> None:
        with self.pipeline_log.open("a", encoding="utf-8") as stream:
            stream.write(message.rstrip() + "\n")

    def command(self, name: str, args: list[str], cwd: Path, env: dict | None = None, openfoam: bool = False) -> Path:
        log = self.logs / f"{name}.log"
        if openfoam:
            invocation = [
                "/bin/bash",
                "-lc",
                'export LD_LIBRARY_PATH="$1/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}"; '
                'source "$1/opt/openfoam13/etc/bashrc" ParaView_TYPE=none >/dev/null 2>&1; '
                'shift; exec "$@"',
                "cpv3-openfoam",
                str(OPENFOAM_ROOT),
                *args,
            ]
        else:
            invocation = args
        self.note(f"[{name}] cwd={cwd} command={' '.join(args)}")
        with log.open("w", encoding="utf-8") as output:
            completed = subprocess.run(
                invocation,
                cwd=cwd,
                env=env,
                stdout=output,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
            )
        if completed.returncode != 0:
            tail = log.read_text(encoding="utf-8", errors="replace")[-4000:]
            raise RuntimeError(f"{name} returned {completed.returncode}\n{tail}")
        return log

    def prepare(self) -> None:
        if self.temp.exists():
            shutil.rmtree(self.temp)
        self.mesh.mkdir(parents=True)
        self.images.mkdir()
        self.logs.mkdir()
        shutil.copytree(PROJECT / "openfoam" / "template", self.case)
        shutil.copy2(self.settings, self.case / "settings.json")

    def generate_mesh(self) -> None:
        environment = os.environ.copy()
        environment.update({
            "CPV3_SETTINGS": str(self.settings),
            "CPV3_OUTPUT_DIR": str(self.mesh),
        })
        self.command(
            "salome",
            [str(SALOME), "-t", str(PROJECT / "salome" / "generate_mesh.py")],
            PROJECT,
            env=environment,
        )
        for expected in ("Mesh.unv", "CourseProject_V3.hdf", "mesh_summary.json"):
            if not (self.mesh / expected).is_file():
                raise RuntimeError(f"SALOME did not create {expected}")

    def import_mesh(self) -> None:
        self.command("ideasUnvToFoam", ["ideasUnvToFoam", str(self.mesh / "Mesh.unv")], self.case, openfoam=True)
        self.command("transformPoints", ["transformPoints", "scale=(0.001 0.001 0.001)"], self.case, openfoam=True)
        self.command(
            "setPatchTypes",
            [sys.executable, str(PROJECT / "scripts" / "set_patch_types.py"), str(self.case / "constant" / "polyMesh" / "boundary")],
            self.case,
        )
        check = self.command("checkMesh", ["checkMesh", "-allGeometry", "-allTopology"], self.case, openfoam=True)
        if "Mesh OK." not in check.read_text(encoding="utf-8", errors="replace"):
            raise RuntimeError("checkMesh did not report Mesh OK")

    def solve(self) -> None:
        self.status("running", "Подготовка OpenFOAM", "case", message="Обновляются U, k, omega и свойства жидкости")
        self.command(
            "parameterizeCase",
            [sys.executable, str(PROJECT / "scripts" / "parameterize_case.py"), str(self.case), str(self.settings)],
            self.case,
        )
        self.status("running", "Стационарная инициализация SIMPLE", "solver", message="Последовательный расчёт без MPI")
        self.command("solver_steady", ["foamRun", "-solver", "incompressibleFluid"], self.case, openfoam=True)
        shutil.copy2(PROJECT / "openfoam" / "transient" / "system" / "controlDict", self.case / "system" / "controlDict")
        shutil.copy2(PROJECT / "openfoam" / "transient" / "system" / "fvSchemes", self.case / "system" / "fvSchemes")
        shutil.copy2(PROJECT / "openfoam" / "transient" / "system" / "fvSolution", self.case / "system" / "fvSolution")
        self.status("running", "Нестационарное продолжение PIMPLE", "solver", message="Расчёт продолжается одну физическую секунду")
        transient = self.command("solver_transient", ["foamRun", "-solver", "incompressibleFluid"], self.case, openfoam=True)
        if not transient.read_text(encoding="utf-8", errors="replace").rstrip().endswith("End"):
            raise RuntimeError("Transient solver log does not end with End")

    def postprocess(self) -> None:
        functions = {
            "flow_inlet": "patchFlowRate(name=inlet,patch=inlet)",
            "flow_outlet": "patchFlowRate(name=outlet,patch=outlet)",
            "p_inlet": "patchAverage(name=pInlet,patch=inlet,field=p)",
            "p_outlet": "patchAverage(name=pOutlet,patch=outlet,field=p)",
            "u_max": "cellMaxMag(U)",
            "u_min": "cellMinMag(U)",
            "p_max": "cellMax(p)",
            "p_min": "cellMin(p)",
        }
        for name, expression in functions.items():
            self.command(name, ["foamPostProcess", "-latestTime", "-func", expression], self.case, openfoam=True)
        (self.case / "course_project.foam").touch()
        environment = os.environ.copy()
        environment["LIBGL_ALWAYS_SOFTWARE"] = "1"
        settings = json.loads(self.settings.read_text(encoding="utf-8"))
        self.command(
            "paraview",
            [str(PVPYTHON), str(PROJECT / "postprocessing" / "render_results.py"), str(self.case / "course_project.foam"), str(self.images), "--rho", str(settings["flow"]["rho"])],
            self.case,
            env=environment,
        )

    def persist(self) -> None:
        for name in ("case", "logs", "screenshots", "results"):
            (self.run_dir / name).mkdir(parents=True, exist_ok=True)
        shutil.copytree(self.case, self.run_dir / "case", dirs_exist_ok=True)
        shutil.copytree(self.logs, self.run_dir / "logs", dirs_exist_ok=True)
        shutil.copytree(self.images, self.run_dir / "screenshots", dirs_exist_ok=True)
        shutil.copy2(self.mesh / "Mesh.unv", self.run_dir / "Mesh.unv")
        shutil.copy2(self.mesh / "CourseProject_V3.hdf", self.run_dir / "CourseProject_V3.hdf")
        shutil.copy2(self.mesh / "mesh_summary.json", self.run_dir / "mesh_summary.json")
        aliases = {
            "solver_transient.log": "solver_transient.log",
            "checkMesh.log": "checkMesh.log",
        }
        for source, target in aliases.items():
            shutil.copy2(self.logs / source, self.run_dir / "logs" / target)
        self.command(
            "buildSummary",
            [sys.executable, str(PROJECT / "scripts" / "build_summary.py"), str(self.run_dir), "--mesh-summary", str(self.run_dir / "mesh_summary.json")],
            PROJECT,
        )
        shutil.copy2(self.logs / "buildSummary.log", self.run_dir / "logs" / "buildSummary.log")

    def persist_mesh(self) -> None:
        for name in ("case", "logs"):
            (self.run_dir / name).mkdir(parents=True, exist_ok=True)
        shutil.copytree(self.case, self.run_dir / "case", dirs_exist_ok=True)
        shutil.copytree(self.logs, self.run_dir / "logs", dirs_exist_ok=True)
        shutil.copy2(self.mesh / "Mesh.unv", self.run_dir / "Mesh.unv")
        shutil.copy2(self.mesh / "CourseProject_V3.hdf", self.run_dir / "CourseProject_V3.hdf")
        shutil.copy2(self.mesh / "mesh_summary.json", self.run_dir / "mesh_summary.json")

    def run(self) -> None:
        self.status("running", "Проверка параметров", "validate", message="Проверяются параметры варианта №3")
        self.prepare()
        self.command("geometry", [sys.executable, str(PROJECT / "scripts" / "geometry.py"), str(self.settings)], PROJECT)
        self.status("running", "Геометрия и сетка SALOME", "salome", message="SALOME строит область и однослойную сетку")
        self.generate_mesh()
        self.status("running", "Импорт и проверка сетки", "mesh", message="Сетка импортируется в OpenFOAM; выполняется checkMesh")
        self.import_mesh()
        if self.stop_after == "mesh":
            self.persist_mesh()
            self.status("done", "Сетка готова", "mesh", message="UNV экспортирован, импорт OpenFOAM и checkMesh завершены: Mesh OK")
            return
        self.solve()
        self.status("running", "Постобработка", "postprocess", message="Вычисляются расходы, экстремумы и изображения ParaView")
        self.postprocess()
        self.status("running", "Сохранение результата", "save", message="Расчётный случай, журналы и PNG сохраняются в run")
        self.persist()
        self.status("done", "Расчёт завершён", "complete", message="Mesh OK, solver End, summary и изображения готовы")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--stop-after", choices=("mesh",))
    args = parser.parse_args()
    pipeline = Pipeline(args.run_dir, args.stop_after)
    try:
        pipeline.run()
    except Exception as error:
        pipeline.note(traceback.format_exc())
        pipeline.status("failed", "Ошибка", pipeline.current_stage_key, message="Расчёт остановлен", error=str(error))
        raise


if __name__ == "__main__":
    main()
