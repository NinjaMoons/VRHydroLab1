# PROJECT AUDIT — курсовой проект, вариант №3

Дата аудита: 13 сентября 2026 года.

## 1. Идентификация готового проекта

Основной проект найден по совокупности исходного кода, расчётных случаев, HDF/UNV, журналов, результатов и пользовательского интерфейса в каталоге `CourseProject_V3`. Соседние каталоги `fast_finish_2026`, `lab3` и корневые отчёты относятся к лабораторным работам и не являются реализацией курсового проекта.

Название приложения в `app/package.json`: `course-project-v3-channel`. Пользовательское название в интерфейсе: «Расчёт канала с квадратными препятствиями». Назначение — параметрический расчёт течения воды в канале варианта №3 с семью квадратными препятствиями.

## 2. Проверенные источники

- `README.md`, `docs/MASTER_PROGRESS.md`, `docs/DECISIONS.md`;
- `settings.json`;
- `app/package.json`, `app/server.js`, `app/public/app.js`, `app/public/index.html`, `app/public/style.css`;
- `scripts/geometry.py`, `scripts/parameterize_case.py`, `scripts/set_patch_types.py`, `scripts/run_pipeline.py`, `scripts/build_summary.py`;
- `salome/generate_mesh.py`, HDF и UNV;
- `openfoam/template` и `openfoam/transient`;
- `postprocessing/render_results.py`;
- `validation/reference_mesh/log.checkMesh`, `validation/run_comparison.csv/json/png`, `validation/acceptance_test_results.json`;
- сохранённые cases, logs, `summary.json` и PNG в `runs/`;
- screenshots в `screenshots/`;
- пример пояснительной записки `КП_СИА_СтарковМА`, доступный в публичной папке Google Drive, — только как ориентир структуры и оформления. Технические данные из него не переносились.

## 3. Фактический программный стек

| Уровень | Реализация | Доказательство |
|---|---|---|
| Пользовательский интерфейс | HTML, CSS, браузерный JavaScript без стороннего frontend framework | `app/public/index.html`, `style.css`, `app.js` |
| Сервер | Node.js, встроенные `http`, `fs`, `path`, `child_process`; npm-зависимостей нет | `app/server.js`, `app/package.json` |
| Оркестрация | Python 3, стандартная библиотека | `scripts/run_pipeline.py` |
| Геометрические проверки | Python и дублирующая серверная проверка JavaScript | `scripts/geometry.py`, функция `validate()` в `app/server.js` |
| Геометрия и сетка | SALOME 9.16.0, Python API GEOM/SMESH, NETGEN 1D–2D, extrusion sweep | `salome/generate_mesh.py`, HDF, UNV |
| CFD | OpenFOAM Foundation 13, `foamRun -solver incompressibleFluid` | dictionaries, pipeline, solver logs |
| Постобработка | OpenFOAM `foamPostProcess`; ParaView 6.1.1 через `pvpython` | `run_pipeline.py`, `render_results.py`, logs и PNG |
| Хранение результата | изолированные каталоги run с JSON, case, logs, HDF/UNV и PNG | `runs/*` |

## 4. Фактическое использование SALOME

SALOME применяется программно и визуально. Скрипт `salome/generate_mesh.py`:

1. читает `settings.json`;
2. строит прямоугольную 2D-область канала;
3. вычисляет центры семи квадратов из `L`, `R`, `P`, `S`, `Y` и вычитает их из канала;
4. выдавливает область на технологическую толщину 1 мм;
5. создаёт геометрические группы `inlet`, `outlet`, `walls`, `obstacles`, `frontAndBack`;
6. строит quad-dominant сетку NETGEN 1D–2D с локальным размером на рёбрах препятствий;
7. выполняет extrusion sweep на один слой по Z;
8. формирует группы граней сетки;
9. экспортирует `Mesh.unv`, сохраняет `CourseProject_V3.hdf` и `mesh_summary.json`.

Реальные GUI-снимки показывают Geometry tree, готовую сетку и группы. Воспроизводимый запуск выполняется из pipeline командой SALOME в пакетном режиме `-t`; HDF не является единственным источником геометрии, поскольку построение полностью описано скриптом.

## 5. Фактическое использование OpenFOAM

- версия: OpenFOAM Foundation 13;
- solver: `foamRun -solver incompressibleFluid`;
- среда: вода, несжимаемая и изотермическая;
- свойства: `nu = 1.006e-6 м²/с`, `rho = 998.2 кг/м³` (плотность используется при переводе кинематического давления в Па);
- турбулентность: RAS, `kOmegaSST`, `turbulence on`, Newtonian viscosity;
- этап 1: стационарная диагностическая инициализация SIMPLE до метки времени/итерации 2500;
- этап 2: нестационарное продолжение PIMPLE до `t = 2501 с`, адаптивный шаг, `maxCo = 0.7`;
- выполнение: только последовательное, без MPI.

Стационарный этап не объявляется сошедшимся решением: после 2500 итераций невязки сохраняли периодические колебания. Отчётные величины относятся к сохранённому финальному состоянию нестационарного продолжения.

## 6. Фактическое использование ParaView

ParaView используется двумя способами:

- интерактивно: сервер может открыть сохранённый `course_project.foam` в ParaView;
- автоматически: `pvpython postprocessing/render_results.py` читает финальное время, преобразует cell data в point data, вычисляет давление в Па и сохраняет пять видов: mesh, velocity, pressure, obstacles zoom и streamlines.

`paraview_summary.json` отдельно хранит диапазоны point data. В отчёте cell extrema OpenFOAM и интерполированные point ranges ParaView не смешиваются.

## 7. Параметры варианта №3

| Параметр | По умолчанию | Единица | Смысл |
|---|---:|---|---|
| `L` | 326 | мм | длина канала |
| `H` | 23 | мм | высота канала |
| `a` | 12 | мм | сторона квадратного препятствия |
| `P` | 60 | мм | шаг препятствий верхнего ряда |
| `S` | 30 | мм | продольный сдвиг нижнего ряда |
| `Y` | 8 | мм | расстояние от нижней стенки до центров нижнего ряда; центры верхнего ряда имеют координату `H − Y` |
| `R` | 60 | мм | отступ центра последнего верхнего препятствия от выхода |
| `Uin` | 0.1 | м/с | скорость на входе |
| `quality` | Medium | — | предустановка сетки |

Центры baseline: верхний ряд `(86; 15)`, `(146; 15)`, `(206; 15)`, `(266; 15)` мм; нижний ряд `(116; 8)`, `(176; 8)`, `(236; 8)` мм.

## 8. Изменяемые параметры и ограничения

Интерфейс позволяет изменять `L`, `H`, `a`, `P`, `S`, `Y`, `R`, `Uin` и предустановку качества `Coarse/Medium/Fine`. Серверные диапазоны:

- `L`: 100…1000 мм; `H`: 15…200 мм; `a`: 2…50 мм;
- `P`: 10…250 мм; `S`: 1…250 мм; `Y`: 1…199 мм; `R`: 10…500 мм;
- `Uin`: 0.005…2 м/с.

Дополнительно проверяются конечность чисел, положительность `nu` и `rho`, условия `S ≥ a`, `P − S ≥ a`, `P ≥ a`, зазоры до верхней/нижней стенок, выход препятствий за вход/выход и попарные пересечения. Технологическая толщина сохраняется равной 1 мм.

## 9. Границы и граничные условия

Фактические patches: `inlet`, `outlet`, `walls`, `obstacles`, `frontAndBack`. В `constant/polyMesh/boundary` они получают типы `patch`, `patch`, `wall`, `wall`, `empty` соответственно.

- `U`: `fixedValue (Uin 0 0)` на входе, `zeroGradient` на выходе, `noSlip` на стенках и препятствиях, `empty` на front/back;
- `p`: `zeroGradient` на входе и твёрдых границах, `fixedValue 0` на выходе, `empty` на front/back;
- `k`: `fixedValue` на входе, `zeroGradient` на выходе, `kqRWallFunction` на твёрдых границах, `empty` на front/back;
- `omega`: `fixedValue` на входе, `zeroGradient` на выходе, `omegaWallFunction` на твёрдых границах, `empty` на front/back;
- `nut`: `calculated` на inlet/outlet, `nutkWallFunction` на твёрдых границах, `empty` на front/back.

## 10. Подтверждённая сетка baseline

SALOME и расширенный `checkMesh -allGeometry -allTopology` подтверждают:

- 11364 узла/points;
- 5267 объёмных ячеек;
- 5101 hexahedra и 166 prisms;
- один слой по Z;
- max aspect ratio 2.5618444;
- max/average non-orthogonality 41.596905° / 4.8437362°;
- max skewness 2.5947718;
- minimum determinant 0.027537398;
- итог `Mesh OK`.

Размеры сетки Medium: max 1.25 мм, min 0.6 мм, локально около препятствий 0.75 мм. Группы SALOME: inlet 18, outlet 18, walls 524, obstacles 448, frontAndBack 10534 граней.

## 11. Подтверждённые результаты baseline

Для `runs/baseline_v3_u0p1`:

- `Re_a = 1192.8429423459245`, характеристическая длина `a = 0.012 м`;
- `Re_H = 2286.282306163022`, характеристическая длина `H = 0.023 м`;
- `Qin = Qout = 2.3e-6 м³/с`, дисбаланс 0.0% в точности вывода;
- cell `max|U| = 0.46627613 м/с`, cell `min|U| = 0.001867985 м/с`;
- area-average pressure drop `Δp = 305.970689626 Па`;
- cell pressure range `−138.030676756…315.580091512 Па`;
- `maxCo = 0.6914771`, финальный шаг `0.00059680162 с`;
- финальное время `2501 с`;
- cumulative continuity error `−4.2313741e−11`;
- solver log завершается строкой `End`.

Поле `p` имеет размерность кинематического давления, а давление в паскалях вычисляется как `p_Pa = rho * p`.

## 12. Валидационные расчёты

| Run | Изменение | Mesh | Solver | Результат |
|---|---|---|---|---|
| `baseline_v3_u0p1` | baseline, `Uin=0.1 м/с` | 5267 cells, Mesh OK | End | `max|U|=0.46627613 м/с`, `Δp=305.970689626 Па` |
| `speed_v3_u0p15` | `Uin=0.15 м/с` | 5267 cells, Mesh OK | End | `max|U|=0.73750655 м/с`, `Δp=682.065777722 Па` |
| `geometry_v3_changed` | `L=350`, `H=25`, `a=11`, `P=62`, `S=31` мм | 6518 cells, Mesh OK | End | `max|U|=0.39990055 м/с`, `Δp=180.958577198 Па` |

Дополнительно интерфейсом выполнены полный baseline-run, полный run при `Uin=0.15 м/с` и mesh-only run изменённой геометрии. Проверены пустое, нечисловое и геометрически недопустимое поле, HTTP 409 при конфликтующем запуске, контролируемый exit code 1 и повторный запуск после ошибки.

## 13. Screenshots и графические доказательства

Существуют и визуально проверены:

- `screenshots/salome_geometry.png` — геометрия и дерево групп;
- `screenshots/salome_mesh.png` — сетка и сгущение около квадратов;
- `screenshots/salome_groups.png` — группы граней;
- `screenshots/openfoam_mesh.png` — импортированная сетка;
- `screenshots/velocity.png`, `pressure.png`, `obstacles_zoom.png`, `streamlines.png` — поля baseline;
- `screenshots/app_default_acceptance.jpg`, `app_changed_acceptance.jpg`, `app_running_acceptance.jpg`, `app_complete_u0p15_acceptance.jpg` — состояния приложения;
- `validation/run_comparison.png` — сравнение A/B/C.

Все используемые файлы существуют. PNG имеют размер 1600×600 для расчётных видов; SALOME-кадры 923×481, 1647×601 и 1633×657; acceptance-кадры интерфейса имеют ширину 764 px и полную вертикальную композицию страницы.

## 14. Как приложение запускает pipeline

`POST /api/calculate` принимает параметры, выполняет серверную валидацию, создаёт отдельный каталог `runs/web-<timestamp>`, сохраняет `settings.json` и запускает `scripts/run_pipeline.py` массивом аргументов через `spawn()`. Pipeline работает в `/tmp/CourseProject_V3/jobs/<run-id>`:

`validation → SALOME/HDF/UNV → ideasUnvToFoam → transformPoints 0.001 → patch types → checkMesh → parameterize case → steady SIMPLE → transient PIMPLE → foamPostProcess → pvpython → summary → persistent run`.

Состояние записывается атомарно в `status.json`. Интерфейс опрашивает `/api/status`, отображает реальные стадии, затем загружает `/api/summary` и PNG. Одновременно допускается один тяжёлый процесс; конфликт возвращает HTTP 409. Любая внешняя команда проверяется по `returncode`; ошибка переводит run в `failed`, а интерфейс снова разрешает ввод.

## 15. Соответствие исходному заданию

| Требование | Как реализовано | Доказательство |
|---|---|---|
| Вариант №3, вода, семь квадратных препятствий | Параметрическая 2D-область, выдавленная на 1 мм; вода с заданными `nu` и `rho` | `settings.json`, `geometry.py`, SALOME HDF/UNV |
| Использование SALOME | Python-генерация геометрии, сетки, групп, HDF и UNV | `salome/generate_mesh.py`, screenshots |
| Использование OpenFOAM | Импорт UNV, проверка сетки, SIMPLE/PIMPLE расчёт `incompressibleFluid`, RAS kOmegaSST | case, dictionaries, logs |
| Использование ParaView | `pvpython` создаёт поля скорости, давления, streamlines и JSON диапазонов; доступен ручной запуск | `render_results.py`, PNG |
| Изменение геометрии | Поля `L,H,a,P,S,Y,R`, динамическая схема и отдельный geometry run | UI, `app_changed_acceptance.jpg`, `geometry_v3_changed` |
| Изменение входной скорости | Поле `Uin`, пересчёт Re/k/omega/U, отдельный подтверждённый run | UI, `speed_v3_u0p15`, case `0/U` |
| Приложение для автоматизации | Web UI + Node server + Python orchestration | `app/`, `run_pipeline.py` |
| Получение результата | Статус, журнал, метрики, PNG и запуск ParaView | API, acceptance screenshots, saved runs |

## 16. Ограничения и фактические неопределённости

- Исследование сеточной независимости не выполнялось.
- Сравнение с экспериментом, DNS или LES не выполнялось.
- Нестационарное продолжение охватывает одну физическую секунду; долговременная статистика по многим периодам не рассчитывалась.
- Отмена активного внешнего процесса из интерфейса не реализована; вместо очереди используется блокировка второго запуска.
- В итоговой записке эти ограничения должны быть сформулированы как границы выполненного исследования, а не скрываться.

## 17. Вывод аудита

Проект является готовой параметрической системой, а не оболочкой одного неизменяемого case. Это подтверждено двумя полными вариантами входных параметров, отдельным изменением геометрии, сохранёнными HDF/UNV/cases/logs/JSON/PNG и функциональными тестами интерфейса. Фактических оснований для повторного CFD-расчёта при подготовке записки нет.
