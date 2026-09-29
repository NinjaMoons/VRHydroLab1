# Фактический аудит пояснительной записки V2

Дата проверки: 14 сентября 2026 года. Проверяемый источник: `docs/REPORT_MASTER_V2.md`.

## Технические утверждения

| Claim | Value | Evidence | Status |
|---|---|---|---|
| вариант и среда | №3, вода | `settings.json`, HDF/UNV, settings принятых runs | VERIFIED |
| приложение | `course-project-v3-channel`; UI «Расчёт канала с квадратными препятствиями» | `app/package.json`, `app/public/index.html` | VERIFIED |
| frontend | HTML, CSS, браузерный JavaScript без framework | `app/public/*` | VERIFIED |
| backend | Node.js, встроенный HTTP API, без npm-зависимостей | `app/server.js`, `package.json` | VERIFIED |
| orchestration | Python 3, последовательный pipeline, без MPI | `scripts/run_pipeline.py` | VERIFIED |
| SALOME | 9.16.0, GEOM/SMESH, NETGEN 1D–2D, quad-dominant | `salome/generate_mesh.py`, HDF/UNV, `mesh_summary.json` | VERIFIED |
| OpenFOAM | Foundation 13, `foamRun -solver incompressibleFluid` | environment logs, pipeline и solver logs | VERIFIED |
| ParaView | 6.1.1, `pvpython` и интерактивное открытие case | `render_results.py`, server route, `paraview_summary.json` | VERIFIED |
| baseline geometry | `L=326, H=23, a=12, P=60, S=30, Y=8, R=60 мм` | `settings.json`, `geometry.py` | VERIFIED |
| baseline velocity | `Uin=0.1 м/с` | `settings.json`, `case/0/U`, summary | VERIFIED |
| пользовательские диапазоны | `L 100…1000`, `H 15…200`, `a 2…50`, `P 10…250`, `S 1…250`, `Y 1…199`, `R 10…500 мм`, `Uin 0.005…2 м/с` | объект `limits` в `app/server.js` | VERIFIED |
| центры baseline | upper: (86,15), (146,15), (206,15), (266,15); lower: (116,8), (176,8), (236,8) мм | `geometry.py` и `derived` в summary | VERIFIED |
| свойства воды | `nu=1.006e-6 м²/с`, `rho=998.2 кг/м³` | `physicalProperties`, settings/summary | VERIFIED |
| характерные числа | `Re_a=1192.842942`, `Re_H=2286.282306` | `derived.json` и baseline summary | VERIFIED |
| turbulence | RAS `kOmegaSST`, turbulence on | `constant/momentumTransport` | VERIFIED |
| temporal algorithm | steady SIMPLE до 2500 как инициализация; transient Euler/PIMPLE до 2501 | steady/transient dictionaries и solver logs | VERIFIED |
| max Co control | `maxCo=0.7`; наблюдалось 0.6914771 baseline | transient `controlDict` и baseline solver log | VERIFIED |
| patches | `inlet`, `outlet`, `walls`, `obstacles`, `frontAndBack` | `polyMesh/boundary`, field files | VERIFIED |
| boundary conditions | `U,p,k,omega,nut` по таблице 6 | фактические файлы `case/0/*` | VERIFIED |
| baseline mesh | 11364 points, 5267 cells, 5101 hex, 166 prisms, 1 слой Z | `mesh_summary.json`, `log.checkMesh` | VERIFIED |
| mesh quality | aspect 2.5618444; non-orthogonality max/avg 41.596905°/4.8437362°; skewness 2.5947718; determinant 0.027537398 | `validation/reference_mesh/log.checkMesh` | VERIFIED |
| mesh acceptance | `Mesh OK` | reference и run logs | VERIFIED |
| baseline velocity extrema | 0.001867985…0.46627613 м/с по ячейкам | `results/summary.json` и `log.Uminmax` | VERIFIED |
| baseline pressure range | −138.030676756…315.580091512 Па | `summary.json`, `log.pminmax`, `rho` | VERIFIED |
| baseline pressure drop | 305.970689626 Па | area-average `p` logs и `rho` | VERIFIED |
| baseline flow rate | `Qin=Qout=2.3e-6 м³/с`, imbalance 0.0% | inlet/outlet flow logs и summary | VERIFIED |
| baseline solver finish | final time 2501 с, final step 0.00059680162 с, continuity −4.2313741e−11, final `End` | baseline solver log | VERIFIED |
| speed run B | `Uin=0.15`, 5267 cells, `max|U|=0.73750655 м/с`, `Δp=682.065777722 Па` | `runs/speed_v3_u0p15/results/summary.json` | VERIFIED |
| geometry run C | `L=350,H=25,a=11,P=62,S=31 мм`, 6518 cells, `max|U|=0.39990055 м/с`, `Δp=180.958577198 Па` | `runs/geometry_v3_changed/results/summary.json` | VERIFIED |
| parameterization | A/B/C имеют разные settings и соответствующие artifacts | `runs/*` и `validation/run_comparison.json` | VERIFIED |
| error handling | invalid input, controlled exit, HTTP 409 and recovery | `validation/acceptance_test_results.json`, server/client source | VERIFIED |
| reference/application comparison | reference и baseline: 11364 points, 5267 cells, 5101/166 elements, одинаковые quality metrics и `Mesh OK` | reference `log.checkMesh` и baseline logs/summary | VERIFIED |
| отдельный manual solver-run | не использован как доказательство; сохранена только reference-сетка | inventory `validation/reference_mesh` | NOT USED |
| сеточная независимость | отдельное исследование не выполнялось | scope проекта и отсутствие такой серии runs | NOT USED |
| эксперимент/DNS/LES | сравнение не выполнялось | scope проекта и отсутствие таких artifacts | NOT USED |
| физическая интерпретация U/p/streamlines | ускорение в сужениях, торможение перед гранями, wake/recirculation | существующие поля и PNG; без новых численных claims | QUALITATIVE |

## Проверка библиографии

Все 20 позиций существуют и используются ссылками `[1]`–`[20]`. Проверены официальные страницы OpenFOAM v13, SALOME 9.16, NETGENPLUGIN, ParaView 6.1, Node.js `child_process`, Python `subprocess`, ECMA-404 и NASA Turbulence Modeling Resource. Метаданные книг Ferziger–Perić–Street и Moukalled–Mangani–Darwish подтверждены Springer, книги Versteeg–Malalasekera — Pearson. DOI статьи Menter и обзора Williamson подтверждены издательскими страницами/каталогами. URL NASA выполняет редирект на актуальный ресурс; это не меняет источник.

## Контроль текста и артефактов

- автоматический QA: 8301 слово, 14 рисунков, 13 таблиц, 15 листингов, 20 источников, 4 приложения;
- нумерация рисунков, таблиц и листингов последовательна;
- все 14 изображений существуют и читаются;
- ссылки `[1]`–`[20]` покрывают все позиции библиографии;
- чужие фамилии, чужие варианты, ошибочное упоминание воздуха и служебные placeholders отсутствуют;
- проверка точных совпадений по окнам из 20 слов в основной части 24 peer reports не нашла совпадений;
- V1 сохранён в `docs/archive/REPORT_MASTER_V1.md` и не изменён.

## Итог

FACT AUDIT V2: PASS. Все количественные утверждения сдаваемой записки имеют локальный источник. Ограничения исследования сформулированы академически и не являются фактическими неопределённостями.
