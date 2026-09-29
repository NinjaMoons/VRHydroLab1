# CourseProject_V3

Курсовой проект по дисциплине «Системы инженерного анализа», вариант №3.

Проект строит параметрический канал с семью квадратными препятствиями, создаёт фактическую CFD-сетку в SALOME 9.16, импортирует её в OpenFOAM Foundation 13, выполняет последовательный расчёт течения воды и формирует результаты ParaView. Лабораторные работы в соседних каталогах не изменяются.

Текущий подтверждённый статус ведётся в `docs/MASTER_PROGRESS.md`. Все размеры геометрии в `settings.json` заданы в миллиметрах; `Uin` задана в м/с, `nu` — в м²/с, `rho` — в кг/м³.

Основные каталоги:

- `salome` — воспроизводимая геометрия, HDF и UNV;
- `openfoam/template` — шаблон совместимого case;
- `postprocessing` — автоматизация ParaView;
- `runs` — изолированные сохранённые расчёты;
- `app` — web-приложение;
- `docs` — прогресс, решения, отчёт и материалы защиты;
- `validation` — журналы проверок.

Проверенный baseline находится в `runs/baseline_v3_u0p1`. Его `results/summary.json` построен только из сохранённых settings, журналов OpenFOAM, статистики SALOME и данных ParaView. Расчёт выполнялся последовательно: стационарный SIMPLE использован как диагностическая инициализация, отчётный участок продолжен transient PIMPLE из-за периодического вихревого следа.

## Web-приложение

Локальный интерфейс не требует установки npm-пакетов:

```bash
cd /media/sf_OpenFOAM_Labs/CourseProject_V3/app
npm start
```

Адрес: `http://127.0.0.1:8083/`. Кнопки `Validate` и `Generate Mesh` позволяют проверять параметры и сетку без CFD; `Run Calculation` запускает полный последовательный pipeline. Внешние процессы запускаются массивом аргументов, а числовые параметры проходят серверную проверку.

## Воспроизводимый полный запуск

Для заранее созданного нового каталога `runs/<run-id>` с собственным `settings.json`:

```bash
python3 scripts/run_pipeline.py --run-dir runs/<run-id>
```

Рабочие файлы создаются в `/tmp/CourseProject_V3/jobs/<run-id>`, затем HDF, UNV, case, logs, screenshots и `summary.json` копируются в persistent run. Runner не использует MPI.

Три принятых расчёта сравниваются командой:

```bash
MPLCONFIGDIR=/tmp/cpv3-matplotlib python3 validation/compare_runs.py
```

Результаты: `validation/run_comparison.csv`, `.json`, `.png`.
