// MoCKA Bridge Service Worker (Stable) v1.0.2
console.log("[MoCKA] Service Worker starting...");

try {
  chrome.runtime.onInstalled.addListener(() => {
    console.log("[MoCKA] Extension installed.");
  });

  // Actionが存在する場合のみリスナーを登録（防御的設計）
  if (chrome.action && chrome.action.onClicked) {
    chrome.action.onClicked.addListener((tab) => {
      console.log("[MoCKA] Action clicked:", tab.id, tab.url);
    });
  }
} catch (e) {
  console.error("[MoCKA ERROR]", e);
}