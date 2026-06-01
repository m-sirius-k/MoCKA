// relay-state.js — グローバル状態管理（全スクリプト共通）
// content_scripts の読み込み順: relay-state.js が最初
'use strict';

window.RelayState = (() => {
  let _turnCount   = 0;
  let _planLevel   = 'free';
  let _sessionId   = null;
  let _messages    = [];
  let _handedOff   = false;

  return {
    getTurnCount:   () => _turnCount,
    getPlanLevel:   () => _planLevel,
    getSessionId:   () => _sessionId,
    getMessages:    () => [..._messages],
    isHandedOff:    () => _handedOff,

    incrementTurn() {
      _turnCount++;
      chrome.runtime.sendMessage({ type: 'TURN_COUNT_UPDATE', count: _turnCount }).catch(() => {});
      return _turnCount;
    },

    addMessage(role, content) {
      _messages.push({ role, content, ts: Date.now() });
      if (_messages.length > 100) _messages.shift();
    },

    reset() {
      _turnCount = 0;
      _messages  = [];
      _handedOff = false;
      _sessionId = `relay_${Date.now()}`;
    },

    markHandedOff() {
      _handedOff = true;
      chrome.runtime.sendMessage({ type: 'HANDOFF_READY' }).catch(() => {});
    },

    async loadPlan() {
      const { relay_plan_level } = await chrome.storage.local.get('relay_plan_level');
      _planLevel = relay_plan_level || 'free';
      return _planLevel;
    },
  };
})();
