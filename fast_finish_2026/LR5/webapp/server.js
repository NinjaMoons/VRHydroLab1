"use strict";

const http = require("http");
const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");

const ROOT = __dirname;
const PUBLIC = path.join(ROOT, "public");
const RUNS = path.join(ROOT, "runs");
const PORT = Number(process.env.PORT || 8081);
fs.mkdirSync(RUNS, { recursive: true });

const mime = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
};

function json(res, status, body) {
  res.writeHead(status, { "Content-Type": "application/json; charset=utf-8" });
  res.end(JSON.stringify(body));
}

function readJson(req) {
  return new Promise((resolve, reject) => {
    let body = "";
    req.on("data", (chunk) => {
      body += chunk;
      if (body.length > 16384) req.destroy();
    });
    req.on("end", () => {
      try { resolve(JSON.parse(body)); } catch (error) { reject(error); }
    });
    req.on("error", reject);
  });
}

function validated(input) {
  const values = {
    sideMm: Number(input.sideMm),
    coldK: Number(input.coldK),
    hotK: Number(input.hotK),
  };
  if (!Number.isFinite(values.sideMm) || values.sideMm < 20 || values.sideMm > 500)
    throw new Error("Сторона должна быть от 20 до 500 мм");
  if (!Number.isFinite(values.coldK) || values.coldK < 200 || values.coldK > 1000)
    throw new Error("Температура холодной стенки должна быть от 200 до 1000 K");
  if (!Number.isFinite(values.hotK) || values.hotK < 200 || values.hotK > 1000)
    throw new Error("Температура горячей стенки должна быть от 200 до 1000 K");
  if (values.hotK <= values.coldK)
    throw new Error("Температура горячей стенки должна быть выше холодной");
  return values;
}

function safeJobDir(job) {
  if (!/^[0-9TZ-]+$/.test(job)) return null;
  const dir = path.join(RUNS, job);
  return dir.startsWith(RUNS + path.sep) ? dir : null;
}

async function handler(req, res) {
  const url = new URL(req.url, `http://${req.headers.host || "localhost"}`);

  if (req.method === "POST" && url.pathname === "/api/calculate") {
    try {
      const params = validated(await readJson(req));
      const job = new Date().toISOString().replace(/[:.]/g, "-");
      const jobDir = path.join(RUNS, job);
      fs.mkdirSync(jobDir, { recursive: false });
      fs.writeFileSync(path.join(jobDir, "params.json"), JSON.stringify(params, null, 2));
      fs.writeFileSync(path.join(jobDir, "status.json"), JSON.stringify({ state: "queued", job }));
      const child = spawn(process.execPath.replace(/node$/, "python3"), [
        path.join(ROOT, "run_calculation.py"), jobDir,
        String(params.sideMm), String(params.coldK), String(params.hotK),
      ], { detached: true, stdio: "ignore" });
      child.unref();
      return json(res, 202, { job, state: "queued" });
    } catch (error) {
      return json(res, 400, { error: error.message });
    }
  }

  if (req.method === "GET" && url.pathname === "/api/status") {
    const jobDir = safeJobDir(url.searchParams.get("job") || "");
    if (!jobDir) return json(res, 400, { error: "Некорректный job id" });
    try {
      return json(res, 200, JSON.parse(fs.readFileSync(path.join(jobDir, "status.json"), "utf8")));
    } catch (_) {
      return json(res, 404, { error: "Job не найден" });
    }
  }

  if (req.method === "GET" && url.pathname === "/api/log") {
    const jobDir = safeJobDir(url.searchParams.get("job") || "");
    if (!jobDir) return json(res, 400, { error: "Некорректный job id" });
    const logPath = path.join(jobDir, "case", "log.foamRun");
    try {
      const data = fs.readFileSync(logPath, "utf8");
      res.writeHead(200, { "Content-Type": "text/plain; charset=utf-8" });
      return res.end(data.slice(-20000));
    } catch (_) {
      return json(res, 404, { error: "Log ещё не создан" });
    }
  }

  let relative = url.pathname === "/" ? "index.html" : url.pathname.replace(/^\//, "");
  if (!/^[a-zA-Z0-9_.-]+$/.test(relative)) relative = "index.html";
  const file = path.join(PUBLIC, relative);
  try {
    const data = fs.readFileSync(file);
    res.writeHead(200, { "Content-Type": mime[path.extname(file)] || "application/octet-stream" });
    return res.end(data);
  } catch (_) {
    return json(res, 404, { error: "Not found" });
  }
}

http.createServer((req, res) => {
  handler(req, res).catch((error) => json(res, 500, { error: error.message }));
}).listen(PORT, "127.0.0.1", () => {
  console.log(`LR5 web app: http://127.0.0.1:${PORT}`);
});

