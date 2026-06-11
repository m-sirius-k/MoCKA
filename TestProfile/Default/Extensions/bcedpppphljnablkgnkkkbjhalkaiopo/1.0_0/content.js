// background.jsからのメッセージを受け取る
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "insertTempMail") {
    // アクティブな要素にメールアドレスを挿入
    const activeElement = document.activeElement;
    if (activeElement && (activeElement.tagName === 'INPUT' || activeElement.tagName === 'TEXTAREA')) {
      activeElement.value = request.email;
    }
  }
});

// メッセージ表示用のスタイルを追加
const style = document.createElement('style');
style.textContent = `
  .temp-mail-message {
    position: fixed;
    top: 20px;
    right: 20px;
    background: #4CAF50;
    color: white;
    padding: 15px 20px;
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    z-index: 10000;
    font-family: Arial, sans-serif;
    animation: fadeInOut 3s forwards;
  }
  @keyframes fadeInOut {
    0% { opacity: 0; transform: translateY(-20px); }
    10% { opacity: 1; transform: translateY(0); }
    90% { opacity: 1; transform: translateY(0); }
    100% { opacity: 0; transform: translateY(-20px); }
  }
`;
document.head.appendChild(style);

// メッセージを表示する関数
function showMessage(message) {
  const messageDiv = document.createElement('div');
  messageDiv.className = 'temp-mail-message';
  messageDiv.textContent = message;
  document.body.appendChild(messageDiv);
  
  // 3秒後にメッセージを削除
  setTimeout(() => {
    messageDiv.remove();
  }, 3000);
}

// メールアドレスを取得してクリップボードにコピーする関数
function copyEmailToClipboard() {
  // メールアドレスを正確に取得
  const emailContainer = document.querySelector('#area-newaddress-view-data .noticebox:first-child b');
  if (emailContainer) {
    const email = emailContainer.textContent.trim();
    
    navigator.clipboard.writeText(email).then(() => {
      showMessage(`コピーしました: ${email}`);
    }).catch(err => {
      console.error('クリップボードへのコピーに失敗しました:', err);
      showMessage('メールアドレスのコピーに失敗しました');
    });
  } else {
    console.error('メールアドレス要素が見つかりませんでした');
    showMessage('メールアドレスの取得に失敗しました');
  }
}

// ページが完全に読み込まれた後に実行
function clickCopyButton() {
  const copyButton = document.querySelector('#link_newaddr_copyaddr');
  if (copyButton) {
    copyButton.click();
  }
}

function clickAddMailButton() {
  const button = document.querySelector('#link_addMailAddrByOnetime');
  if (button) {
    button.click();
    // 1秒後にメールアドレスをコピー
    setTimeout(copyEmailToClipboard, 1000);
  }
}

// DOMContentLoadedだけでなく、完全なページ読み込みを待つ
if (document.readyState === 'complete') {
  clickAddMailButton();
} else {
  window.addEventListener('load', clickAddMailButton);
}
