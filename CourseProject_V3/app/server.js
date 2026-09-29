"use strict";

const http = require("http");
const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");

const PROJECT = path.resolve(__dirname, "..");
const PUBLIC = path.join(__dirname, "public");
const RUNS = path.resolve(process.env.CPV3_RUN_ROOT || path.join(PROJECT, "runs"));
const DEFAULTS = path.join(PROJECT, "settings.json");
const PIPELINE = path.join(PROJECT, "scripts", "run_pipeline.py");
const PORT = Number(process.env.PORT || 8083);
const PYTHON = process.env.CPV3_PYTHON || "python3";
let activeJob = null;
fs.mkdirSync(RUNS, { recursive: true });

const mime = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
};

function sendJson(res, status, body) {
  res.writeHead(status, { "Content-Type": mime[".json"], "Cache-Control": "no-store" });
  res.end(JSON.stringify(body));
}

function readJson(req) {
  return new Promise((resolve, reject) => {
    let body = "";
    req.on("data", chunk => {
      body += chunk;
      if (body.length > 65536) req.destroy(new Error("Request body is too large"));
    });
    req.on("end", () => {
      try { resolve(JSON.parse(body)); } catch (_) { reject(new Error("Некорректный JSON")); }
    });
    req.on("error", reject);
  });
}

function number(value, name) {
  if (value === null || value === undefined || String(value).trim() === "") {
    throw new Error(`Заполните поле «${name}»`);
  }
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) throw new Error(`В поле «${name}» нужно ввести число`);
  return parsed;
}

function centres(g) {
  const upper = [3, 2, 1, 0].map((m, index) => ({ name: `В${index + 1}`, x: g.L - g.R - m * g.P, y: g.H - g.Y, row: "upper" }));
  const lower = upper.slice(0, 3).map((item, index) => ({ name: `Н${index + 1}`, x: item.x + g.S, y: g.Y, row: "lower" }));
  return [...upper, ...lower];
}

function validate(input) {
  const sourceGeometry = input.geometryMm || input;
  const sourceFlow = input.flow || input;
  const sourceMesh = input.mesh || input;
  const g = Object.fromEntries(["L", "H", "a", "P", "S", "Y", "R"].map(key => [key, number(sourceGeometry[key], key)]));
  const Uin = number(sourceFlow.Uin, "Uin");
  const nu = number(sourceFlow.nu ?? 1.006e-6, "nu");
  const rho = number(sourceFlow.rho ?? 998.2, "rho");
  const limits = { L: [100, 1000], H: [15, 200], a: [2, 50], P: [10, 250], S: [1, 250], Y: [1, 199], R: [10, 500], Uin: [0.005, 2] };
  for (const [name, [low, high]] of Object.entries(limits)) {
    const value = name === "Uin" ? Uin : g[name];
    if (value < low || value > high) throw new Error(`Параметр ${name} должен находиться в диапазоне ${low}…${high}`);
  }
  if (nu <= 0 || rho <= 0) throw new Error("Вязкость и плотность воды должны быть положительными");
  if (g.S < g.a) throw new Error("Смещение S должно быть не меньше стороны препятствия a");
  if (g.P - g.S < g.a) throw new Error("Увеличьте шаг P или уменьшите S: препятствия разных рядов пересекаются");
  if (g.P < g.a) throw new Error("Шаг P должен быть не меньше стороны препятствия a");
  if (g.Y - g.a / 2 <= 0) throw new Error("Нижнее препятствие выходит за нижнюю стенку: увеличьте Y или уменьшите a");
  if (g.H - g.Y - g.a / 2 <= 0) throw new Error("Верхнее препятствие выходит за верхнюю стенку: увеличьте H или уменьшите Y/a");
  const obstacles = centres(g);
  for (const item of obstacles) {
    if (item.x - g.a / 2 <= 0 || item.x + g.a / 2 >= g.L) throw new Error(`Препятствие ${item.name} выходит за границу канала: измените L, P, S, R или a`);
  }
  for (let i = 0; i < obstacles.length; i += 1) {
    for (let j = i + 1; j < obstacles.length; j += 1) {
      if (Math.abs(obstacles[i].x - obstacles[j].x) < g.a && Math.abs(obstacles[i].y - obstacles[j].y) < g.a) {
        throw new Error(`Препятствия ${obstacles[i].name} и ${obstacles[j].name} пересекаются: измените P, S или a`);
      }
    }
  }
  const Re_a = Uin * g.a * 1e-3 / nu;
  const Re_H = Uin * g.H * 1e-3 / nu;
  const intensity = 0.16 * Math.pow(Re_H, -1 / 8);
  const lengthScale = 0.07 * g.H * 1e-3;
  const kInlet = 1.5 * Math.pow(Uin * intensity, 2);
  const omegaInlet = Math.sqrt(kInlet) / (Math.pow(0.09, 0.25) * lengthScale);
  const quality = String(sourceMesh.quality || "Medium");
  const presets = {
    Coarse: { maxSizeMm: 2.0, minSizeMm: 0.9, obstacleSizeMm: 1.0 },
    Medium: { maxSizeMm: 1.25, minSizeMm: 0.6, obstacleSizeMm: 0.75 },
    Fine: { maxSizeMm: 0.8, minSizeMm: 0.35, obstacleSizeMm: 0.45 },
  };
  if (!presets[quality]) throw new Error("Выберите качество сетки: Coarse, Medium или Fine");
  const preset = presets[quality];
  return {
    variant: 3,
    geometryMm: g,
    flow: { Uin, nu, rho, turbulenceModel: "kOmegaSST" },
    mesh: {
      quality,
      maxSizeMm: number(sourceMesh.maxSizeMm ?? preset.maxSizeMm, "maxSizeMm"),
      minSizeMm: number(sourceMesh.minSizeMm ?? preset.minSizeMm, "minSizeMm"),
      obstacleSizeMm: number(sourceMesh.obstacleSizeMm ?? preset.obstacleSizeMm, "obstacleSizeMm"),
      quadAllowed: true,
      thicknessMm: 1,
    },
    derived: { obstacles, Re_a, Re_H, turbulenceIntensity: intensity, turbulenceLengthScaleM: lengthScale, kInlet, omegaInlet },
  };
}

function safeRunId(value) {
  if (!/^[a-zA-Z0-9_.-]+$/.test(value || "")) return null;
  const resolved = path.resolve(RUNS, value);
  return resolved.startsWith(RUNS + path.sep) ? resolved : null;
}

function loadIfExists(file) {
  try { return JSON.parse(fs.readFileSync(file, "utf8")); } catch (_) { return null; }
}

function listRuns() {
  return fs.readdirSync(RUNS, { withFileTypes: true })
    .filter(entry => entry.isDirectory())
    .map(entry => {
      const dir = path.join(RUNS, entry.name);
      return {
        id: entry.name,
        status: loadIfExists(path.join(dir, "status.json")),
        summary: loadIfExists(path.join(dir, "results", "summary.json")),
      };
    })
    .filter(item => item.status || item.summary)
    .sort((a, b) => b.id.localeCompare(a.id));
}

function launch(checked, mode) {
  if (activeJob) {
    const error = new Error(`Уже выполняется расчёт ${activeJob.runId}. Дождитесь его завершения.`);
    error.statusCode = 409;
    throw error;
  }
  delete checked.derived;
  const stamp = new Date().toISOString().replace(/[:.]/g, "-");
  const runId = `${mode === "mesh" ? "mesh" : "web"}-${stamp}`;
  const runDir = path.join(RUNS, runId);
  fs.mkdirSync(runDir);
  fs.writeFileSync(path.join(runDir, "settings.json"), `${JSON.stringify(checked, null, 2)}\n`);
  const statusFile = path.join(runDir, "status.json");
  fs.writeFileSync(statusFile, `${JSON.stringify({ state: "queued", stage: "Подготовка задания", stageKey: "validate", runId, updatedAt: new Date().toISOString() }, null, 2)}\n`);
  const extra = mode === "mesh" ? ["--stop-after", "mesh"] : [];
  const child = spawn(PYTHON, [PIPELINE, "--run-dir", runDir, ...extra], { detached: true, stdio: "ignore", cwd: PROJECT });
  activeJob = { runId, child };
  const failLaunch = message => {
    const status = loadIfExists(statusFile);
    if (!status || !["done", "failed"].includes(status.state)) {
      fs.writeFileSync(statusFile, `${JSON.stringify({ state: "failed", stage: "Ошибка запуска", stageKey: status?.stageKey || "validate", runId, error: message, message, updatedAt: new Date().toISOString() }, null, 2)}\n`);
    }
  };
  child.once("error", error => {
    failLaunch(`Не удалось запустить расчёт: ${error.message}`);
    if (activeJob?.child === child) activeJob = null;
  });
  child.once("exit", code => {
    if (code !== 0) failLaunch(`Расчётный процесс завершился с кодом ${code}`);
    if (activeJob?.child === child) activeJob = null;
  });
  child.unref();
  return { runId, state: "queued", mode };
}

async function handler(req, res) {
  const url = new URL(req.url, `http://${req.headers.host || "localhost"}`);
  if (req.method === "GET" && url.pathname === "/api/defaults") {
    const defaults = JSON.parse(fs.readFileSync(DEFAULTS, "utf8"));
    return sendJson(res, 200, validate(defaults));
  }
  if (req.method === "POST" && url.pathname === "/api/validate") {
    try { return sendJson(res, 200, validate(await readJson(req))); }
    catch (error) { return sendJson(res, 400, { error: error.message }); }
  }
  if (req.method === "GET" && url.pathname === "/api/runs") return sendJson(res, 200, listRuns());
  if (req.method === "POST" && url.pathname === "/api/calculate") {
    try {
      const checked = validate(await readJson(req));
      return sendJson(res, 202, launch(checked, "full"));
    } catch (error) { return sendJson(res, error.statusCode || 400, { error: error.message }); }
  }
  if (req.method === "POST" && url.pathname === "/api/generate-mesh") {
    try { return sendJson(res, 202, launch(validate(await readJson(req)), "mesh")); }
    catch (error) { return sendJson(res, error.statusCode || 400, { error: error.message }); }
  }
  if (req.method === "POST" && url.pathname === "/api/open-paraview") {
    const runDir = safeRunId(url.searchParams.get("run"));
    const foam = runDir && path.join(runDir, "case", "course_project.foam");
    if (!runDir || !fs.existsSync(foam)) return sendJson(res, 404, { error: "OpenFOAM case не найден" });
    const executable = "/home/pavel/openfoam-lab/tools/ParaView-6.1.1-MPI-Linux-Python3.12-x86_64/bin/paraview";
    const child = spawn(executable, ["--disable-registry", `--data=${foam}`], { detached: true, stdio: "ignore", env: { ...process.env, DISPLAY: process.env.DISPLAY || ":0" } });
    child.unref();
    return sendJson(res, 202, { state: "opened", runId: path.basename(runDir) });
  }
  if (req.method === "GET" && url.pathname === "/api/status") {
    const runDir = safeRunId(url.searchParams.get("run"));
    if (!runDir) return sendJson(res, 400, { error: "Некорректный run id" });
    const status = loadIfExists(path.join(runDir, "status.json"));
    return status ? sendJson(res, 200, status) : sendJson(res, 404, { error: "Расчёт не найден" });
  }
  if (req.method === "GET" && url.pathname === "/api/summary") {
    const runDir = safeRunId(url.searchParams.get("run"));
    if (!runDir) return sendJson(res, 400, { error: "Некорректный run id" });
    const summary = loadIfExists(path.join(runDir, "results", "summary.json"));
    return summary ? sendJson(res, 200, summary) : sendJson(res, 404, { error: "Summary ещё не готов" });
  }
  if (req.method === "GET" && url.pathname === "/api/log") {
    const runDir = safeRunId(url.searchParams.get("run"));
    if (!runDir) return sendJson(res, 400, { error: "Некорректный run id" });
    const candidates = [path.join(runDir, "logs", "pipeline.log"), path.join(runDir, "logs", "solver_transient.log")];
    const file = candidates.find(candidate => fs.existsSync(candidate));
    if (!file) return sendJson(res, 404, { error: "Log ещё не создан" });
    const body = fs.readFileSync(file, "utf8");
    res.writeHead(200, { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store" });
    return res.end(body.slice(-30000));
  }
  if (req.method === "GET" && url.pathname === "/api/image") {
    const runDir = safeRunId(url.searchParams.get("run"));
    const name = url.searchParams.get("name");
    if (!runDir || !/^[a-z0-9_-]+\.png$/.test(name || "")) return sendJson(res, 400, { error: "Некорректный путь" });
    const file = path.join(runDir, "screenshots", name);
    try { const body = fs.readFileSync(file); res.writeHead(200, { "Content-Type": "image/png", "Cache-Control": "no-store" }); return res.end(body); }
    catch (_) { return sendJson(res, 404, { error: "Изображение не найдено" }); }
  }
  const rel = url.pathname === "/" ? "index.html" : url.pathname.replace(/^\//, "");
  if (!/^[a-zA-Z0-9_.-]+$/.test(rel)) return sendJson(res, 404, { error: "Not found" });
  const file = path.join(PUBLIC, rel);
  try { const body = fs.readFileSync(file); res.writeHead(200, { "Content-Type": mime[path.extname(file)] || "application/octet-stream" }); return res.end(body); }
  catch (_) { return sendJson(res, 404, { error: "Not found" }); }
}

http.createServer((req, res) => handler(req, res).catch(error => sendJson(res, 500, { error: error.message })))
  .listen(PORT, "127.0.0.1", () => console.log(`CourseProject_V3: http://127.0.0.1:${PORT}`));
