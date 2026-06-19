'use strict';
// Relay v4.1.0 — background.js
// v4.7: calcBreakEven現実ベース改定 + トークン補正係数2.5導入（誤差20%以内）
// v4.3: LB_001連番TODO番号体系 + RELAY_COMPLETE_BY_NUM / RELAY_GET_TODO_LIST 追加
// 引き継ぎ機能 (getHandoffPacket / endSession / startSession) は変更なし

importScripts('relay-utils.js');

const KEYS = {
  SESSIONS:        'relay_sessions',
  CURRENT:         'relay_current',
  METRICS:         'relay_metrics',
  SETTINGS:        'relay_settings',
  TODOS:           'relay_todos',
  TODO_CTR:        'relay_todo_counter',   // LB連番カウンター
  LOGBOOK_CURRENT: 'relay_logbook_current', // Free版引き継ぎパケット（直近1chat）
  PLAN:            'relay_plan',            // 'free' | 'pro' | 'one'
  DENSITY_HISTORY: 'relay_density_history', // One版密度スコア履歴
  VAULT:           'relay_logbook_vault',   // One版無制限Logbook
  LICENSE_KEY:     'relay_license_key',     // ライセンスキー文字列
  LICENSE_EXP:     'relay_license_expiry',  // 有効期限 YYYYMMDD 文字列
};

// ─── ライセンス検証キー ────────────────────────────────────────────────────────
// ⚠️  PLACEHOLDER: Cloudflare WorkerのRELAY_SECRET環境変数と必ず一致させること
// 本番デプロイ前にきむら博士が両方に同じ値を設定する
const _RELAY_VK = 'RELAY_VK_PLACEHOLDER_REPLACE_BEFORE_PRODUCTION_DEPLOY_2026';

// MOCKA_DEV_MODE: 開発者バイパス
const MOCKA_DEV_ID = "m-sirius-k";

// ─── One: ライセンス検証 (HMAC-SHA256, Web Crypto API) ───────────────────────

async function _relayHmacVerify(prefix, expiryStr, serialHex, sigHex) {
  try {
    const enc = new TextEncoder();
    const keyMaterial = await crypto.subtle.importKey(
      'raw', enc.encode(_RELAY_VK),
      { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']
    );
    const msg    = enc.encode(prefix + expiryStr + serialHex);
    const sigBuf = await crypto.subtle.sign('HMAC', keyMaterial, msg);
    const sigArr = Array.from(new Uint8Array(sigBuf)).slice(0, 8);
    const expected = sigArr.map(b => b.toString(16).padStart(2, '0')).join('').toUpperCase();
    return expected === sigHex.toUpperCase();
  } catch (e) {
    return false;
  }
}

// キー形式: RLY-P-{YYYYMMDD:8}{serial:6}{sig:16} (30文字body)
//           RLY-O-{YYYYMMDD:8}{serial:6}{sig:16}
async function validateRelayLicense(key) {
  if (!key || typeof key !== 'string') return { plan: 'free', expiry: null };
  const k = key.trim().toUpperCase();

  let prefix = '';
  if      (k.startsWith('RLY-P-')) prefix = 'RLY-P';
  else if (k.startsWith('RLY-O-')) prefix = 'RLY-O';
  else if (k.startsWith('RLY-F-')) return { plan: 'free', expiry: null }; // Free
  else return { plan: 'free', expiry: null };

  const body = k.slice(6); // prefix "RLY-P-" は6文字
  if (body.length !== 30) return { plan: 'free', expiry: null };

  const expiryStr = body.slice(0,  8);
  const serialHex = body.slice(8,  14);
  const sigHex    = body.slice(14, 30);

  // 有効期限チェック
  const expYear  = parseInt(expiryStr.slice(0, 4));
  const expMonth = parseInt(expiryStr.slice(4, 6)) - 1;
  const expDay   = parseInt(expiryStr.slice(6, 8));
  const expDate  = new Date(expYear, expMonth, expDay, 23, 59, 59);
  if (expDate < new Date()) return { plan: 'free', expiry: null, expired: true };

  // HMAC署名検証
  const valid = await _relayHmacVerify(prefix, expiryStr, serialHex, sigHex);
  if (!valid) return { plan: 'free', expiry: null };

  const plan = prefix === 'RLY-P' ? 'pro' : 'one';
  return { plan, expiry: expiryStr };
}

// ─── One: 密度エンジン定数 ────────────────────────────────────────────────────

const DENSITY_THRESHOLD = 0.65;
const SHIFT_THRESHOLD   = 0.30;

function detectBreakevenPoint(history) {
  if (history.length < 2) return 'NORMAL';
  const latest = history[history.length - 1] || 0;
  const prev   = history[history.length - 2] || 0;
  const last3  = history.slice(-3);
  if (last3.length >= 3 && last3.every(s => s >= DENSITY_THRESHOLD)) return 'HIGH_DENSITY';
  if (Math.abs(latest - prev) >= SHIFT_THRESHOLD) return 'TOPIC_SHIFT';
  return 'NORMAL';
}

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

async function startSession(sessionId, pageTitle) {
  try {
    const current = {
      session_id:       sessionId,
      page_title:       pageTitle || '',
      started_at:       Date.now(),
      turn_count:       0,
      estimated_tokens: 0,
      work_mode:        'heavy',
      cpi_peak:         0,
      decisions:        [],
      filePaths:        [],
      keywords:         [],
      convBuffer:       '',
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
    // One: density history はセッション単位でリセット
    await chrome.storage.local.remove([KEYS.DENSITY_HISTORY]);
    console.log('[Relay] Session started:', sessionId);
  } catch (err) {
    console.error('[Relay] startSession error:', err);
  }
}

// ─── Free Handoff Packet (5W1H, APIキー不要) ──────────────────────────────────

function generateFreeHandoffPacketSync(current, allTodos, capturedFiles) {
  const todos = allTodos.filter(t => t.status === 'active');
  const now   = new Date();
  const pad   = n => String(n).padStart(2, '0');
  const dateStr = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}`;

  const decisions = current.decisions || [];
  const filePaths = [...new Set([...(current.filePaths || []), ...(capturedFiles || [])])];
  const keywords  = current.keywords  || [];
  const turnCount = current.turn_count || 0;

  const topicSrc = [...decisions.slice(0, 1), ...todos.slice(0, 1).map(t => t.text)];
  const topic    = topicSrc.length ? topicSrc[0].slice(0, 60) : '作業継続';

  const lines = [
    '## 引き継ぎパケット [Relay Free]',
    `**いつ**: ${dateStr} (${turnCount}ターン)`,
    `**何を**: ${topic}`,
  ];

  if (decisions.length) {
    lines.push('**決定事項**:');
    decisions.slice(0, 5).forEach(d => lines.push(`- ${d}`));
  }

  if (todos.length) {
    lines.push('**TODO/次のアクション**:');
    todos.slice(0, 8).forEach(t => lines.push(`- [${t.id}] ${t.text}`));
  }

  if (filePaths.length) {
    lines.push('**関連ファイル**:');
    filePaths.slice(0, 5).forEach(p => lines.push(`- ${p}`));
  }

  if (keywords.length) {
    lines.push('**重要メモ**:');
    keywords.slice(0, 5).forEach(k => lines.push(`- ${k}`));
  }

  if (!decisions.length && !todos.length && !filePaths.length && !keywords.length) {
    lines.push('（引き継ぎデータなし）');
  }

  return lines.join('\n');
}

// ─── One: Vault ヘルパー ──────────────────────────────────────────────────────

function inferVaultTitle(current, todos) {
  if (current.page_title)         return current.page_title.slice(0, 60);
  const active = todos.filter(t => t.status === 'active');
  if (current.decisions?.length)  return current.decisions[0].slice(0, 40);
  if (active.length)              return active[0].text.slice(0, 40);
  if (current.keywords?.length)   return current.keywords.slice(0, 3).join(' / ').slice(0, 40);
  return `セッション (${current.turn_count || 0}ターン)`;
}

async function buildVaultPacket(selectedIds, density) {
  const s     = await chrome.storage.local.get(KEYS.VAULT);
  const vault = s[KEYS.VAULT] || [];
  const d     = density || 3;

  let entries;
  if (selectedIds?.length) {
    entries = vault.filter(e => selectedIds.includes(e.id));
  } else {
    const count = d >= 5 ? 5 : d >= 4 ? 3 : d >= 3 ? 2 : 1;
    entries = vault.slice(0, count);
  }
  if (!entries.length) return null;

  const lines = ['[Relay Vault — 文脈プリロード]', '━'.repeat(28), ''];
  const pad   = n => String(n).padStart(2, '0');

  for (const entry of entries) {
    const dt      = new Date(entry.date || entry.timestamp);
    const dateStr = `${dt.getFullYear()}-${pad(dt.getMonth()+1)}-${pad(dt.getDate())} ${pad(dt.getHours())}:${pad(dt.getMinutes())}`;

    lines.push(`【前回の続き（${dateStr}）】`);
    const summaryText = entry.summary || entry.packet || '';
    lines.push(d === 1 ? summaryText.split('\n').slice(0, 3).join('\n') : summaryText);

    if (d >= 3 && entry.decisions?.length) {
      lines.push('\n【重要決定事項】');
      entry.decisions.slice(0, d >= 5 ? undefined : 3).forEach(dec => lines.push(`- ${dec}`));
    }
    if (d >= 4 && entry.files?.length) {
      lines.push('\n【関連ファイル】');
      entry.files.slice(0, d >= 5 ? undefined : 5).forEach(f => lines.push(`- ${f}`));
    }
    if (d >= 5 && entry.todos?.length) {
      lines.push('\n【未完了TODO】');
      entry.todos.forEach(t => lines.push(`- ${t}`));
    }
    lines.push('');
  }

  lines.push('━'.repeat(28));
  lines.push('上記は前回の会話の引き継ぎ情報です。この文脈を踏まえて会話を始めてください。');
  return lines.join('\n');
}

// ─── Pro Handoff Packet (Claude API 5W1H要約) ─────────────────────────────────

async function generateProHandoffPacket(current, todos, apiKey) {
  const activeTodos = todos.filter(t => t.status === 'active');
  const convBuffer  = current.convBuffer || '';
  const decisionsText = (current.decisions || []).slice(0, 5).join('\n- ');
  const filePathsText = (current.filePaths || []).slice(0, 5).join(', ');

  const contextParts = [
    convBuffer,
    decisionsText ? `決定事項:\n- ${decisionsText}` : '',
    activeTodos.length ? `TODO:\n${activeTodos.slice(0, 5).map(t => `- ${t.text}`).join('\n')}` : '',
    filePathsText ? `関連ファイル: ${filePathsText}` : '',
  ].filter(Boolean).join('\n\n');

  const prompt = `以下の会話を引き継ぎ用に要約してください。
形式: WHO（誰が）/ WHAT（何を）/ WHERE（どこで・どのファイル）/ WHY（なぜ）/ HOW（どうやって）/ NEXT（次のアクション）
会話:
${contextParts}`;

  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: 'claude-haiku-4-5-20251001',
      max_tokens: 600,
      messages: [{ role: 'user', content: prompt }],
    }),
  });

  if (!response.ok) {
    const errText = await response.text();
    throw new Error(`Claude API ${response.status}: ${errText}`);
  }

  const data    = await response.json();
  const summary = data.content?.[0]?.text || '';
  const now = new Date();
  const pad = n => String(n).padStart(2, '0');
  const dateStr = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}`;

  return [
    '## 引き継ぎパケット [Relay Pro — AI要約]',
    `**日時**: ${dateStr} (${current.turn_count || 0}ターン)`,
    '',
    summary,
  ].join('\n');
}

/**
 * Free版用: ルールベースの軽量セッション要約を生成する（AI API不使用）
 * relay_logbook_history に保存する形式（entry.packet を持つ）で返す
 */
function buildFreeSessionSummary(current, todos) {
  const activeTodos = todos.filter(t => t.status === 'active');
  const decisions   = current.decisions  || [];
  const filePaths   = current.filePaths  || [];
  const keywords    = current.keywords   || [];
  const turnCount   = current.turn_count || 0;
  const convExcerpt = (current.convBuffer || '').substring(0, 300).replace(/\n+/g, ' ').trim();

  const now = new Date();
  const pad = n => String(n).padStart(2, '0');
  const dateStr = `${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}`;

  const lines = [
    `## 前セッション要約 [Relay Free] — ${dateStr} (${turnCount}ターン)`,
  ];
  if (convExcerpt)       lines.push(`**会話概要**: ${convExcerpt}`);
  if (decisions.length)  lines.push(`**決定事項**: ${decisions.slice(0, 3).join(' / ')}`);
  if (activeTodos.length) {
    lines.push('**未完了TODO**:');
    activeTodos.slice(0, 8).forEach(t => lines.push(`  - [${t.id}] ${t.text}`));
  }
  if (filePaths.length)  lines.push(`**関連ファイル**: ${filePaths.slice(0, 3).join(', ')}`);
  if (keywords.length)   lines.push(`**重要メモ**: ${keywords.slice(0, 3).join(' / ')}`);

  return {
    timestamp: Date.now(),
    packet:    lines.join('\n'),
    plan:      'free',
    turn_count: turnCount,
  };
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

    // Pro/One: check plan + AI summary settings
    const proStored = await chrome.storage.local.get([KEYS.PLAN, 'relay_ai_summary_enabled', 'relay_api_key', 'relay_captured_files']);
    // MOCKA_DEV_MODE: 開発者IDが設定されていればOneプランとして扱う
    const _effectivePlan = MOCKA_DEV_ID === "m-sirius-k" ? 'one' : (proStored[KEYS.PLAN] || 'free');
    const isPro  = ['pro', 'one'].includes(_effectivePlan);
    const isOne  = _effectivePlan === 'one';
    const apiKey = proStored.relay_api_key || '';

    let logbookEntry = generateFreeHandoffPacketSync(current, todos, isPro ? proStored.relay_captured_files || [] : []);
    if (isPro && proStored.relay_ai_summary_enabled && apiKey) {
      try {
        logbookEntry = await generateProHandoffPacket(current, todos, apiKey);
      } catch (e) {
        console.error('[Relay Pro] AI summary failed, using free packet:', e);
      }
    }

    // Pro: 10件保持 / One: 無制限（Free は relay_logbook_history に保存しない）
    if (isPro) {
      const histStored = await chrome.storage.local.get('relay_logbook_history');
      const history = histStored.relay_logbook_history || [];
      history.unshift({ timestamp: Date.now(), packet: logbookEntry });
      if (!isOne && history.length > 10) history.pop(); // Pro: max 10件, One: 無制限
      await chrome.storage.local.set({ relay_logbook_history: history });
    }
    // Free: relay_logbook_history には保存しない
    // getHandoffPacket() が relay_current.convBuffer を直接参照する

    // One: Vault（無制限Logbook）にリッチ形式で保存
    if (isOne) {
      const vaultStored = await chrome.storage.local.get([KEYS.VAULT, KEYS.DENSITY_HISTORY]);
      let vault = vaultStored[KEYS.VAULT] || [];
      const densityHist = vaultStored[KEYS.DENSITY_HISTORY] || [];
      const densityScore = densityHist.length ? densityHist[densityHist.length - 1] : 0;

      const now2 = new Date();
      const pad2 = n => String(n).padStart(2, '0');
      const isoDate = `${now2.getFullYear()}-${pad2(now2.getMonth()+1)}-${pad2(now2.getDate())}T${pad2(now2.getHours())}:${pad2(now2.getMinutes())}:${pad2(now2.getSeconds())}`;
      const vaultId = `vault_${isoDate.replace(/[-:T]/g,'').slice(0, 14)}`;

      vault.unshift({
        id:            vaultId,
        date:          isoDate,
        timestamp:     Date.now(),
        title:         inferVaultTitle(current, todos),
        summary:       logbookEntry,
        decisions:     current.decisions || [],
        files:         [...new Set([...(current.filePaths || []), ...(proStored.relay_captured_files || [])])],
        todos:         todos.filter(t => t.status === 'active').map(t => t.text),
        keywords:      current.keywords || [],
        turn_count:    current.turn_count || 0,
        density_score: densityScore,
        session_id:    current.session_id,
      });

      // 容量管理: 100件上限 + ストレージ使用量チェック
      if (vault.length > 100) vault = vault.slice(0, 100);
      await chrome.storage.local.set({ [KEYS.VAULT]: vault });

      chrome.storage.local.getBytesInUse(KEYS.VAULT, (bytes) => {
        if (bytes > 4.5 * 1024 * 1024) {
          chrome.storage.local.get(KEYS.VAULT, (sv) => {
            const trimmed = (sv[KEYS.VAULT] || []).slice(0, Math.floor((sv[KEYS.VAULT] || []).length * 0.7));
            chrome.storage.local.set({ [KEYS.VAULT]: trimmed });
            console.warn('[Relay Vault] Trimmed for storage capacity');
          });
        }
      });
    }

    await chrome.storage.local.set({
      [KEYS.SESSIONS]:        sessions,
      [KEYS.CURRENT]:         null,
      [KEYS.LOGBOOK_CURRENT]: logbookEntry,
    });
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

// ─── Stale Storage Cleaning ───────────────────────────────────────────────────

async function cleanStaleStorage() {
  const FLAG_KEY = 'relay_stale_cleaned_v1';
  try {
    const flagStore = await chrome.storage.local.get(FLAG_KEY);
    if (flagStore[FLAG_KEY]) return; // already run

    const stored = await chrome.storage.local.get(KEYS.TODOS);
    const todos  = stored[KEYS.TODOS] || [];

    const activeBefore = todos.filter(t => t.status === 'active').length;
    let rejectedCount  = 0;

    const cleaned = todos.map(t => {
      if (t.status === 'active' && !isValidTodoContent(t.text)) {
        rejectedCount++;
        return { ...t, status: 'rejected_stale', rejected_at: Date.now() };
      }
      return t;
    });

    const activeAfter = activeBefore - rejectedCount;

    await chrome.storage.local.set({ [KEYS.TODOS]: cleaned, [FLAG_KEY]: true });
    console.log(`[Relay] cleanStaleStorage: active_before=${activeBefore} rejected_stale=${rejectedCount} active_after=${activeAfter}`);
  } catch (err) {
    console.error('[Relay] cleanStaleStorage error:', err);
  }
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

async function addTodo(text, source, why, where) {
  try {
    const stored = await chrome.storage.local.get(KEYS.TODOS);
    const todos  = stored[KEYS.TODOS] || [];

    // テキスト重複チェック（activeのみ）
    if (todos.some(t => t.text === text && t.status === 'active')) return;

    const num = await nextLbNum();
    const entry = {
      id:         lbId(num),
      num,
      text,
      status:     'active',
      created_at: Date.now(),
      source:     source || 'auto',
    };
    if (why)   entry.why   = why.slice(0, 100);
    if (where) entry.where = where.slice(0, 100);
    todos.push(entry);
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

// ─── 設計思想・経緯ブロック（固定テキスト）────────────────────────────────────
const RELAY_PHILOSOPHY_BLOCK = `
## Relay 設計思想
- miniMoCKA鉄則: PHI-OSと連携するが単独でも動く
- AIを信じるな、システムで縛れ
- 記録なき作業はMoCKAとして存在しない

## 製品構成
- Free: ルールベース引き継ぎ + Logbook
- Pro: AI要約(ユーザーAPIキー) + ファイルキャプチャ + 決定事項抽出
- One: 内容密度検知タイミング + Vault文脈注入

## 実装完了履歴
- TODO_173: content.js init()に/new判定追加（引き継ぎバグ修正）完了
- TODO_174/175/176: Free/Pro/One実装完了（2026-05-27）
- TODO_177: Vault文脈注入 指示書作成済み・未実装（保留中）
- DOM実測修正: .font-claude-response-bodyセレクタに統一済み（E20260603_107/122）
- Session RESUME実装: F5リロード時にtokens引き継ぎ済み（E20260603_057）
- 80%/100%切替バナー実装済み（E20260603_057）

## 未着手TODO（次フェーズ）
- TODO_177: Vault文脈注入（指示書あり・未実装）
- TODO_178: Stripe + CWS + LP（収益化未着手）
- TODO_219: token fallback時の非会話テキスト混入対策
`.trim();

async function getHandoffPacket() {
  try {
    // ── プラン判定 ──────────────────────────────────────────
    const planStored    = await chrome.storage.local.get(KEYS.PLAN);
    const _plan         = MOCKA_DEV_ID === "m-sirius-k" ? 'one' : (planStored[KEYS.PLAN] || 'free');
    const isPro         = ['pro', 'one'].includes(_plan);
    const isOne         = _plan === 'one';

    const stored = await chrome.storage.local.get([
      KEYS.SESSIONS, KEYS.TODOS, KEYS.CURRENT,
      ...(isPro ? ['relay_logbook_history'] : []),
    ]);
    const current     = stored[KEYS.CURRENT]  || {};
    const activeTodos = (stored[KEYS.TODOS]   || []).filter(t => t.status === 'active' && isValidTodoContent(t.text));
    const sessions    = stored[KEYS.SESSIONS] || [];
    const logHistory  = isPro ? (stored.relay_logbook_history || []) : [];

    // ── Free: シンプルパケット（設計思想・LB・経緯なし）──────
    if (!isPro) {
      const now = new Date();
      const pad = n => String(n).padStart(2, '0');
      const ts  = `${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}`;
      const buf = (current.convBuffer || '').substring(0, 200).replace(/\n+/g, ' ').trim();
      return [
        '[Relay引き継ぎ - 自動生成]',
        '━'.repeat(36),
        '',
        '## 引き継ぎパケット [Relay Free]',
        `**いつ**: ${ts} (${current.turn_count || 0}ターン)`,
        `**何を**: ${buf || '（会話内容なし）'}`,
        '',
        '━'.repeat(36),
        '上記を踏まえて作業を継続してください。',
      ].join('\n');
    }

    // ── Pro / One: フルパケット（設計思想 + LB + 経緯）───────
    const lines = [
      '[Relay引き継ぎ - 自動生成]',
      '━'.repeat(36),
      '',
      RELAY_PHILOSOPHY_BLOCK,
      '',
      '━'.repeat(36),
      '',
    ];

    // LBリスト（Pro/One のみ）
    if (activeTodos.length) {
      lines.push('■ 未完了タスク（LBリスト）');
      activeTodos.slice(0, 10).forEach(t => {
        const ctx = t.context?.why ? `（${t.context.why.slice(0, 60)}）` : '';
        lines.push(`  - [${t.id}] ${t.text}${ctx}`);
      });
      lines.push('');
    }

    // 現在のセッション（Pro/One のみ）
    if (current.session_id) {
      const d = new Date(current.started_at || Date.now());
      const dateStr = `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`;
      lines.push(`■ 現在のセッション（${dateStr}〜）`);
      lines.push(`  ターン数: ${current.turn_count || 0}`);
      if (current.decisions?.length) {
        lines.push('  決定事項: ' + current.decisions.slice(0, 3).join(' / '));
      }
      lines.push('');
    }

    // 直近2セッション（Pro/One: Logbook優先、なければ sessions フォールバック）
    const recentLogbook = logHistory.slice(0, 2);
    if (recentLogbook.length) {
      recentLogbook.forEach((entry, i) => {
        const label   = i === 0 ? '前セッション' : '前々セッション';
        const ts      = entry.timestamp ? new Date(entry.timestamp) : null;
        const dateStr = ts
          ? `${ts.getMonth() + 1}/${ts.getDate()} ${ts.getHours()}:${String(ts.getMinutes()).padStart(2, '0')}`
          : '日時不明';
        lines.push(`■ ${label}（${dateStr}）[Logbook]`);
        const packetText = entry.packet || '';
        const summary = packetText.split('\n').filter(l => l.trim() && !l.startsWith('##')).slice(0, 4).join(' / ');
        if (summary) lines.push(`  ${summary.slice(0, 200)}`);
        lines.push('');
      });
    } else {
      sessions.slice(0, 2).forEach((session, i) => {
        const label   = i === 0 ? '前セッション' : '前々セッション';
        const d       = new Date(session.ended_at || session.started_at);
        const dateStr = `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`;
        lines.push(`■ ${label}（${dateStr}）`);
        if (session.summary) {
          lines.push(`  作業: ${session.summary.work_description}`);
          if (session.summary.pending_todos?.length) {
            lines.push('  未完了TODO:');
            session.summary.pending_todos.slice(0, 5).forEach(t => lines.push(`    - ${t}`));
          }
          if (session.summary.completed_todos?.length) {
            lines.push(`  完了済: ${session.summary.completed_todos.slice(0, 3).join(' / ')}`);
          }
          if (session.summary.key_decisions?.length) {
            lines.push('  重要決定: ' + session.summary.key_decisions.slice(0, 2).join(' / '));
          }
        }
        lines.push('');
      });
    }

    if (!activeTodos.length && !sessions.length && !recentLogbook.length && !current.session_id) {
      lines.push('（引き継ぎデータなし — 新規セッション開始）');
      lines.push('');
    }

    lines.push('━'.repeat(36));
    lines.push('上記の設計思想・経緯・未完了タスクを踏まえて作業を継続してください。');

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
      await startSession(msg.sessionId, msg.pageTitle);
      return { ok: true };

    case 'RELAY_SESSION_END':
      await endSession();
      return { ok: true };

    case 'RELAY_TURN_UPDATE': {
      const stored  = await chrome.storage.local.get(KEYS.CURRENT);
      const current = stored[KEYS.CURRENT] || {};
      const rawTokens   = msg.tokens || 150;
      const RAW_TO_REAL = 2.5;
      current.turn_count = (current.turn_count || 0) + 1;

      // DOM実測値を優先（全会話の累計推定なので上書き代入）
      // 取得できない場合は RAW_TO_REAL 補正の増分加算にフォールバック
      if (msg.domTokens && msg.domTokens > 0) {
        current.estimated_tokens = msg.domTokens;
        current.token_source     = 'dom';
      } else {
        current.estimated_tokens = (current.estimated_tokens || 0) + Math.round(rawTokens * RAW_TO_REAL);
        current.token_source     = 'raw';
      }

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
      await addTodo(msg.text, msg.source, msg.why, msg.where);
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
        token_source:     current.token_source     || 'raw',
      };
    }

    case 'RELAY_GET_METRICS': {
      const stored = await chrome.storage.local.get(KEYS.METRICS);
      return stored[KEYS.METRICS] || { cpi: 0 };
    }

    case 'RELAY_GET_HANDOFF': {
      const proStored2 = await chrome.storage.local.get([KEYS.PLAN, 'relay_ai_summary_enabled', 'relay_api_key']);
      if (['pro', 'one'].includes(proStored2[KEYS.PLAN]) && proStored2.relay_ai_summary_enabled && proStored2.relay_api_key) {
        const s2 = await chrome.storage.local.get([KEYS.CURRENT, KEYS.TODOS]);
        const curr = s2[KEYS.CURRENT];
        if (curr) {
          try {
            const packet = await generateProHandoffPacket(curr, s2[KEYS.TODOS] || [], proStored2.relay_api_key);
            return { packet };
          } catch (e) {
            console.error('[Relay Pro] AI handoff failed, fallback:', e);
          }
        }
      }
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

    // ── Free版: 決定事項・ファイルパス・重要キーワード蓄積 ──
    case 'RELAY_ADD_DECISIONS': {
      const s = await chrome.storage.local.get([KEYS.CURRENT, KEYS.PLAN, 'relay_decisions']);
      const c = s[KEYS.CURRENT] || {};
      c.decisions = [...new Set([...(c.decisions || []), ...msg.items])].slice(0, 20);
      const updates = { [KEYS.CURRENT]: c };
      if (['pro', 'one'].includes(s[KEYS.PLAN])) {
        const existing = s.relay_decisions || [];
        updates.relay_decisions = [...new Set([...existing, ...msg.items])].slice(0, 100);
      }
      await chrome.storage.local.set(updates);
      return { ok: true };
    }

    case 'RELAY_ADD_FILEPATHS': {
      const s = await chrome.storage.local.get([KEYS.CURRENT, KEYS.PLAN, 'relay_captured_files']);
      const c = s[KEYS.CURRENT] || {};
      c.filePaths = [...new Set([...(c.filePaths || []), ...msg.items])].slice(0, 20);
      const updates = { [KEYS.CURRENT]: c };
      if (['pro', 'one'].includes(s[KEYS.PLAN])) {
        const existing = s.relay_captured_files || [];
        updates.relay_captured_files = [...new Set([...existing, ...msg.items])].slice(0, 100);
      }
      await chrome.storage.local.set(updates);
      return { ok: true };
    }

    case 'RELAY_ADD_KEYWORDS': {
      const s = await chrome.storage.local.get(KEYS.CURRENT);
      const c = s[KEYS.CURRENT] || {};
      c.keywords = [...new Set([...(c.keywords || []), ...msg.items])].slice(0, 20);
      await chrome.storage.local.set({ [KEYS.CURRENT]: c });
      return { ok: true };
    }

    case 'RELAY_GET_FREE_HANDOFF': {
      const s = await chrome.storage.local.get([KEYS.CURRENT, KEYS.TODOS]);
      const current = s[KEYS.CURRENT];
      if (!current) return { packet: null };
      const packet = generateFreeHandoffPacketSync(current, s[KEYS.TODOS] || []);
      return { packet };
    }

    // ── Pro: 会話バッファ蓄積 ──
    case 'RELAY_UPDATE_CONV_BUFFER': {
      const s = await chrome.storage.local.get(KEYS.CURRENT);
      const c = s[KEYS.CURRENT] || {};
      c.convBuffer = ((c.convBuffer || '') + '\n' + (msg.text || '')).slice(-4000);
      await chrome.storage.local.set({ [KEYS.CURRENT]: c });
      return { ok: true };
    }

    // ── Pro: APIキーテスト接続 ──
    case 'RELAY_TEST_API_KEY': {
      try {
        const resp = await fetch('https://api.anthropic.com/v1/messages', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'x-api-key': msg.apiKey,
            'anthropic-version': '2023-06-01',
          },
          body: JSON.stringify({
            model: 'claude-haiku-4-5-20251001',
            max_tokens: 5,
            messages: [{ role: 'user', content: 'hi' }],
          }),
        });
        return { ok: resp.ok, status: resp.status };
      } catch (e) {
        return { ok: false, error: e.message };
      }
    }

    // ── Pro: Logbook履歴取得 ──
    case 'RELAY_GET_LOGBOOK_HISTORY': {
      const s = await chrome.storage.local.get('relay_logbook_history');
      return { history: s.relay_logbook_history || [] };
    }

    // ── Pro: プラン取得/設定 ──
    case 'RELAY_GET_PLAN': {
      // MOCKA_DEV_MODE: 開発者IDが設定されていればOneプランを即返す
      if (MOCKA_DEV_ID === "m-sirius-k") return { plan: 'one', expiry: null };
      const s = await chrome.storage.local.get([KEYS.PLAN, KEYS.LICENSE_EXP]);
      return { plan: s[KEYS.PLAN] || 'free', expiry: s[KEYS.LICENSE_EXP] || null };
    }

    case 'RELAY_SET_PLAN': {
      await chrome.storage.local.set({ [KEYS.PLAN]: msg.plan });
      return { ok: true };
    }

    // ── ライセンスキー検証・設定 ──
    case 'RELAY_SET_LICENSE': {
      const result = await validateRelayLicense(msg.key);
      if (result.expired) return { ok: false, expired: true, plan: 'free' };
      await chrome.storage.local.set({
        [KEYS.LICENSE_KEY]: msg.key.trim(),
        [KEYS.PLAN]:        result.plan,
        [KEYS.LICENSE_EXP]: result.expiry || '',
      });
      return { ok: true, plan: result.plan, expiry: result.expiry };
    }

    // ── ライセンスキー削除（Free降格）──
    case 'RELAY_REMOVE_LICENSE': {
      await chrome.storage.local.remove([KEYS.LICENSE_KEY, KEYS.LICENSE_EXP]);
      await chrome.storage.local.set({ [KEYS.PLAN]: 'free' });
      return { ok: true, plan: 'free' };
    }

    // ── Pro: Pro設定（AI要約ON/OFF、APIキー）保存 ──
    case 'RELAY_SET_PRO_SETTINGS': {
      const updates = {};
      if (msg.aiSummaryEnabled !== undefined) updates.relay_ai_summary_enabled = msg.aiSummaryEnabled;
      if (msg.apiKey !== undefined)            updates.relay_api_key            = msg.apiKey;
      await chrome.storage.local.set(updates);
      return { ok: true };
    }

    // ── Pro: Pro設定取得 ──
    case 'RELAY_GET_PRO_SETTINGS': {
      const s = await chrome.storage.local.get(['relay_ai_summary_enabled', 'relay_api_key', KEYS.PLAN]);
      return {
        plan:             s[KEYS.PLAN] || 'free',
        aiSummaryEnabled: s.relay_ai_summary_enabled || false,
        apiKeySet:        !!(s.relay_api_key),
      };
    }

    // ── One: 密度スコア更新 ──
    case 'RELAY_DENSITY_UPDATE': {
      const s = await chrome.storage.local.get(KEYS.PLAN);
      if (s[KEYS.PLAN] !== 'one') return { notify: false };
      const stored  = await chrome.storage.local.get(KEYS.DENSITY_HISTORY);
      const history = stored[KEYS.DENSITY_HISTORY] || [];
      history.push(msg.score || 0);
      if (history.length > 20) history.shift();
      await chrome.storage.local.set({ [KEYS.DENSITY_HISTORY]: history });
      const status = detectBreakevenPoint(history);
      return { notify: true, status };
    }

    // ── One: 密度履歴取得 ──
    case 'RELAY_GET_DENSITY': {
      const s = await chrome.storage.local.get(KEYS.DENSITY_HISTORY);
      return { history: s[KEYS.DENSITY_HISTORY] || [] };
    }

    // ── One: Vault全件取得 ──
    case 'RELAY_GET_VAULT': {
      const s = await chrome.storage.local.get(KEYS.VAULT);
      return { vault: s[KEYS.VAULT] || [] };
    }

    // ── One: Vault関連度ランキング（上位3件）──
    case 'RELAY_RANK_VAULT': {
      const s = await chrome.storage.local.get([KEYS.VAULT, KEYS.CURRENT]);
      const vault   = s[KEYS.VAULT]   || [];
      const current = s[KEYS.CURRENT] || {};
      const ctxKws  = [
        ...(current.keywords  || []),
        ...(current.decisions || []),
      ].map(k => k.toLowerCase());
      const ranked = vault.map(entry => {
        const ekws    = (entry.keywords || []).map(k => k.toLowerCase());
        const overlap = ekws.filter(k => ctxKws.some(ck => ck.includes(k) || k.includes(ck))).length;
        return { ...entry, relevance: overlap };
      }).sort((a, b) => b.relevance - a.relevance).slice(0, 3);
      return { ranked };
    }

    // ── One: Vault特定エントリをhandoff packetとして設定 ──
    case 'RELAY_USE_VAULT_ENTRY': {
      await chrome.storage.local.set({ relay_handoff_packet: msg.packet });
      return { ok: true };
    }

    // ── One: 選択エントリ or 密度レベルでVaultパケット生成 ──
    case 'RELAY_GET_VAULT_PACKET': {
      const packet = await buildVaultPacket(msg.selectedIds, msg.density);
      return { packet };
    }

    // ── One: Vaultパケットを生成してhandoff_packetに保存 ──
    case 'RELAY_INJECT_VAULT': {
      const packet = await buildVaultPacket(msg.selectedIds, msg.density);
      if (packet) {
        await chrome.storage.local.set({ relay_handoff_packet: packet });
      }
      return { packet };
    }

    // ── One: VaultデータをJSONでエクスポート ──
    case 'RELAY_EXPORT_VAULT': {
      const s = await chrome.storage.local.get(KEYS.VAULT);
      const vault = s[KEYS.VAULT] || [];
      return { json: JSON.stringify(vault, null, 2) };
    }

    // ── One: Vault設定取得（注入密度レベル、自動注入ON/OFF）──
    case 'RELAY_GET_VAULT_SETTINGS': {
      const s = await chrome.storage.local.get(['relay_inject_density', 'relay_auto_inject']);
      return {
        density:    s.relay_inject_density ?? 3,
        autoInject: s.relay_auto_inject    ?? false,
      };
    }

    // ── One: Vault設定保存 ──
    case 'RELAY_SET_VAULT_SETTINGS': {
      const updates = {};
      if (msg.density    !== undefined) updates.relay_inject_density = msg.density;
      if (msg.autoInject !== undefined) updates.relay_auto_inject    = msg.autoInject;
      await chrome.storage.local.set(updates);
      return { ok: true };
    }

    // ── Intent Engine v4.0: Claude API自然言語判定 ──
    // content.jsから「これTODOにして」「3番消して」等を受け取り、構造化intentを返す
    case 'RELAY_CLASSIFY_INTENT': {
      const apiStored = await chrome.storage.local.get(['relay_api_key', KEYS.PLAN]);
      const apiKey    = apiStored.relay_api_key || '';
      if (!apiKey) {
        // APIキー未設定時はフォールバック（無判定）
        return { intent: null };
      }
      const prompt = `You are a task manager assistant embedded in a browser extension called Relay.
The user typed a message. Determine if it is a TODO operation or normal conversation.

Current TODO list:
${msg.todoSummary || '（なし）'}

Last AI message (for context):
${(msg.lastAIText || '').slice(0, 200)}

User typed:
"${msg.userText}"

Reply ONLY with a JSON object (no markdown, no explanation):
- If normal conversation: {"type":"none"}
- If user wants to SEE the TODO list: {"type":"list"}
- If user wants to ADD a TODO: {"type":"add","what":"<task description>","why":"<reason if mentioned, else empty>"}
- If user wants to COMPLETE a single item (e.g. "3番完了", "LB_005消して", "three done"): {"type":"single","num":<integer>}
- If user wants to COMPLETE a range (e.g. "1から5完了", "LB_001〜003消して"): {"type":"range","from":<int>,"to":<int>}
- If user wants to COMPLETE ALL items: {"type":"complete_all"}

Rules:
- "これ" "this" "it" "さっきの" refer to the last AI message content
- Natural Japanese: 「消して」「片付けて」「終わった」「覚えといて」「メモして」all count
- Natural English: "done", "finished", "close it", "remember this", "add to list" all count
- If ambiguous, return {"type":"none"}`;

      try {
        const resp = await fetch('https://api.anthropic.com/v1/messages', {
          method: 'POST',
          headers: {
            'Content-Type':         'application/json',
            'x-api-key':            apiKey,
            'anthropic-version':    '2023-06-01',
          },
          body: JSON.stringify({
            model:      'claude-haiku-4-5',
            max_tokens: 120,
            messages:   [{ role: 'user', content: prompt }],
          }),
        });
        if (!resp.ok) return { intent: null };
        const data   = await resp.json();
        const raw    = (data.content?.[0]?.text || '').trim();
        const clean  = raw.replace(/```json|```/g, '').trim();
        const intent = JSON.parse(clean);
        return { intent };
      } catch(e) {
        console.error('[Relay] RELAY_CLASSIFY_INTENT error:', e);
        return { intent: null };
      }
    }

    // ── 全TODO完了 ──
    case 'RELAY_COMPLETE_ALL': {
      const s     = await chrome.storage.local.get(KEYS.TODOS);
      const todos = s[KEYS.TODOS] || [];
      let count   = 0;
      const updated = todos.map(t => {
        if (t.status === 'active') { count++; return { ...t, status: 'done', done_at: Date.now() }; }
        return t;
      });
      await chrome.storage.local.set({ [KEYS.TODOS]: updated });
      return { ok: true, count };
    }

    default:
      return { error: `Unknown type: ${msg.type}` };
  }
}

cleanStaleStorage();
