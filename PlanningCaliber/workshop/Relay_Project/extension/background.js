// background.js — MoCKA Relay v2.0
// Service Worker。content.js からのメッセージを受け取りログ管理のみ担当。
'use strict';

// relay_dom_selector ping (TODO_350 Phase5 Step3)
// MV3のservice workerは非アクティブ時に停止するため setInterval は不可。
// chrome.alarms APIで1分毎に起動し、app.pyの POST /relay/ping へpingを送信する。
// health_check.pyのrelay_dom_selectorチェックは GET /relay/status (app.py側でlast_pingの
// 鮮度を判定して返す読み取り専用エンドポイント)を参照するため、ここではPOST /relay/pingのみ呼ぶ。
const RELAY_PING_ALARM = 'relayPing';

chrome.runtime.onInstalled.addListener(() => {
  chrome.alarms.create(RELAY_PING_ALARM, { periodInMinutes: 1 });
});

chrome.runtime.onStartup.addListener(() => {
  chrome.alarms.create(RELAY_PING_ALARM, { periodInMinutes: 1 });
});

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name !== RELAY_PING_ALARM) return;
  fetch('http://localhost:5000/relay/ping', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ version: '2.0.0' }),
  }).catch(() => {}); // MoCKAサーバー未起動時は無視
});

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg.type === 'SESSION_STARTED') {
    console.log('[Relay] セッション開始:', msg.url);
  } else if (msg.type === 'TURN_UPDATE') {
    // ターン数の更新通知（将来のバッジ表示等に利用可能）
    console.log('[Relay] ターン数:', msg.count);
  } else if (msg.type === 'OPEN_POPUP') {
    // MV3 では chrome.action.openPopup() は userGesture が必要なため通知で代替
    chrome.notifications.create('relay-open-popup', {
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: 'MoCKA Relay',
      message: '拡張機能アイコンをクリックして引き継ぎパケットを生成してください',
    });
  }
});
