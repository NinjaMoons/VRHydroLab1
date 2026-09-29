# Листинги для основной части

Полные исходные файлы следует поместить в приложения. В основной части достаточно следующих пяти коротких фрагментов.

## Листинг 1 — Baseline-настройки варианта № 3

**Source file:** `settings.json`, строки 1–25.

**Почему выбран:** показывает единый набор геометрии, свойств воды и сетки.

```json
"geometryMm": { "L": 326.0, "H": 23.0, "a": 12.0,
  "P": 60.0, "S": 30.0, "Y": 8.0, "R": 60.0 },
"flow": { "Uin": 0.1, "nu": 1.006e-6,
  "rho": 998.2, "turbulenceModel": "kOmegaSST" }
```

## Листинг 2 — Расчёт центров препятствий

**Source file:** `scripts/geometry.py`, строки 23–39.

**Почему выбран:** связывает размеры официальной схемы с реальной геометрией.

```python
last_upper = L - R
upper_x = [last_upper - multiplier * P for multiplier in (3, 2, 1, 0)]
lower_x = [value + S for value in upper_x[:3]]
```

## Листинг 3 — Передача Uin в поле скорости

**Source file:** `scripts/parameterize_case.py`, строки 38–44.

**Почему выбран:** показывает, что скорость из интерфейса действительно попадает в `0/U`.

```python
velocity = float(flow["Uin"])
replace_all(
    case / "0" / "U",
    rf"uniform\s+\({NUMBER}\s+0\s+0\);",
    f"uniform ({velocity:.12g} 0 0);",
    minimum=2,
)
```

## Листинг 4 — Последовательный запуск расчёта

**Source file:** `scripts/run_pipeline.py`, строки 135–150.

**Почему выбран:** кратко показывает SIMPLE-инициализацию и PIMPLE-продолжение без MPI.

```python
self.command("solver_steady", ["foamRun", "-solver", "incompressibleFluid"], self.case, openfoam=True)
shutil.copy2(PROJECT / "openfoam" / "transient" / "system" / "controlDict",
             self.case / "system" / "controlDict")
transient = self.command("solver_transient",
    ["foamRun", "-solver", "incompressibleFluid"], self.case, openfoam=True)
```

## Листинг 5 — Автоматическая визуализация ParaView

**Source file:** `postprocessing/render_results.py`, строки 96–114.

**Почему выбран:** показывает формирование двух основных полей для отчёта.

```python
ColorBy(display, ("POINTS", "U", "Magnitude"))
display.RescaleTransferFunctionToDataRange(True, False)
SaveScreenshot(os.path.join(output_dir, "velocity.png"), view)

ColorBy(display, ("POINTS", "p_Pa"))
display.RescaleTransferFunctionToDataRange(True, False)
SaveScreenshot(os.path.join(output_dir, "pressure.png"), view)
```
