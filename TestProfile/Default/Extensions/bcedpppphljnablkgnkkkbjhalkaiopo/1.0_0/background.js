// コンテキストメニューの作成
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "generateTempMail",
    title: "期限付き捨てメアドを生成",
    contexts: ["editable"]
  });
});

// コンテキストメニューがクリックされたときの処理
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "generateTempMail") {
    // kuku.luを新しいタブで開く
    chrome.tabs.create({
      url: "https://m.kuku.lu/ja.php"
    });
  }
});
