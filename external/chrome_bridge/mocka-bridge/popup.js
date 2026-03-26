document.addEventListener('DOMContentLoaded', () => {
    const log = document.getElementById('log-output');
    const injectBtn = document.getElementById('injectBtn');

    // 博士が構築したログ表示ロジックを尊重
    function showLog(msg) {
        if (log) log.innerText = msg;
    }

    // 「B:共有」ボタンに、AIへの流し込み機能のみを「非破壊的」に追加
    if (injectBtn) {
        injectBtn.addEventListener('click', async () => {
            try {
                const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
                const text = await navigator.clipboard.readText();
                
                await chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    func: (t) => {
                        if (window.injectToAIField) {
                            window.injectToAIField(t);
                            return true;
                        }
                        return false;
                    },
                    args: [text]
                });
                showLog("SHARED: DATA INJECTED TO ACTIVE AI");
            } catch (e) {
                showLog("ERROR: " + e.message);
            }
        });
    }
});
