# Передача геометрических параметров

## Последовательность

`L/H/a/P/S/Y/R` вводятся в web-форме. JavaScript отправляет их JSON-объектом на Node.js server. Сервер повторно проверяет числовые диапазоны, зазоры до стенок, положение внутри канала и пересечения. Проверенные значения сохраняются в `runs/<id>/settings.json`.

Python-функция `obstacle_centres()` использует формулы:

```python
last_upper = L - R
upper_x = [last_upper - multiplier * P for multiplier in (3, 2, 1, 0)]
lower_x = [value + S for value in upper_x[:3]]
y_upper = H - Y
y_lower = Y
```

При baseline получаются центры верхнего ряда `(86;15)`, `(146;15)`, `(206;15)`, `(266;15)` мм и нижнего ряда `(116;8)`, `(176;8)`, `(236;8)` мм.

`salome/generate_mesh.py` читает тот же файл настроек, строит прямоугольник `L × H`, создаёт семь квадратов со стороной `a`, вычитает их из области и выполняет выдавливание на 1 мм. Затем создаются группы `inlet`, `outlet`, `walls`, `obstacles`, `frontAndBack`, строится сетка и сохраняются `CourseProject_V3.hdf`, `Mesh.unv` и `mesh_summary.json`.

UNV импортируется в OpenFOAM командой `ideasUnvToFoam`, после чего координаты переводятся из миллиметров в метры командой `transformPoints "scale=(0.001 0.001 0.001)"`. Типы patches назначаются по именам, а `checkMesh -allGeometry -allTopology` проверяет полученный `polyMesh`.

Фактическая цепочка:

`поля формы → JSON → проверка Node.js/Python → координаты препятствий → SALOME GEOM → SALOME SMESH → HDF/UNV → ideasUnvToFoam → polyMesh → checkMesh`.

Изменение геометрии проверено сохранённым расчётом `geometry_v3_changed`: `L=350`, `H=25`, `a=11`, `P=62`, `S=31`, `Y=8`, `R=60` мм. SALOME создал другую сетку на 6518 ячеек, а OpenFOAM подтвердил `Mesh OK`.
