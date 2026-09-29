"use strict";

const http = require("http");
const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");

const ROOT = __dirname;
const PUBLIC = path.join(ROOT, "public");
// Keep the default report artifacts in the project, but allow production runs
// on a VM-local filesystem.  VirtualBox shared folders are much slower for the
// tens of thousands of small solver writes.
const RUNS = path.resolve(process.env.LR7_RUN_ROOT || path.join(ROOT, "runs"));
const PORT = Number(process.env.PORT || 8082);
fs.mkdirSync(RUNS, { recursive: true });

const mime = { ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "application/javascript; charset=utf-8" };
function sendJson(res, status, body) { res.writeHead(status, { "Content-Type": "application/json; charset=utf-8" }); res.end(JSON.stringify(body)); }
function readJson(req) { return new Promise((resolve, reject) => { let body = ""; req.on("data", chunk => { body += chunk; if (body.length > 16384) req.destroy(); }); req.on("end", () => { try { resolve(JSON.parse(body)); } catch (e) { reject(e); } }); req.on("error", reject); }); }

function validate(input) {
  const p = {
    pInput: Number(input.pInput), tInput: Number(input.tInput), pOutput: Number(input.pOutput),
    massFlow: Number(input.massFlow), alpha: Number(input.alpha), beta: Number(input.beta),
  };
  if (!Number.isFinite(p.pInput) || p.pInput < 10000 || p.pInput > 2000000) throw new Error("Входное давление: 10 000…2 000 000 Па");
  if (!Number.isFinite(p.tInput) || p.tInput < 200 || p.tInput > 5000) throw new Error("Входная температура: 200…5000 K");
  if (!Number.isFinite(p.pOutput) || p.pOutput <= 0 || p.pOutput >= p.pInput) throw new Error("Выходное давление должно быть положительным и меньше входного");
  if (!Number.isFinite(p.massFlow) || p.massFlow <= 0 || p.massFlow > 100) throw new Error("Расход: 0…100 кг/с");
  if (!Number.isFinite(p.alpha) || p.alpha < 1 || p.alpha > 80 || !Number.isFinite(p.beta) || p.beta < 1 || p.beta > 80) throw new Error("Углы должны быть от 1 до 80°");
  return p;
}
function safeJob(job) { if (!/^[0-9TZ-]+$/.test(job || "")) return null; const dir = path.join(RUNS, job); return dir.startsWith(RUNS + path.sep) ? dir : null; }

async function handler(req, res) {
  const url = new URL(req.url, `http://${req.headers.host || "localhost"}`);
  if (req.method === "POST" && url.pathname === "/api/calculate") {
    try {
      const params = validate(await readJson(req));
      const job = new Date().toISOString().replace(/[:.]/g, "-");
      const dir = path.join(RUNS, job); fs.mkdirSync(dir); fs.writeFileSync(path.join(dir, "params.json"), JSON.stringify(params, null, 2)); fs.writeFileSync(path.join(dir, "status.json"), JSON.stringify({ state: "queued", job }));
      const child = spawn(process.execPath.replace(/node$/, "python3"), [path.join(ROOT, "run_calculation.py"), dir], { detached: true, stdio: "ignore" }); child.unref();
      return sendJson(res, 202, { job, state: "queued" });
    } catch (e) { return sendJson(res, 400, { error: e.message }); }
  }
  if (req.method === "GET" && url.pathname === "/api/status") {
    const dir = safeJob(url.searchParams.get("job")); if (!dir) return sendJson(res, 400, { error: "Некорректный job id" });
    try {
      const state = JSON.parse(fs.readFileSync(path.join(dir, "status.json"), "utf8"));
      const logPath = path.join(dir, "case", "log.foamRun");
      if (fs.existsSync(logPath)) {
        const log = fs.readFileSync(logPath, "utf8");
        const matches = [...log.matchAll(/^Time = ([0-9.eE+-]+)s?$/gm)];
        if (matches.length) {
          state.solverTime = Number(matches[matches.length - 1][1]);
          state.targetTime = 0.015;
          state.progressPercent = Math.min(100, 100 * state.solverTime / state.targetTime);
        }
      }
      const meshPath = path.join(dir, "case", "log.checkMesh");
      state.meshOk = fs.existsSync(meshPath) && fs.readFileSync(meshPath, "utf8").includes("Mesh OK.");
      return sendJson(res, 200, state);
    } catch (_) { return sendJson(res, 404, { error: "Job не найден" }); }
  }
  if (req.method === "GET" && url.pathname === "/api/log") {
    const dir = safeJob(url.searchParams.get("job")); if (!dir) return sendJson(res, 400, { error: "Некорректный job id" });
    try { const data = fs.readFileSync(path.join(dir, "case", "log.foamRun"), "utf8"); res.writeHead(200, { "Content-Type": "text/plain; charset=utf-8" }); return res.end(data.slice(-20000)); } catch (_) { return sendJson(res, 404, { error: "Log ещё не создан" }); }
  }
  if (req.method === "GET" && url.pathname === "/api/result") {
    const dir = safeJob(url.searchParams.get("job")); if (!dir) return sendJson(res, 400, { error: "Некорректный job id" });
    try { const data = fs.readFileSync(path.join(dir, "result.png")); res.writeHead(200, { "Content-Type": "image/png" }); return res.end(data); } catch (_) { return sendJson(res, 404, { error: "Изображение результата ещё не создано" }); }
  }
  let rel = url.pathname === "/" ? "index.html" : url.pathname.replace(/^\//, ""); if (!/^[a-zA-Z0-9_.-]+$/.test(rel)) rel = "index.html";
  const file = path.join(PUBLIC, rel);
  try { const data = fs.readFileSync(file); res.writeHead(200, { "Content-Type": mime[path.extname(file)] || "application/octet-stream" }); return res.end(data); } catch (_) { return sendJson(res, 404, { error: "Not found" }); }
}
http.createServer((req, res) => handler(req, res).catch(e => sendJson(res, 500, { error: e.message }))).listen(PORT, "127.0.0.1", () => console.log(`LR7 web app: http://127.0.0.1:${PORT}`));
