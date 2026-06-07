/**
 * PR-OS Command Center — Dashboard
 * knowledge_store/index.json + scheduler/queue.json を読み込み各ビューを描画
 */

'use strict';

// ── State ──────────────────────────────────────────
let _ksIndex   = { records: [] };
let _queueData = { queue: [] };

// ── Navigation ──────────────────────────────────────
function goto(name, el) {
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('pane-' + name).classList.add('active');
  if (el) el.classList.add('active');

  const titles = {
    dashboard: 'Dashboard',
    knowledge: 'Knowledge Board',
    publish:   'Publish Manager',
    adapters:  'Adapters (TSI)',
    aigate:    'AI Gate',
    scheduler: 'Scheduler',
    analytics: 'Analytics (GA4)',
    rewriter:  'AI Rewriter',
  };
  document.getElementById('page-title').textContent = titles[name] || name;

  if (name === 'knowledge') renderKS();
  if (name === 'publish')   renderPublish();
  if (name === 'scheduler') renderQueue();
}

// ── Data Fetching ────────────────────────────────────
async function loadIndex() {
  try {
    const r = await fetch('../knowledge_store/index.json?_=' + Date.now());
    if (r.ok) _ksIndex = await r.json();
  } catch { /* fallback: keep existing */ }
  return _ksIndex;
}

async function loadQueue() {
  try {
    const r = await fetch('../scheduler/queue.json?_=' + Date.now());
    if (r.ok) _queueData = await r.json();
  } catch { /* fallback */ }
  return _queueData;
}

async function refreshAll() {
  await Promise.all([loadIndex(), loadQueue()]);
  renderDashboard();
  const active = document.querySelector('.tab-pane.active');
  if (active?.id === 'pane-knowledge') renderKS();
  if (active?.id === 'pane-publish')   renderPublish();
  if (active?.id === 'pane-scheduler') renderQueue();
}

// ── Helpers ──────────────────────────────────────────
const fmt = iso => iso ? iso.slice(0, 10) : '—';

function statusBadge(s) {
  const m = {
    confirmed:        ['b-green',  '確定済み'],
    draft:            ['b-gray',   'Draft'],
    pending_approval: ['b-yellow', '承認待ち'],
    rejected:         ['b-red',    '差し戻し'],
  };
  const [cls, label] = m[s] || ['b-gray', s];
  return `<span class="badge ${cls}">${label}</span>`;
}

function pubBadge(s) {
  const m = {
    published: ['b-green',  '公開済み'],
    scheduled: ['b-blue',   '予約済み'],
    pending:   ['b-yellow', '保留中'],
    failed:    ['b-red',    'エラー'],
    not_set:   ['b-gray',   '未設定'],
  };
  const [cls, label] = m[s] || ['b-gray', s || '未設定'];
  return `<span class="badge ${cls}">${label}</span>`;
}

function jobBadge(s) {
  const m = {
    pending:   ['b-yellow', 'Pending'],
    running:   ['b-blue',   'Running'],
    done:      ['b-green',  'Done'],
    failed:    ['b-red',    'Failed'],
    cancelled: ['b-gray',   'Cancelled'],
  };
  const [cls, label] = m[s] || ['b-gray', s];
  return `<span class="badge ${cls}">${label}</span>`;
}

function scoreBar(score) {
  if (score == null) return '<span style="color:var(--muted)">—</span>';
  const pct   = Math.round(score * 100);
  const color = score >= 0.9 ? 'var(--green)'
              : score >= 0.8 ? 'var(--accent)'
              : score >= 0.6 ? 'var(--yellow)'
              : 'var(--red)';
  return `
    <div class="score-bar">
      <div class="score-track">
        <div class="score-fill" style="width:${pct}%;background:${color}"></div>
      </div>
      <span style="font-size:12px;color:${color};width:36px;text-align:right">${score.toFixed(2)}</span>
    </div>`;
}

function updateScoreDist(records, suffix = '') {
  const scores = records.map(r => r.ai_gate_log?.score).filter(s => s != null);
  const total  = Math.max(scores.length, 1);
  const cnt    = { excellent: 0, good: 0, review: 0, reject: 0 };
  scores.forEach(s => {
    if (s >= 0.9)      cnt.excellent++;
    else if (s >= 0.8) cnt.good++;
    else if (s >= 0.6) cnt.review++;
    else               cnt.reject++;
  });
  for (const [k, v] of Object.entries(cnt)) {
    const el  = document.getElementById(`sc${suffix}-${k}`);
    const bar = document.getElementById(`sd${suffix}-${k}`);
    if (el)  el.textContent = v;
    if (bar) bar.style.width = Math.round(v / total * 100) + '%';
  }
}

// ── Dashboard ────────────────────────────────────────
function renderDashboard() {
  const records = _ksIndex.records || [];

  document.getElementById('s-total').textContent     = records.length;
  document.getElementById('s-confirmed').textContent = records.filter(r => r.status === 'confirmed').length;
  document.getElementById('s-pending').textContent   = records.filter(r => r.status === 'pending_approval').length;

  let pub = 0;
  records.forEach(r => Object.values(r.publish_status || {}).forEach(s => { if (s === 'published') pub++; }));
  document.getElementById('s-published').textContent = pub;

  // 最近のKS
  const el    = document.getElementById('recent-ks');
  const recent = [...records].reverse().slice(0, 6);
  if (!recent.length) {
    el.innerHTML = '<div class="empty-state"><div class="empty-icon">◧</div>まだ Knowledge Source がありません</div>';
  } else {
    el.innerHTML = `
      <div class="table-wrap"><table>
        <thead><tr><th>ID</th><th>タイトル</th><th>ステータス</th><th>スコア</th><th>作成日</th></tr></thead>
        <tbody>
          ${recent.map(r => `<tr>
            <td><code>${r.id}</code></td>
            <td>${r.title}</td>
            <td>${statusBadge(r.status)}</td>
            <td>${scoreBar(r.ai_gate_log?.score)}</td>
            <td>${fmt(r.created_at)}</td>
          </tr>`).join('')}
        </tbody>
      </table></div>`;
  }

  updateScoreDist(records, '');
  updateScoreDist(records, '2');
}

// ── Knowledge Board ──────────────────────────────────
function renderKS() {
  const filter  = document.getElementById('ks-filter')?.value || '';
  const records = [...(_ksIndex.records || [])].reverse()
    .filter(r => !filter || r.status === filter);
  const tbody = document.getElementById('ks-tbody');

  if (!records.length) {
    tbody.innerHTML = `<tr><td colspan="7" class="empty-state"><div class="empty-icon">◧</div>レコードがありません</td></tr>`;
    return;
  }

  tbody.innerHTML = records.map(r => {
    const adapters = ['wordpress','x','instagram','github_pages','newsletter'];
    const pubHtml = adapters
      .filter(a => r.publish_status?.[a] && r.publish_status[a] !== 'not_set')
      .map(a => `<span title="${a}">${pubBadge(r.publish_status[a])}</span>`)
      .join(' ') || '<span class="badge b-gray">未配信</span>';

    return `<tr>
      <td><code>${r.id}</code></td>
      <td>${r.title}</td>
      <td>${statusBadge(r.status)}</td>
      <td>${scoreBar(r.ai_gate_log?.score)}</td>
      <td>${r.category || '—'}</td>
      <td>${fmt(r.created_at)}</td>
      <td>${pubHtml}</td>
    </tr>`;
  }).join('');
}

// ── Publish Manager ──────────────────────────────────
function renderPublish() {
  const records = (_ksIndex.records || []).filter(r => r.status === 'confirmed');
  const tbody   = document.getElementById('pub-tbody');

  if (!records.length) {
    tbody.innerHTML = `<tr><td colspan="7" class="empty-state"><div class="empty-icon">◉</div>確定済みKSがありません</td></tr>`;
    return;
  }

  const adapters = ['wordpress','x','instagram','github_pages','newsletter'];
  tbody.innerHTML = [...records].reverse().map(r => `
    <tr>
      <td><code>${r.id}</code></td>
      <td>${r.title}</td>
      ${adapters.map(a => `<td>${pubBadge(r.publish_status?.[a])}</td>`).join('')}
    </tr>`).join('');
}

// ── Scheduler ────────────────────────────────────────
function renderQueue() {
  const jobs  = _queueData.queue || [];
  const tbody = document.getElementById('queue-tbody');

  // 統計
  document.getElementById('q-total').textContent   = jobs.length;
  document.getElementById('q-pending').textContent = jobs.filter(j => j.status === 'pending').length;
  document.getElementById('q-done').textContent    = jobs.filter(j => j.status === 'done').length;
  document.getElementById('q-failed').textContent  = jobs.filter(j => j.status === 'failed').length;

  if (!jobs.length) {
    tbody.innerHTML = `<tr><td colspan="6" class="empty-state">
      <div class="empty-icon">◷</div>
      予約ジョブがありません<br>
      <code style="font-size:11px;margin-top:8px;display:block">python pros.py schedule KS_001 wordpress 2026-06-10T10:00:00+09:00</code>
    </td></tr>`;
    return;
  }

  tbody.innerHTML = [...jobs].reverse().map(j => `
    <tr>
      <td><code>${j.job_id}</code></td>
      <td><code>${j.ks_id}</code></td>
      <td>${j.adapter}</td>
      <td style="font-family:monospace;font-size:12px">${j.publish_at?.slice(0,16) || '—'}</td>
      <td>${jobBadge(j.status)}</td>
      <td>${fmt(j.created_at)}</td>
    </tr>`).join('');
}

// ── Clock ────────────────────────────────────────────
function updateClock() {
  const now = new Date();
  const pad = n => String(n).padStart(2, '0');
  document.getElementById('clock').textContent =
    `${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())} `
    + `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
}

// ── Init ────────────────────────────────────────────
(async () => {
  updateClock();
  setInterval(updateClock, 1000);
  await refreshAll();
  // 30秒ごとに自動更新
  setInterval(refreshAll, 30_000);
})();
