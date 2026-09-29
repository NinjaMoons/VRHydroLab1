# Передача скорости Uin от формы до OpenFOAM

## 1. Поле формы

В `app/public/index.html` скорость задаётся отдельным полем потока:

```html
<input name="Uin" type="number" min="0.005" max="2" step="0.005" required>
```

Подпись прямо указывает физический смысл и единицу: «Скорость воды на входе, Uin», м/с. На SVG это значение показано отдельной стрелкой у `inlet`, а не размерной линией.

## 2. JSON-запрос

`app/public/app.js` собирает форму через `FormData` и передаёт значения в `POST /api/validate`, `POST /api/generate-mesh` или `POST /api/calculate`:

```js
function values() {
  return Object.fromEntries(new FormData(form).entries());
}
```

## 3. Проверка и сохранение

В `app/server.js` строковое значение преобразуется в число и проверяется в диапазоне 0.005…2 м/с. Для расчёта сервер формирует структуру `flow.Uin` и записывает проверенный набор в `runs/<id>/settings.json`.

```js
const Uin = number(sourceFlow.Uin, "Uin");
if (Uin < 0.005 || Uin > 2) {
  throw new Error("Параметр Uin должен находиться в диапазоне 0.005…2");
}
```

## 4. Python-параметризация

`scripts/parameterize_case.py` читает сохранённый JSON. Помимо скорости, функция `derived_values()` рассчитывает `Re_a`, `Re_H`, начальные `k` и `omega`.

```python
velocity = float(flow["Uin"])
replace_all(
    case / "0" / "U",
    rf"uniform\s+\({NUMBER}\s+0\s+0\);",
    f"uniform ({velocity:.12g} 0 0);",
    minimum=2,
)
```

## 5. Граница inlet и решатель

В созданном case поле `0/U` получает значение `uniform (Uin 0 0)` на границе `inlet`; начальное внутреннее поле синхронизируется с той же скоростью. После этого тот же изолированный case запускается командой `foamRun -solver incompressibleFluid`.

Фактическая цепочка:

`форма Uin → JSON request → runs/<id>/settings.json → parameterize_case.py → case/0/U → inlet fixedValue → foamRun`.

Она подтверждается сохранёнными расчётами: baseline использует `Uin=0.10 м/с`, а тест скорости — `Uin=0.15 м/с`. Во втором случае `max|U|` выросло с 0.4663 до 0.7375 м/с, а перепад давления — с 305.97 до 682.07 Па.
