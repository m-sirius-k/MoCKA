// MoCKA Bridge v1.3 - Dynamic Orchestrator
console.log("[MoCKA] System Initializing...");

chrome.action.onClicked.addListener(async () => {
  console.log("[MoCKA] Scanning for active AI agents...");

  // Chrome 121+ の lastAccessed を考慮してタブを取得
  const allTabs = await chrome.tabs.query({});
  
  // AIドメインの定義
  const aiDomains = ["gemini.google.com", "claude.ai", "openai.com", "perplexity.ai", "microsoft.com"];
  
  // 対象タブのフィルタリングとソート（新しい順）
  const targetTabs = allTabs
    .filter(tab => aiDomains.some(domain => tab.url?.includes(domain)))
    .sort((a, b) => (b.lastAccessed || 0) - (a.lastAccessed || 0));

  if (targetTabs.length === 0) {
    console.warn("[MoCKA] No AI tabs detected. Please open Gemini, Claude, or ChatGPT.");
    return;
  }

  const primaryTab = targetTabs[0];
  console.log(`[MoCKA] Target locked: ${primaryTab.title} (ID: ${primaryTab.id})`);

  // ターゲットタブへの介入テスト
  chrome.scripting.executeScript({
    target: { tabId: primaryTab.id },
    func: (title) => {
      console.log(`%c[MoCKA Bridge] Connected to ${title}`, "color: #00ff00; font-weight: bold; font-size: 14px;");
      alert(`MoCKA Bridge が ${title} を捕捉しました。\nシステム通信準備完了。`);
    },
    args: [primaryTab.title]
  });
});