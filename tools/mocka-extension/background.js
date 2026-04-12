chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && tab.url.includes('claude.ai/new')) {
        console.log("[MOCKA] DNA注入開始: " + tab.url);
        
        // メッセージ送信ではなく、直接スクリプトを実行してステータスバーを強制描画
        chrome.scripting.executeScript({
            target: { tabId: tabId },
            files: ['content.js']
        }).then(() => {
            console.log("[MOCKA] content.js 物理注入完了");
        }).catch(err => console.error("[MOCKA] 注入失敗:", err));
    }
});

// fetch要求を受け取るリスナー
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === "GET_SYSTEM_STATUS") {
        fetch('http://127.0.0.1:5000/get_latest_dna')
            .then(response => response.json())
            .then(data => sendResponse({ status: 'OK', dna: data }))
            .catch(err => sendResponse({ status: 'ERROR', error: err.message }));
        return true; // 非同期応答を維持
    }
});
