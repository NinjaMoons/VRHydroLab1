"use strict";

const form = document.querySelector("#parameters");
const validationBox = document.querySelector("#validation");
const channel = document.querySelector("#channel");
const coordinates = document.querySelector("#coordinates");
const reA = document.querySelector("#reA");
const reH = document.querySelector("#reH");
const statusBox = document.querySelector("#status");
const runIdBox = document.querySelector("#runId");
const stages = [...document.querySelectorAll("#stages div")];
const completionBanner = document.querySelector("#completionBanner");
const logBox = document.querySelector("#log");
const logButton = document.querySelector("#logButton");
const runSelect = document.querySelector("#runSelect");
const resultInputs = document.querySelector("#resultInputs");
const resultMeta = document.querySelector("#resultMeta");
const resultMetrics = document.querySelector("#resultMetrics");
const resultImage = document.querySelector("#resultImage");
const resultCaption = document.querySelector("#resultCaption");
const resultTabs = [...document.querySelectorAll("[data-result-image]")];
const runButton = form.querySelector("button.primary");
const meshButton = document.querySelector("#meshButton");
let defaults;
let currentValidation;
let selectedRunId = "";
let busy = false;
let validateTimer;
let activeParameter = "";
let activeResultImage = "velocity.png";

function values() {
  return Object.fromEntries(new FormData(form).entries());
}

function format(value, digits = 3) {
  return Number(value).toLocaleString("ru-RU", { maximumFractionDigits: digits });
}

function setBusy(value) {
  busy = value;
  runButton.disabled = value || !currentValidation;
  meshButton.disabled = value || !currentValidation;
}

function showMessage(message, type = "") {
  completionBanner.textContent = message;
  completionBanner.className = `completion ${type}`.trim();
  completionBanner.hidden = !message;
}

function renderPairs(container, pairs) {
  container.replaceChildren(...pairs.map(([label, value]) => {
    const item = document.createElement("div");
    const term = document.createElement("span");
    const content = document.createElement("strong");
    term.textContent = label;
    content.textContent = value;
    item.append(term, content);
    return item;
  }));
}

function selectResultImage(name, caption) {
  activeResultImage = name;
  resultImage.dataset.image = name;
  resultImage.alt = caption;
  resultCaption.textContent = caption;
  resultTabs.forEach(tab => {
    const selected = tab.dataset.resultImage === name;
    tab.classList.toggle("active", selected);
    tab.setAttribute("aria-selected", String(selected));
  });
  if (selectedRunId) {
    resultImage.src = `/api/image?run=${encodeURIComponent(selectedRunId)}&name=${encodeURIComponent(name)}`;
  }
}

function applyHighlight(parameter) {
  document.querySelectorAll("[data-param]").forEach(element => {
    const parameters = String(element.dataset.param || "").split(/\s+/);
    element.classList.toggle("is-highlighted", Boolean(parameter) && parameters.includes(parameter));
  });
}

function dimensionHorizontal(parameter, x1, x2, y, label, textY = y - 8) {
  return `<g class="dimension-group" data-param="${parameter}">
    <line x1="${x1}" y1="${y}" x2="${x2}" y2="${y}" marker-start="url(#dim-start)" marker-end="url(#dim-end)"/>
    <line x1="${x1}" y1="${y - 9}" x2="${x1}" y2="${y + 9}"/><line x1="${x2}" y1="${y - 9}" x2="${x2}" y2="${y + 9}"/>
    <text x="${(x1 + x2) / 2}" y="${textY}" text-anchor="middle">${label}</text>
  </g>`;
}

function dimensionVertical(parameter, x, y1, y2, label, side = "right") {
  const textX = side === "left" ? x - 13 : x + 13;
  const anchor = side === "left" ? "end" : "start";
  return `<g class="dimension-group" data-param="${parameter}">
    <line x1="${x}" y1="${y1}" x2="${x}" y2="${y2}" marker-start="url(#dim-start)" marker-end="url(#dim-end)"/>
    <line x1="${x - 9}" y1="${y1}" x2="${x + 9}" y2="${y1}"/><line x1="${x - 9}" y1="${y2}" x2="${x + 9}" y2="${y2}"/>
    <text x="${textX}" y="${(y1 + y2) / 2 + 5}" text-anchor="${anchor}">${label}</text>
  </g>`;
}

function draw(data) {
  const g = data.geometryMm;
  const x0 = 75;
  const x1 = 1025;
  const y0 = 125;
  const y1 = 305;
  const sx = (x1 - x0) / g.L;
  const sy = (y1 - y0) / g.H;
  const mapX = value => x0 + value * sx;
  const mapY = value => y1 - value * sy;
  // The channel is intentionally exaggerated vertically for readability, while
  // obstacles remain visually square as in the official Variant 3 drawing.
  const obstacleSide = Math.max(20, Math.min(54, 40 * g.a / 12));
  const obstacleWidth = obstacleSide;
  const obstacleHeight = obstacleSide;
  const upper = data.derived.obstacles.filter(item => item.row === "upper");
  const lower = data.derived.obstacles.filter(item => item.row === "lower");
  const obstacles = data.derived.obstacles.map((item, index) => {
    const x = mapX(item.x) - obstacleWidth / 2;
    const y = mapY(item.y) - obstacleHeight / 2;
    const marker = index === 6 ? ' data-param="a"' : "";
    return `<rect class="obstacle-shape"${marker} x="${x}" y="${y}" width="${obstacleWidth}" height="${obstacleHeight}" rx="3"><title>${item.name}: центр (${format(item.x, 1)}; ${format(item.y, 1)}) мм</title></rect>`;
  }).join("");
  const pLeft = mapX(upper[2].x);
  const pRight = mapX(upper[3].x);
  const sLeft = mapX(upper[0].x);
  const sRight = mapX(lower[0].x);
  const rLeft = mapX(upper[3].x);
  const lastUpperY = mapY(upper[3].y);
  const lowerY = mapY(lower[1].y);
  const lowerWall = y1;
  const aX1 = mapX(upper[3].x) - obstacleWidth / 2;
  const aX2 = mapX(upper[3].x) + obstacleWidth / 2;

  channel.innerHTML = `
    <defs>
      <marker id="flow-arrow" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#5de1d0"/></marker>
      <marker id="dim-start" markerWidth="8" markerHeight="8" refX="1" refY="4" orient="auto"><path d="M8 0L0 4L8 8" fill="none" stroke="context-stroke" stroke-width="1.6"/></marker>
      <marker id="dim-end" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8" fill="none" stroke="context-stroke" stroke-width="1.6"/></marker>
    </defs>
    <text class="boundary-label" x="${x0}" y="108" text-anchor="middle">inlet</text>
    <text class="boundary-label" x="${x1}" y="108" text-anchor="middle">outlet</text>
    <rect class="channel-part" data-param="L H" x="${x0}" y="${y0}" width="${x1 - x0}" height="${y1 - y0}" rx="3" fill="#236b79" stroke="#91b6b8" stroke-width="2"/>
    ${obstacles}
    <g class="dimension-group" data-param="Uin">
      <path d="M12 ${(y0 + y1) / 2}H65" stroke="#5de1d0" stroke-width="7" marker-end="url(#flow-arrow)"/>
      <text x="14" y="${(y0 + y1) / 2 - 17}" fill="#5de1d0">Uin = ${format(data.flow.Uin, 3)} м/с</text>
    </g>
    ${dimensionHorizontal("L", x0, x1, 49, `L = ${format(g.L, 1)} мм`, 36)}
    ${dimensionVertical("H", 1060, y0, y1, `H = ${format(g.H, 1)} мм`, "left")}
    ${dimensionHorizontal("P", pLeft, pRight, 91, `P = ${format(g.P, 1)} мм`, 78)}
    ${dimensionHorizontal("S", sLeft, sRight, 326, `S = ${format(g.S, 1)} мм`, 352)}
    ${dimensionHorizontal("R", rLeft, x1, 357, `R = ${format(g.R, 1)} мм`, 383)}
    ${dimensionVertical("Y", mapX(lower[1].x) + obstacleWidth / 2 + 28, lowerY, lowerWall, `Y = ${format(g.Y, 1)} мм`)}
    ${dimensionHorizontal("a", aX1, aX2, lastUpperY - obstacleHeight / 2 - 20, `a = ${format(g.a, 1)} мм`, lastUpperY - obstacleHeight / 2 - 29)}
    `;

  channel.querySelectorAll(".dimension-group[data-param]").forEach(element => {
    element.addEventListener("pointerenter", () => applyHighlight(element.dataset.param));
    element.addEventListener("pointerleave", () => applyHighlight(activeParameter));
    element.addEventListener("click", () => form.elements[element.dataset.param]?.focus());
  });
  applyHighlight(activeParameter);
  coordinates.innerHTML = data.derived.obstacles.map(item => `<span>${item.name}: (${format(item.x, 1)}; ${format(item.y, 1)}) мм</span>`).join("");
  reA.textContent = format(data.derived.Re_a, 0);
  reH.textContent = format(data.derived.Re_H, 0);
}

async function validateNow() {
  try {
    const response = await fetch("/api/validate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values()),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error);
    currentValidation = data;
    validationBox.textContent = "Параметры корректны: диапазоны, зазоры и пересечения проверены";
    validationBox.className = "validation";
    draw(data);
    setBusy(busy);
    return true;
  } catch (error) {
    currentValidation = null;
    validationBox.textContent = error.message || "Не удалось проверить параметры";
    validationBox.className = "validation bad";
    setBusy(busy);
    return false;
  }
}

function scheduleValidation() {
  clearTimeout(validateTimer);
  validateTimer = setTimeout(validateNow, 150);
}

function fill(data) {
  for (const [name, value] of Object.entries({ ...data.geometryMm, Uin: data.flow.Uin })) {
    form.elements[name].value = value;
  }
  form.elements.quality.value = data.mesh.quality;
  scheduleValidation();
}

function setStage(stage, state = "running") {
  const order = ["validate", "salome", "mesh", "case", "solver", "postprocess", "save", "complete"];
  const activeIndex = order.indexOf(stage);
  stages.forEach((element, index) => {
    if (state === "done" && stage === "complete") element.className = "done";
    else if (index < activeIndex) element.className = "done";
    else if (index === activeIndex) element.className = state === "failed" ? "failed" : state === "done" ? "done" : "active";
    else element.className = "";
  });
}

async function showRun(runId) {
  selectedRunId = runId;
  runIdBox.textContent = runId;
  logBox.hidden = true;
  logButton.textContent = "Показать журнал";
  try {
    const response = await fetch(`/api/summary?run=${encodeURIComponent(runId)}`);
    const summary = await response.json();
    if (!response.ok) throw new Error(summary.error);
    const items = [
      ["Ячеек", summary.mesh.salome.cells],
      ["max |U|", `${format(summary.velocity.cellMaximumMagnitudeMps, 4)} м/с`],
      ["Δp", `${format(summary.pressure.dropPa, 2)} Па`],
      ["Дисбаланс", `${format(summary.flow.imbalancePercent, 4)} %`],
      ["max Co", format(summary.solver.courantMax, 3)],
    ];
    renderPairs(resultMetrics, items);
    const g = summary.settings.geometryMm;
    const f = summary.settings.flow;
    renderPairs(resultInputs, [
      ["L × H", `${format(g.L)} × ${format(g.H)} мм`],
      ["a / P / S", `${format(g.a)} / ${format(g.P)} / ${format(g.S)} мм`],
      ["Y / R", `${format(g.Y)} / ${format(g.R)} мм`],
      ["Uin", `${format(f.Uin, 4)} м/с`],
      ["Качество сетки", summary.settings.mesh.quality],
      ["Rea / ReH", `${format(summary.dimensionless.Re_a, 0)} / ${format(summary.dimensionless.Re_H, 0)}`],
    ]);
    const transientInterval = Math.max(0, Number(summary.solver.finalTime) - 2500);
    renderPairs(resultMeta, [
      ["Статус", summary.status === "VERIFIED" ? "Подтверждён" : summary.status],
      ["Решатель", summary.solver.application],
      ["Режим", summary.solver.algorithm],
      ["Каталог времени", format(summary.solver.finalTime, 4)],
      ["Нестационарный интервал", `${format(transientInterval, 4)} с`],
      ["Идентификатор", summary.runId],
    ]);
    resultImage.src = `/api/image?run=${encodeURIComponent(runId)}&name=${encodeURIComponent(activeResultImage)}`;
    statusBox.textContent = "Расчёт завершён: Mesh OK, solver End, результат сохранён";
    setStage("complete", "done");
    showMessage(`Расчёт ${runId} успешно завершён. Результаты и журнал доступны ниже.`, "success");
  } catch (error) {
    statusBox.textContent = error.message || "Не удалось загрузить результат";
    showMessage(statusBox.textContent, "error");
  }
}

async function refreshRuns(preferred) {
  const response = await fetch("/api/runs");
  const runs = await response.json();
  const completed = runs.filter(run => run.summary);
  runSelect.replaceChildren(...completed.map(run => {
    const option = document.createElement("option");
    option.value = run.id;
    option.textContent = run.id;
    return option;
  }));
  const selected = preferred || (completed.some(run => run.id === "baseline_v3_u0p1") ? "baseline_v3_u0p1" : completed[0]?.id);
  if (selected) {
    runSelect.value = selected;
    await showRun(selected);
  }
}

async function poll(runId, mode) {
  try {
    const response = await fetch(`/api/status?run=${encodeURIComponent(runId)}`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.error);
    statusBox.textContent = data.message || data.stage || data.state;
    runIdBox.textContent = runId;
    setStage(data.stageKey || "validate", data.state);
    if (data.state === "done") {
      setBusy(false);
      if (mode === "full") {
        const summaryResponse = await fetch(`/api/summary?run=${encodeURIComponent(runId)}`);
        if (!summaryResponse.ok) throw new Error("Расчёт завершён, но итоговый summary.json не найден");
        await refreshRuns(runId);
      } else {
        showMessage(`Сетка ${runId} готова: UNV экспортирован, checkMesh подтвердил Mesh OK.`, "success");
      }
      return;
    }
    if (data.state === "failed") {
      setBusy(false);
      const message = data.error || data.message || "Расчёт завершился ошибкой";
      validationBox.textContent = message;
      validationBox.className = "validation bad";
      showMessage(message, "error");
      return;
    }
    setTimeout(() => poll(runId, mode), 2000);
  } catch (error) {
    setBusy(false);
    statusBox.textContent = error.message || "Ошибка получения состояния";
    showMessage(statusBox.textContent, "error");
  }
}

async function launch(endpoint, mode) {
  if (!(await validateNow())) return;
  setBusy(true);
  logBox.hidden = true;
  showMessage("");
  statusBox.textContent = "Задание передаётся на сервер";
  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values()),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error);
    selectedRunId = data.runId;
    poll(data.runId, mode);
  } catch (error) {
    setBusy(false);
    validationBox.textContent = error.message || "Не удалось запустить расчёт";
    validationBox.className = "validation bad";
    showMessage(validationBox.textContent, "error");
  }
}

form.addEventListener("input", event => {
  const parameter = event.target.name;
  if (["L", "H", "a", "P", "S", "Y", "R", "Uin"].includes(parameter)) {
    activeParameter = parameter;
    applyHighlight(parameter);
  }
  scheduleValidation();
});
document.querySelectorAll("[data-param]").forEach(label => {
  const parameter = label.dataset.param;
  if (!form.elements[parameter]) return;
  label.addEventListener("pointerenter", () => applyHighlight(parameter));
  label.addEventListener("pointerleave", () => applyHighlight(activeParameter));
  form.elements[parameter].addEventListener("focus", () => {
    activeParameter = parameter;
    applyHighlight(parameter);
  });
  form.elements[parameter].addEventListener("blur", () => {
    activeParameter = "";
    applyHighlight("");
  });
});
form.addEventListener("submit", event => {
  event.preventDefault();
  launch("/api/calculate", "full");
});
document.querySelector("#reset").addEventListener("click", () => fill(defaults));
document.querySelector("#validateButton").addEventListener("click", validateNow);
meshButton.addEventListener("click", () => launch("/api/generate-mesh", "mesh"));

logButton.addEventListener("click", async () => {
  if (!selectedRunId) return;
  if (!logBox.hidden) {
    logBox.hidden = true;
    logButton.textContent = "Показать журнал";
    return;
  }
  const response = await fetch(`/api/log?run=${encodeURIComponent(selectedRunId)}`);
  logBox.textContent = response.ok ? await response.text() : (await response.json()).error;
  logBox.hidden = false;
  logButton.textContent = "Скрыть журнал";
});

document.querySelector("#openParaView").addEventListener("click", async () => {
  if (!selectedRunId) return;
  const response = await fetch(`/api/open-paraview?run=${encodeURIComponent(selectedRunId)}`, { method: "POST" });
  const data = await response.json();
  statusBox.textContent = response.ok ? `ParaView открыт для ${selectedRunId}` : data.error;
});

document.querySelector("#newCalculation").addEventListener("click", () => {
  fill(defaults);
  showMessage("");
  logBox.hidden = true;
  statusBox.textContent = "Готово к новому запуску";
  setStage("validate");
  form.scrollIntoView({ behavior: "smooth", block: "start" });
});

runSelect.addEventListener("change", () => showRun(runSelect.value));
resultTabs.forEach(tab => tab.addEventListener("click", () => {
  selectResultImage(tab.dataset.resultImage, tab.dataset.resultCaption);
}));

async function init() {
  const response = await fetch("/api/defaults");
  defaults = await response.json();
  fill(defaults);
  await refreshRuns("baseline_v3_u0p1");
}

init().catch(error => {
  statusBox.textContent = error.message || "Не удалось инициализировать приложение";
  showMessage(statusBox.textContent, "error");
});
