const form = document.querySelector("#form");
const statusBox = document.querySelector("#status");
const logBox = document.querySelector("#log");

const labels = {
  queued: "Задание поставлено в очередь",
  preparing: "Создаётся отдельная рабочая копия case",
  meshing: "Строится/проверяется сетка и выполняется расчёт",
  done: "Расчёт завершён: Mesh OK и solver End",
  failed: "Расчёт завершился ошибкой",
};

async function poll(job) {
  const response = await fetch(`/api/status?job=${encodeURIComponent(job)}`);
  const data = await response.json();
  statusBox.textContent = data.error ? data.error : `${labels[data.state] || data.state} · ${job}`;
  statusBox.className = `status ${data.state || ""}`;
  if (data.state === "done" || data.state === "failed") {
    form.querySelector("button").disabled = false;
    const logResponse = await fetch(`/api/log?job=${encodeURIComponent(job)}`);
    if (logResponse.ok) { logBox.textContent = await logResponse.text(); logBox.hidden = false; }
    return;
  }
  setTimeout(() => poll(job), 2000);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  form.querySelector("button").disabled = true;
  logBox.hidden = true;
  const body = Object.fromEntries(new FormData(form));
  const response = await fetch("/api/calculate", {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  });
  const data = await response.json();
  if (!response.ok) {
    statusBox.textContent = data.error || "Ошибка запроса";
    statusBox.className = "status failed";
    form.querySelector("button").disabled = false;
    return;
  }
  poll(data.job);
});

