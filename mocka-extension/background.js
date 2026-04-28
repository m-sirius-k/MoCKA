const AI_DOMAINS = {
  'ChatGPT':    'chatgpt.com',
  'Gemini':     'gemini.google.com',
  'Perplexity': 'perplexity.ai',
  'Claude':     'claude.ai',
  'Copilot':    'copilot.microsoft.com',
  'Genspark':   'genspark.ai'
};

// ── 右クリックメニュー ──────────────────────────────────────
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({ id:'mocka_collect_selected', title:'選択範囲をMoCKAに収集', contexts:['selection'] });
    chrome.contextMenus.create({ id:'mocka_collect_full',     title:'このchat全文をMoCKAに収集', contexts:['page'] });
    chrome.contextMenus.create({ id:'mocka_share',            title:'MoCKAに共有（Broadcast）', contexts:['selection'] });
    chrome.contextMenus.create({ id:'mocka_collaborate',      title:'MoCKAで協議（Orchestra）', contexts:['selection'] });
    chrome.contextMenus.create({ id:'mocka_hint',  title:'ヒント！（成功シグナル）', contexts:['selection','page'] });
    chrome.contextMenus.create({ id:'mocka_great', title:'グレイト！（強い成功シグナル）', contexts:['selection','page'] });
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  const source = detectSource(tab.url);

  
  // ── ヒント！/グレイト！ ──────────────────────────────────────────────────
  if (info.menuItemId === 'mocka_hint' || info.menuItemId === 'mocka_great') {
    const text    = info.selectionText || document.title || '';
    const outcome = info.menuItemId === 'mocka_great' ? 'success_great' : 'success_hint';
    const label   = info.menuItemId === 'mocka_great' ? 'グレイト！' : 'ヒント！';
    if (!text) return;
    try {
      await fetch('http://127.0.0.1:5000/success', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text:       text,
          what_type:  outcome,
          source:     source,
          label:      label,
          timestamp:  new Date().toISOString()
        })
      });
      chrome.notifications.create({
        type: 'basic', iconUrl: 'icon.png',
        title: `MoCKA ${label}`,
        message: text.slice(0, 60)
      });
    } catch(e) { console.error('success signal error:', e); }
    return;
  }

  if (info.menuItemId === 'mocka_share') {
    const text = info.selectionText || '';
    if (!text) return;
    try {
      await fetch('http://127.0.0.1:5000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ c: 'B', o: text, memo: `${source}から共有` })
      });
      chrome.notifications.create({ type:'basic', iconUrl:'icon.png', title:'MoCKA共有完了', message:'オーケストラに送信しました' });
    } catch(e) { console.error('share error:', e); }
    return;
  }

  if (info.menuItemId === 'mocka_collaborate') {
    const text = info.selectionText || '';
    if (!text) return;
    try {
      await fetch('http://127.0.0.1:5000/orchestra', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: text, mode: 'orchestra' })
      });
      chrome.notifications.create({ type:'basic', iconUrl:'icon.png', title:'MoCKA協議開始', message:'4AI合議を開始しました' });
    } catch(e) { console.error('collaborate error:', e); }
    return;
  }

  if (info.menuItemId === 'mocka_collect_selected') {
    await sendToMocka(source, info.selectionText, tab.url, 'selected');
  } else if (info.menuItemId === 'mocka_collect_full') {
    // NY抽出モード: 全文 → /ny_extract → essence自動反映
    const fullResults = await chrome.scripting.executeScript({
      target: { tabId: tabId },
      func: function() {
        document.execCommand('selectAll');
        const t = window.getSelection().toString().trim();
        window.getSelection().removeAllRanges();
        return t;
      }
    });
    const fullText = fullResults?.[0]?.result || '';
    if (fullText) {
      try {
        const res = await fetch('http://127.0.0.1:5000/ny_extract', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({text: fullText, source: source})
        });
        const data = await res.json();
        chrome.notifications.create({
          type: 'basic', iconUrl: 'icon.png',
          title: 'MoCKA NY抽出完了',
          message: `グレイト:${data.great}件 ヒント:${data.hint}件 インシデント:${data.incident}件 → Essence反映中`
        });
      } catch(e) { console.error('ny_extract error:', e); }
    }
    return; //
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: async function(source) {
        let last = null;
        for (let i = 0; i < 30; i++) {
          window.scrollTo(0, 0);
          await new Promise(r => setTimeout(r, 1200));
          const h = document.body.scrollHeight;
          if (h === last) break;
          last = h;
        }
        await new Promise(r => setTimeout(r, 2000));
        const SEL = {
          chatgpt:    '[data-message-author-role]',
          claude:     '[data-testid*="message"], .font-claude-message',
          gemini:     'message-content, model-response, user-query',
          perplexity: '[class*="Message"]',
          copilot:    '[class*="message"]',
        };
        const sel = SEL[source] || '[class*="message"], p';
        const nodes = document.querySelectorAll(sel);
        let lines = [];
        nodes.forEach((n, i) => {
          const role = n.getAttribute('data-message-author-role') || (i%2===0 ? 'user' : 'assistant');
          const text = n.innerText.trim();
          if (text) lines.push(`[${role}] ${text}`);
        });
        if (!lines.length) {
          document.execCommand('selectAll');
          const t = window.getSelection().toString().trim();
          window.getSelection().removeAllRanges();
          if (t) lines.push(t);
        }
        return lines.join('\n\n');
      },
      args: [source]
    });
    if (results && results[0] && results[0].result) {
      await sendToMocka(source, results[0].result, tab.url, 'full_scroll');
    }
  }
});

// ── ユーティリティ ──────────────────────────────────────────
function detectSource(url) {
  if (!url) return 'unknown';
  if (url.includes('chatgpt.com'))       return 'chatgpt';
  if (url.includes('gemini.google.com')) return 'gemini';
  if (url.includes('perplexity.ai'))     return 'perplexity';
  if (url.includes('claude.ai'))         return 'claude';
  if (url.includes('microsoft.com'))     return 'copilot';
  return 'unknown';
}

async function sendToMocka(source, text, url, mode) {
  if (!text) return;
  try {
    const res = await fetch('http://127.0.0.1:5000/collect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source, text, url, mode, timestamp: new Date().toISOString() })
    });
    if (res.ok) {
      chrome.notifications.create({ type:'basic', iconUrl:'icon.png', title:'MoCKA収集完了', message:`${source} から収集しました` });
    }
  } catch(e) { console.error('MoCKA send error:', e); }
}

// ── TODO サマリー自動取得（DNA注入同梱用）──────────────────────────────
const MOCKA_LOCAL = 'http://127.0.0.1:5000';
const TODO_CACHE_KEY = 'mocka_todo_summary';
const TODO_CACHE_TTL = 60 * 60 * 1000; // 1時間

async function fetchTodoSummary() {
  try {
    const cached = await chrome.storage.local.get(TODO_CACHE_KEY);
    const now = Date.now();
    if (cached[TODO_CACHE_KEY] && (now - cached[TODO_CACHE_KEY].fetched_at) < TODO_CACHE_TTL) {
      return cached[TODO_CACHE_KEY].data;
    }
    const res = await fetch(`${MOCKA_LOCAL}/public/todo`, { method:'GET' });
    if (!res.ok) return null;
    const data = await res.json();
    const todos = (data.todos || [])
      .filter(t => t.status === '未着手' || t.status === '進行中')
      .slice(0, 5)
      .map(t => `[${t.id}] ${t.title} (${t.priority || '中'})`);
    const summary = {
      generated_at: new Date().toISOString(),
      top5: todos,
      text: '【MoCKA TODO TOP5】\n' + todos.map((t,i) => `${i+1}. ${t}`).join('\n')
    };
    await chrome.storage.local.set({ [TODO_CACHE_KEY]: { data: summary, fetched_at: now } });
    return summary;
  } catch(e) {
    console.error('fetchTodoSummary error:', e);
    return null;
  }
}

// 起動時・インストール時にTODOを先読み
chrome.runtime.onInstalled.addListener(() => { fetchTodoSummary(); });
chrome.runtime.onStartup.addListener(() => { fetchTodoSummary(); });

// 新規AIチャットページ検知 → DNA + TODOサマリーをクリップボードにコピー
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (changeInfo.status !== 'complete') return;
  const url = tab.url || '';
  const isNewChat =
    url === 'https://gemini.google.com/app' ||
    url.startsWith('https://gemini.google.com/app?') ||
    url === 'https://chatgpt.com/' ||
    url.startsWith('https://chatgpt.com/?') ||
    url === 'https://copilot.microsoft.com/' ||
    url.startsWith('https://copilot.microsoft.com/?');
  if (!isNewChat) return;

  const todoSummary = await fetchTodoSummary();
  if (!todoSummary) return;

  // DNA + TODOサマリーをタブに注入
  try {
    await chrome.scripting.executeScript({
      target: { tabId: tabId },
      func: function(todoText) {
        // クリップボードにコピー（ユーザーが貼り付けられる状態にする）
        navigator.clipboard.writeText(todoText).catch(() => {});
        // 画面右下に通知バッジ表示
        const badge = document.createElement('div');
        badge.style.cssText = 'position:fixed;bottom:20px;right:20px;background:#005700;color:#fff;padding:10px 16px;border-radius:8px;font-size:13px;z-index:99999;font-family:monospace;white-space:pre-line;max-width:360px;box-shadow:0 2px 12px rgba(0,0,0,0.4)';
        badge.textContent = 'MoCKA TODO同梱済\n' + todoText.slice(0, 200);
        document.body.appendChild(badge);
        setTimeout(() => badge.remove(), 6000);
      },
      args: [todoSummary.text]
    });
  } catch(e) { console.error('DNA inject error:', e); }
});