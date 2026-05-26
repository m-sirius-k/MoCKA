'use strict';
// Relay v4.1.0 — background.js
// v4.7: calcBreakEven現実ベース改定 + トークン補正係数2.5導入（誤差20%以内）
// v4.3: LB_001連番TODO番号体系 + RELAY_COMPLETE_BY_NUM / RELAY_GET_TODO_LIST 追加
// 引き継ぎ機能 (getHandoffPacket / endSession / startSession) は変更なし

const KEYS = {
  SESSIONS:  'relay_sessions',
  CURRENT:   'relay_current',
  METRICS:   'relay_metrics',
  SETTINGS:  'relay_settings',
  TODOS:     'relay_todos',
  TODO_CTR:  'relay_todo_counter',  // LB連番カウンター
};

const DEFAULT_SETTINGS = {
  work_mode: 'heavy',
  auto_inject: true,
};

const pendingRequests = new Map();

// ─── webRequest Monitoring ────────────────────────────────────────────────────

chrome.webRequest.onBeforeRequest.addListener(
  (details) => {
    pendingRequests.set(details.requestId, {
      startTime: details.timeStamp,
      url: details.url,
    });
  },
  { urls: ['https://claude.ai/*'] }
);

chrome.webRequest.onCompleted.addListener(
  (details) => {
    const req = pendingRequests.get(details.requestId);
    if (!req) return;

    const latency = details.timeStamp - req.startTime;
    const responseSize = getContentLength(details.responseHeaders);
    pendingRequests.delete(details.requestId);

    if (latency < 30 && responseSize < 200) return;

    updateMetrics({ latency, responseSize }).catch(console.error);
  },
  { urls: ['https://claude.ai/*'] },
  ['responseHeaders']
);

chrome.webRequest.onErrorOccurred.addListener(
  (details) => { pendingRequests.delete(details.requestId); },
  { urls: ['https://claude.ai/*'] }
);

function getContentLength(headers) {
  if (!headers) return 0;
  const h = headers.find(h => h.name.toLowerCase() === 'content-length');
  return h ? (parseInt(h.value, 10) || 0) : 0;
}

// ─── CPI Engine ───────────────────────────────────────────────────────────────

async function updateMetrics(measurement) {
  try {
    const stored = await chrome.storage.local.get(KEYS.METRICS);
    const metrics = stored[KEYS.METRICS] || {
      measurements: [],
      baseline: null,
      cpi: 0,
      baselineHeap: 0,
      baselineDom: 0,
      lastHeap: 0,
      lastDom: 0,
    };

    metrics.measurements.push({ ...measurement, ts: Date.now() });
    if (metrics.measurements.length > 60) {
      metrics.measurements = metrics.measurements.slice(-60);
    }

    if (metrics.measurements.length === 3 && !metrics.baseline) {
      metrics.baseline = {
        latency: avg(metrics.measurements.map(m => m.latency)),
        responseSize: avg(metrics.measurements.map(m => m.responseSize)),
      };
    }

    if (metrics.baseline) {
      metrics.cpi = computeCPI(metrics);
    }

    await chrome.storage.local.set({ [KEYS.METRICS]: metrics });
  } catch (err) {
    console.error('[Relay] updateMetrics error:', err);
  }
}

function computeCPI(metrics) {
  const { baseline, measurements, lastHeap, baselineHeap, lastDom, baselineDom } = metrics;
  if (!baseline || measurements.length < 4) return 1.0;

  const recent = measurements.slice(-3);
  const avgLatency = avg(recent.map(m => m.latency));
  const avgResponseSize = avg(recent.map(m => m.responseSize));

  const latencyRate      = baseline.latency > 0      ? avgLatency / baseline.latency           : 1.0;
  const responseSizeRate = baseline.responseSize > 0  ? avgResponseSize / baseline.responseSize : 1.0;
  const heapRate         = baselineHeap > 0           ? (lastHeap || baselineHeap) / baselineHeap : 1.0;
  const domRate          = baselineDom > 0            ? (lastDom  || baselineDom)  / baselineDom  : 1.0;

  const cpi = 0.40 * latencyRate
            + 0.25 * heapRate
            + 0.20 * domRate
            + 0.15 * responseSizeRate;

  return Math.round(cpi * 100) / 100;
}

function avg(arr) {
  if (!arr.length) return 0;
  return arr.reduce((a, b) => a + b, 0) / arr.length;
}

// ─── Session Management ───────────────────────────────────────────────────────

async function startSession(sessionId) {
  try {
    const current = {
      session_id: sessionId,
      started_at: Date.now(),
      turn_count: 0,
      estimated_tokens: 0,
      work_mode: 'heavy',
      cpi_peak: 0,
      decisions: [],
    };
    await chrome.storage.local.set({ [KEYS.CURRENT]: current });
    await chrome.storage.local.set({
      [KEYS.METRICS]: {
        measurements: [],
        baseline: null,
        cpi: 0,
        baselineHeap: 0,
        baselineDom: 0,
        lastHeap: 0,
        lastDom: 0,
      },
    });
    console.log('[Relay] Session started:', sessionId);
  } catch (err) {
    console.error('[Relay] startSession error:', err);
  }
}

async function endSession() {
  try {
    const stored = await chrome.storage.local.get([KEYS.CURRENT, KEYS.SESSIONS, KEYS.METRICS, KEYS.TODOS]);
    const current = stored[KEYS.CURRENT];
    if (!current || !current.session_id) return;

    const metrics  = stored[KEYS.METRICS]  || {};
    const todos    = stored[KEYS.TODOS]    || [];
    const sessions = stored[KEYS.SESSIONS] || [];

    const session = {
      ...current,
      ended_at:  Date.now(),
      cpi_final: metrics.cpi || 0,
      cpi_peak:  Math.max(current.cpi_peak || 0, metrics.cpi || 0),
      todos,
      summary:   generateSummary(current, todos),
    };

    sessions.unshift(session);
    if (sessions.length > 20) sessions.pop();

    await chrome.storage.local.set({ [KEYS.SESSIONS]: sessions, [KEYS.CURRENT]: null });
    console.log('[Relay] Session ended:', current.session_id);
  } catch (err) {
    console.error('[Relay] endSession error:', err);
  }
}

function generateSummary(session, todos) {
  const completed  = todos.filter(t => t.status === 'done');
  const pending    = todos.filter(t => t.status === 'active');
  const durationMin = session.started_at
    ? Math.round((Date.now() - session.started_at) / 60000)
    : 0;

  return {
    work_description: inferWorkDescription(todos),
    completed_todos:  completed.map(t => t.text),
    pending_todos:    pending.map(t => t.text),
    key_decisions:    session.decisions || [],
    duration_min:     durationMin,
  };
}

function inferWorkDescription(todos) {
  if (!todos.length) return '作業内容不明';
  const text = todos.map(t => t.text || '').join(' ').toLowerCase();
  const heavy = ['実装', '設計', 'コード', 'fix', 'implement', 'build', 'create', 'debug'];
  const review = ['確認', '調査', 'review', 'check', 'test', 'verify'];
  if (heavy.some(k => text.includes(k)))  return '実装・設計作業';
  if (review.some(k => text.includes(k))) return '確認・レビュー作業';
  return '一般作業';
}

// ─── TODO Management (v4.3: LB_001連番) ──────────────────────────────────────

// 次のLB番号を発行する
async function nextLbNum() {
  const stored = await chrome.storage.local.get(KEYS.TODO_CTR);
  const next   = (stored[KEYS.TODO_CTR] || 0) + 1;
  await chrome.storage.local.set({ [KEYS.TODO_CTR]: next });
  return next;
}

// LB_001形式にフォーマット
function lbId(num) {
  return 'LB_' + String(num).padStart(3, '0');
}

async function addTodo(text, source) {
  try {
    const stored = await chrome.storage.local.get(KEYS.TODOS);
    const todos  = stored[KEYS.TODOS] || [];

    // テキスト重複チェック（activeのみ）
    if (todos.some(t => t.text === text && t.status === 'active')) return;

    const num = await nextLbNum();
    todos.push({
      id:         lbId(num),     // LB_001形式
      num,                       // 数値（検索用）
      text,
      status:     'active',
      created_at: Date.now(),
      source:     source || 'auto',
    });
    await chrome.storage.local.set({ [KEYS.TODOS]: todos });
    console.log('[Relay] TODO added:', lbId(num), text.slice(0, 40));
  } catch (err) {
    console.error('[Relay] addTodo error:', err);
  }
}

// IDまたはnum番号で完了にする
async function completeTodoByNum(num) {
  try {
    const stored = await chrome.storage.local.get(KEYS.TODOS);
    const todos  = stored[KEYS.TODOS] || [];
    let hit = false;
    const updated = todos.map(t => {
      if (t.num === num && t.status === 'active') {
        hit = true;
        return { ...t, status: 'done', completed_at: Date.now() };
      }
      return t;
    });
    if (hit) {
      await chrome.storage.local.set({ [KEYS.TODOS]: updated });
      console.log('[Relay] TODO done: LB_' + String(num).padStart(3, '0'));
    }
    return hit;
  } catch (err) {
    console.error('[Relay] completeTodoByNum error:', err);
    return false;
  }
}

// 範囲完了（例: 1〜5）
async function completeTodoRange(from, to) {
  let count = 0;
  for (let n = from; n <= to; n++) {
    const hit = await completeTodoByNum(n);
    if (hit) count++;
  }
  return count;
}

async function completeTodo(id) {
  try {
    const stored = await chrome.storage.local.get(KEYS.TODOS);
    const todos  = (stored[KEYS.TODOS] || []).map(t =>
      t.id === id ? { ...t, status: 'done', completed_at: Date.now() } : t
    );
    await chrome.storage.local.set({ [KEYS.TODOS]: todos });
  } catch (err) {
    console.error('[Relay] completeTodo error:', err);
  }
}

async function deleteTodo(id) {
  try {
    const stored = await chrome.storage.local.get(KEYS.TODOS);
    const todos  = (stored[KEYS.TODOS] || []).filter(t => t.id !== id);
    await chrome.storage.local.set({ [KEYS.TODOS]: todos });
  } catch (err) {
    console.error('[Relay] deleteTodo error:', err);
  }
}

// activeなTODOを番号付きで返す
async function getTodoList() {
  const stored = await chrome.storage.local.get(KEYS.TODOS);
  const todos  = stored[KEYS.TODOS] || [];
  return todos.filter(t => t.status === 'active');
}

// ─── Break-Even Calculation ───────────────────────────────────────────────────

function calcBreakEven(mode, currentTokens) {
  // T* = c_handoff / k  （最適引き継ぎトークン数）
  // c_handoff: 引き継ぎコスト固定費（パケット注入+新セッション立ち上げ ≒ 1000tok）
  // k: コンテキスト劣化率（モードによる1ターンあたりの限界効用低下）
  //
  // light: テキストのみ。1ターン≒200tok。T*≒12,500tok（約60ターン）
  // heavy: コード+長文。 1ターン≒600tok。T*≒ 5,000tok（約 8ターン）
  // file:  ファイル添付。1ターン≒1,500tok。T*≒ 2,500tok（約 2ターン）
  const params = {
    light: { k: 0.08, c_handoff: 1000 },
    heavy: { k: 0.20, c_handoff: 1000 },
    file:  { k: 0.40, c_handoff: 1000 },
  };
  const { k, c_handoff } = params[mode] || params.heavy;
  const T_star   = Math.round(c_handoff / k);
  const margin   = Math.max(0, T_star - currentTokens);
  const progress = Math.min(1.0, currentTokens / T_star);
  return { T_star, margin, progress };
}

// ─── Handoff Packet ───────────────────────────────────────────────────────────
// ※ 引き継ぎ機能: 変更なし

async function getHandoffPacket() {
  try {
    const stored = await chrome.storage.local.get([KEYS.SESSIONS, KEYS.TODOS, KEYS.CURRENT]);
    const sessions    = stored[KEYS.SESSIONS] || [];
    const activeTodos = (stored[KEYS.TODOS]   || []).filter(t => t.status === 'active');
    const current     = stored[KEYS.CURRENT]  || {};

    const lines = ['[Relay引き継ぎ - 自動生成]', '━'.repeat(36), ''];

    if (activeTodos.length) {
      lines.push('■ 未完了タスク');
      activeTodos.slice(0, 10).forEach(t => lines.push(`  - [${t.id}] ${t.text}`));
      lines.push('');
    }

    if (current.session_id) {
      const d = new Date(current.started_at || Date.now());
      const dateStr = `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`;
      lines.push(`■ 現在のセッション（${dateStr}〜）`);
      lines.push(`  ターン数: ${current.turn_count || 0}`);
      lines.push('');
    }

    const recent = sessions.slice(0, 2);
    recent.forEach((session, i) => {
      const label   = i === 0 ? '前セッション' : '前々セッション';
      const ts      = session.ended_at || session.started_at;
      const d       = new Date(ts);
      const dateStr = `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`;

      lines.push(`■ ${label}（${dateStr}）`);

      if (session.summary) {
        lines.push(`  作業: ${session.summary.work_description}`);

        if (session.summary.pending_todos?.length) {
          lines.push('  未完了TODO:');
          session.summary.pending_todos.slice(0, 5).forEach(t => lines.push(`    - ${t}`));
        }

        if (session.summary.completed_todos?.length) {
          const done = session.summary.completed_todos.slice(0, 3).join(' / ');
          lines.push(`  完了済: ${done}`);
        }

        if (session.summary.key_decisions?.length) {
          lines.push('  重要決定: ' + session.summary.key_decisions.slice(0, 2).join(' / '));
        }
      }
      lines.push('');
    });

    if (!activeTodos.length && !sessions.length && !current.session_id) {
      lines.push('（引き継ぎデータなし — 新規セッション開始）');
      lines.push('');
    }

    lines.push('━'.repeat(36));
    lines.push('上記を踏まえて作業を継続してください。');

    return lines.join('\n');
  } catch (err) {
    console.error('[Relay] getHandoffPacket error:', err);
    return null;
  }
}

// ─── Message Hub ──────────────────────────────────────────────────────────────

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  handleMessage(msg).then(sendResponse).catch(err => {
    console.error('[Relay] handler error for', msg.type, err);
    sendResponse({ error: err.message });
  });
  return true;
});

async function handleMessage(msg) {
  switch (msg.type) {

    case 'RELAY_SESSION_START':
      await startSession(msg.sessionId);
      return { ok: true };

    case 'RELAY_SESSION_END':
      await endSession();
      return { ok: true };

    case 'RELAY_TURN_UPDATE': {
      const stored  = await chrome.storage.local.get(KEYS.CURRENT);
      const current = stored[KEYS.CURRENT] || {};
      // 補正係数 2.5: content.jsはClaudeの返答テキストのみ計測（text.length/4）
      // 実際は入力tok+コンテキスト蓄積+ファイル分が加算されるため補正
      // → 誤差20%以内を目標とした実用係数
      const RAW_TO_REAL = 2.5;
      const rawTokens   = msg.tokens || 150;
      current.turn_count       = (current.turn_count       || 0) + 1;
      current.estimated_tokens = (current.estimated_tokens || 0) + Math.round(rawTokens * RAW_TO_REAL);
      await chrome.storage.local.set({ [KEYS.CURRENT]: current });
      return { ok: true };
    }

    case 'RELAY_METRICS_UPDATE': {
      const stored  = await chrome.storage.local.get([KEYS.METRICS, KEYS.CURRENT]);
      const metrics = stored[KEYS.METRICS]  || {};
      const current = stored[KEYS.CURRENT]  || {};

      if (!metrics.baselineHeap && msg.heap)    metrics.baselineHeap = msg.heap;
      if (!metrics.baselineDom  && msg.domSize) metrics.baselineDom  = msg.domSize;
      if (msg.heap)    metrics.lastHeap = msg.heap;
      if (msg.domSize) metrics.lastDom  = msg.domSize;

      if (metrics.baseline) {
        metrics.cpi = computeCPI(metrics);
        if (metrics.cpi > (current.cpi_peak || 0)) {
          current.cpi_peak = metrics.cpi;
          await chrome.storage.local.set({ [KEYS.CURRENT]: current });
        }
      }

      await chrome.storage.local.set({ [KEYS.METRICS]: metrics });
      return { ok: true };
    }

    case 'RELAY_ADD_TODO':
      await addTodo(msg.text, msg.source);
      return { ok: true };

    case 'RELAY_COMPLETE_TODO':
      await completeTodo(msg.id);
      return { ok: true };

    // ── 新規: 番号指定完了 ──
    case 'RELAY_COMPLETE_BY_NUM': {
      const hit = await completeTodoByNum(msg.num);
      return { ok: hit };
    }

    // ── 新規: 範囲指定完了 ──
    case 'RELAY_COMPLETE_RANGE': {
      const count = await completeTodoRange(msg.from, msg.to);
      return { ok: true, count };
    }

    case 'RELAY_DELETE_TODO':
      await deleteTodo(msg.id);
      return { ok: true };

    case 'RELAY_GET_TODOS': {
      const stored = await chrome.storage.local.get(KEYS.TODOS);
      return { todos: stored[KEYS.TODOS] || [] };
    }

    // ── 新規: active一覧取得 ──
    case 'RELAY_GET_TODO_LIST': {
      const list = await getTodoList();
      return { todos: list };
    }

    case 'RELAY_GET_STATS': {
      const stored   = await chrome.storage.local.get([KEYS.CURRENT, KEYS.METRICS, KEYS.SETTINGS]);
      const current  = stored[KEYS.CURRENT]  || {};
      const metrics  = stored[KEYS.METRICS]  || {};
      const settings = stored[KEYS.SETTINGS] || DEFAULT_SETTINGS;
      const mode     = current.work_mode || settings.work_mode || 'heavy';
      const be       = calcBreakEven(mode, current.estimated_tokens || 0);
      return {
        turn_count:       current.turn_count       || 0,
        estimated_tokens: current.estimated_tokens || 0,
        cpi:              metrics.cpi              || 0,
        work_mode:        mode,
        break_even:       be,
        session_id:       current.session_id || null,
      };
    }

    case 'RELAY_GET_METRICS': {
      const stored = await chrome.storage.local.get(KEYS.METRICS);
      return stored[KEYS.METRICS] || { cpi: 0 };
    }

    case 'RELAY_GET_HANDOFF': {
      const packet = await getHandoffPacket();
      return { packet };
    }

    case 'RELAY_STORE_HANDOFF': {
      await chrome.storage.local.set({ relay_handoff_packet: msg.packet });
      return { ok: true };
    }

    case 'RELAY_OPEN_TAB': {
      await chrome.tabs.create({ url: 'https://claude.ai/new', active: true });
      return { ok: true };
    }

    case 'RELAY_OPEN_POPUP': {
      // サイドパネルからポップアップへ戻す
      try { await chrome.action.openPopup(); } catch (_) {}
      return { ok: true };
    }

    case 'RELAY_SET_MODE': {
      const stored   = await chrome.storage.local.get([KEYS.SETTINGS, KEYS.CURRENT]);
      const settings = { ...(stored[KEYS.SETTINGS] || DEFAULT_SETTINGS), work_mode: msg.mode };
      const current  = stored[KEYS.CURRENT] || {};
      current.work_mode = msg.mode;
      await chrome.storage.local.set({ [KEYS.SETTINGS]: settings, [KEYS.CURRENT]: current });
      return { ok: true };
    }

    default:
      return { error: `Unknown type: ${msg.type}` };
  }
}
