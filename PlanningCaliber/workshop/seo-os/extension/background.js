// バックグラウンドで承認待ちを定期チェック
// 新しいJobが追加されたら通知する

const API = "http://localhost:8750";
let lastPendingCount = 0;

async function checkPending() {
  try {
    const r = await fetch(
      `${API}/api/jobs?status=pending`);
    if (!r.ok) return;
    const jobs = await r.json();
    const count = jobs.length;

    // 件数が増えた場合に通知
    if (count > lastPendingCount && count > 0) {
      chrome.notifications.create({
        type:    "basic",
        iconUrl: "icons/icon48.png",
        title:   "SEO-OS — 承認待ちあり",
        message: `${count}件の案件が承認を待っています`
      });
    }
    lastPendingCount = count;

    // バッジ更新
    chrome.action.setBadgeText(
      {text: count > 0 ? String(count) : ""});
    chrome.action.setBadgeBackgroundColor(
      {color: "#c9a84c"});
  } catch {
    // サーバー未起動時はスキップ
  }
}

// 起動時・30秒ごとにチェック
checkPending();
setInterval(checkPending, 30000);
