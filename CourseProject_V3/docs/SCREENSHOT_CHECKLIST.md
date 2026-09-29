# SCREENSHOT CHECKLIST — CourseProject_V3

Использовать только изображения текущего проекта. `VERIFIED` означает: файл существует, формат проверен, содержание визуально сопоставлено с реальным case/status.

| № | Источник | Кадр | Плановый путь | Статус |
|---:|---|---|---|---|
| 1 | SALOME | Рисунок 2 — геометрия канала и 7 отверстий; в дереве видны `Fluid_domain_2D/3D` | `screenshots/salome_geometry.png` | VERIFIED |
| 2 | SALOME | Рисунок 3 — сетка целиком; различимы сгущение и один слой по Z | `screenshots/salome_mesh.png` | VERIFIED |
| 3 | SALOME | Рисунок 4 — сетка и раскрытые группы `inlet/outlet/walls/obstacles/frontAndBack` | `screenshots/salome_groups.png` | VERIFIED |
| 4 | Web app | Рисунок 1 — русская форма, стандартные параметры, динамическая схема и доступные действия | `screenshots/app_default_acceptance.jpg` | VERIFIED |
| 5 | Web app | Рисунок 10 — изменённая геометрия C, новые центры и пересчитанные числа Рейнольдса | `screenshots/app_changed_acceptance.jpg` | VERIFIED |
| 6 | Web app | Рисунок 11 — реальный полный pipeline на стадии SALOME; повторный запуск заблокирован | `screenshots/app_running_acceptance.jpg` | VERIFIED |
| 7 | Web app | Рисунок 12 — завершённый UI-run B с использованными входами, временем, статусом и показателями | `screenshots/app_complete_u0p15_acceptance.jpg` | VERIFIED |
| 8 | ParaView | Поле модуля скорости, `t=2501 с` | `screenshots/velocity.png` | VERIFIED |
| 9 | ParaView | Поле давления, пересчитанное в Па, `t=2501 с` | `screenshots/pressure.png` | VERIFIED |
| 10 | ParaView | Линии тока из входного сечения, `t=2501 с` | `screenshots/streamlines.png` | VERIFIED |
| 11 | ParaView | Увеличение поля скорости около препятствий | `screenshots/obstacles_zoom.png` | VERIFIED |

Старые файлы `app_default.jpg`, `app_changed.jpg`, `app_running.jpg` и `app_complete.jpg` сохранены как evidence прежней версии и больше не используются в пояснительной записке. Новые кадры получены непосредственно из работающего локального интерфейса `http://127.0.0.1:8083/`; формат и размеры проверены (`JPEG`, 764 px по ширине).
