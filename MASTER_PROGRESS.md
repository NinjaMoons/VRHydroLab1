# MASTER PROGRESS

Последнее обновление: 2026-09-13 18:31 MSK.

Вычислительная контрольная точка: CFD и обязательные evidence для ЛР2–ЛР8 завершены; повторные solver/MPI/mesh jobs не требуются. Оба ручных SALOME-кадра ЛР3 и ЛР6 получены, визуально проверены и встроены в отчёты. Созданы подробные `FINAL_REPORT_LR2.md` … `FINAL_REPORT_LR8.md`, `MASTER_STUDY_GUIDE.md` и `DEFENSE_30_MIN.md`; исходные drafts сохранены. Final UNVERIFIED cleanup выполнен по существующим данным: целевой grep по финальным материалам не нашёл служебных меток.

## Environment

- Workspace: `/media/sf_OpenFOAM_Labs` (подтверждено `pwd`).
- OpenFOAM Foundation 13, build `13-18870c24d21c`.
- Активация: `/home/pavel/openfoam-lab/of-root/activate-of13.sh`.
- Проверены и доступны: `blockMesh`, `icoFoam`, `foamRun`, `paraFoam`, системные `pvpython` и `pvbatch`.
- Рабочий ParaView 6.1.1: `/home/pavel/openfoam-lab/tools/ParaView-6.1.1-MPI-Linux-Python3.12-x86_64`.
- SALOME 9.16.0: `/home/pavel/openfoam-lab/tools/SALOME-9.16.0`; `run_salome.sh info` успешно сообщил Python 3.10.16 и Salome 9.16.0.
- Последовательные расчёты использовать по умолчанию. Warning `mpicc: command not found` не мешает им. Установки OpenFOAM/SALOME, VPN/DNS, Ubuntu, kernel и VirtualBox не изменять.
- Диагностика зависания VM: выделено 4 vCPU и 7.3 GiB RAM; во время проверки оставалось около 3.9–4.2 GiB доступной памяти, swap почти не использовался, OOM/FATAL/segfault в solver logs отсутствовали. Причина пауз — четыре MPI rank, занявшие все 4 vCPU, плюс GUI/Codex и интенсивные записи в VirtualBox shared folder. Рабочее решение: один последовательный solver на локальном `/tmp`; добавлять RAM не требуется. Если у host не менее 8 потоков/16 GiB, опционально можно выделить VM 6 vCPU и 10–12 GiB, оставляя не менее двух vCPU свободными для GUI/host.
- Источники найдены: методички ЛР2–ЛР8 и отчёты `СтарковМА_ЛР2.pdf` … `СтарковМА_ЛР8.pdf`.

## Finalization plan

1. [x] Повторно сверить cases, dictionaries, HDF/UNV/scripts, logs и CSV.
2. [x] Привести `REPORT_DRAFT_LR2.md` … `REPORT_DRAFT_LR8.md` к единой структуре и встроить существующие evidence-файлы.
3. [x] Финализировать `DEFENSE_CHEATSHEET.md` по подтверждённым значениям.
4. [x] Получить один объединённый SALOME-скриншот для ЛР3.
5. [x] Получить один объединённый SALOME-скриншот для ЛР6.
6. [x] После получения двух кадров проверить их и заменить в отчётах пометки `UNVERIFIED`.
7. [x] Создать отдельные финальные отчёты ЛР2–ЛР8, не изменяя drafts.
8. [x] Перенести все 35 официальных вопросов методичек, подготовить короткие и подробные ответы.
9. [x] Создать общий учебный конспект и 30-минутный план подготовки к защите.
10. [x] Выполнить final cleanup: проверить fine mesh, извлечь extrema ЛР5, академически оформить ограничение SOLIDWORKS и воспроизводимые команды SALOME/ParaView.

## LR2

STATUS: DONE

Done:

- Базовый `manual-lab2/cavity`: 20×20×1, расчёт `icoFoam` 0–1 s, поля `Ux/Uy/Uz`.
- Старые рабочие кейсы `/home/pavel/openfoam-lab/cavity`, `cavityFine`, `cavityHighRe`, `cavityTurbulent` сохранены.
- `cavityFine`: 40×40×1, `deltaT=0.0025`, есть `mapFields` и расчёт до 1 s.
- `cavityHighRe`: `nu=0.001` (Re=100), расчёт `icoFoam` до 1 s.
- `cavityTurbulent`: RAS, `nu=1e-5` (Re=10000), расчёт совместимой командой `pisoFoam` до 2 s.
- Для базового/fine/graded/high-Re/RAS/clipped cases воспроизводимо созданы и визуально проверены все изображения и профиль Ux.

Verified:

- Базовая сетка: 400 hex, `Mesh OK`, solver log оканчивается `End`, max Courant на 1 s = 0.852134.
- Fine: 1600 cells; новый `log.checkMesh` содержит `Mesh OK`, max non-orthogonality 0°, max aspect ratio 1; `log.blockMesh`, `log.mapFields`, `log.icoFoam` оканчиваются `End`.
- HighRe и turbulent: реальные временные каталоги и solver logs с `End`.
- Граничные условия базового кейса и `nu=0.01` (Re=10) ранее сверены.

Missing: обязательных вычислений и изображений нет; подробный результат оформлен в `FINAL_REPORT_LR2.md`, draft сохранён.

GUI: не нужен; все изображения получены через `pvpython` и визуально проверены.

Screenshots: готовы 14 файлов в `screenshots/LR2`: mesh/pressure/10 contours/glyphs/streamlines/profile, fine/graded, Re=100, RAS и clipped t=0.5/0.6.

Next technical step: отчёт готов; вычислительных действий не требуется.

Known issues:

- `fast_finish_2026/LR2/cavityGrade`: 400 graded hex, `Mesh OK`, поля перенесены из fine at 0.7 s, `icoFoam` дошёл до 0.8 s, maxCo=0.440057, все logs `End`.
- `fast_finish_2026/LR2/cavityClipped`: 336 hex, `Mesh OK`, несогласованное mapping из base at 0.5 s, расчёт дошёл до 0.6 s, maxCo=0.834722, все logs `End`.
- `fast_finish_2026/LR2/cavityHighRe`: безопасная копия продолжена до 2 s, `Mesh OK`, solver `End`.
- `fast_finish_2026/LR2/cavityRAS`: безопасная копия продолжена до 20 s, `Mesh OK`, solver `End`; финальный maxCo=1.00305, то есть на 0.3% выше строгой границы 1. Результат устойчив, но для формального соответствия желательно повторить продолжение с `maxCo<1`/меньшим dt.
- Начатый новый `/home/pavel/openfoam-lab/manual-lab2/cavityFine` имеет сетку и каталог `0.5`, но перенос не завершён. Он не нужен для повторного расчёта, поскольку старый `/home/pavel/openfoam-lab/cavityFine` уже содержит подтверждённый результат; не удалять.

## LR3

STATUS: DONE

Done:

- Исправлен допуск склейки в `lab3/damBreakLaminar/mesh1_withBoundary.py`; SALOME 9.16 воспроизводимо построил структурированную сетку.
- Сохранены `Mesh_1.unv`, `Lab3-final.hdf` и `Lab3-final-dump.py`.
- UNV импортирован в `fast_finish_2026/LR3/damBreakLaminar`; patches назначены как wall/patch/empty, выполнены масштабирование и `setFields`.
- Основной вариант и варианты `centerBox`/`sphere` рассчитаны до 1 s.
- Сохранены изображения сетки, начальной фазы и временной последовательности 0.25/0.5/0.65/0.85 s для трёх вариантов.

Verified:

- SALOME mesh: 4222 nodes, 2016 hexahedra; группы `leftWall=46`, `rightWall=46`, `lowerWall=52`, `atmosphere=44`, `frontAndBack=4032`.
- OpenFOAM `checkMesh`: `Mesh OK`, max non-orthogonality 0.
- Все три `foamRun` завершены строкой `End`; основной расчёт: wall-clock около 53 s, final maxCo≈0.83.

Missing: нет.

GUI: больше не нужен; расчёт и генерацию сетки не повторять.

Screenshots: расчётные изображения и `screenshots/LR3/salome_mesh_groups.png` готовы; SALOME-кадр проверен как PNG 1335×610 и встроен в `FINAL_REPORT_LR3.md`.

Next technical step: дополнительных действий по ЛР3 нет.

## LR4

STATUS: DONE

Done: созданы и рассчитаны отдельные cases `fast_finish_2026/LR4/Re_41` и `Re_140` с шестиблочной геометрией методички; подробный результат оформлен в `FINAL_REPORT_LR4.md`.

Verified: вода 293.2 K, D=0.01 m, скорости 0.0041246/0.014084 m/s при `nu=1.006e-6 m2/s` дают Re=41/140. Каждая сетка содержит 10500 hex, `Mesh OK`, max non-orthogonality 43.96335. Оба расчёта дошли до 100 s и завершились строкой `End`; wall-clock 550/791 s, final maxCo≈0.78/0.92.

Missing: обязательных вычислений и изображений нет.

GUI: не нужен; изображения воспроизводимо получены через `pvpython` и визуально проверены.

Screenshots: готовы `screenshots/LR4/Re_41_mesh.png`, `Re_41_velocity.png`, `Re_41_streamlines.png`, `Re_140_velocity.png`, `Re_140_streamlines.png`.

Next technical step: отчёт готов; вычислительных действий не требуется.

## LR5

STATUS: DONE

Done: создан и рассчитан `fast_finish_2026/LR5/buoyantCavity`; geometry 0.1×0.1×0.01 m, 40×40×5 cells, hot 305 K, cold 295 K, initial 300 K. Реализовано локальное веб-приложение в `fast_finish_2026/LR5/webapp`.

Verified: 8000 hex, `Mesh OK`; `foamRun` дошёл до 500 s, wall-clock около 58 s, exit 0 и `End`. Полный web job `runs/2026-09-12T23-50-01-637Z` выполнил сетку, проверку и solver до 500 s со статусом `done`.

Missing: обязательных вычислений и изображений нет. Неуспешные попытки `fieldMinMax` не используются как источник. Прямое чтение готового слоя 500 через `extract_extrema.py` подтверждает `T=295,066986…304,933014 K` и `|U|=7,387406·10⁻6…0,040992715 м/с`; журнал сохранён в `validation/log.extrema.t500`.

GUI: не нужен; браузерный и ParaView screenshots сохранены и проверены.

Screenshots: готовы `screenshots/LR5/mesh.png`, `temperature.png`, `velocity_streamlines.png`, `web_form.png`.

Next technical step: отчёт готов; вычислительных действий не требуется.

## LR6

STATUS: DONE

Done:

- `fast_finish_2026/LR6/calc_nozzle.py` вычисляет входное, критическое и выходное сечения для p0=200000 Pa, T0=1800 K, pout=9000 Pa, G=1.5 kg/s, углов 14/28°, R=287, k=1.4.
- `generate_salome.py` воспроизводимо создал параметрическую двухблочную сетку, `Mesh.unv` и `LR6-nozzle.hdf`.
- UNV импортирован и отдельно проверен в `salomeMeshCheck`.
- Создан совместимый OF13 compressible case `fast_finish_2026/LR6/nozzle`: 8000 hex, поля p/T/U и начальная ступень давления заданы.
- PIMPLE `fluid` воспроизводимо дал локальный скачок Co и отрицательную температуру около t=0.002962; отдельный probe штатного `shockFluid`/Kurganov при maxCo=0.2 прошёл эту отметку до t=0.0032 и завершился `End`.
- Методичка уточнена: начальная T должна быть uniform 1800 K. Создан чистый `nozzleShockFluidFresh` с правильной T и скачком только p.
- Из-за паузы VM при 4 MPI ranks финальный run перенесён на локальный диск `/tmp` и выполнен одним процессом; все временные слои 0.0065–0.015 и журналы безопасно возвращены в workspace.
- На сверхзвуковом выходе p исправлено с переопределённого `fixedValue` на физически корректный `zeroGradient`; параметр pOutput=9000 Pa остаётся в аналитике/геометрии и начальном поле расширяющейся части.

Verified:

- Аналитика: throat Mach=1, d=100.118 mm; outlet Mach=2.6697, d=176.078 mm; длины 1.188030/0.152328 m.
- SALOME mesh: 16482 nodes, 8000 hex; группы inlet/outlet/axis/wall/frontAndBack. Импортированный `checkMesh`: `Mesh OK`, max non-orthogonality 13.8336.
- Нативный case: 8000 hex, `Mesh OK`, max non-orthogonality 13.9226, skewness 0.619734.
- Устойчивый probe: `End` при t=0.0032, maxCo=0.200001; внутреннее T при записи t=0.003 положительно (785.574…1856.42 K).
- Финальный fresh run дошёл до t=0.015 и завершился строкой `End`; три последовательных сегмента имеют wall-clock 496+617+335≈1448 s, последнее maxCo=0.29984.
- Финальные диапазоны внутренних полей: p=19.398…200.286 kPa, T=923.139…1800.76 K, |U|=98.524…1327.73 m/s, rho=0.07304…0.38660 kg/m³. Отрицательных/нефизических полей нет.

Missing: нет.

GUI: больше не нужен; solver и генерацию сетки не повторять.

Screenshots: финальные CFD p/T/U/Mach и `screenshots/LR6/salome_nozzle_mesh_groups.png` готовы; SALOME-кадр проверен как PNG 1338×660 и встроен в `FINAL_REPORT_LR6.md`.

Next technical step: дополнительных действий по ЛР6 нет. Финальный отчёт явно разделяет SALOME-import mesh и native mesh контрольного CFD case.

## LR7

STATUS: DONE

Done: реализовано независимое от внешних пакетов web-приложение `fast_finish_2026/LR7/webapp` с шестью полями, серверной валидацией, отдельными каталогами jobs, Python runner, возобновлением экрана по `?job=...`, реальным прогрессом solver и отображением результата ParaView.

Verified: корректная и некорректная формы проверены. Smoke job вычислил аналитику, сгенерировал чистый case и получил `Mesh OK`. Полный API job `2026-09-13T01-50-54-310Z` на тех же шести параметрах построил 8000 hex, получил `Mesh OK`, рассчитался до t=0.015 за 1402 s wall-clock, завершил solver строкой `End`, затем прошёл `LR8_POSTPROCESS_OK` на 30 временных слоях. Финальный UI показывает 100%, Mesh OK, solver End и реальное поле давления.

Missing: обязательных вычислений, evidence и screenshots нет.

GUI: не нужен; все браузерные проверки и screenshots выполнены автоматически.

Screenshots: готовы `screenshots/LR7/web_form.png`, `web_progress.png`, `web_complete.png`.

Next technical step: отчёт готов; evidence сохранён в `fast_finish_2026/LR7/webapp/runs/full-2026-09-13T01-50-54-310Z`.

## LR8

STATUS: DONE

Done:

- Создан воспроизводимый `fast_finish_2026/LR8/postprocess_nozzle.py`: чтение p/T/U, CellDataToPoint, вычисление Mach, пять видов и Plot Over Line на 601 точке.
- Создан `plot_centerline.py`: графики U+T и p+Mach, а также таблица CFD/аналитика для входа, горла и выхода.
- Конвейер успешно выполнен на финальном времени LR6 t=0.015.

Verified: `pvpython` завершился `LR8_POSTPROCESS_OK`, определил final time 0.015 и 601 точку профиля; созданы `mesh.png`, `pressure.png`, `temperature.png`, `velocity.png`, `mach.png`, `centerline.csv`, два графика и `section_comparison.csv`. Все виды и оба графика визуально открыты и проверены. Исправлено реальное разрешение ParaView-кадров до 1500×500. По 30 временным слоям создана и проверена `pressure_evolution.gif` 1000×333. Выходной нефизический пик отсутствует.

Missing: обязательных вычислений, статических материалов и анимации нет.

GUI: не нужен; только опциональная демонстрация ParaView pipeline/анимации преподавателю.

Screenshots: финальные p/T/U/Mach/mesh, два графика, CSV-таблица и GIF-анимация готовы в `screenshots/LR8`.

Next technical step: отчёт готов; CFD не перезапускать.

## Финальный комплект отчётов — 2026-09-13

STATUS: DONE

Созданы и проверены `final_reports/FINAL_REPORT_LR2.docx`–`FINAL_REPORT_LR8.docx` и соответствующие PDF. Комплект содержит 109 страниц PDF и 56 встроенных подтверждённых изображений. Все DOCX прошли проверку целостности, все PDF имеют формат A4 и открываются средствами Poppler/pypdf.

Выполнена постраничная визуальная проверка 109 отрендеренных страниц. Исправлено отображение корня в формулах скорости звука; повторный рендер ЛР6 и ЛР8 подтверждает корректное отображение формул. Подробный протокол находится в `FINAL_FORMAT_AUDIT.md`.

Исходные `REPORT_DRAFT_LR*.md` и `FINAL_REPORT_LR*.md` сохранены. Solver, MPI и генерация сеток на этапе подготовки DOCX/PDF не запускались.
