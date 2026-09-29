# FIGURE INDEX — CourseProject_V3

| № | Раздел | Файл | Подпись | Что подтверждает |
|---:|---|---|---|---|
| 1 | 2.2 | `screenshots/app_default_report.png` | Стандартные параметры варианта №3 и динамическая схема канала | доступность `L,H,a,P,S,Y,R,Uin`, baseline Re и расположение 7 квадратов |
| 2 | 2.3 | `screenshots/salome_geometry.png` | Геометрия канала варианта №3 с семью квадратными препятствиями в SALOME | реальную 2D/3D геометрию и дерево групп |
| 3 | 2.3 | `screenshots/salome_mesh.png` | Однослойная quad-dominant сетка расчётной области в SMESH | тип и локальное сгущение сетки |
| 4 | 2.3 | `screenshots/salome_groups.png` | Именованные группы `inlet`, `outlet`, `walls`, `obstacles`, `frontAndBack` | соответствие групп будущим OpenFOAM patches |
| 5 | 2.4 | `screenshots/openfoam_mesh_report.png` | Принятая quad-dominant сетка после импорта в OpenFOAM | целостность сетки и семь отверстий; исходный кадр — `openfoam_mesh.png` |
| 6 | 2.12 | `screenshots/velocity_report.png` | Модуль скорости воды `|U|` в baseline при времени 2501 | ускорение в проходах и зоны малой скорости в следах; исходный кадр — `velocity.png` |
| 7 | 2.12 | `screenshots/pressure_report.png` | Давление после перевода кинематического `p` в Па | падение среднего давления и локальные зоны давления; исходный кадр — `pressure.png` |
| 8 | 2.12 | `screenshots/streamlines_report.png` | Линии тока через шахматный массив | отклонение струй и вихревые следы; исходный кадр — `streamlines.png` |
| 9 | 2.12 | `screenshots/obstacles_zoom_report.png` | Увеличенное поле скорости около препятствий | локальная структура ускорения и торможения; исходный кадр — `obstacles_zoom.png` |
| 10 | 3.1 | `screenshots/architecture.png` | Фактическая архитектура приложения и pipeline | связь UI, Node.js, Python, SALOME, OpenFOAM, ParaView и runs |
| 11 | 3.2 | `screenshots/app_changed_report.png` | Параметрическая схема для изменённой геометрии C | изменение размеров, координат препятствий и Re |
| 12 | 3.5 | `screenshots/app_running_report.png` | Неблокирующее отображение стадии SALOME | реальный прогресс полного запуска и блокировку повторного запуска |
| 13 | 3.6 | `screenshots/app_complete_u0p15_report.png` | Завершённый тест B при `Uin=0.15 м/с` | propagation скорости, status, summary и сохранённые поля |
| 14 | 4.1 | `validation/run_comparison.png` | Сравнение `Re_a`, максимальной скорости и перепада давления | различия трёх подтверждённых расчётов A/B/C |

Все 14 файлов существуют и распознаются как PNG. Файлы `*_report.png` являются отчётными кадрированиями/композициями исходных доказательных кадров; оригиналы сохранены без изменения.
