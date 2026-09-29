# SCREENSHOT CHECKLIST

Обновлено: 2026-09-13 18:30 MSK. Отмечать `[x]` только после сохранения постоянного файла изображения или вставки в отчёт. Скриншоты получены из реальных cases и встроены в `FINAL_REPORT_LR2.md` … `FINAL_REPORT_LR8.md`.

## Minimal manual capture order

Все расчётные, браузерные и два объединённых SALOME-кадра готовы и проверены. Оставшихся ручных screenshots нет.

## LR2 — Cavity

- [x] LR: LR2; Figure: базовая сетка; Case: `fast_finish_2026/LR2/cavityBase`; Time: 1; Field: Solid Color; Filter: none; Camera/view: +Z, XY; What must be visible: равномерная сетка 20×20, все границы области; Caption: «Равномерная расчётная сетка 20×20×1»; Why required: подтверждает дискретизацию базового случая. File: `screenshots/LR2/base_mesh.png`.
- [x] LR: LR2; Figure: давление; Case: `cavityBase`; Time: 1; Field: p; Filter: Cell Data to Point Data; Camera/view: +Z; What must be visible: legend, минимум слева сверху и максимум справа сверху; Caption: «Распределение кинематического давления в полости при t=1 s»; Why required: показывает действие движущейся крышки. File: `screenshots/LR2/base_pressure.png`.
- [x] LR: LR2; Figure: изобары; Case: `cavityBase`; Time: 1; Field: p; Filter: Slice + Contour, 10 levels; Camera/view: +Z; What must be visible: ровно 10 уровней и legend; Caption: «Контуры давления при t=1 s»; Why required: обязательная контурная постобработка. File: `screenshots/LR2/base_pressure_contours.png`.
- [x] LR: LR2; Figure: векторы скорости; Case: `cavityBase`; Time: 1; Field: U; Filter: Glyph; Camera/view: +Z; What must be visible: arrows, scale factor 0.005, legend; Caption: «Векторное поле скорости в полости»; Why required: показывает основной вихрь. File: `screenshots/LR2/base_velocity_glyphs.png`.
- [x] LR: LR2; Figure: линии тока; Case: `cavityBase`; Time: 1; Field: U; Filter: Stream Tracer + Tube; Camera/view: +Z; What must be visible: замкнутая циркуляция по часовой стрелке; Caption: «Линии тока в полости»; Why required: визуализация структуры течения. File: `screenshots/LR2/base_streamlines.png`.
- [x] LR: LR2; Figure: профиль Ux; Case: base + fine; Time: 1; Field: Ux; Filter: Plot Over Line; Camera/view: chart; What must be visible: обе серии вдоль x=0.05, y=0…0.1; Caption: «Сравнение профиля Ux для сеток 20×20 и 40×40»; Why required: исследование сеточной сходимости. Files: `screenshots/LR2/ux_profile_coarse_fine.csv`, `ux_profile_coarse_fine.png`.
- [x] LR: LR2; Figure: утончённая сетка; Case: `fast_finish_2026/LR2/cavityFine`; Time: 1; Field: Solid Color; Filter: none; Camera/view: +Z; What must be visible: 40×40 cells; Caption: «Уточнённая сетка 40×40×1»; Why required: раздел refinement. File: `screenshots/LR2/fine_mesh.png`.
- [x] LR: LR2; Figure: сгущённая сетка; Case: `fast_finish_2026/LR2/cavityGrade`; Time: 0.8; Field: Solid Color; Filter: none; Camera/view: +Z, Surface With Edges; What must be visible: четыре блока и сгущение к стенкам; Caption: «Сетка со сгущением к стенкам полости»; Why required: раздел grading. File: `screenshots/LR2/graded_mesh.png`.
- [x] LR: LR2; Figure: Re=100; Case: `fast_finish_2026/LR2/cavityHighRe`; Time: 2; Field: U; Filter: Stream Tracer + Tube; Camera/view: +Z; What must be visible: изменённая структура вихря; Caption: «Поле скорости при Re=100»; Why required: влияние числа Рейнольдса. Files: `screenshots/LR2/highRe_velocity.png`, `highRe_streamlines.png`.
- [x] LR: LR2; Figure: RAS; Case: `fast_finish_2026/LR2/cavityRAS`; Time: 20; Field: p and U; Filter: surface; Camera/view: +Z; What must be visible: legend and whole cavity; Caption: «Результат RAS k–epsilon при Re=10000»; Why required: turbulent/high-Re section. Files: `screenshots/LR2/ras_pressure.png`, `ras_velocity.png`.
- [x] LR: LR2; Figure: clipped geometry; Case: `fast_finish_2026/LR2/cavityClipped`; Time: 0.5 and 0.6; Field: U; Filter: surface; Camera/view: +Z; What must be visible: вырез 0.04×0.04 m в правом нижнем углу and comparison; Caption: «Поле скорости в изменённой геометрии cavityClipped»; Why required: geometry mapping/postprocessing section. Files: `screenshots/LR2/clipped_t0_5.png`, `clipped_t0_6.png`.

## LR3 — Dam break / SALOME

- [x] MANUAL 1/2; LR: LR3; Figure: combined SALOME preprocessing evidence; Study: `fast_finish_2026/LR3/damBreakLaminar/Lab3-final.hdf`; Field: n/a; Module: Mesh; Camera/view: axonometric + Fit All; What is visible in one frame: structured damBreak mesh, expanded `Mesh_1` tree with `leftWall`, `rightWall`, `lowerWall`, `atmosphere`, `frontAndBack`, and Mesh Information with 4222 nodes / 2016 hexahedra; Caption: «Структурированная сетка damBreak и группы граничных поверхностей в SALOME»; Why required: combines geometry/mesh/group proof in the minimum one screenshot. Verified file: `screenshots/LR3/salome_mesh_groups.png` (PNG, 1335×610, 166335 bytes; visually checked 2026-09-13).

  Точные GUI-действия для MANUAL 1/2:

  1. В SALOME выбрать `File → Open` и открыть `/media/sf_OpenFOAM_Labs/fast_finish_2026/LR3/damBreakLaminar/Lab3-final.hdf`.
  2. В выпадающем списке модулей выбрать `Mesh`.
  3. В Object Browser раскрыть `Mesh_1`, затем убедиться, что одновременно видны группы `leftWall`, `rightWall`, `lowerWall`, `atmosphere`, `frontAndBack`.
  4. Выделить `Mesh_1`, включить его отображение (`Show`), выбрать фронтальный вид вдоль оси OZ и нажать `Fit All`, чтобы вся область с перегородкой помещалась в окне.
  5. Щёлкнуть правой кнопкой по `Mesh_1` → `Mesh Information`; оставить открытой вкладку/секцию, где одновременно читаются `Nodes: 4222` и `Hexahedrons/Hexahedra: 2016`.
  6. Сдвинуть окно Mesh Information вправо, не закрывая дерево групп и не перекрывая сетку. Сделать один снимок всего окна SALOME без терминала и посторонних окон.
  7. Сохранить PNG как `/media/sf_OpenFOAM_Labs/screenshots/LR3/salome_mesh_groups.png` или прикрепить снимок в чат для проверки.
- [x] LR: LR3; Figure: initial phase; Case: final imported case; Time: 0; Field: alpha.water; Filter: surface; Camera/view: front; What must be visible: initial water block; Caption: «Начальное распределение фазы воды»; Why required: verifies setFields. File: `screenshots/LR3/alpha_water_t0.png`.
- [x] LR: LR3; Figure: transient sequence; Case: final imported case; Time: approximately 0.25, 0.5, 0.65, 0.85; Field: alpha.water; Filter: contour/surface; Camera/view: front; What must be visible: advancing/collapsing water front; Caption: «Эволюция свободной поверхности»; Why required: solver result. Files: `screenshots/LR3/alpha_water_t0_25.png` … `alpha_water_t0_85.png`.
- [x] LR: LR3; Figure: alternative initialization; Case: second setFields variant; Time: 0 and selected later times; Field: alpha.water; Filter: surface; Camera/view: front; What must be visible: modified blocks and their evolution; Caption: «Расчёт с изменённым начальным распределением»; Why required: additional method assignment. Files: `screenshots/LR3/centerBox/` and `screenshots/LR3/sphere/`.

## LR4 — Flow over cylinder

- [x] LR: LR4; Figure: mesh; Case: `fast_finish_2026/LR4/Re_41`; Time: 0; Field: Solid Color; Filter: none; Camera/view: along thickness axis, zoom at cylinder; What must be visible: six blocks, circular cylinder and wake refinement; Caption: «Шестиблочная сетка вокруг цилиндра»; Why required: geometry/mesh validation. File: `screenshots/LR4/Re_41_mesh.png`.
- [x] LR: LR4; Figure: Re=41 velocity; Case: `Re_41`; Time: 100; Field: U or U_X; Filter: surface; Camera/view: whole domain; What must be visible: steady symmetric recirculation; Caption: «Поле скорости при Re=41»; Why required: first calculation. File: `screenshots/LR4/Re_41_velocity.png`.
- [x] LR: LR4; Figure: Re=41 streamlines; Case: `Re_41`; Time: 100; Field: U; Filter: Stream Tracer; Camera/view: wake behind cylinder; What must be visible: two symmetric attached vortices; Caption: «Линии тока при Re=41»; Why required: flow structure. File: `screenshots/LR4/Re_41_streamlines.png`.
- [x] LR: LR4; Figure: Re=140; Case: `Re_140`; Time: 100 (or verified final); Field: U; Filter: surface + streamlines; Camera/view: cylinder and wake; What must be visible: asymmetric/unsteady vortex street; Caption: «Поле скорости и вихревой след при Re=140»; Why required: Reynolds-number comparison. Files: `screenshots/LR4/Re_140_velocity.png`, `Re_140_streamlines.png`.

## LR5 — Natural convection

- [x] LR: LR5; Figure: mesh; Case: final buoyantCavity; Time: 0; Field: Solid Color; Filter: Surface With Edges; Camera/view: front; What must be visible: square cavity mesh; Caption: «Расчётная сетка полости»; Why required: preprocessing. File: `screenshots/LR5/mesh.png`.
- [x] LR: LR5; Figure: temperature; Case: final buoyantCavity; Time: final; Field: T; Filter: surface/contour; Camera/view: front; What must be visible: 305 K hot side, 295 K cold side, thermal plume/gradient and legend; Caption: «Распределение температуры при естественной конвекции»; Why required: primary result. File: `screenshots/LR5/temperature.png`.
- [x] LR: LR5; Figure: velocity; Case: same; Time: final; Field: U; Filter: Glyph/Stream Tracer; Camera/view: front; What must be visible: buoyancy-driven circulation; Caption: «Поле скорости естественной конвекции»; Why required: physical interpretation. File: `screenshots/LR5/velocity_streamlines.png`.
- [x] LR: LR5; Figure: web form; Case: LR5 app; Time: n/a; Field: n/a; Filter: browser; Camera/view: full page; What must be visible: hot/cold temperature inputs and calculation result/status; Caption: «Веб-интерфейс управления расчётом»; Why required: application section. File: `screenshots/LR5/web_form.png`.

## LR6 — Laval nozzle

- [x] MANUAL 2/2; LR: LR6; Figure: combined SALOME preprocessing evidence; Study: `fast_finish_2026/LR6/LR6-nozzle.hdf`; Field: n/a; Module: Mesh; Camera/view: longitudinal SALOME view; What is visible in one frame: nozzle mesh, expanded `Nozzle_mesh` group tree with `inlet`, `outlet`, `axis`, `wall`, `frontAndBack`, and Mesh Information with 16482 nodes / 8000 hexahedra; Caption: «Параметрическая сетка сопла Лаваля и группы граничных поверхностей в SALOME»; Why required: combines profile/mesh/group proof in the minimum one screenshot. Verified file: `screenshots/LR6/salome_nozzle_mesh_groups.png` (PNG, 1338×660, 145454 bytes; visually checked 2026-09-13).
- [x] LR: LR6; Figure: CFD fields; Case: `fast_finish_2026/LR6/nozzleShockFluidFresh`; Time: 0.015; Field: p, T, U, Mach; Filter: Cell Data to Point Data + Calculator; Camera/view: longitudinal section; What must be visible: pressure/temperature drop and acceleration through throat; Caption: «Распределения p, T и U в сопле Лаваля»; Why required: solver result. Files: `screenshots/LR8/pressure.png`, `temperature.png`, `velocity.png`, `mach.png`.

## LR7 — Nozzle web application

- [x] LR: LR7; Figure: main form; Case: LR7 app; Time: n/a; Field: n/a; Filter: browser; Camera/view: full page; What must be visible: six required inputs; Caption: «Главная форма ввода параметров сопла»; Why required: UI requirement. File: `screenshots/LR7/web_form.png`.
- [x] LR: LR7; Figure: result/progress; Case: job `2026-09-13T01-50-54-310Z`; Time: live; Field: n/a; Filter: browser; Camera/view: full page; What must be visible: submitted parameters, Mesh OK, solver time and percent; Caption: «Форма выполнения расчёта»; Why required: workflow integration. File: `screenshots/LR7/web_progress.png`.
- [x] LR: LR7; Figure: completion/result; Case: job `2026-09-13T01-50-54-310Z`; Time: 0.015; Field: real LR6 pressure; Filter: browser result view; Camera/view: full page; What must be visible: `Mesh OK`, solver `End`, 100%, real ParaView pressure image and log; Caption: «Результат автоматизированного расчёта»; Why required: end-to-end proof. File: `screenshots/LR7/web_complete.png`.

## LR8 — ParaView postprocessing

- [x] LR: LR8; Figure: processed nozzle view/animation; Case: `nozzleShockFluidFresh`; Time: 0.0005–0.015; Field: U/T/p/Mach; Filter: Cell Data to Point Data + Calculator; Camera/view: longitudinal, white background; What must be visible: real changing solution and legends; Caption: «Постобработка результатов сопла»; Why required: animation workflow. Files: `screenshots/LR8/mesh.png`, `pressure.png`, `temperature.png`, `velocity.png`, `mach.png`, `pressure_evolution.gif` (30 frames, 1000×333).
- [x] LR: LR8; Figure: U and T plots; Case: `nozzleShockFluidFresh`; Time: 0.015; Field: |U|, T; Filter: Plot Over Line; Camera/view: chart; What must be visible: distance axis and both series; Caption: «Распределение скорости и температуры по длине сопла»; Why required: assignment. File: `screenshots/LR8/velocity_temperature_plot.png`.
- [x] LR: LR8; Figure: p plot; Case: `nozzleShockFluidFresh`; Time: 0.015; Field: p, Mach; Filter: Plot Over Line; Camera/view: chart; What must be visible: pressure curve and critical section; Caption: «Распределение давления по длине сопла»; Why required: assignment. File: `screenshots/LR8/pressure_mach_plot.png`.
- [x] LR: LR8; Figure: comparison table; Case: report; Time: 0.015; Field: p/T/U/Mach; Filter: n/a; Camera/view: table; What must be visible: inlet/throat/outlet CFD vs analytical values; Caption: «Сравнение численного и аналитического расчётов»; Why required: final method requirement. File: `screenshots/LR8/section_comparison.csv`; formatted table is in `FINAL_REPORT_LR8.md`.
