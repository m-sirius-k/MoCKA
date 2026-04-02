const AI_DOMAINS = {
  'ChatGPT':    'chatgpt.com',
  'Gemini':     'gemini.google.com',
  'Perplexity': 'perplexity.ai',
  'Claude':     'claude.ai',
  'Copilot':    'copilot.microsoft.com',
  'Genspark':   'genspark.ai'
};

// 既存: MoCKA→AI送信
async function poll() {
  for (const [name, domain] of Object.entries(AI_DOMAINS)) {
    try {
      const res = await fetch(`http://127.0.0.1:5000/get_intent/${name}`).catch(() => null);
      if (!res || !res.ok) continue;
      const data = await res.json();
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
        });
      } else {
        chrome.tabs.create({ url: 'https://' + domain });
      }
    } catch(e) { console.error(e); }
  }
}
setInterval(poll, 1500);

// 追加: AI→MoCKA収集（右クリックメニュー）
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({ id:'mocka_collect', title:'MoCKAに収集', contexts:['page'] });
  chrome.contextMenus.create({ id:'mocka_collect_selected', title:'選択範囲をMoCKAに収集', contexts:['selection'] });
  chrome.contextMenus.create({ id:'mocka_collect_full', title:'このchat全文をMoCKAに収集', contexts:['page'] });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  const source = detectSource(tab.url);

  if (info.menuItemId === 'mocka_collect_selected') {
    // 選択テキストをそのまま送信
    await sendToMocka(source, info.selectionText, tab.url, 'selected');

  } else if (info.menuItemId === 'mocka_collect' || info.menuItemId === 'mocka_collect_full') {
    // 各AI対応のDOM収集スクリプトを実行
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: collectChat,
      args: [source]
    });
    if (results && results[0] && results[0].result) {
      await sendToMocka(source, results[0].result, tab.url, 'full');
    }
  }
});

function detectSource(url) {
  if (!url) return 'unknown';
  if (url.includes('chatgpt.com'))       return 'chatgpt';
  if (url.includes('gemini.google.com')) return 'gemini';
  if (url.includes('perplexity.ai'))     return 'perplexity';
  if (url.includes('claude.ai'))         return 'claude';
  if (url.includes('microsoft.com'))     return 'copilot';
  if (url.includes('genspark.ai'))       return 'genspark';
  return 'unknown';
}

// DOM収集関数（各AIページで実行）
function collectChat(source) {
  const SELECTORS = {
    chatgpt:    { msg: '[data-message-author-role]', role: 'data-message-author-role', text: '.markdown, .text-base' },
    gemini:     { msg: 'message-content, .conversation-turn', role: null, text: '.markdown, p' },
    perplexity: { msg: '.message, [class*="Message"]', role: null, text: 'p, .prose' },
    claude:     { msg: '[data-testid*="message"], .font-claude-message', role: null, text: 'p, .prose' },
    copilot:    { msg: '[class*="message"], .cib-message', role: null, text: 'p, span' },
    default:    { msg: 'p, .message, .chat-message', role: null, text: 'p' }
  };
  const sel = SELECTORS[source] || SELECTORS.default;
  const msgs = document.querySelectorAll(sel.msg);
  if (!msgs.length) return document.body.innerText.slice(0, 50000);
  const lines = [];
  msgs.forEach(m => {
    const role = sel.role ? (m.getAttribute(sel.role) || 'unknown') : 'message';
    const textEl = m.querySelector(sel.text) || m;
    const text = textEl.innerText.trim();
    if (text) lines.push(`[${role}] ${text}`);
  });
  return lines.join('\n\n');
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
      chrome.notifications.create({
        type: 'basic', iconUrl: 'icon.png',
        title: 'MoCKA収集完了',
        message: `${source} から収集しました`
      });
    }
  } catch(e) { console.error('MoCKA send error:', e); }
}
