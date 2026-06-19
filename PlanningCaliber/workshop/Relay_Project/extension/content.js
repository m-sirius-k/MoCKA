'use strict';
// Relay v4.6 — content.js
// Fix v4.1: Extension context invalidated guard + CSP Google Fonts removed
// Fix v4.2: Smart handoff — invisible inject on first send (not pasted into input)

const CONFIG = {
  TURN_WARN:     20,
  SCAN_INTERVAL: 3000,
  IDLE_WAIT:     1500,
  BADGE_ID:      'relay-badge',
  INJECT_DELAY:  1500,
};

const INPUT_SELECTORS = [
  'div[contenteditable="true"][data-testid="composer-input"]',
  'div[contenteditable="true"].ProseMirror',
  'div[contenteditable="true"]',
];

const SEND_BUTTON_SELECTORS = [
  'button[data-testid="send-button"]',
  'button[aria-label="Send message"]',
  'button[aria-label="メッセージを送信"]',
  'button[type="submit"]',
];

// TODO patterns — priority order
const EN_PATTERNS = [
  /^\[RELAY_TODO\]\s*(.+)/i,
  /^-\s*\[\s*\]\s*(.+)/,
  /^(?:TODO|Fix|Add|Update|Create|Check|Review|Implement|Deploy)\s*[:：]?\s*(.+)/i,
];

const JA_PATTERNS = [
  /^(?:TODO|タスク|作業|対応|修正|追加|確認)\s*[:：]\s*(.+)/,
  /^[・•]\s*(.{15,})/,
  /^(\d+[.)]\s*.{15,})/,
];

// ─── Extension Context Guard ──────────────────────────────────────────────────

function isExtensionAlive() {
  try { return !!(chrome?.runtime?.id); } catch (e) { return false; }
}

function safeSendMessage(msg) {
  if (!isExtensionAlive()) return Promise.resolve(null);
  try { return chrome.runtime.sendMessage(msg).catch(() => null); }
  catch (e) { return Promise.resolve(null); }
}

// ─── State ───────────────────────────────────────────────────────────────────

let currentUrl         = location.href;
let turnCount          = 0;
let processedMessages  = new Set();
let streamingTimer     = null;
let badgeEl            = null;
let mutationObserver   = null;
let initialized        = false;

// 不可視注入用
let pendingHandoff     = null;
let sendIntercepted    = false;
let sendButtonObserver = null;
let turnWarningShown   = false;

// ─── Init ────────────────────────────────────────────────────────────────────

function init() {
  if (initialized) return;
  initialized = true;

  console.log('[Relay] Initializing on', location.href);
  createBadge();
  observeUrlChanges();
  observeDOM();
  scheduleMetricsPush();

  // URL確定後に1回だけセッション開始通知
  // /new → /chat/xxx の遷移はonUrlChangeが処理するため、
  // ここではchat確定ページのみ通知する（/newは遷移後に任せる）
  if (/\/chat\/[a-z0-9-]+/.test(location.href)) {
    notifySessionStart();
  } else if (/\/new($|\?)/.test(location.href)) {
    // /new は遷移後のonUrlChangeでnotifySessionStart+prepareInvisibleHandoffが走る
    // ただし/newで止まる場合（直接開いた場合）のためフォールバック
    setTimeout(() => {
      if (/\/new($|\?)/.test(location.href)) {
        notifySessionStart();
        prepareInvisibleHandoff();
      }
    }, CONFIG.INJECT_DELAY);
  } else {
    // その他のページ（トップページ等）でも一応通知
    notifySessionStart();
  }
}

// ─── URL / Session Lifecycle ─────────────────────────────────────────────────

function observeUrlChanges() {
  let lastUrl = location.href;

  setInterval(() => {
    if (location.href !== lastUrl) {
      const prev = lastUrl;
      lastUrl    = location.href;
      onUrlChange(prev, location.href);
    }
  }, 100);

  window.addEventListener('popstate', () => {
    if (location.href !== currentUrl) {
      onUrlChange(currentUrl, location.href);
      currentUrl = location.href;
    }
  });
}

function onUrlChange(from, to) {
  console.log('[Relay] URL:', from.split('/').slice(-2).join('/'), '->', to.split('/').slice(-2).join('/'));

  const wasActive = /\/(chat|new)/.test(from);
  const isNew     = /\/new($|\?)/.test(to);
  const isChat    = /\/chat\/[a-z0-9-]+/.test(to);

  if (isNew || isChat) {
    turnCount = 0;
    processedMessages.clear();
    turnWarningShown = false;
    recentMessageTexts   = [];
    densityNotifiedTypes = new Set();

    // Fix v4.9: SESSION_START を先に送り relay_current を確立してから
    // SESSION_END を送る。逆順だと popup の RELAY_GET_STATS が
    // relay_current=null の瞬間を踏んで no-session 表示になる。
    notifySessionStart();

    if (wasActive) {
      // 新セッションが storage に書き込まれるのを待ってから旧セッションを閉じる
      setTimeout(() => safeSendMessage({ type: 'RELAY_SESSION_END' }), 150);
    }

    if (isNew) {
      chrome.storage.local.remove(['relay_injected']).catch(() => {});
      setTimeout(prepareInvisibleHandoff, CONFIG.INJECT_DELAY);
    }
  } else if (wasActive) {
    // chat でも /new でもないページへ移動した場合のみ即時 END
    safeSendMessage({ type: 'RELAY_SESSION_END' });
  }

  currentUrl = to;
  updateBadge();
}

function notifySessionStart() {
  const sessionId = extractSessionId(location.href);
  safeSendMessage({ type: 'RELAY_SESSION_START', sessionId, pageTitle: document.title });
}

function extractSessionId(url) {
  const m = url.match(/\/chat\/([a-z0-9-]+)/);
  return m ? m[1] : 'session_' + Date.now();
}

// ─── DOM Observation ──────────────────────────────────────────────────────────

function observeDOM() {
  if (mutationObserver) mutationObserver.disconnect();

  mutationObserver = new MutationObserver(debounce(checkForNewMessages, 600));
  mutationObserver.observe(document.body, { childList: true, subtree: true });
}

function checkForNewMessages() {
  if (!isExtensionAlive()) return;
  const messages = getAIMessages();

  // 未処理メッセージのみ抽出
  const unprocessed = messages.filter(el => !processedMessages.has(getMessageId(el)));
  if (!unprocessed.length) return;

  // タイマーはループ外で1回だけセット
  clearTimeout(streamingTimer);
  streamingTimer = setTimeout(() => {
    if (isStreaming()) return;
    unprocessed.forEach(el => {
      const freshId = getMessageId(el);
      if (!processedMessages.has(freshId)) {
        processMessage(el, freshId);
      }
    });
  }, CONFIG.IDLE_WAIT);
}

function getAIMessages() {
  // 2026年版 claude.ai セレクター（優先順）
  const selectors = [
    // 現行 claude.ai DOM（2026-06-03 実機確認済み）
    '.font-claude-response-body',
    // フォールバック群
    '[class*="assistant-message"]',
    '[class*="AssistantMessage"]',
    'div[class*="message-content"]',
  ];

  for (const sel of selectors) {
    try {
      const els = Array.from(document.querySelectorAll(sel));
      if (els.length) return els;
    } catch(e) {}
  }

  // 汎用フォールバック: 会話エリア内の100文字超テキストブロック
  // role="presentation" や article タグも対象
  const containers = [
    document.querySelector('[class*="conversation-content"]'),
    document.querySelector('[class*="ConversationContent"]'),
    document.querySelector('main'),
    document.body,
  ].filter(Boolean);

  for (const conv of containers) {
    const candidates = Array.from(conv.querySelectorAll(
      'div[class*="message"], article, [role="article"]'
    )).filter(el => el.textContent.length > 100);
    if (candidates.length) return candidates;
  }

  return [];
}

function getMessageId(el) {
  const attr = el.dataset?.messageId || el.id;
  if (attr) return attr;
  return hashText((el.textContent || '').slice(0, 120));
}

function isStreaming() {
  return !!(
    document.querySelector('[data-is-streaming="true"]') ||
    document.querySelector('[class*="stop-button"]:not([disabled])') ||
    document.querySelector('button[aria-label*="Stop"]') ||
    document.querySelector('[class*="loading-indicator"]')
  );
}

function processMessage(el, id) {
  if (!isExtensionAlive()) return;
  processedMessages.add(id);
  turnCount++;

  const text   = el.textContent || '';
  const tokens = estimateTokens(text);

  const domEst = estimateActualTokens();
  safeSendMessage({
    type:      'RELAY_TURN_UPDATE',
    tokens,
    domTokens: domEst.tokens,
    domChars:  domEst.chars,
    jpRatio:   domEst.jpRatio,
    langMode:  domEst.mode,
  });

  const todos = extractTodos(text);
  todos.forEach(t => {
    safeSendMessage({ type: 'RELAY_ADD_TODO', text: t, source: 'auto' });
  });

  if (todos.length) console.log('[Relay] Extracted', todos.length, 'TODOs');

  // Pro: 会話バッファに蓄積（AI要約用、最大500文字/ターン）
  safeSendMessage({ type: 'RELAY_UPDATE_CONV_BUFFER', text: text.slice(0, 500) });

  // One: 密度スコアリング用メッセージバッファ蓄積
  recentMessageTexts.push(text.slice(0, 500));
  if (recentMessageTexts.length > 5) recentMessageTexts.shift();
  if (turnCount % DENSITY_CHECK_INTERVAL === 0) checkDensity();

  // Free: 決定事項・ファイルパス・重要キーワード抽出して蓄積
  const decisions = extractDecisions(text);
  const filePaths = extractFilePaths(text);
  const keywords  = extractKeywords(text);
  if (decisions.length) safeSendMessage({ type: 'RELAY_ADD_DECISIONS', items: decisions });
  if (filePaths.length) safeSendMessage({ type: 'RELAY_ADD_FILEPATHS', items: filePaths });
  if (keywords.length)  safeSendMessage({ type: 'RELAY_ADD_KEYWORDS',  items: keywords });

  // 20ターン警告（1セッション1回のみ）
  if (turnCount === CONFIG.TURN_WARN) showTurnWarning();

  detectAndSetWorkMode(text);
  updateBadge();
  console.log('[Relay] Turn', turnCount, '— tokens ~', tokens);
}

function estimateTokens(text) {
  return Math.round(text.length / 4);
}

/**
 * claude.ai DOM の全メッセージ文字数からトークン数を実測推定する。
 * 日本語混在率を自動判定し係数を切り替える。
 * @returns {{ tokens: number, chars: number, jpRatio: number, mode: string }}
 */
function estimateActualTokens() {
  // ── セレクタ（claude.ai 現行DOM）─────────────────────────
  const MSG_SELECTORS = [
    '[data-testid="user-message"]',
    '.font-claude-response-body',
    '[class*="human-turn"]',
    '[class*="assistant-turn"]',
  ];

  let allText = '';
  for (const sel of MSG_SELECTORS) {
    try {
      const els = document.querySelectorAll(sel);
      if (els.length > 0) {
        els.forEach(el => { allText += el.textContent + '\n'; });
        break;
      }
    } catch (e) {}
  }

  // セレクタ未ヒット時のフォールバック
  let usedFallback = false;
  if (!allText.trim()) {
    allText = document.body?.textContent || '';
    usedFallback = true;
  }

  const totalChars = allText.length;
  if (totalChars === 0) return { tokens: 0, chars: 0, jpRatio: 0, mode: 'unknown' };

  // ── 言語係数 ──────────────────────────────────────────────
  // 日本語文字（ひらがな・カタカナ・漢字）の比率を計算
  const jpChars = (allText.match(/[぀-鿿]/g) || []).length;
  const jpRatio = jpChars / totalChars;

  // 係数定義（実測ベース）
  // 日本語: 1トークン ≒ 2.6文字 → 1文字 ≒ 0.38トークン
  // 英語:   1トークン ≒ 4.0文字 → 1文字 ≒ 0.25トークン
  // 混在:   比率で線形補間
  const JP_COEF = 0.38;
  const EN_COEF = 0.25;
  const coef    = EN_COEF + (JP_COEF - EN_COEF) * jpRatio;

  const mode = jpRatio > 0.6 ? 'japanese'
             : jpRatio > 0.2 ? 'mixed'
             : 'english';

  // フォールバック時はUI/nav要素込みのため×0.6で過大推定を補正
  const FALLBACK_CORRECTION = 0.6;
  const raw = Math.round(totalChars * coef);
  const tokens = usedFallback ? Math.round(raw * FALLBACK_CORRECTION) : raw;
  return { tokens, chars: totalChars, jpRatio: Math.round(jpRatio * 100) / 100, mode };
}

// ─── Work Mode Detection ──────────────────────────────────────────────────────

function detectAndSetWorkMode(text) {
  const codeBlocks = (text.match(/```/g) || []).length;
  const hasCode    = codeBlocks > 4;
  const isLarge    = text.length > 5000;

  let mode = 'light';
  if (hasCode || isLarge) {
    mode = 'file';
  } else {
    const heavyKw = ['実装', '設計', 'コード', 'エラー', 'バグ', 'fix', 'implement', 'design', 'debug', 'build'];
    if (heavyKw.some(k => text.toLowerCase().includes(k))) mode = 'heavy';
  }

  safeSendMessage({ type: 'RELAY_SET_MODE', mode });
}

// ─── TODO Extraction ─────────────────────────────────────────────────────────

// ★ 引き継ぎパケット起源テキストを extractTodos に渡さないためのガード
// processMessage() 経由でのみ呼び出す（直接呼び出し禁止）
function isHandoffPacketText(text) {
  return /^\[Relay引き継ぎ/.test(text.trim()) ||
         /^## 引き継ぎパケット/.test(text.trim()) ||
         /^━{10,}/.test(text.trim());
}

function extractTodos(text) {
  // 引き継ぎパケット本文は絶対に処理しない
  if (isHandoffPacketText(text)) return [];

  const lines   = text.split('\n');
  const todos   = [];
  let inCode    = false;
  // 引き継ぎブロック内フラグ（パケットが会話の一部として現れた場合）
  let inHandoff = false;

  for (const line of lines) {
    if (line.startsWith('```')) { inCode = !inCode; continue; }
    if (inCode) continue;

    const trimmed = line.trim();

    // ★ 引き継ぎブロック開始/終了検出
    if (/^\[Relay引き継ぎ/.test(trimmed) || /^## 引き継ぎパケット/.test(trimmed)) {
      inHandoff = true; continue;
    }
    if (inHandoff && /^━{10,}$/.test(trimmed)) {
      // 2本目の区切り線で終了
      inHandoff = false; continue;
    }
    if (inHandoff) continue;

    if (trimmed.length < 15 || trimmed.length > 200) continue;

    // Reject high symbol density (likely code)
    const symbols = (trimmed.match(/[^a-zA-Z0-9぀-龯\s\-:.,]/g) || []).length;
    if (symbols / trimmed.length > 0.30) continue;

    // ★ Reject: Relay引き継ぎブロックの区切り・ヘッダー行
    if (/^━+$/.test(trimmed)) continue;
    if (/^■\s/.test(trimmed)) continue;
    // ★ Reject: [LB_xxx] 形式の引き継ぎTODO行（自己ブロック）
    if (/^\[LB_\d+\]/.test(trimmed)) continue;
    // ★ Reject: Relay引き継ぎセクション識別子
    if (/^\[Relay引き継ぎ/.test(trimmed)) continue;
    if (/^上記を踏まえて/.test(trimmed)) continue;
    // ★ Reject: ターン数・作業・未完了TODOの引き継ぎ記述行
    if (/^(?:ターン数|作業|未完了TODO)\s*[:：]/.test(trimmed)) continue;
    // ★ Reject: MoCKA形式の完了報告行 (TODO_xxx完了, LB_xxx完了, _170完了 等)
    if (/(?:TODO[_-]?\d+|LB[_-]?\d+|_\d+)\s*(?:[（(].*?[)）])?\s*[:：]?\s*.*(?:完了|done|finished)/i.test(trimmed)) continue;
    // ★ Reject: _数字（〜）形式の引き継ぎ行全般
    if (/^_\d+[（(【]/.test(trimmed)) continue;
    // ★ Reject: 🚫 ✅ → 等の記号付き注釈行
    if (/^(?:→|→\s*🚫|→\s*✅|🚫|✅)/.test(trimmed)) continue;
    // ★ Reject: 日付+完了パターン
    if (/20\d\d[-\/]\d\d[-\/]\d\d.*完了/.test(trimmed)) continue;
    // ★ Reject: 表組みの行
    if (/^\|.+\|/.test(trimmed)) continue;
    // ★ Reject: コードスニペット・テンプレートの残骸 (LB_001原因)
    if (/d_at\s*:|updated_at\s*:|created_at\s*:/.test(trimmed)) continue;
    if (/\/\/\s*(WHEN|WHERE|WHO|WHAT|WHY|HOW)\s*$/.test(trimmed)) continue;
    if (/:\s*1234567890/.test(trimmed)) continue;
    // ★ Reject: 完了マーク付き行 (LB_004原因)
    if (/\u2705/.test(trimmed)) continue;
    // ★ Reject: _数字: 形式の説明行 (LB_005/006原因)
    if (/^_\d+[:： ]/.test(trimmed)) continue;
    // ★ Reject: 質問・提案文 (LB_006/008原因)
    if (/(?:しましょうか|ますか)[？?]\s*$/.test(trimmed)) continue;
    // ★ Reject: 「内容TODO_xxx」形式 (LB_015原因)
    if (/^内容TODO_\d+/.test(trimmed)) continue;
    if (/TODO_\d+.*TODO_\d+/.test(trimmed)) continue;
    // ★ Reject: #コメント行
    if (/^#\s+[→]/.test(trimmed)) continue;
    // ★ Reject: × 数字（補正係数的な記述）
    if (/^[×x]\s*\d/.test(trimmed)) continue;
    // ★ Reject: 数字+ = 〜 のような計算式行
    if (/^\d+[\+\-\*\/]\s*\d/.test(trimmed)) continue;
    // ★ Reject: 番号付きリスト行（1. 2. 3. 形式 — 手順・説明文の誤爆防止）
    if (/^\d+\.\s+.{5,}/.test(trimmed)) continue;
    // ★ Reject: 番号付きリスト行（1) 2) 3) 形式）
    if (/^\d+\)\s*.{5,}/.test(trimmed)) continue;
    // ★ Reject: **太字** マークダウン見出し的な行
    if (/^\*\*[^*]+\*\*[：:]\s*/.test(trimmed)) continue;
    // ★ Reject: 「いつ」「何を」等のパケットフィールド行
    if (/^\*\*(?:いつ|何を|TODO|次の|アクション)\*\*/.test(trimmed)) continue;

    let matched = null;

    for (const pat of EN_PATTERNS) {
      const m = trimmed.match(pat);
      if (m) { matched = (m[1] || '').trim(); break; }
    }

    if (!matched) {
      for (const pat of JA_PATTERNS) {
        const m = trimmed.match(pat);
        if (m) { matched = (m[1] || '').trim(); break; }
      }
    }

    // Japanese imperative endings
    if (!matched && /(?:してください|しておく|しておいて|お願いします|必要です)$/.test(trimmed)) {
      matched = trimmed;
    }

    if (matched && matched.length >= 15 && matched.length <= 200) {
      todos.push(matched);
    }
  }

  return [...new Set(todos)]; // dedup
}

// ─── One: Density Scoring Engine (API-zero, pure local) ──────────────────────

const DENSITY_CHECK_INTERVAL = 5;
const IMPORTANT_KEYWORDS = [
  'エラー','バグ','修正','実装','完了','決定','採用','却下',
  'TODO','次に','あとで','問題','解決','変更','追加','削除',
  'error','bug','fix','implement','done','decision',
];

let recentMessageTexts   = [];
let densityNotifiedTypes = new Set();

function calcKeywordDensity(msgs) {
  const text  = msgs.join(' ').toLowerCase();
  const words = text.split(/\s+/).filter(Boolean);
  if (!words.length) return 0;
  const hits = words.filter(w => IMPORTANT_KEYWORDS.some(kw => w.includes(kw.toLowerCase()))).length;
  return Math.min(1.0, (hits / words.length) * 10);
}

function calcFilePathCount(msgs) {
  const text = msgs.join(' ');
  const RE = /(?:[A-Z]:\\[^\s"']+\.[a-zA-Z]{1,5}|\/[a-zA-Z0-9_\-\/]+\.[a-zA-Z]{1,5}|\b\w+\.(js|py|json|ts|html|css|md|txt)\b)/g;
  return Math.min(1.0, (text.match(RE) || []).length / 5);
}

function calcDecisionCount(msgs) {
  const text = msgs.join('\n');
  const RE = /(?:にした|に決定|を採用|を却下|することにした|\[RELAY_DECISION\])/g;
  return Math.min(1.0, (text.match(RE) || []).length / 5);
}

function calcTopicShift(msgs) {
  if (msgs.length < 2) return 0;
  const latest = new Set(msgs[msgs.length - 1].toLowerCase().split(/\s+/).filter(w => w.length > 3));
  const oldest = msgs[0].toLowerCase().split(/\s+/).filter(w => w.length > 3);
  const overlap = oldest.filter(w => latest.has(w)).length;
  return Math.max(0, 1.0 - overlap / Math.max(latest.size, 1));
}

function calcDensityScore(msgs) {
  return (
    calcKeywordDensity(msgs)  * 0.35 +
    calcFilePathCount(msgs)   * 0.25 +
    calcDecisionCount(msgs)   * 0.25 +
    calcTopicShift(msgs)      * 0.15
  );
}

async function checkDensity() {
  const msgs  = recentMessageTexts.slice(-5);
  const score = Math.round(calcDensityScore(msgs) * 100) / 100;
  const res   = await safeSendMessage({ type: 'RELAY_DENSITY_UPDATE', score });
  if (!res?.notify || !res?.status || res.status === 'NORMAL') return;
  if (densityNotifiedTypes.has(res.status)) return;
  densityNotifiedTypes.add(res.status);
  showDensityNotification(res.status);
  if (res.status === 'TOPIC_SHIFT') {
    setTimeout(() => densityNotifiedTypes.delete('TOPIC_SHIFT'), 15000);
  }
}

function showDensityNotification(type) {
  if (document.getElementById('relay-density-notify')) return;
  const MESSAGES = {
    HIGH_DENSITY: '重要な情報が集中しています。今が引き継ぎのベストタイミングです',
    TOPIC_SHIFT:  '話題が大きく変わりました。前のトピックを引き継いでおきましょう',
  };
  const color = type === 'HIGH_DENSITY' ? '#ef4444' : '#f59e0b';
  const icon  = type === 'HIGH_DENSITY' ? '🔴' : '🟡';

  const overlay = document.createElement('div');
  overlay.id = 'relay-density-notify';
  overlay.style.cssText = [
    'position:fixed','top:50%','left:50%','transform:translate(-50%,-50%)',
    'background:#0c1220',`border:1px solid ${color}`,
    'border-radius:14px','padding:24px 28px','z-index:9999999',
    'font-family:ui-monospace,monospace','box-shadow:0 8px 40px rgba(0,0,0,0.8)',
    'min-width:300px','max-width:380px','text-align:center',
  ].join(';');
  overlay.innerHTML = `
    <div style="font-size:22px;margin-bottom:8px;">${icon}</div>
    <div style="color:${color};font-size:13px;font-weight:700;margin-bottom:8px;">
      ${type === 'HIGH_DENSITY' ? '密度ピーク検知' : '話題転換検知'}
    </div>
    <div style="color:#94a3b8;font-size:12px;margin-bottom:18px;line-height:1.6;">
      ${MESSAGES[type]}
    </div>
    <div style="display:flex;gap:10px;justify-content:center;">
      <button id="relay-density-handoff" style="background:#0369a1;border:1px solid #38bdf8;border-radius:8px;color:#38bdf8;font-size:12px;font-weight:700;padding:9px 18px;cursor:pointer;font-family:inherit;">⚡ 引き継ぎを準備</button>
      <button id="relay-density-dismiss" style="background:transparent;border:1px solid #334155;border-radius:8px;color:#64748b;font-size:12px;padding:9px 18px;cursor:pointer;font-family:inherit;">後で</button>
    </div>`;
  document.body.appendChild(overlay);
  document.getElementById('relay-density-handoff')?.addEventListener('click', async () => { overlay.remove(); await handleBadgeClick(); });
  document.getElementById('relay-density-dismiss')?.addEventListener('click', () => overlay.remove());
  setTimeout(() => document.getElementById('relay-density-notify')?.remove(), 30000);
}

// ─── Pro-enhanced FILE_PATTERNS ──────────────────────────────────────────────

const FILE_PATTERNS_PRO = [
  /[A-Z]:\\[^\s"']+\.[a-zA-Z]{1,5}/g,
  /\/[a-zA-Z0-9_\-\/]+\.[a-zA-Z]{1,5}/g,
  /\b\w+\.(js|py|json|ts|html|css|md|txt|csv)\b/g,
];

// ─── Free Extraction (ルールベース) ──────────────────────────────────────────

function extractDecisions(text) {
  const decisions = [];
  const lines = text.split('\n');
  let inCode = false;

  const DECISION_PATTERNS = [
    /(.{5,60})(?:にした|に決定|に決めた|を採用|を却下|することにした)/,
    /(?:採用|却下|決定|確定)\s*[:：]\s*(.{5,60})/,
    /(.{5,60})\s*(?:で行く|でいく|に統一)/,
  ];

  for (const line of lines) {
    if (line.startsWith('```')) { inCode = !inCode; continue; }
    if (inCode) continue;
    const trimmed = line.trim();
    if (trimmed.length < 10 || trimmed.length > 150) continue;
    // Pro: [RELAY_DECISION] マーカー付き行を優先検出
    if (/\[RELAY_DECISION\]/.test(trimmed)) {
      decisions.push(trimmed.replace(/\[RELAY_DECISION\]/, '').trim() || trimmed);
      continue;
    }

    for (const pat of DECISION_PATTERNS) {
      const m = trimmed.match(pat);
      if (m) {
        const decision = (m[1] || trimmed).trim();
        if (decision.length >= 5) { decisions.push(decision); break; }
      }
    }
  }
  return [...new Set(decisions)].slice(0, 5);
}

function extractFilePaths(text) {
  const FILE_PATH_RE = /(?:[A-Za-z]:\\[\w\\\/.:-]+|\/[\w/.-]{4,}\.(?:js|ts|py|json|md|txt|html|css|jsx|tsx|vue|go|rs|java|rb|sh|yaml|yml)|[\w.-]+\/[\w/.-]+\.(?:js|ts|py|json|md|html|css|jsx|tsx|go|py))/g;
  const base = text.match(FILE_PATH_RE) || [];
  const pro  = FILE_PATTERNS_PRO.flatMap(re => Array.from(text.matchAll(new RegExp(re.source, re.flags))).map(m => m[0]));
  return [...new Set([...base, ...pro])].filter(p => p.length > 3).slice(0, 10);
}

function extractKeywords(text) {
  const results = [];
  const PATTERNS = [
    /(?:エラー|バグ|修正|実装|完了|設計|警告|問題|解決)\s*[:：]\s*(.{5,60})/g,
    /(?:error|bug|fix|implement|done|design|issue|warn)\s*[:：]?\s*(.{5,60})/gi,
  ];
  for (const pat of PATTERNS) {
    const re = new RegExp(pat.source, pat.flags);
    let m;
    while ((m = re.exec(text)) !== null) {
      const kw = (m[1] || '').trim();
      if (kw.length >= 5) results.push(kw.slice(0, 60));
    }
  }
  return [...new Set(results)].slice(0, 5);
}

// ─── 20ターン警告ポップアップ ─────────────────────────────────────────────────

function showTurnWarning() {
  if (turnWarningShown) return;
  turnWarningShown = true;

  const overlay = document.createElement('div');
  overlay.id = 'relay-turn-warning';
  overlay.style.cssText = [
    'position:fixed', 'top:50%', 'left:50%',
    'transform:translate(-50%,-50%)',
    'background:#0c1220', 'border:1px solid #f59e0b',
    'border-radius:14px', 'padding:24px 28px',
    'z-index:9999999', 'font-family:ui-monospace,monospace',
    'box-shadow:0 8px 40px rgba(0,0,0,0.8),0 0 20px rgba(245,158,11,0.3)',
    'min-width:300px', 'max-width:380px', 'text-align:center',
  ].join(';');

  overlay.innerHTML = `
    <div style="font-size:22px;margin-bottom:8px;color:#f59e0b;">⚠</div>
    <div style="color:#f59e0b;font-size:14px;font-weight:700;margin-bottom:8px;">
      20ターン到達
    </div>
    <div style="color:#94a3b8;font-size:12px;margin-bottom:18px;line-height:1.6;">
      会話が長くなってきました。<br>引き継ぎを準備しますか？
    </div>
    <div style="display:flex;gap:10px;justify-content:center;">
      <button id="relay-warn-handoff" style="
        background:#0369a1;border:1px solid #38bdf8;border-radius:8px;
        color:#38bdf8;font-size:12px;font-weight:700;padding:9px 18px;
        cursor:pointer;font-family:inherit;
      ">⚡ 引き継ぎを準備</button>
      <button id="relay-warn-dismiss" style="
        background:transparent;border:1px solid #334155;border-radius:8px;
        color:#64748b;font-size:12px;padding:9px 18px;
        cursor:pointer;font-family:inherit;
      ">後で</button>
    </div>
  `;

  document.body.appendChild(overlay);

  document.getElementById('relay-warn-handoff')?.addEventListener('click', async () => {
    overlay.remove();
    await handleBadgeClick();
  });

  document.getElementById('relay-warn-dismiss')?.addEventListener('click', () => {
    overlay.remove();
  });

  // 30秒後に自動消去
  setTimeout(() => { const el = document.getElementById('relay-turn-warning'); el?.remove(); }, 30000);
}

// ─── Invisible Handoff (案A) ─────────────────────────────────────────────────

async function prepareInvisibleHandoff() {
  if (!isExtensionAlive()) return;

  // 二重注入防止フラグ確認
  const injCheck = await chrome.storage.local.get(['relay_injected']);
  if (injCheck.relay_injected) {
    console.log('[Relay] Already injected — skip');
    return;
  }

  // popup経由の手動引き継ぎパケットを最優先確認
  const stored = await chrome.storage.local.get([
    'relay_handoff_packet', 'relay_logbook_current',
    'relay_auto_inject', 'relay_inject_density', 'relay_plan',
  ]);
  let packet = stored.relay_handoff_packet || null;
  if (packet) {
    await chrome.storage.local.remove(['relay_handoff_packet']);
    console.log('[Relay] Handoff packet from popup');
  } else if (stored.relay_plan === 'one' && stored.relay_auto_inject) {
    // One版: Vault自動注入
    const density = stored.relay_inject_density ?? 3;
    const res = await safeSendMessage({ type: 'RELAY_GET_VAULT_PACKET', density });
    packet = res?.packet || null;
    if (packet) console.log('[Relay] Handoff packet from Vault (One auto-inject)');
  }
  if (!packet) {
    // Free版: relay_logbook_current から自動取得（直近1chat分）
    packet = stored.relay_logbook_current || null;
    if (packet) {
      console.log('[Relay] Handoff packet from logbook (Free)');
    } else {
      const res = await safeSendMessage({ type: 'RELAY_GET_HANDOFF' });
      packet = res?.packet || null;
    }
  }

  if (!packet) {
    console.log('[Relay] No handoff packet — clean start');
    return;
  }

  // 注入フラグを立てる（二重注入防止）
  await chrome.storage.local.set({ relay_injected: true });

  // テキストボックスが出現するまで最大5秒待ってから即入力
  console.log('[Relay] Handoff packet ready — waiting for input box...');
  injectWhenReady(packet, 0);
}

function injectWhenReady(packet, attempts) {
  const MAX = 20; // 20 * 250ms = 5秒
  const input = findInputEl();
  if (input) {
    setInputValue(input, packet);
    showBadgeFlash('safe');
    console.log('[Relay] Handoff injected into input box');
    return;
  }
  if (attempts >= MAX) {
    // fallback: 送信ボタン押下時に注入
    pendingHandoff  = packet;
    sendIntercepted = false;
    showBadgeReady();
    console.log('[Relay] Input not found — fallback to send-intercept mode');
    waitForSendButton();
    return;
  }
  setTimeout(() => injectWhenReady(packet, attempts + 1), 250);
}

function waitForSendButton() {
  if (sendButtonObserver) sendButtonObserver.disconnect();
  const btn = findSendButton();
  if (btn) { interceptSendButton(btn); return; }
  sendButtonObserver = new MutationObserver(() => {
    const b = findSendButton();
    if (b) { sendButtonObserver.disconnect(); interceptSendButton(b); }
  });
  sendButtonObserver.observe(document.body, { childList: true, subtree: true });
}

function findSendButton() {
  for (const sel of SEND_BUTTON_SELECTORS) {
    const el = document.querySelector(sel);
    if (el) return el;
  }
  return null;
}

function interceptSendButton(btn) {
  if (!pendingHandoff) return;
  btn.addEventListener('click', onFirstSend, { capture: true, once: true });
  const input = findInputEl();
  if (input) input.addEventListener('keydown', onFirstSendKey, { capture: true });
  console.log('[Relay] Send button intercepted');
}

function onFirstSend() {
  if (sendIntercepted || !pendingHandoff) return;
  sendIntercepted = true;
  prependHandoffToInput();
  clearPendingHandoff();
}

function onFirstSendKey(e) {
  if (e.key !== 'Enter' || e.shiftKey) return;
  if (sendIntercepted || !pendingHandoff) return;
  sendIntercepted = true;
  prependHandoffToInput();
  clearPendingHandoff();
  const input = findInputEl();
  if (input) input.removeEventListener('keydown', onFirstSendKey, { capture: true });
}

function prependHandoffToInput() {
  const input = findInputEl();
  if (!input || !pendingHandoff) return;
  const current  = input.innerText || input.textContent || '';
  const combined = pendingHandoff + '\n\n' + current;
  input.focus();
  const sel = window.getSelection();
  const rng = document.createRange();
  rng.selectNodeContents(input);
  sel.removeAllRanges();
  sel.addRange(rng);
  const ok = document.execCommand('insertText', false, combined);
  if (!ok) {
    input.innerText = combined;
    input.dispatchEvent(new InputEvent('input', { bubbles: true, cancelable: true }));
  }
  console.log('[Relay] Handoff invisibly prepended');
  showBadgeFlash('safe');
}

function clearPendingHandoff() {
  pendingHandoff  = null;
  sendIntercepted = false;
  if (sendButtonObserver) { sendButtonObserver.disconnect(); sendButtonObserver = null; }
}

function findInputEl() {
  for (const sel of INPUT_SELECTORS) {
    const el = document.querySelector(sel);
    if (el) return el;
  }
  return null;
}

function setInputValue(el, text) {
  el.focus();

  // Select all existing content
  const sel = window.getSelection();
  const rng = document.createRange();
  rng.selectNodeContents(el);
  sel.removeAllRanges();
  sel.addRange(rng);

  // Insert text via execCommand for React compatibility
  const ok = document.execCommand('insertText', false, text);

  // Fallback if execCommand is blocked
  if (!ok) {
    el.innerText = text;
    el.dispatchEvent(new InputEvent('input', { bubbles: true, cancelable: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  }
}

// ─── Badge ────────────────────────────────────────────────────────────────────

function createBadge() {
  if (document.getElementById(CONFIG.BADGE_ID)) return;

  injectBadgeStyles();

  badgeEl = document.createElement('div');
  badgeEl.id = CONFIG.BADGE_ID;
  badgeEl.innerHTML = `
    <div class="relay-badge-indicator">
      <div class="relay-dot"></div>
      <div class="relay-metric-row">
        <span class="relay-metric-lbl">CPI</span>
        <span class="relay-cpi-val">—</span>
      </div>
      <div class="relay-metric-row">
        <span class="relay-metric-lbl">TOK</span>
        <span class="relay-tok-val">—</span>
      </div>
      <span class="relay-cpi-label">正常</span>
    </div>
    <div class="relay-turns">T:0</div>
  `;

  badgeEl.title = 'Relay — クリックで引き継ぎ注入';
  badgeEl.addEventListener('click', handleBadgeClick);

  document.body.appendChild(badgeEl);
  makeDraggable(badgeEl, 'relay_badge_pos', 16, 180);
}

// ─── Drag Support ─────────────────────────────────────────────────────────────

/**
 * バッジをドラッグ移動可能にする
 * @param {HTMLElement} el       - ドラッグ対象要素
 * @param {string} storageKey   - 位置保存用ストレージキー
 * @param {number} defaultRight  - デフォルト right (px)
 * @param {number} defaultBottom - デフォルト bottom (px)
 */
function makeDraggable(el, storageKey, defaultRight, defaultBottom) {
  if (!isExtensionAlive()) return;
  try {
    chrome.storage.local.get(storageKey, (r) => {
      const pos = r[storageKey];
      if (pos) {
        el.style.left   = pos.left !== undefined ? pos.left + 'px' : 'auto';
        el.style.top    = pos.top  !== undefined ? pos.top  + 'px' : 'auto';
        el.style.right  = '';
        el.style.bottom = '';
      }
    });
  } catch (e) { /* extension context invalidated */ }

  let isDragging = false;
  let startX, startY, startLeft, startTop;

  el.addEventListener('mousedown', (e) => {
    if (e.button !== 0) return;
    isDragging = false;
    const rect = el.getBoundingClientRect();
    startX = e.clientX; startY = e.clientY;
    startLeft = rect.left; startTop = rect.top;
    el.style.right = ''; el.style.bottom = '';   // 先にクリア（!important対策）
    el.style.left = startLeft + 'px'; el.style.top = startTop + 'px';

    const onMove = (e) => {
      const dx = e.clientX - startX, dy = e.clientY - startY;
      if (Math.abs(dx) > 5 || Math.abs(dy) > 5) isDragging = true;
      if (isDragging) {
        el.style.left = Math.max(0, Math.min(window.innerWidth  - el.offsetWidth,  startLeft + dx)) + 'px';
        el.style.top  = Math.max(0, Math.min(window.innerHeight - el.offsetHeight, startTop  + dy)) + 'px';
      }
    };
    const onUp = () => {
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
      if (isDragging && isExtensionAlive()) {
        try {
          chrome.storage.local.set({ [storageKey]: { left: parseInt(el.style.left), top: parseInt(el.style.top) } });
        } catch (e) { /* extension context invalidated — 無視 */ }
      }
    };
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
    e.preventDefault();
  });

  el.addEventListener('click', (e) => {
    if (isDragging) { e.stopImmediatePropagation(); isDragging = false; }
  }, true);

  el.style.cursor = 'grab';
}

function injectBadgeStyles() {
  if (document.getElementById('relay-badge-styles')) return;
  const style = document.createElement('style');
  style.id = 'relay-badge-styles';
  style.textContent = `
    #relay-badge {
      position: fixed !important;
      bottom: 180px;
      right: 16px;
      left: auto !important;
      transform: none;
      width: 72px;
      height: 88px;
      background: #0c1220;
      border: 1px solid #1e3a5f;
      border-radius: 12px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: space-between;
      padding: 7px 6px;
      cursor: pointer;
      z-index: 9000 !important;
      box-shadow: 0 4px 24px rgba(0,0,0,0.7), inset 0 1px 0 rgba(255,255,255,0.04);
      transition: transform 0.25s cubic-bezier(0.4,0,0.2,1),
                  border-color 0.3s ease,
                  box-shadow 0.3s ease;
      font-family: ui-monospace, 'Cascadia Code', 'Fira Code', monospace;
      user-select: none;
    }
    #relay-badge:hover {
      transform: translateY(-3px) scale(1.04);
      border-color: #38bdf8;
      box-shadow: 0 8px 32px rgba(0,0,0,0.8), 0 0 16px rgba(56,189,248,0.25);
    }
    #relay-badge:active {
      transform: translateY(-1px) scale(1.01);
    }
    .relay-badge-indicator {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 3px;
      width: 100%;
    }
    .relay-metric-row {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      width: 100%;
      gap: 2px;
    }
    .relay-metric-lbl {
      font-size: 8px;
      color: #f0e060;
      opacity: 0.7;
      letter-spacing: 0.3px;
      flex-shrink: 0;
    }
    .relay-dot {
      width: 11px;
      height: 11px;
      border-radius: 50%;
      background: #22c55e;
      box-shadow: 0 0 8px rgba(34,197,94,0.7);
      transition: background 0.4s ease, box-shadow 0.4s ease;
    }
    .relay-dot.warn {
      background: #f59e0b;
      box-shadow: 0 0 8px rgba(245,158,11,0.7);
      animation: relay-pulse 1.8s ease-in-out infinite;
    }
    .relay-dot.ready {
      background: #38bdf8;
      box-shadow: 0 0 8px rgba(56,189,248,0.7);
      animation: relay-pulse 2.5s ease-in-out infinite;
    }
    .relay-dot.danger {
      background: #ef4444;
      box-shadow: 0 0 10px rgba(239,68,68,0.8);
      animation: relay-pulse 0.9s ease-in-out infinite;
    }
    .relay-cpi-val {
      font-size: 13px;
      font-weight: 700;
      color: #f0e060;
      letter-spacing: 0;
      line-height: 1.1;
    }
    .relay-cpi-label {
      font-size: 8px;
      color: #22c55e;
      letter-spacing: 0;
    }
    .relay-cpi-label.warn   { color: #f59e0b; }
    .relay-cpi-label.danger { color: #ef4444; }
    .relay-tokens-row {
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .relay-tok-val {
      font-size: 11px;
      font-weight: 600;
      color: #f0e060;
      letter-spacing: 0;
    }
    .relay-turns {
      font-size: 9px;
      color: #f0e060;
      letter-spacing: 0.4px;
    }
    #relay-badge.handoff-ready {
      border-color: #38bdf8 !important;
      box-shadow: 0 0 16px rgba(56,189,248,0.4) !important;
    }
    #relay-badge.flash-safe {
      border-color: #22c55e !important;
      box-shadow: 0 0 24px rgba(34,197,94,0.6) !important;
      transition: border-color 0.1s ease, box-shadow 0.1s ease;
    }
    @keyframes relay-pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50%       { opacity: 0.5; transform: scale(0.9); }
    }
  `;
  document.head.appendChild(style);
}

async function handleBadgeClick() {
  if (!isExtensionAlive()) return;
  try {
    // セッション終了してパケット生成
    await safeSendMessage({ type: 'RELAY_SESSION_END' });
    await new Promise(r => setTimeout(r, 400));

    const res = await safeSendMessage({ type: 'RELAY_GET_HANDOFF' });
    const packet = res?.packet || null;

    if (!packet) {
      showBadgeFlash('warn');
      console.log('[Relay] Badge click — no handoff data');
      return;
    }

    // storageに保存 → 新規タブのcontent.jsが自動取得して注入
    await safeSendMessage({ type: 'RELAY_STORE_HANDOFF', packet });
    await safeSendMessage({ type: 'RELAY_OPEN_TAB' });
    showBadgeFlash('safe');

    // DNA_v3 Commit: 引き継ぎ時にセッション状態を保存
    try {
      const commitData = {
        new_fact: null,
        new_decision: {
          decision: '保留',
          reason: 'セッション引き継ぎ実行',
          error_solved: null
        },
        remaining_task: 'Relay引き継ぎパケット参照',
        tension: null,
        next_hook: '次セッション: restore_packet.jsonを確認してから作業開始'
      };
      fetch('http://localhost:5000/commit_session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json; charset=utf-8' },
        body: JSON.stringify(commitData)
      }).catch(() => {}); // サーバー未起動時は無視
    } catch(e) {}

  } catch (err) {
    console.error('[Relay] Badge click error:', err);
  }
}

function updateBadge() {
  if (!badgeEl || !isExtensionAlive()) return;

  const dot      = badgeEl.querySelector('.relay-dot');
  const cpiValEl = badgeEl.querySelector('.relay-cpi-val');
  const cpiLblEl = badgeEl.querySelector('.relay-cpi-label');
  const tokEl    = badgeEl.querySelector('.relay-tok-val');
  const tEl      = badgeEl.querySelector('.relay-turns');

  if (tEl) tEl.textContent = `T:${turnCount}`;

  safeSendMessage({ type: 'RELAY_GET_STATS' }).then(s => {
    if (!s) return;

    // CPI
    const cpi = s.cpi || 0;
    if (cpiValEl) cpiValEl.textContent = cpi > 0 ? cpi.toFixed(2) : '—';

    // CPI ラベル + 色
    if (cpiLblEl) {
      let label, cls;
      if      (cpi <= 0)   { label = '待機中'; cls = ''; }
      else if (cpi < 1.2)  { label = '正常';   cls = ''; }
      else if (cpi < 1.8)  { label = '注意';   cls = 'warn'; }
      else if (cpi < 2.5)  { label = '警告';   cls = 'warn'; }
      else                 { label = '危険！'; cls = 'danger'; }
      cpiLblEl.textContent = label;
      cpiLblEl.className   = 'relay-cpi-label' + (cls ? ' ' + cls : '');
    }

    // DOT 色
    if (dot) {
      dot.className = 'relay-dot';
      if      (cpi >= 2.5) dot.classList.add('danger');
      else if (cpi >= 1.2) dot.classList.add('warn');
    }

    // TOKENS
    const tok = s.estimated_tokens || 0;
    if (tokEl) {
      tokEl.textContent = tok >= 1000
        ? (tok / 1000).toFixed(1) + 'K'
        : tok > 0 ? tok.toString() : '—';
    }
  }).catch(() => {});
}

function showBadgeReady() {
  if (!badgeEl) return;
  badgeEl.classList.add('handoff-ready');
  badgeEl.title = 'Relay — 引き継ぎ準備完了 (送信時に自動注入)';
  const dot = badgeEl.querySelector('.relay-dot');
  if (dot) dot.className = 'relay-dot ready';
}

function showBadgeFlash(type) {
  if (!badgeEl) return;
  badgeEl.classList.remove('handoff-ready');
  badgeEl.classList.add(`flash-${type}`);
  setTimeout(() => badgeEl.classList.remove(`flash-${type}`), 1600);
}

// ─── Metrics Push ─────────────────────────────────────────────────────────────

function scheduleMetricsPush() {
  setInterval(() => {
    if (!isExtensionAlive()) return;
    const heap    = performance.memory?.usedJSHeapSize || 0;
    const domSize = document.body?.innerHTML?.length   || 0;

    safeSendMessage({ type: 'RELAY_METRICS_UPDATE', heap, domSize });
    updateBadge();
  }, CONFIG.SCAN_INTERVAL);
}

// ─── Message Listener (from popup) ───────────────────────────────────────────

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'RELAY_INJECT_HANDOFF') {
    const input = findInputEl();
    if (input && msg.packet) {
      setInputValue(input, msg.packet);
      showBadgeFlash('safe');
      sendResponse({ ok: true });
    } else {
      sendResponse({ error: 'input not found' });
    }
    return true;
  }
});

// ─── Utilities ────────────────────────────────────────────────────────────────

function debounce(fn, ms) {
  let timer;
  return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), ms); };
}

function hashText(str) {
  let h = 0;
  for (let i = 0; i < str.length; i++) {
    h = Math.imul(31, h) + str.charCodeAt(i) | 0;
  }
  return (h >>> 0).toString(36);
}

// ─── Intent Engine v4.0 — Claude API自然言語判定 ────────────────────────────
// 正規表現廃止。Claudeが「TODO登録/完了/一覧/無関係」を判定する。
// ストレスなし自然言語操作: 「これ覚えといて」「3番消して」「片付けたリスト見せて」等
// ※ 引き継ぎ注入ロジックには一切触れない

(function() {

  // ── 直前のClaudeメッセージを取得 ─────────────────────────────────────────
  function getLastAIText() {
    const selectors = [
      '.font-claude-response-body',
      '[data-testid="assistant-message"]',
      'div[class*="font-claude"]',
      '[class*="assistant-message"]',
    ];
    for (const sel of selectors) {
      try {
        const els = Array.from(document.querySelectorAll(sel));
        if (els.length) {
          return (els[els.length - 1].textContent || '').trim().slice(0, 300);
        }
      } catch(e) {}
    }
    return '';
  }

  // ── 軽量ローカル事前フィルタ（APIコスト節約）────────────────────────────
  // 明らかにTODO操作でない長文は早期リターン
  const QUICK_TODO_HINT = /todo|タスク|LB_?\d|完了|消して|終わった|登録|片付け|覚えといて|remind|task|done|finish|close|list|一覧|見せ|add|mark/i;

  function mightBeIntent(text) {
    // 50文字超の通常会話はAPIに投げない
    if (text.length > 120) return false;
    return QUICK_TODO_HINT.test(text);
  }

  // ── Claude API判定 ────────────────────────────────────────────────────────
  // background.jsのRELAY_CLASSIFY_INTENTメッセージで判定（APIキー不要）
  // background.jsが持つAPIキーを使うためにmessage経由
  async function classifyIntent(userText, lastAIText, currentTodos) {
    try {
      const todoSummary = currentTodos.slice(0, 10)
        .map(t => `  LB_${String(t.num).padStart(3,'0')}: ${t.text.slice(0,40)}`)
        .join('\n') || '（なし）';

      const res = await safeSendMessage({
        type:        'RELAY_CLASSIFY_INTENT',
        userText,
        lastAIText,
        todoSummary,
      });
      return res?.intent || null;
    } catch(e) {
      console.error('[Relay Intent v4] classify error:', e);
      return null;
    }
  }

  // ── トースト表示 ─────────────────────────────────────────────────────────
  function showIntentToast(msg, color, duration) {
    const el = document.createElement('div');
    el.style.cssText = [
      'position:fixed', 'bottom:100px', 'right:24px',
      `background:${color || '#22c55e'}`, 'color:#fff',
      'padding:9px 16px', 'border-radius:10px', 'font-size:13px',
      'z-index:9999999', 'font-family:ui-monospace,monospace',
      'box-shadow:0 4px 16px rgba(0,0,0,0.5)', 'max-width:340px',
      'white-space:pre-line',
    ].join(';');
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), duration || 3500);
  }

  // ── TODO登録処理 ─────────────────────────────────────────────────────────
  async function handleAdd(intent) {
    if (!isExtensionAlive()) return;
    const what = (intent.what || '').trim();
    if (!what || what.length < 5) {
      showIntentToast('⚠ TODOの内容を取得できませんでした', '#f59e0b');
      return;
    }
    await safeSendMessage({
      type:   'RELAY_ADD_TODO',
      text:   what,
      why:    intent.why || '',
      where:  location.href.replace('https://claude.ai', ''),
      source: 'voice_ai',
    });
    const msg = intent.why
      ? `📌 TODO登録\nWHAT: ${what.slice(0,50)}\nWHY: ${intent.why.slice(0,50)}`
      : `📌 TODO登録\n${what.slice(0,60)}`;
    showIntentToast(msg);
  }

  // ── TODO一覧をトーストで表示 ─────────────────────────────────────────────
  async function showTodoList() {
    if (!isExtensionAlive()) return;
    try {
      const res   = await safeSendMessage({ type: 'RELAY_GET_TODO_LIST' });
      const todos = res?.todos || [];
      if (!todos.length) { showIntentToast('📋 未完了TODOはありません', '#475569'); return; }
      const lines = ['📋 未完了TODO:'];
      todos.slice(0, 8).forEach(t => {
        const why = t.why ? ` (${t.why.slice(0,20)})` : '';
        lines.push(`  ${t.id}: ${t.text.slice(0,40)}${why}`);
      });
      if (todos.length > 8) lines.push(`  … 他${todos.length - 8}件`);
      showIntentToast(lines.join('\n'), '#0f172a', 5000);
    } catch(e) { console.error('[Relay Intent] showTodoList error:', e); }
  }

  // ── 完了処理 ─────────────────────────────────────────────────────────────
  async function handleComplete(intent) {
    if (!isExtensionAlive()) return;
    try {
      if (intent.type === 'single' && intent.num != null) {
        const res = await safeSendMessage({ type: 'RELAY_COMPLETE_BY_NUM', num: intent.num });
        if (res?.ok) showIntentToast(`✓ LB_${String(intent.num).padStart(3,'0')} 完了`);
        else showIntentToast(`LB_${String(intent.num).padStart(3,'0')} が見つかりません`, '#f59e0b');
      } else if (intent.type === 'range' && intent.from != null && intent.to != null) {
        const res = await safeSendMessage({ type: 'RELAY_COMPLETE_RANGE', from: intent.from, to: intent.to });
        showIntentToast(`✓ LB_${String(intent.from).padStart(3,'0')} 〜 LB_${String(intent.to).padStart(3,'0')} 完了 (${res?.count || 0}件)`);
      } else if (intent.type === 'complete_all') {
        const res = await safeSendMessage({ type: 'RELAY_COMPLETE_ALL' });
        showIntentToast(`✓ 全TODO完了 (${res?.count || 0}件)`);
      }
    } catch(e) { console.error('[Relay Intent] handleComplete error:', e); }
  }

  // ── Enterキー監視 ─────────────────────────────────────────────────────────
  let _classifying = false; // 二重処理防止

  document.addEventListener('keydown', function onIntentKey(e) {
    if (e.key !== 'Enter' || e.shiftKey) return;

    const input = document.querySelector('div[contenteditable="true"]') ||
                  document.querySelector('textarea');
    if (!input) return;

    const text = (input.innerText || input.value || '').trim();
    if (!text || text.length < 2) return;

    // 軽量フィルタ — TODO操作の匂いがなければスキップ
    if (!mightBeIntent(text)) return;

    if (_classifying) return;
    _classifying = true;

    setTimeout(async () => {
      try {
        showIntentToast('🤔 …', '#475569', 8000);

        // 現在のTODOリスト取得
        const res   = await safeSendMessage({ type: 'RELAY_GET_TODO_LIST' });
        const todos = res?.todos || [];

        const lastAI = getLastAIText();
        const intent = await classifyIntent(text, lastAI, todos);

        // トースト消去
        document.querySelectorAll('[data-relay-toast]').forEach(el => el.remove());

        if (!intent || intent.type === 'none') {
          // TODO操作ではなかった — 何もしない（通常送信）
        } else if (intent.type === 'list') {
          await showTodoList();
        } else if (intent.type === 'add') {
          await handleAdd(intent);
        } else {
          await handleComplete(intent);
        }
      } catch(err) {
        console.error('[Relay Intent v4] error:', err);
      } finally {
        _classifying = false;
      }
    }, 300);

  }, false);

  console.log('[Relay] Intent Engine v4.0 (Claude API判定) loaded');

})();

// ─── Manual TODO — 選択テキスト右クリック (半自動) ───────────────────────────
// テキスト選択後Ctrl+Shift+T でTODO登録
// ※ 右クリックはmanifest.jsonのcontextMenusで対応、ここではキーショートカット

(function() {

  document.addEventListener('keydown', function onManualTodo(e) {
    // Ctrl+Shift+T (Windows/Linux) or Cmd+Shift+T (Mac)
    if (!((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T')) return;

    const sel = window.getSelection();
    const text = sel ? sel.toString().trim() : '';

    if (!text || text.length < 5) {
      // 選択なし → TODOリスト表示
      safeSendMessage({ type: 'RELAY_GET_TODO_LIST' }).then(res => {
        const todos = res?.todos || [];
        if (!todos.length) {
          showManualToast('📋 未完了TODOはありません', '#475569');
          return;
        }
        const lines = todos.slice(0, 6).map(t => `${t.id}: ${t.text.slice(0,45)}`);
        showManualToast('📋 ' + lines.join('\n'), '#0f172a');
      }).catch(() => {});
      return;
    }

    if (text.length > 200) {
      showManualToast('選択テキストが長すぎます（200文字以内）', '#f59e0b');
      return;
    }

    safeSendMessage({ type: 'RELAY_ADD_TODO', text, source: 'manual' }).then(() => {
      showManualToast(`📌 TODO登録: ${text.slice(0, 50)}${text.length > 50 ? '…' : ''}`);
    }).catch(() => {});

    e.preventDefault();
  }, false);

  function showManualToast(msg, color) {
    const el = document.createElement('div');
    el.textContent = msg;
    el.style.cssText = [
      'position:fixed', 'bottom:100px', 'right:24px',
      `background:${color || '#3b82f6'}`, 'color:#fff',
      'padding:9px 16px', 'border-radius:10px', 'font-size:13px',
      'z-index:9999999', 'font-family:ui-monospace,monospace',
      'box-shadow:0 4px 16px rgba(0,0,0,0.5)', 'white-space:pre-line',
      'max-width:340px',
    ].join(';');
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 3500);
  }

  console.log('[Relay] Manual TODO (Ctrl+Shift+T) loaded');

})();

// ─── Boot ────────────────────────────────────────────────────────────────────

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
