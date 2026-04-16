from pathlib import Path

f = Path(r"C:\Users\sirok\MoCKA\tools\mocka-extension\background.js")
c = f.read_text(encoding="utf-8")

# mocka-collectブロックを新版に置き換え
old = """  if (info.menuItemId === 'mocka-collect') {
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
          perplexity: '.prose, [class*="answer"], .break-words',
          copilot:    '[class*="message"]',
        };
        const sel = SEL[source] || 'p';
        const nodes = document.querySelectorAll(sel);
        let lines = [];
        nodes.forEach((n, i) => {
          const role = n.getAttribute('data-message-author-role') || (i%2===0 ? 'user' : 'assistant');
          const text = n.innerText.trim();
          if (text) lines.push('[' + role + '] ' + text);
        });
        if (!lines.length) {
          document.execCommand('selectAll');
          const t = window.getSelection().toString().trim();
          window.getSelection().removeAllRanges();
          if (t) lines.push(t);
        }
        return lines.join('\\n\\n');
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
        func: () => alert('MoCKA: collected')
      });
    }
  }"""

new = """  if (info.menuItemId === 'mocka-collect') {
    // まずexecuteScriptを試みる（ポリシーでブロックされる場合はクリップボード方式にフォールバック）
    let collected = false;
    try {
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
            perplexity: '.prose, [class*="answer"], .break-words',
            copilot:    '[class*="message"]',
          };
          const sel = SEL[source] || 'p';
          const nodes = document.querySelectorAll(sel);
          let lines = [];
          nodes.forEach((n, i) => {
            const role = n.getAttribute('data-message-author-role') || (i%2===0 ? 'user' : 'assistant');
            const text = n.innerText.trim();
            if (text) lines.push('[' + role + '] ' + text);
          });
          if (!lines.length) {
            document.execCommand('selectAll');
            const t = window.getSelection().toString().trim();
            window.getSelection().removeAllRanges();
            if (t) lines.push(t);
          }
          return lines.join('\\n\\n');
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
          func: () => alert('MoCKA: collected')
        });
        collected = true;
      }
    } catch(e) {
      console.warn('[MoCKA] executeScript blocked by policy, trying clipboard fallback:', e.message);
    }

    // フォールバック: クリップボード経由（Perplexity等のポリシー制限ページ用）
    if (!collected) {
      try {
        const clipText = await navigator.clipboard.readText();
        if (clipText && clipText.length > 50) {
          await fetch('http://127.0.0.1:5000/collect', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
              source: source,
              text: clipText,
              url: tab.url,
              mode: 'clipboard_fallback',
              timestamp: new Date().toISOString()
            })
          });
          collected = true;
          alert('MoCKA: collected (clipboard mode)\\n※Perplexityはクリップボード経由で収集しました');
        } else {
          alert('MoCKA: collection failed\\n手順: Ctrl+A → Ctrl+C でページを選択コピー後に再実行してください');
        }
      } catch(e2) {
        alert('MoCKA: collection failed\\nポリシー制限によりスクリプト実行不可\\n手順: Ctrl+A → Ctrl+C後に再実行');
        console.error('[MoCKA] clipboard fallback also failed:', e2);
      }
    }
  }"""

if old.strip() in c:
    c = c.replace(old, new)
    f.write_text(c, encoding="utf-8")
    print("✓ mocka-collect クリップボードフォールバック版に更新完了")
else:
    # 部分マッチで確認
    print("完全一致なし。mocka-collectブロックの開始を確認:")
    idx = c.find("if (info.menuItemId === 'mocka-collect')")
    if idx >= 0:
        print(c[idx:idx+200])
    else:
        print("mocka-collectブロックが見つかりません")
