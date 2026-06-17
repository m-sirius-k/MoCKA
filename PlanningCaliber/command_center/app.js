const API = "http://127.0.0.1:8000/api";

// ── 接続状態 ─────────────────────────────────────
async function checkConnection() {
  try {
    await fetch(`${API}/events`, { signal: AbortSignal.timeout(2000) });
    setOnline(true);
  } catch {
    setOnline(false);
  }
}

function setOnline(online) {
  const dot   = document.getElementById("conn-dot");
  const label = document.getElementById("conn-label");
  const status = document.getElementById("api-status");
  if (online) {
    dot.classList.remove("offline");
    label.style.color = "var(--green)";
    label.textContent = "ONLINE";
    if (status) { status.style.color = "var(--green)"; status.textContent = "接続中"; }
  } else {
    dot.classList.add("offline");
    label.style.color = "var(--red)";
    label.textContent = "OFFLINE";
    if (status) { status.style.color = "var(--red)"; status.textContent = "未接続"; }
  }
}

// ── Caliber ───────────────────────────────────────
async function loadCaliber() {
  try {
    const res  = await fetch(`${API}/caliber`);
    const data = await res.json();

    const scoreEl = document.getElementById("m-score");
    const deltaEl = document.getElementById("m-score-delta");
    const avgEl   = document.getElementById("caliber-avg");

    if (scoreEl) scoreEl.textContent = data.score.toFixed(3);
    if (deltaEl) { deltaEl.textContent = `直近${data.items.length}件の平均`; deltaEl.style.color = "var(--text2)"; }
    if (avgEl)   avgEl.textContent = `APIスコア: ${data.score.toFixed(3)}（直近 ${data.items.length} 件）`;
  } catch {
    const scoreEl = document.getElementById("m-score");
    if (scoreEl) scoreEl.textContent = "—";
  }
}

// ── Events ────────────────────────────────────────
async function loadEvents() {
  try {
    const res  = await fetch(`${API}/events`);
    const data = await res.json();

    const evEl    = document.getElementById("m-events");
    const deltaEl = document.getElementById("m-events-delta");
    if (evEl)    evEl.textContent = data.length;
    if (deltaEl) { deltaEl.textContent = "直近50件表示中"; deltaEl.style.color = "var(--text2)"; }

    const list = document.getElementById("eventList");
    if (!list) return;

    if (data.length === 0) {
      list.innerHTML = `<div class="event-item">
        <div class="event-icon update">📭</div>
        <div class="event-text" style="color:var(--text2)">イベントなし（バックエンド接続済み）</div>
        <span class="event-time">—</span>
      </div>`;
      return;
    }

    list.innerHTML = data.slice().reverse().slice(0, 6).map(e => {
      const ts   = new Date(e.ts * 1000);
      const time = ts.toTimeString().slice(0, 8);
      const icon = iconFor(e.action);
      const result = e.result ? JSON.stringify(e.result).slice(0, 60) : "";
      return `<div class="event-item">
        <div class="event-icon action">${icon}</div>
        <div class="event-text"><b>${e.action}</b> ${result}</div>
        <span class="event-time">${time}</span>
      </div>`;
    }).join("");
  } catch {
    // サイレントフェイル（接続チェックで状態表示済み）
  }
}

function iconFor(action) {
  const map = { evaluate: "⚖️", submit: "📤", publish: "📡", sync: "🔄" };
  return map[action] || "▶️";
}

// ── Action 実行 ───────────────────────────────────
async function runAction(action) {
  const btn = document.getElementById(`btn-${action}`);
  if (btn) btn.classList.add("running");

  try {
    await fetch(`${API}/action/${action}`, { method: "POST" });
    await loadAll();
  } catch {
    setOnline(false);
  } finally {
    if (btn) btn.classList.remove("running");
  }
}

// ── 全同期 ────────────────────────────────────────
async function doSync() {
  await checkConnection();
  await loadCaliber();
  await loadEvents();

  const el  = document.getElementById("lastSync");
  const now = new Date();
  const ts  = now.getFullYear() + "-"
            + String(now.getMonth() + 1).padStart(2, "0") + "-"
            + String(now.getDate()).padStart(2, "0") + " "
            + String(now.getHours()).padStart(2, "0") + ":"
            + String(now.getMinutes()).padStart(2, "0") + ":"
            + String(now.getSeconds()).padStart(2, "0");
  if (el) el.textContent = "最終同期: " + ts;
}

async function loadAll() {
  await loadCaliber();
  await loadEvents();
}

// ── 初期化 ────────────────────────────────────────
checkConnection();
loadAll();
setInterval(doSync, 30000);
