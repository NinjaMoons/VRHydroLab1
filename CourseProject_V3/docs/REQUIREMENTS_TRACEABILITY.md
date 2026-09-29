# Трассировка требований курсового проекта

Дата проверки: 14 сентября 2026 года. Источник требований — задание варианта №3 и финальное master-ТЗ. Источники реализации — только файлы и сохранённые артефакты `CourseProject_V3`.

| № | Требование задания | Реализация | Файл/код | Доказательство | Статус |
|---:|---|---|---|---|---|
| 1 | Вариант №3, рабочая среда — вода | семь квадратных препятствий в прямоугольном канале; `nu=1.006e-6 м²/с`, `rho=998.2 кг/м³` | `settings.json`, `scripts/geometry.py` | HDF/UNV, cases и сводки runs содержат вариант 3 и свойства воды | DONE |
| 2 | Изменение размеров по схеме | поля `L,H,a,P,S,Y,R`, пересчёт семи центров | `app/public/index.html`, `app/server.js`, `scripts/geometry.py` | UI-кадры стандартной и изменённой геометрии, run C | DONE |
| 3 | Изменение входной скорости | поле `Uin`; пересчёт `U,k,omega,Re` | `app/server.js`, `scripts/parameterize_case.py` | run B: `Uin=0.15 м/с` и собственный case/summary | DONE |
| 4 | Проверка пользовательских параметров | числовые диапазоны, геометрические зазоры, пересечения | `app/server.js::validate`, `scripts/geometry.py::validate_settings` | acceptance tests D и сообщения UI | DONE |
| 5 | Геометрия в SALOME | параметрический fluid domain, extrusion 1 мм | `salome/generate_mesh.py` | `CourseProject_V3.hdf` и кадр SALOME Geometry | DONE |
| 6 | Граничные группы | `inlet`, `outlet`, `walls`, `obstacles`, `frontAndBack` | `salome/generate_mesh.py` | HDF/UNV, `mesh_summary.json` и кадр групп | DONE |
| 7 | Сетка SALOME и передача в OpenFOAM | NETGEN 1D–2D, quad-dominant, extrusion, HDF и UNV | `salome/generate_mesh.py` | baseline: 11364 points, 5267 cells; HDF/UNV сохранены | DONE |
| 8 | Проверка качества сетки | импорт, масштабирование и расширенный `checkMesh` | `scripts/run_pipeline.py` | `validation/reference_mesh/log.checkMesh` и logs каждого принятого run: `Mesh OK` | DONE |
| 9 | Расчёт средствами OpenFOAM | Foundation 13, `foamRun -solver incompressibleFluid` | `openfoam/template`, `openfoam/transient`, pipeline | solver logs A/B/C заканчиваются `End` | DONE |
| 10 | Физическая и численная постановка | RAS `kOmegaSST`; steady SIMPLE как инициализация, transient PIMPLE как отчётный этап | `momentumTransport`, `controlDict`, `fvSchemes`, `fvSolution` | dictionaries и логи финального времени 2501 с | DONE |
| 11 | Постобработка ParaView | автоматические виды mesh, `|U|`, `p`, zoom, streamlines; ручное открытие case | `postprocessing/render_results.py`, `app/server.js` | PNG и `paraview_summary.json` в runs | DONE |
| 12 | Пользовательское приложение | браузерный frontend, локальный Node.js backend, Python-runner | `app/public/*`, `app/server.js`, `scripts/run_pipeline.py` | acceptance screenshots и API-тесты | DONE |
| 13 | Мониторинг и обработка отказов | стадии, журнал, `failed`, блокировка второго job кодом 409, восстановление формы | `app/server.js`, `app/public/app.js` | acceptance tests D/E и `acceptance_test_results.json` | DONE |
| 14 | Подтверждение параметричности | полные runs A/B/C: baseline, новая скорость, новая геометрия | `runs/*`, `validation/compare_runs.py` | три `summary.json`, `run_comparison.json/png` | DONE |
| 15 | Сохранение и воспроизводимость результата | изолированный run: вход, HDF/UNV, case, logs, PNG, summary | `scripts/run_pipeline.py` | каталоги `runs/baseline_v3_u0p1`, `speed_v3_u0p15`, `geometry_v3_changed` | DONE |

## Итог

Покрыто 15 из 15 проверяемых требований. Функциональных пробелов задания не обнаружено. Не реализованная из UI отмена активного процесса и отсутствие очереди не являются требованиями исходного задания: они зафиксированы как ограничения локального однопользовательского приложения.
