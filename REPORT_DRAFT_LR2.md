# Лабораторная работа №2

## Цель работы

Освоить структуру расчётного case OpenFOAM, построение и проверку сетки, задание начальных и граничных условий, перенос полей между сетками и постобработку результатов в ParaView на примере течения в полости с движущейся крышкой.

## Постановка задачи

Рассматривается двумерное изотермическое течение несжимаемой жидкости в квадратной полости. Верхняя стенка движется вправо со скоростью 1 м/с, остальные стенки неподвижны. Исследованы базовая и уточнённая сетки, сетка со сгущением, режимы Re=10, 100 и 10000, а также полость с вырезом.

## Используемое программное обеспечение

- OpenFOAM Foundation 13: `blockMesh`, `checkMesh`, `mapFields`, `icoFoam`, совместимый вызов `pisoFoam`, `foamPostProcess`.
- ParaView 6.1.1: отображение сетки, давления, векторов, линий тока и профиля скорости.

## Исходные данные

Базовая область имеет размеры 0,1×0,1×0,01 м. В направлении z задана одна ячейка и граница `empty`, поэтому решается двумерная задача. При U=1 м/с и характерном размере L=0,1 м число Рейнольдса равно `Re=UL/nu`.

| Case | nu, м²/с | Re | Сетка | Конечное время |
|---|---:|---:|---:|---:|
| `cavityBase` | 0,01 | 10 | 20×20×1 | 1 с |
| `cavityFine` | 0,01 | 10 | 40×40×1 | 1 с |
| `cavityGrade` | 0,01 | 10 | 4 блока по 10×10×1 | 0,8 с |
| `cavityHighRe` | 0,001 | 100 | 20×20×1 | 2 с |
| `cavityRAS` | 1·10⁻⁵ | 10000 | 20×20×1 | 20 с |
| `cavityClipped` | 0,01 | 10 | 336 ячеек | 0,6 с |

## Расчётная область / геометрия

В `cavityBase`, `cavityFine`, `cavityHighRe` и `cavityRAS` используется квадратная полость. `cavityGrade` делит её на четыре блока для сгущения к стенкам. В `cavityClipped` из нижнего правого угла исключён участок 0,04×0,04 м; верхняя движущаяся граница переименована в `lid`.

## Построение сетки

Сетки созданы утилитой `blockMesh` по реальным файлам `system/blockMeshDict`.

| Case | Ячейки | Группы/patches | Результат проверки |
|---|---:|---|---|
| `cavityBase` | 400 hex | `movingWall`, `fixedWalls`, `frontAndBack` | `Mesh OK`, max non-orthogonality 0°, max aspect ratio 1 |
| `cavityFine` | 1600 hex | те же | отдельный `log.checkMesh` отсутствует — **UNVERIFIED**; `blockMesh` и `icoFoam` завершены `End` |
| `cavityGrade` | 400 hex | те же | `Mesh OK`, max non-orthogonality 0°, max aspect ratio 2 |
| `cavityHighRe` | 400 hex | те же | `Mesh OK`, max non-orthogonality 0° |
| `cavityRAS` | 400 hex | те же | `Mesh OK`, max non-orthogonality 0° |
| `cavityClipped` | 336 hex | `lid`, `fixedWalls`, `frontAndBack` | `Mesh OK`, max non-orthogonality 0° |

![Базовая сетка 20×20×1](screenshots/LR2/base_mesh.png)

![Уточнённая сетка 40×40×1](screenshots/LR2/fine_mesh.png)

![Четырёхблочная сетка со сгущением](screenshots/LR2/graded_mesh.png)

## Граничные условия

Условия одинаковы для всех квадратных ламинарных cases; в `cavityClipped` patch `movingWall` называется `lid`.

| Patch | Поле | Тип | Значение | Физический смысл |
|---|---|---|---|---|
| `movingWall` / `lid` | `U` | `fixedValue` | `(1 0 0)` м/с | движущаяся верхняя крышка |
| `fixedWalls` | `U` | `noSlip` | 0 | неподвижные твёрдые стенки |
| `movingWall` / `lid` | `p` | `zeroGradient` | нормальный градиент 0 | давление не фиксируется на стенке |
| `fixedWalls` | `p` | `zeroGradient` | нормальный градиент 0 | то же |
| `frontAndBack` | `U`, `p` | `empty` | — | двумерность задачи |

Для `cavityRAS` дополнительно присутствуют `k`, `epsilon` и `nut`; в `constant/momentumTransport` реально заданы `simulationType RAS` и модель `kEpsilon`.

## Настройка расчёта

Ламинарные cases решались `icoFoam`. В `constant/physicalProperties` задана кинематическая вязкость. Для базового случая `controlDict` содержит `endTime=1`, `deltaT=0.005`, `writeInterval=20`; для fine шаг уменьшен до 0,0025 с. `fvSchemes` использует Euler по времени, Gauss linear для градиентов и интерполяции, `div(phi,U) Gauss linear`. В `fvSolution` применены PCG/DIC для `p`, `smoothSolver/symGaussSeidel` для `U` и два корректора PISO.

Для `cavityRAS`: `endTime=20`, `deltaT=0.02`; алгоритм относится к модулю `incompressibleFluid`. Финальный maxCo=1,00305 на 0,3% выше единицы; расчёт завершился штатно, но это превышение нельзя скрывать.

## Выполнение работы

В журналах зафиксирована следующая последовательность.

```bash
blockMesh
```

Создаёт сетку по `system/blockMeshDict`.

```bash
checkMesh -allGeometry -allTopology
```

Проверяет геометрию и топологию. Для fine отдельный журнал этой команды не найден, поэтому её результат для этого case не утверждается.

```bash
icoFoam
```

Выполняет переходный ламинарный расчёт. Так рассчитаны `cavityBase`, `cavityFine`, `cavityGrade`, `cavityHighRe` и `cavityClipped`.

```bash
mapFields -consistent ../cavity
```

Так поля базового решения были перенесены на fine-сетку. Для graded-сетки журнал фиксирует `mapFields -consistent -sourceTime 0.7 /home/pavel/openfoam-lab/cavityFine`.

```bash
mapFields -sourceTime 0.5 /home/pavel/openfoam-lab/cavity
```

Переносит поля на отличающуюся геометрию `cavityClipped`; `mapFieldsDict` задаёт `patchMap (lid movingWall)`.

```bash
pisoFoam
```

Запускает расчёт RAS. В OpenFOAM 13 устаревшее имя перенаправляется на общий модуль `foamRun -solver incompressibleFluid`.

```bash
foamPostProcess -func components(U)
```

Создаёт скалярные компоненты `Ux`, `Uy`, `Uz` для построения профилей.

## Результаты и обсуждение

Все solver logs заканчиваются строкой `End`. Финальные значения числа Куранта: base 0,852134; fine 0,926452; graded 0,440057; highRe 0,839937; clipped 0,834722; RAS 1,00305.

![Кинематическое давление в базовой полости](screenshots/LR2/base_pressure.png)

![Линии тока базового случая](screenshots/LR2/base_streamlines.png)

Движущаяся крышка формирует главный вихрь по часовой стрелке: поток идёт вправо у крышки, вниз вдоль правой стенки и возвращается влево у дна.

![Сравнение профилей Ux на грубой и fine-сетке](screenshots/LR2/ux_profile_coarse_fine.png)

Сравнение профилей показывает влияние разрешения сетки, особенно около стенок с большими градиентами скорости.

![Поле скорости при Re=100](screenshots/LR2/highRe_velocity.png)

![Поле скорости RAS при Re=10000](screenshots/LR2/ras_velocity.png)

![Поле после переноса на полость с вырезом, t=0,5 с](screenshots/LR2/clipped_t0_5.png)

![Адаптированное поле в полости с вырезом, t=0,6 с](screenshots/LR2/clipped_t0_6.png)

## Вывод

Выполнен полный цикл OpenFOAM: генерация и контроль сеток, расчёты при разных Re, перенос полей и постобработка. Уточнение и сгущение сетки лучше разрешают пристеночные градиенты; уменьшение вязкости усиливает инерционные и вихревые эффекты. Все вычислительные варианты завершены штатно; единственная явно неподтверждённая позиция — отдельный результат `checkMesh` для `cavityFine`.
