console.log("[MOCKA] background.js 起動開始");
const AI_DOMAINS = {
  ChatGPT:    'chatgpt.com',
  Gemini:     'gemini.google.com',
  Perplexity: 'perplexity.ai',
  Claude:     'claude.ai',
  Copilot:    'copilot.microsoft.com',
  Genspark:   'genspark.ai'
};

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
// 5秒後に開始（起動直後のクラッシュ防止）
setTimeout(() => { safePoll(); setInterval(safePoll, 1500); }, 5000);

const injectedTabs = new Set();
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url && tab.url.includes('claude.ai')) {
    if (injectedTabs.has(tabId)) return;
    injectedTabs.add(tabId);
    chrome.scripting.executeScript({
      target: { tabId: tabId },
      files: ['content.js']
    }).catch(() => {});
  }
});
chrome.tabs.onRemoved.addListener((tabId) => { injectedTabs.delete(tabId); });
chrome.tabs.onUpdated.addListener((tabId, changeInfo) => {
  if (changeInfo.url) injectedTabs.delete(tabId);
});

chrome.runtime.onInstalled.addListener(() => {
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

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  const text   = info.selectionText || '';
  const source = detectSource(tab.url);

  if (info.menuItemId === 'mocka-save') {
    fetch('http://localhost:5000/ask', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({c:'A', o:'infield', memo:'[save] ' + text})
    }).then(() => {
      chrome.scripting.executeScript({ target: {tabId: tab.id}, func: () => alert('MoCKA: saved') });
    }).catch(() => {});
  }

  if (info.menuItemId === 'mocka-share') {
    const targets = ['ChatGPT','Gemini','Claude','Perplexity','Copilot'];
    targets.forEach(t => {
      fetch('http://localhost:5000/ask', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({c:'B', o:t, memo:text})
      }).catch(() => {});
    });
    fetch('http://localhost:5000/orchestra', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({prompt: text, mode: 'share'})
    }).then(() => {
      chrome.scripting.executeScript({ target: {tabId: tab.id}, func: () => alert('MoCKA: shared') });
    }).catch(() => {});
  }

  if (info.menuItemId === 'mocka-orchestra') {
    fetch('http://localhost:5000/orchestra', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({prompt: text})
    }).then(() => {
      chrome.scripting.executeScript({ target: {tabId: tab.id}, func: () => alert('MoCKA: orchestra started') });
    }).catch(() => {});
  }

  if (info.menuItemId === 'mocka-mataka' || info.menuItemId === 'mocka-claim') {
    const type = info.menuItemId === 'mocka-mataka' ? 'mataka' : 'claim';
    await sendIncident(type, info.selectionText || '', tab.url || '');
    return;
  }

  if (info.menuItemId === 'mocka-hint') {
    fetch('http://localhost:5000/ask', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({c:'A', o:'infield', memo:'[hint] ' + text})
    }).then(() => {
      chrome.scripting.executeScript({ target: {tabId: tab.id}, func: () => alert('MoCKA: ヒント記録！') });
    }).catch(() => {});
    fetch('http://localhost:5000/success', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({type: 'hint', text: text, source: source, url: tab.url})
    }).catch(() => {});
  }

  if (info.menuItemId === 'mocka-great') {
    fetch('http://localhost:5000/ask', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({c:'A', o:'infield', memo:'[great] ' + text})
    }).then(() => {
      chrome.scripting.executeScript({ target: {tabId: tab.id}, func: () => alert('MoCKA: グレイト記録！！') });
    }).catch(() => {});
    fetch('http://localhost:5000/success', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({type: 'great', text: text, source: source, url: tab.url})
    }).catch(() => {});
  }

  // ===== chat全文収集 (Perplexity対応強化版) =====
  if (info.menuItemId === 'mocka-collect') {
    let collected = false;
    try {
      const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: async function(source) {
          for (let i = 0; i < 10; i++) {
            window.scrollTo(0, document.body.scrollHeight);
            await new Promise(r => setTimeout(r, 800));
          }
          window.scrollTo(0, 0);
          await new Promise(r => setTimeout(r, 1000));

          // Perplexity: innerText全文をrawで送る
          if (source === 'perplexity') {
            return '[perplexity_raw]\n' + document.body.innerText;
          }

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

      if (results && results[0] && results[0].result) {
        await fetch('http://127.0.0.1:5000/collect', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            source: source,
            text: results[0].result,
            url: tab.url,
            mode: 'full_scroll',
            timestamp: new Date().toISOString()
          })
        });
        chrome.scripting.executeScript({
          target: {tabId: tab.id},
          func: () => alert('MoCKA: collected!')
        });
        collected = true;
      }
    } catch(e) {
      console.warn('[MoCKA] collect error:', e.message);
    }

    if (!collected) {
      chrome.scripting.executeScript({
        target: {tabId: tab.id},
        func: () => alert('MoCKA: collection failed')
      });
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
    const data = await res.json();
    const count = data.recurrence_count || 1;
    const msg = type === 'mataka'
      ? `😤 またか！記録完了\nパターン: ${data.pattern || selectedText.slice(0,30)}\n再発: ${count}回目`
      : `🚨 クレーム記録完了\nインシデント: ${data.event_id}`;
    alert(msg);
  } catch(e) {
    alert('記録失敗: ' + e.message);
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
