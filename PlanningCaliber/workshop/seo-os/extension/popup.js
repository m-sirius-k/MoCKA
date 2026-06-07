const API = "http://localhost:8750";
let currentTab = "pending";
let rejectTargetId = null;

// ── 起動 ──────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  checkServer();
  load();
  setInterval(() => { checkServer(); load(); }, 15000);
});

// ── サーバー状態確認 ───────────────────────────────
async function checkServer() {
  const dot = document.getElementById("server-status");
  try {
    const r = await fetch(`${API}/api/jobs`,
                          {signal: AbortSignal.timeout(2000)});
    dot.className = r.ok
      ? "status-dot online"
      : "status-dot offline";
  } catch {
    dot.className = "status-dot offline";
  }
}

// ── データ読み込み ─────────────────────────────────
async function load() {
  try {
    const [pending, approved, running, done, failed] =
      await Promise.all([
        fetchJobs("pending"),
        fetchJobs("approved"),
        fetchJobs("running"),
        fetchJobs("done"),
        fetchJobs("failed")
      ]);

    // Stats更新
    document.getElementById("cnt-pending").textContent =
      pending.length;
    document.getElementById("cnt-running").textContent =
      running.length;
    document.getElementById("cnt-done").textContent =
      done.length;
    document.getElementById("cnt-failed").textContent =
      failed.length;

    // Tab別表示
    const map = { pending, approved, done };
    renderJobs(map[currentTab] || []);

    // バッジ通知（承認待ちあり）
    if (pending.length > 0) {
      chrome.action.setBadgeText(
        {text: String(pending.length)});
      chrome.action.setBadgeBackgroundColor(
        {color: "#c9a84c"});
    } else {
      chrome.action.setBadgeText({text: ""});
    }
  } catch(e) {
    document.getElementById("job-list").innerHTML =
      `<div class="empty-msg">
         ⚠️ サーバー未起動<br>
         <small>localhost:8750 を確認</small>
       </div>`;
  }
}

async function fetchJobs(status) {
  const r = await fetch(
    `${API}/api/jobs?status=${status}`,
    {signal: AbortSignal.timeout(3000)});
  return r.ok ? r.json() : [];
}

// ── Job描画 ───────────────────────────────────────
function renderJobs(jobs) {
  const el = document.getElementById("job-list");
  if (!jobs.length) {
    el.innerHTML =
      '<div class="empty-msg">案件なし</div>';
    return;
  }
  el.innerHTML = jobs.map(j => `
    <div class="job-card">
      <div class="job-header">
        <span class="job-id">${j.id}</span>
        <span class="badge ${j.status}">
          ${j.status}
        </span>
      </div>
      <div class="job-title">${j.title}</div>
      <div class="job-meta">
        ${j.type} → ${j.target || "-"} |
        ${j.ai_draft ? "🤖 AI生成" : "✍️ 博士起草"} |
        P${j.priority}
      </div>
      <div class="job-actions">
        ${j.status === "pending" ? `
          <button class="btn-approve"
            onclick="approve('${j.id}')">
            承認
          </button>
          <button class="btn-reject"
            onclick="openReject('${j.id}')">
            却下
          </button>` : ""}
        ${j.status === "approved" ? `
          <button class="btn-run"
            onclick="runJob('${j.id}')">
            ▶ 実行
          </button>` : ""}
      </div>
    </div>
  `).join("");
}

// ── Tab切替 ───────────────────────────────────────
function setTab(tab) {
  currentTab = tab;
  document.querySelectorAll(".tab").forEach(b => {
    b.classList.remove("active");
  });
  document.getElementById(`tab-${tab}`)
          .classList.add("active");
  load();
}

// ── Job操作 ───────────────────────────────────────
async function approve(id) {
  await fetch(`${API}/api/jobs/${id}/approve`,
              {method: "POST"});
  load();
}

async function runJob(id) {
  await fetch(`${API}/api/jobs/${id}/run`,
              {method: "POST"});
  load();
}

function openReject(id) {
  rejectTargetId = id;
  document.getElementById("reject-modal")
          .classList.remove("hidden");
}

function hideReject() {
  rejectTargetId = null;
  document.getElementById("reject-modal")
          .classList.add("hidden");
  document.getElementById("reject-reason").value = "";
}

async function submitReject() {
  const reason =
    document.getElementById("reject-reason").value;
  await fetch(
    `${API}/api/jobs/${rejectTargetId}/reject`,
    {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({reason})
    });
  hideReject();
  load();
}

// ── New Job ───────────────────────────────────────
function showNewJob() {
  document.getElementById("new-job-form")
          .classList.remove("hidden");
}

function hideNewJob() {
  document.getElementById("new-job-form")
          .classList.add("hidden");
}

async function submitJob() {
  const body = {
    title:    document.getElementById("f-title").value,
    type:     document.getElementById("f-type").value,
    target:   document.getElementById("f-target").value,
    pipeline: document.getElementById("f-pipeline").value,
    ai_draft: document.getElementById("f-ai").value,
    priority: 3,
    note:     document.getElementById("f-note").value
  };
  if (!body.title) return;
  await fetch(`${API}/api/jobs`, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify(body)
  });
  hideNewJob();
  load();
}

// ── フル画面 ──────────────────────────────────────
function openDashboard() {
  chrome.tabs.create({url: `${API}`});
}
