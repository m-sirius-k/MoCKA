const AI_DOMAINS = {
  'ChatGPT': 'chatgpt.com', 'Gemini': 'gemini.google.com', 'Perplexity': 'perplexity.ai', 
  'Claude': 'claude.ai', 'Copilot': 'copilot.microsoft.com', 'Genspark': 'genspark.ai'
};

async function poll() {
  for (const [name, domain] of Object.entries(AI_DOMAINS)) {
    try {
      const res = await fetch(http://127.0.0.1:5000/get_intent/ + name).catch(() => null);
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
    } catch (e) { console.error(e); }
  }
}

// 1.5秒おきにチェック
setInterval(poll, 1500);
