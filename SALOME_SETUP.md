# SALOME: окружение для лабораторной работы №3

Проверено 19 августа 2026 года на Ubuntu 26.04 LTS (Wayland), OpenFOAM
Foundation 13.

## Установка

- Версия: **SALOME 9.16.0 Linux Universal**.
- Каталог: `/home/pavel/openfoam-lab/tools/SALOME-9.16.0`.
- Исходный официальный архив:
  `/home/pavel/openfoam-lab/tools/SALOME-9.16.0.tar.gz`.
- MD5 архива: `78f08d5e49079602fafdc7e82cde13cb` (совпала с
  опубликованной SALOME контрольной суммой).
- Сборка автономная, основана на CentOS Stream 8 и содержит необходимые
  библиотеки. Системный Python, PATH и shell-конфигурация не изменялись.

SALOME 9.16.0 выбрана вместо старой 9.8.0 из методички. Это актуальный
выпуск, поддерживающий современные Linux-системы; универсальная сборка
работает с glibc >= 2.28. В Ubuntu 26.04 установлена glibc 2.43.

## Запуск

Обычный графический запуск:

```bash
/home/pavel/openfoam-lab/tools/SALOME-9.16.0/run_salome.sh
```

Открытие существующего study:

```bash
/home/pavel/openfoam-lab/tools/SALOME-9.16.0/run_salome.sh /путь/к/Study.hdf
```

Резервный запуск со встроенной программной Mesa-графикой:

```bash
/home/pavel/openfoam-lab/tools/SALOME-9.16.0/run_salome.sh --mesa
```

Режим `--mesa` нужен только при проблемах 3D-окна, удалённом X11 или
нестабильном аппаратном OpenGL. В текущей Wayland/XWayland-сессии обычный
GUI запускается и отображается корректно. Не нужно запускать SALOME через
`sudo` и не нужно предварительно активировать OpenFOAM.

Проверка версии:

```bash
/home/pavel/openfoam-lab/tools/SALOME-9.16.0/run_salome.sh info
```

Ожидается `Salome 9.16.0` и встроенный Python 3.10.16.

## Особенности по сравнению со старой методичкой

- Модули **Geometry** и **Mesh** сохранены и подходят для шагов ЛР3.
- Команды File -> Dump Study и экспорт UNV доступны.
- В Python API 9.16 прямой вызов dump имеет четыре аргумента:

  ```python
  salome.myStudy.DumpStudy(output_directory, "DumpName", True, False)
  ```

  SALOME самостоятельно добавляет расширение `.py`.
- Новый модуль Shaper не требуется для выполнения старой методики:
  Geometry остаётся доступен.
- SALOME и OpenFOAM следует запускать в отдельных командах. Не надо
  смешивать их `LD_LIBRARY_PATH`: автономный launcher SALOME сам создаёт
  своё окружение.

## Импорт UNV в OpenFOAM 13

Активировать именно установленный OpenFOAM Foundation 13:

```bash
source /home/pavel/openfoam-lab/of-root/activate-of13.sh
```

Из корня подготовленного кейса импортировать сетку:

```bash
ideasUnvToFoam Mesh_1.unv
checkMesh -allGeometry -allTopology
```

Либо явно указать кейс:

```bash
ideasUnvToFoam -case /путь/к/case /путь/к/Mesh_1.unv
checkMesh -case /путь/к/case -allGeometry -allTopology
```

После импорта проверить `constant/polyMesh/boundary` и назначить типы
патчей, требуемые задачей: стены — `wall`, атмосфера — `patch`, передняя и
задняя стороны двумерной задачи — `empty`. Имена групп из SALOME переходят
в имена boundary patches. Не полагаться на номера строк и `sed` из старого
отчёта: порядок секций может меняться.

Если геометрия построена не в метрах, масштабирование выполняется после
импорта, например:

```bash
transformPoints "scale = (0.146 0.146 0.146)"
```

Коэффициент должен соответствовать фактическим единицам конкретной модели.

## Проведённая проверка

Тестовые материалы находятся в
`/media/sf_OpenFOAM_Labs/salome-validation`.

- `validate_salome.py` успешно запущен SALOME в terminal mode.
- Geometry создал объёмный параллелепипед 1 x 1 x 0.1.
- Созданы шесть именованных групп граней.
- Mesh построил структурированную гексаэдрическую сетку:
  125 узлов, 64 гексаэдра, 96 граничных граней.
- Каждая из шести boundary-групп содержит 16 граней.
- Study сохранён как `ValidationStudy.hdf`.
- Python dump сохранён как `ValidationDump.py` и содержит команды GEOM,
  SMESH, GroupOnGeom и ExportUNV.
- Сетка экспортирована в `ValidationMesh.unv`.
- `ideasUnvToFoam` из OpenFOAM 13 прочитал 125 точек, 64 ячейки,
  96 граничных граней и все шесть именованных patches.
- Полный `checkMesh -allGeometry -allTopology` завершился сообщением
  `Mesh OK`: одна связная область, 64 hexahedra, нулевая
  non-orthogonality, корректные topology и geometry.
- GUI запущен в Ubuntu Wayland через XWayland; окно
  `SALOME 9.16.0 - [ValidationStudy]` создано и тестовый HDF открыт.

## ЛР3: прогресс на 20 августа 2026 года

Рабочий пример OpenFOAM 13 скопирован в:

```text
/media/sf_OpenFOAM_Labs/lab3/damBreakLaminar
```

Исходный пример совпал с
`$FOAM_TUTORIALS/incompressibleVoF/damBreakLaminar` по `diff -qr`.

В SALOME вручную выполнены следующие этапы:

- созданы 12 точек в плоскости `z = 0` по первым 12 вершинам
  `system/blockMeshDict`;
- построены 16 линий и пять плоских граней;
- грани объединены в `Compound_1`;
- выполнена Extrusion по OZ на `0.1`, создан `Extrusion_1`;
- совпадающие грани склеены с допуском `1e-7`, создан `Glue_1`;
- создана базовая структурированная сетка `Mesh_1`: Hexahedron (i,j,k),
  Quadrangle: Mapping, Wire Discretisation, глобально 15 сегментов;
- создана группа `Edges_Z_1cell` из 12 рёбер длиной `0.1`;
- вручную создана подсетка с одним сегментом по Z и успешно выполнен
  Compute;
- автоматически выбраны только геометрические группы рёбер (для
  исключения ошибок выбора совпадающих передних и задних рёбер):
  `Edges_X_left_23`, `Edges_X_barrier_2`, `Edges_X_right_19`,
  `Edges_Y_lower_4`, `Edges_Y_upper_42`;
- вручную создана и успешно рассчитана подсетка для
  `Edges_X_left_23` с 23 сегментами.

Создание подсетки `Edges_X_barrier_2` с двумя сегментами было описано,
но её выполнение пользователем ещё не подтверждено. Продолжать следует
именно с проверки/создания этой подсетки, затем вручную назначить:

```text
Edges_X_right_19  -> 19 сегментов
Edges_Y_lower_4   -> 4 сегмента
Edges_Y_upper_42  -> 42 сегмента
```

После всех подсеток выполнить Compute и проверить ожидаемый итог:
`4222` узла и `2016` гексаэдров.

Созданные файлы:

```text
lab3/damBreakLaminar/points.py
lab3/damBreakLaminar/solid.py
lab3/damBreakLaminar/create_edge_groups.py
lab3/damBreakLaminar/mesh1.py
lab3/damBreakLaminar/mesh1_withBoundary.py
```

`solid.py` — штатный Dump Study геометрии. `create_edge_groups.py`
использован только для отбора рёбер по точной длине; назначение подсеток
выполняется вручную для освоения интерфейса SALOME. `mesh1.py` и
`mesh1_withBoundary.py` оставлены как резерв и средство проверки, а не
как замена ручному выполнению лабораторной.

Из-за зависаний при работе с HDF непосредственно в общей папке VirtualBox
ручное исследование открыто из локальной копии:

```text
/tmp/Lab3-working.hdf
```

Сохранённые резервные файлы в каталоге задачи:

```text
lab3.hdf
Lab3-before-mesa.hdf
```

Перед завершением SALOME необходимо нажать `Ctrl+S`, а затем скопировать
актуальную локальную копию из `/tmp` в каталог задачи. Временное изменение
GNOME `check-alive-timeout` полностью отменено; текущее значение снова
равно исходным `5000` мс. Режим `--mesa` не помог и далее не нужен.

## Для новых сессий Codex

- Не переустанавливать SALOME 9.8.0 из старой методички.
- Не изменять OpenFOAM и результаты ЛР2.
- SALOME terminal mode использует локальный CORBA-порт. В ограниченной
  песочнице Codex такой запуск может требовать выполнения команды вне
  сетевой sandbox; это ограничение Codex, а не ошибка SALOME.
- Проверочный сценарий можно повторить командой:

  ```bash
  /home/pavel/openfoam-lab/tools/SALOME-9.16.0/run_salome.sh start -t -w 1 \
    /media/sf_OpenFOAM_Labs/salome-validation/validate_salome.py
  ```

- Установочный архив занимает около 5.75 GiB, распакованный каталог —
  около 11 GiB. Архив оставлен для восстановления или повторной проверки.
