chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "mocka-save",
    title: "MoCKAに保存",
    contexts: ["selection"]
  });
  chrome.contextMenus.create({
    id: "mocka-share",
    title: "MoCKAで共有",
    contexts: ["selection"]
  });
  chrome.contextMenus.create({
    id: "mocka-orchestra",
    title: "MoCKAで協議",
    contexts: ["selection"]
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  const text = info.selectionText;
  const title = new Date().toLocaleString("ja-JP");

  if (info.menuItemId === "mocka-save") {
    fetch("http://localhost:5000/ask", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({c:"A", o:"infield", memo:"【保存】" + text})
    }).then(() => {
      chrome.scripting.executeScript({
        target: {tabId: tab.id},
        func: () => alert("MoCKAに保存しました")
      });
    });
  }

  if (info.menuItemId === "mocka-share") {
    const targets = ["ChatGPT","Gemini","Claude","Perplexity","Copilot"];
    targets.forEach(t => {
      fetch("http://localhost:5000/ask", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({c:"B", o:t, memo:text})
      });
    });
    chrome.scripting.executeScript({
      target: {tabId: tab.id},
      func: () => alert("MoCKAで共有しました")
    });
  }

  if (info.menuItemId === "mocka-orchestra") {
    fetch("http://localhost:5000/orchestra", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({prompt: text})
    }).then(() => {
      chrome.scripting.executeScript({
        target: {tabId: tab.id},
        func: () => alert("MoCKAオーケストラを起動しました")
      });
    });
  }
});
