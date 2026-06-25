// content.js — MoCKA Relay v2.0
// 仕様根拠: MoCKA_Relay_handoff_spec_v1.md / 要件定義書 v1.0
// 旧実装コードは一切引き継がない。仕様書のみを基準に新規実装。
'use strict';

(function () {

  // ─── 定数 ───────────────────────────────────────────────────────────────────

  const TURN_WARNING_THRESHOLD = 20;
  const STORAGE = {
    TODOS:           'relay_todos',
    LOGBOOK_CURRENT: 'relay_logbook_current',
    INJECTED:        'relay_injected',
  };

  // ─── 状態 ───────────────────────────────────────────────────────────────────

  let turnCount   = 0;
  let warnShown   = false;
  let domObserver = null;
  let lastUrl     = location.href;

  // ─── URL判定 ────────────────────────────────────────────────────────────────

  function isNewChatUrl(url) {
    return /claude\.ai\/(new|chats\/new)/i.test(url);
  }

  function isChatUrl(url) {
    // /chat/xxx 形式（/new は含まない）
    return /claude\.ai\/chat\/[a-zA-Z0-9_-]+/.test(url);
  }

  // ─── ターン数カウント ────────────────────────────────────────────────────────

  function countTurns() {
    // claude.ai の人間側メッセージを数える
    // data-message-author-role="human" が最も確実
    const humanMsgs = document.querySelectorAll('[data-message-author-role="human"]');
    if (humanMsgs.length > 0) return humanMsgs.length;

    // フォールバック: fieldset/role的なコンテナ
    const altMsgs = document.querySelectorAll('.human-turn, [class*="HumanTurn"]');
    return altMsgs.length;
  }

  function checkTurnWarning() {
    const n = countTurns();
    turnCount = n;
    chrome.runtime.sendMessage({ type: 'TURN_UPDATE', count: n }).catch(() => {});

    if (n >= TURN_WARNING_THRESHOLD && !warnShown) {
      warnShown = true;
      showTurnWarning(n);
    }
  }

  // ─── 警告ポップアップ ────────────────────────────────────────────────────────

  function showTurnWarning(n) {
    const existing = document.getElementById('relay-turn-warning');
    if (existing) existing.remove();

    const el = document.createElement('div');
    el.id = 'relay-turn-warning';
    el.style.cssText = [
      'position:fixed', 'top:20px', 'right:20px', 'z-index:2147483647',
      'background:#0f172a', 'border:2px solid #ef4444', 'border-radius:12px',
      'padding:16px 20px', 'color:#f1f5f9', 'font-family:system-ui,sans-serif',
      'font-size:14px', 'max-width:300px', 'box-shadow:0 8px 32px rgba(0,0,0,0.6)',
      'line-height:1.5',
    ].join(';');

    el.innerHTML = `
      <div style="font-weight:700;color:#ef4444;margin-bottom:6px;">⚠️ ${n}ターン到達</div>
      <div style="color:#94a3b8;margin-bottom:14px;font-size:13px;">引き継ぎを準備しますか？</div>
      <div style="display:flex;gap:8px;">
        <button id="relay-warn-ok" style="
          flex:1;background:#ef4444;border:none;color:#fff;
          padding:8px 10px;border-radius:8px;cursor:pointer;
          font-size:13px;font-weight:600;
        ">引き継ぎを準備</button>
        <button id="relay-warn-dismiss" style="
          flex:1;background:#1e293b;border:1px solid #334155;color:#94a3b8;
          padding:8px 10px;border-radius:8px;cursor:pointer;font-size:13px;
        ">閉じる</button>
      </div>
    `;
    document.body.appendChild(el);

    el.querySelector('#relay-warn-ok').addEventListener('click', () => {
      el.remove();
      // popupを開くようにバックグラウンドに依頼（MV3ではcontent→bgへ委譲）
      chrome.runtime.sendMessage({ type: 'OPEN_POPUP' }).catch(() => {});
    });
    el.querySelector('#relay-warn-dismiss').addEventListener('click', () => el.remove());
  }

  // ─── 引き継ぎパケットブロック判定 ────────────────────────────────────────────
  // 仕様書 §2 に従い、ブロックを行単位で管理し範囲を返す。
  // ブロック内の行は TODO 抽出の前に完全除外する（順序厳守）。

  function getHandoffBlockRanges(lines) {
    const ranges = [];
    let inBlock = false;
    let blockStart = -1;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (!inBlock && line.startsWith('## 引き継ぎパケット [Relay')) {
        inBlock = true;
        blockStart = i;
      } else if (inBlock && i > blockStart && line.startsWith('## ')) {
        // 独立した ## 見出しがブロック終端（この行はブロック外）
        ranges.push({ start: blockStart, end: i });
        inBlock = false;
        blockStart = -1;
      }
    }
    if (inBlock) {
      ranges.push({ start: blockStart, end: lines.length });
    }
    return ranges;
  }

  function isInBlock(idx, ranges) {
    return ranges.some(r => idx >= r.start && idx < r.end);
  }

  // ─── TODO抽出パイプライン ───────────────────────────────────────────────────
  // 仕様書 §3 の「抽出パイプラインの順序（厳守）」に従う。

  const TODO_PATTERNS = [
    /\[RELAY_TODO\]/,
    /^TODO[:\s]/i,
    /^-\s*TODO/i,
    /^あとで[:：]/,
    /^次に[:：]/,
    /次のアクション[:：]/,
    /要対応[:：]/,
  ];

  function extractTodosFromText(fullText) {
    const lines = fullText.split('\n');

    // Step 1: 引き継ぎパケットブロック範囲を先に確定
    const blockRanges = getHandoffBlockRanges(lines);

    const todos = [];
    const seen = new Set();

    for (let i = 0; i < lines.length; i++) {
      // Step 2: ブロック内なら即除外（TODOパターン判定をしない）
      if (isInBlock(i, blockRanges)) continue;

      // Step 3: ブロック外のみTODOパターンにかける
      const line = lines[i].trim();
      if (!line) continue;

      for (const pat of TODO_PATTERNS) {
        if (pat.test(line) && !seen.has(line)) {
          seen.add(line);
          todos.push({
            id: `todo_${Date.now()}_${i}`,
            text: line,
            done: false,
            createdAt: new Date().toISOString(),
          });
          break;
        }
      }
    }
    return todos;
  }

  // ─── 会話テキスト取得 ────────────────────────────────────────────────────────

  function getConversationText() {
    // [data-message-author-role] を持つ要素のテキストを結合
    const msgs = document.querySelectorAll('[data-message-author-role]');
    if (msgs.length > 0) {
      return Array.from(msgs)
        .map(el => el.innerText || el.textContent || '')
        .join('\n\n');
    }
    // フォールバック
    const main = document.querySelector('main');
    return main ? (main.innerText || main.textContent || '') : '';
  }

  // ─── 引き継ぎパケット生成 ────────────────────────────────────────────────────
  // 仕様書 §1 の正式テンプレートに厳密一致。

  function generatePacket(plan) {
    const now = new Date();
    const pad = n => String(n).padStart(2, '0');
    const dateStr = `${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}`;

    const fullText = getConversationText();
    const lines = fullText.split('\n');
    const blockRanges = getHandoffBlockRanges(lines);
    const eligible = lines.filter((_, i) => !isInBlock(i, blockRanges));

    const topic    = extractTopic(eligible);
    const decisions = extractLines(eligible, [/決定[:：]/, /確定[:：]/, /方針[:：]/, /合意[:：]/]);
    const todos     = extractLines(eligible, [/TODO/i, /あとで/, /次に[:：]/, /\[RELAY_TODO\]/]);
    const files     = extractLines(eligible, [/\b[\w./\\-]+\.(js|ts|py|md|json|html|css|txt|yml|yaml)\b/]);
    const memos     = extractLines(eligible, [/注意[:：]/, /重要[:：]/, /メモ[:：]/, /⚠/, /memo[:：]/i]);

    const fmt = arr => arr.length > 0
      ? arr.map(s => `- ${s}`).join('\n')
      : '- (なし)';

    // 仕様書テンプレートに厳密一致（見出し・順序・省略不可）
    return [
      `## 引き継ぎパケット [Relay ${plan}]`,
      `**いつ**: ${dateStr} (${turnCount}ターン)`,
      `**何を**: ${topic}`,
      `**決定事項**:`,
      fmt(decisions),
      `**TODO/次のアクション**:`,
      fmt(todos),
      `**関連ファイル**:`,
      fmt(files),
      `**重要メモ**:`,
      fmt(memos),
    ].join('\n');
  }

  function extractTopic(lines) {
    for (const line of lines) {
      const t = line.trim();
      if (t.length >= 10 && !t.startsWith('#') && !t.startsWith('-')) {
        return t.slice(0, 80) + (t.length > 80 ? '…' : '');
      }
    }
    return '(自動抽出できませんでした)';
  }

  function extractLines(lines, patterns) {
    const results = [];
    const seen = new Set();
    for (const line of lines) {
      const t = line.trim();
      if (!t || seen.has(t)) continue;
      for (const pat of patterns) {
        if (pat.test(t)) {
          seen.add(t);
          results.push(t.replace(/^[-*•]\s*/, ''));
          break;
        }
      }
      if (results.length >= 8) break;
    }
    return results;
  }

  // ─── TODO保存（既存とマージ） ────────────────────────────────────────────────

  function saveTodos(newTodos, callback) {
    chrome.storage.local.get(STORAGE.TODOS, result => {
      const existing = result[STORAGE.TODOS] || [];
      const existTexts = new Set(existing.map(t => t.text));
      const merged = [...existing, ...newTodos.filter(t => !existTexts.has(t.text))];
      chrome.storage.local.set({ [STORAGE.TODOS]: merged }, () => callback && callback(merged));
    });
  }

  // ─── 新規chat自動注入 ────────────────────────────────────────────────────────

  function handleNewChat() {
    chrome.storage.local.get([STORAGE.LOGBOOK_CURRENT, STORAGE.INJECTED], result => {
      if (result[STORAGE.INJECTED]) return;

      const packet = result[STORAGE.LOGBOOK_CURRENT];
      if (!packet) return;

      const inputEl = findInputArea();
      if (inputEl) {
        injectToInput(inputEl, packet);
      } else {
        // フォールバック: クリップボード
        navigator.clipboard.writeText(packet).then(() => {
          showNotice('引き継ぎパケットをクリップボードにコピーしました', '#22c55e');
        });
      }
      chrome.storage.local.set({ [STORAGE.INJECTED]: true });
    });
  }

  function findInputArea() {
    return (
      document.querySelector('[contenteditable="true"][data-placeholder]') ||
      document.querySelector('div[contenteditable="true"]') ||
      document.querySelector('textarea')
    );
  }

  function injectToInput(el, text) {
    el.focus();
    if (el.tagName === 'TEXTAREA') {
      const nativeSetter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
      nativeSetter.call(el, text);
      el.dispatchEvent(new Event('input', { bubbles: true }));
    } else {
      // contenteditable
      el.innerText = text;
      el.dispatchEvent(new Event('input', { bubbles: true }));
    }
    showNotice('引き継ぎパケットを入力欄に挿入しました', '#22c55e');
  }

  function showNotice(msg, color) {
    const el = document.createElement('div');
    el.style.cssText = [
      'position:fixed', 'bottom:24px', 'right:24px', 'z-index:2147483647',
      `background:#0f172a`, `border:1px solid ${color}`, 'border-radius:10px',
      'padding:12px 16px', `color:${color}`, 'font-family:system-ui,sans-serif',
      'font-size:13px', 'box-shadow:0 4px 16px rgba(0,0,0,0.5)',
    ].join(';');
    el.textContent = '✅ ' + msg;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 4000);
  }

  // ─── セッション開始通知 ──────────────────────────────────────────────────────

  function notifySessionStart() {
    chrome.runtime.sendMessage({ type: 'SESSION_STARTED', url: location.href }).catch(() => {});
  }

  // ─── MutationObserver ────────────────────────────────────────────────────────

  function startObserver() {
    if (domObserver) domObserver.disconnect();
    domObserver = new MutationObserver(() => checkTurnWarning());
    domObserver.observe(document.body, { childList: true, subtree: true });
  }

  // ─── URL変更ハンドラ ────────────────────────────────────────────────────────

  function onUrlChange(newUrl) {
    // 新しいchatセッションなので注入フラグをリセット
    chrome.storage.local.remove(STORAGE.INJECTED);

    // ターン数・警告リセット
    turnCount = 0;
    warnShown = false;

    if (isNewChatUrl(newUrl)) {
      // /new → onUrlChange側でセッション開始通知（init()側とは一本化）
      notifySessionStart();
      setTimeout(handleNewChat, 1500);
    }
    // /chat/xxx への遷移はinit()で処理済みのため何もしない

    startObserver();
  }

  // ─── メッセージハンドラ ──────────────────────────────────────────────────────

  chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
    if (msg.type === 'GENERATE_PACKET') {
      const packet = generatePacket(msg.plan || 'Free');
      chrome.storage.local.set({ [STORAGE.LOGBOOK_CURRENT]: packet });
      sendResponse({ packet });
      return true;
    }

    if (msg.type === 'EXTRACT_TODOS') {
      const newTodos = extractTodosFromText(getConversationText());
      saveTodos(newTodos, merged => sendResponse({ todos: merged }));
      return true;
    }

    if (msg.type === 'GET_TURN_COUNT') {
      sendResponse({ count: turnCount });
      return true;
    }
  });

  // ─── 初期化 ─────────────────────────────────────────────────────────────────

  function init() {
    const url = location.href;

    // /chat/xxx で開いた場合のみ init() 内でセッション開始通知
    // /new はonUrlChange()側に一本化し、二重発火させない
    if (isChatUrl(url)) {
      notifySessionStart();
    }

    startObserver();
    checkTurnWarning();

    // /new で最初から開いた場合
    if (isNewChatUrl(url)) {
      notifySessionStart();
      setTimeout(handleNewChat, 1500);
    }

    // SPA対応: URL変更をポーリングで検知
    setInterval(() => {
      if (location.href !== lastUrl) {
        const newUrl = location.href;
        lastUrl = newUrl;
        onUrlChange(newUrl);
      }
    }, 600);

    // COMMAND CENTER relay_dom 生存確認用: 60秒ごとに /relay/ping へPOST
    function sendRelayPing() {
      fetch('http://127.0.0.1:5000/relay/ping', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ version: '2.0.0' }),
      }).catch(() => {}); // サーバー未起動時は無視
    }
    sendRelayPing();
    setInterval(sendRelayPing, 60000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
