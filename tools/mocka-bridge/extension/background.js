console.log("[MOCKA] background.js 起動開始");
const AI_DOMAINS = {
  ChatGPT:    'chatgpt.com',
  Gemini:     'gemini.google.com',
  Perplexity: 'perplexity.ai',
  Claude:     'claude.ai',
  Copilot:    'copilot.microsoft.com',
  Genspark:   'genspark.ai'
};

const POLL_INTERVAL_MS = 1500;
const POLL_START_DELAY_MS = 5000;
const KEEPALIVE_ALARM = 'mocka-poll-keepalive';

// Service Worker には window が無いため alert() は使えない。
// 通知は chrome.notifications 経由に統一する。
function notify(title, message) {
  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'icons/icon128.png',
    title: title,
    message: String(message || '')
  }, () => { void chrome.runtime.lastError; });
}

// ページ側に alert を出す。制限ページ等では executeScript が reject するため
// 必ず catch し、失敗時は拡張通知にフォールバックする。
function alertOnPage(tabId, message) {
  if (typeof tabId !== 'number') {
    notify('MoCKA', message);
    return;
  }
  chrome.scripting.executeScript({
    target: { tabId: tabId },
    func: (text) => alert(text),
    args: [message]
  }).catch(() => { notify('MoCKA', message); });
}

async function poll() {
  for (const [name, domain] of Object.entries(AI_DOMAINS)) {
    try {
      const res = await fetch(`http://127.0.0.1:5000/get_intent/${name}`, {
        signal: AbortSignal.timeout(3000)
      }).catch(() => null);
      if (!res || !res.ok) continue;
      if (res.status === 204) continue;
      let data = null;
      try { data = await res.json(); } catch(e) { continue; }
      if (!data) continue;
      const tabs = await chrome.tabs.query({});
      const targetTab = tabs.find(t => t.url && t.url.includes(domain));
      if (targetTab) {
        await chrome.tabs.update(targetTab.id, { active: true });
        await chrome.windows.update(targetTab.windowId, { focused: true });
        chrome.scripting.executeScript({
          target: { tabId: targetTab.id },
          func: (text) => {
            const el = document.querySelector('textarea, [contenteditable="true"], input');
            if (el) {
              if (el.tagName === 'DIV') el.innerText = text; else el.value = text;
              el.dispatchEvent(new Event('input', { bubbles: true }));
              el.focus();
            }
          },
          args: [data.payload]
        }).catch(() => {});
      } else {
        chrome.tabs.create({ url: 'https://' + domain });
      }
    } catch(e) {
      console.warn('[MoCKA] poll error:', e.message);
    }
  }
}

function safePoll() {
  poll().catch(e => console.warn('[MoCKA] safePoll:', e.message));
}

// MV3 の Service Worker は休止すると setInterval も破棄される。
// alarm で叩き起こした際にポーリングを張り直す。
let pollTimer = null;
function startPolling() {
  if (pollTimer !== null) return;
  pollTimer = setInterval(safePoll, POLL_INTERVAL_MS);
  safePoll();
}

// 起動直後のクラッシュ防止のため少し待ってから開始
setTimeout(startPolling, POLL_START_DELAY_MS);

chrome.alarms.get(KEEPALIVE_ALARM, (alarm) => {
  void chrome.runtime.lastError;
  if (!alarm) chrome.alarms.create(KEEPALIVE_ALARM, { periodInMinutes: 0.5 });
});

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === KEEPALIVE_ALARM) startPolling();
});

chrome.runtime.onStartup.addListener(() => { startPolling(); });

const injectedTabs = new Set();
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url && tab.url.includes('claude.ai')) {
    if (injectedTabs.has(tabId)) return;
    injectedTabs.add(tabId);
    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      files: ['content.js']
    }).catch(() => {});
  }
});
chrome.tabs.onRemoved.addListener((tabId) => { injectedTabs.delete(tabId); });
chrome.tabs.onUpdated.addListener((tabId, changeInfo) => {
  if (changeInfo.url) injectedTabs.delete(tabId);
});

// 既存メニューが残ったまま create すると duplicate id エラーになるため
// 必ず removeAll してから作り直す。
function setupContextMenus() {
  chrome.contextMenus.removeAll(() => {
    void chrome.runtime.lastError;
    chrome.contextMenus.create({ id:'mocka-save',      title:'💾 MoCKAに保存',               contexts:['selection'] });
    chrome.contextMenus.create({ id:'mocka-share',     title:'📡 MoCKAで共有',               contexts:['selection'] });
    chrome.contextMenus.create({ id:'mocka-orchestra', title:'🤝 MoCKAで協議',               contexts:['selection'] });
    chrome.contextMenus.create({ id:'separator-1', type:'separator', contexts:['selection'] });
    chrome.contextMenus.create({ id:'mocka-hint',      title:'💡 ヒント！',                  contexts:['selection'] });
    chrome.contextMenus.create({ id:'mocka-great',     title:'🏆 グレイト！',                contexts:['selection'] });
    chrome.contextMenus.create({ id:'separator-2', type:'separator', contexts:['selection'] });
    chrome.contextMenus.create({ id:'mocka-collect',   title:'📥 このchat全文をMoCKAに収集', contexts:['page'] });
    chrome.contextMenus.create({ id:'separator-3', type:'separator', contexts:['selection'] });
    chrome.contextMenus.create({ id:'mocka-mataka', title:'😤 またか！（再発クレーム）', contexts:['selection'] });
    chrome.contextMenus.create({ id:'mocka-claim',  title:'🚨 クレーム！（インシデント）', contexts:['selection'] });
  });
}

chrome.runtime.onInstalled.addListener(() => { setupContextMenus(); });

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  const text   = info.selectionText || '';
  const tabId  = tab && typeof tab.id === 'number' ? tab.id : null;
  const tabUrl = (tab && tab.url) || '';
  const source = detectSource(tabUrl);

  if (info.menuItemId === 'mocka-save') {
    fetch('http://localhost:5000/ask', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({c:'A', o:'infield', memo:'[save] ' + text})
    }).then(() => {
      alertOnPage(tabId, 'MoCKA: saved');
    }).catch(() => {});
  }

  if (info.menuItemId === 'mocka-share') {
    const targets = ['ChatGPT','Gemini','Claude','Perplexity','Copilot'];
    targets.forEach(t => {
      fetch('http://localhost:5000/ask', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({c:'B', o:t, memo:text})
      }).catch(() => { console.warn('[MoCKA] share intent failed'); });
    });
    fetch('http://localhost:5000/orchestra', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({prompt: text, mode: 'share'})
    }).then(() => {
      alertOnPage(tabId, 'MoCKA: shared');
    }).catch(() => {
      alertOnPage(tabId, 'MoCKA ERROR: サーバー停止中 (localhost:5000)');
    });
  }

  if (info.menuItemId === 'mocka-orchestra') {
    fetch('http://localhost:5000/orchestra', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({prompt: text})
    }).then(() => {
      alertOnPage(tabId, 'MoCKA: orchestra started');
    }).catch(() => {});
  }

  if (info.menuItemId === 'mocka-mataka' || info.menuItemId === 'mocka-claim') {
    const type = info.menuItemId === 'mocka-mataka' ? 'mataka' : 'claim';
    await sendIncident(type, info.selectionText || '', tabUrl);
    return;
  }

  if (info.menuItemId === 'mocka-hint') {
    fetch('http://localhost:5000/ask', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({c:'A', o:'infield', memo:'[hint] ' + text})
    }).then(() => {
      alertOnPage(tabId, 'MoCKA: ヒント記録！');
    }).catch(() => {});
    fetch('http://localhost:5000/success', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({type: 'hint', text: text, source: source, url: tabUrl})
    }).catch(() => {});
  }

  if (info.menuItemId === 'mocka-great') {
    fetch('http://localhost:5000/ask', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({c:'A', o:'infield', memo:'[great] ' + text})
    }).then(() => {
      alertOnPage(tabId, 'MoCKA: グレイト記録！！');
    }).catch(() => {});
    fetch('http://localhost:5000/success', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({type: 'great', text: text, source: source, url: tabUrl})
    }).catch(() => {});
  }

  // ===== chat全文収集 (clipboard専用版) =====
  if (info.menuItemId === 'mocka-collect') {
    let collected = false;

    // まずexecuteScriptを試みる（claude/chatgpt用）
    try {
      const results = await chrome.scripting.executeScript({
        target: { tabId: tabId },
        func: async function(source) {
          const SEL = {
            chatgpt:    '[data-message-author-role]',
            claude:     '[data-testid*="message"], .font-claude-message',
            gemini:     'message-content, model-response, user-query',
            copilot:    '[class*="message"]',
          };
          const sel = SEL[source] || 'p';
          const nodes = document.querySelectorAll(sel);
          let lines = [];
          nodes.forEach((n, i) => {
            const role = n.getAttribute('data-message-author-role') || (i%2===0 ? 'user' : 'assistant');
            const t = n.innerText.trim();
            if (t) lines.push('[' + role + '] ' + t);
          });
          if (!lines.length) lines.push(document.body.innerText.trim());
          return lines.join('\n\n');
        },
        args: [source]
      });
      if (results && results[0] && results[0].result && results[0].result.length > 50) {
        await fetch('http://127.0.0.1:5000/collect', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ source, text: results[0].result, url: tabUrl, mode: 'script', timestamp: new Date().toISOString() })
        });
        alertOnPage(tabId, 'MoCKA: collected!');
        collected = true;
      }
    } catch(e) {
      console.warn('[MoCKA] script collect blocked, trying clipboard:', e.message);
    }

    // content script経由でclipboard取得（Perplexity等CSPブロックサイト用）
    if (!collected) {
      try {
        const response = await chrome.tabs.sendMessage(tabId, { action: 'collect_clipboard' });
        if (response && response.ok && response.text && response.text.length > 20) {
          await fetch('http://127.0.0.1:5000/collect', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ source, text: response.text, url: tabUrl, mode: 'clipboard', timestamp: new Date().toISOString() })
          });
          notify('MoCKA収集完了', source + ' から ' + response.text.length + '文字収集しました');
          collected = true;
        } else {
          notify('MoCKA収集失敗', 'Ctrl+A -> Ctrl+C 後に再実行してください');
        }
      } catch(e2) {
        console.warn('[MoCKA] content script message failed:', e2.message);
        notify('MoCKA収集失敗', e2.message);
      }
    }
  }
});

async function sendIncident(type, selectedText, url) {
  const source = detectSource(url);
  const endpoint = type === 'mataka' ? '/mataka' : '/claim';
  try {
    const res = await fetch('http://127.0.0.1:5000' + endpoint, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        selected_text: selectedText,
        url: url,
        who: source,
        timestamp: new Date().toISOString(),
        type: type
      })
    });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();
    const count = data.recurrence_count || 1;
    const msg = type === 'mataka'
      ? `😤 またか！記録完了\nパターン: ${data.pattern || selectedText.slice(0,30)}\n再発: ${count}回目`
      : `🚨 クレーム記録完了\nインシデント: ${data.event_id}`;
    notify('MoCKA', msg);
  } catch(e) {
    notify('MoCKA 記録失敗', e.message);
  }
}

function detectSource(url) {
  if (!url) return 'unknown';
  if (url.includes('chatgpt.com'))       return 'chatgpt';
  if (url.includes('gemini.google.com')) return 'gemini';
  if (url.includes('perplexity.ai'))     return 'perplexity';
  if (url.includes('claude.ai'))         return 'claude';
  if (url.includes('microsoft.com'))     return 'copilot';
  return 'unknown';
}
