// app.js — PR-OS Command Center
// ルール: fetch → render のみ。状態を持つな。判断するな。

const API = "http://localhost:8000";

// ── 描画関数（状態を持たない） ──

function renderEvents(data) {
  const el = document.getElementById("eventList");
  if (!el) return;
  if (!data.events || data.events.length === 0) {
    el.innerHTML = '<div style="color:var(--color-text-secondary);padding:8px">イベントなし</div>';
    return;
  }
  el.innerHTML = data.events.slice().reverse().map(e => {
    const ts = new Date(e.ts * 1000).toLocaleTimeString("ja-JP");
    const ok = e.status === "success";
    const color = ok ? "var(--color-text-success)" : e.status === "running" ? "var(--color-text-warning)" : "var(--color-text-danger)";
    return `<div style="padding:4px 0;border-bottom:0.5px solid var(--color-border-tertiary);font-size:13px">
      <span style="color:var(--color-text-secondary)">${ts}</span>
      <span style="margin:0 8px;color:${color}">●</span>
      <span>${e.action}</span>
      <span style="margin-left:8px;color:var(--color-text-secondary)">${e.status}</span>
      ${e.error ? `<span style="color:var(--color-text-danger);font-size:11px;margin-left:8px">${e.error}</span>` : ""}
    </div>`;
  }).join("");
}

function renderCaliber(data) {
  const scoreEl = document.getElementById("m-score");
  const eventsEl = document.getElementById("m-events");
  if (scoreEl) scoreEl.textContent = data.score ?? "-";
  if (eventsEl) eventsEl.textContent = data.total_events ?? "-";
}

function renderConnection(ok) {
  const dot = document.getElementById("conn-dot");
  const label = document.getElementById("conn-label");
  if (dot) dot.style.background = ok ? "var(--color-text-success)" : "var(--color-text-danger)";
  if (label) label.textContent = ok ? "接続中" : "未接続";
}

// ── API呼び出し（fetch → render のみ） ──

async function doSync() {
  try {
    const [evRes, calRes] = await Promise.all([
      fetch(`${API}/api/events`),
      fetch(`${API}/api/caliber`),
    ]);
    if (!evRes.ok || !calRes.ok) throw new Error("API error");
    const [evData, calData] = await Promise.all([evRes.json(), calRes.json()]);
    renderEvents(evData);
    renderCaliber(calData);
    renderConnection(true);
  } catch {
    renderConnection(false);
  }
}

async function runAction(action, payload = {}) {
  try {
    const res = await fetch(`${API}/api/action/${action}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ payload }),
    });
    await doSync(); // 実行後は即同期
  } catch {
    await doSync();
  }
}

// ── ボタンバインド ──

document.addEventListener("DOMContentLoaded", () => {
  const btnEval = document.getElementById("btn-evaluate");
  const btnSubmit = document.getElementById("btn-submit");
  const btnPublish = document.getElementById("btn-publish");

  if (btnEval) btnEval.addEventListener("click", () => runAction("evaluate"));
  if (btnSubmit) btnSubmit.addEventListener("click", () => runAction("submit"));
  if (btnPublish) btnPublish.addEventListener("click", () => runAction("publish"));

  // 初回同期 + 30秒ごと自動同期
  doSync();
  setInterval(doSync, 30000);
});
