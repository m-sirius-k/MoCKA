from pathlib import Path

path = r"C:\Users\sirok\MoCKA\mocka-extension\background.js"
with open(path, encoding="utf-8") as f:
    src = f.read()

addition = r"""
// ── CLAUDE.AI 自動ping注入 & 自動収集 ──────────────────────

// claude.aiのタブが更新されたら自動注入
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (changeInfo.status !== 'complete') return;
  if (!tab.url || !tab.url.includes('claude.ai')) return;

  // 1. ping_latest.jsonを取得
  let ping = null;
  try {
    const res = await fetch('http://127.0.0.1:5000/loop/status');
    const d = await res.json();
    if (d.inject_mode !== 'ON') return; // OFFなら注入しない
    ping = d.ping_latest;
  } catch(e) { return; }

  if (!ping || !ping.H) return;

  // 2. MoCKAヘッダー形式でパケット生成
  const packet = `[MOCKA]${JSON.stringify(ping)}`;

  // 3. claude.aiのテキストボックスに注入（1.5秒待ってから）
  setTimeout(() => {
    chrome.scripting.executeScript({
      target: { tabId },
      func: (packetText) => {
        // 新規チャットのテキストボックスを探す
        const selectors = [
          'div[contenteditable="true"]',
          'textarea',
          '[data-placeholder]',
        ];
        let el = null;
        for (const sel of selectors) {
          el = document.querySelector(sel);
          if (el) break;
        }
        if (!el) return;

        // 既にpingが注入済みなら重複注入しない
        const current = el.innerText || el.value || '';
        if (current.includes('[MOCKA]')) return;

        // 注入
        if (el.tagName === 'DIV') {
          el.innerText = packetText;
        } else {
          el.value = packetText;
        }
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.focus();

        // 通知（オプション）
        console.log('[MoCKA] DNA packet injected to claude.ai');
      },
      args: [packet]
    }).catch(e => console.error('inject error:', e));
  }, 1500);
});

// claude.aiの会話を定期的に自動収集（30秒ごと）
setInterval(async () => {
  try {
    const tabs = await chrome.tabs.query({ url: '*://claude.ai/*' });
    for (const tab of tabs) {
      if (!tab.id) continue;
      const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
          const nodes = document.querySelectorAll(
            '[data-testid*="message"], .font-claude-message, [class*="Message"]'
          );
          const lines = [];
          nodes.forEach((n, i) => {
            const text = n.innerText.trim();
            if (text && text.length > 10) {
              const role = i % 2 === 0 ? 'user' : 'assistant';
              lines.push(`[${role}] ${text}`);
            }
          });
          return lines.join('\n\n');
        }
      }).catch(() => null);

      if (results && results[0] && results[0].result) {
        const text = results[0].result;
        if (text.length < 50) continue; // 短すぎるものはスキップ

        fetch('http://127.0.0.1:5000/collect', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            source: 'claude',
            text,
            url: tab.url,
            mode: 'auto_realtime',
            timestamp: new Date().toISOString()
          })
        }).catch(() => {});
      }
    }
  } catch(e) { console.error('auto collect error:', e); }
}, 30000);
"""

# background.jsの末尾に追加
with open(path, "w", encoding="utf-8") as f:
    f.write(src + addition)
print("OK: background.js updated")
print("  - claude.ai自動ping注入追加")
print("  - claude.ai会話30秒自動収集追加")
