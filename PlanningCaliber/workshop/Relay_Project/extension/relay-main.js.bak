/**
 * Relay — relay-main.js
 * @version 3.4.0
 * @description 起動順制御・引き継ぎパケット生成・popup.jsメッセージ受信。
 *              manifest の content_scripts[].js に最後に注入する。
 *
 * Purpose  : 全サービスの起動順制御・引き継ぎ機能・popup↔content bridge
 * Owns     : 起動シーケンス / handoff trigger / chrome.runtime.onMessage リスナー
 * Must not : DOM監視・TODO抽出・state 直接書き込み（サービス経由のみ）
 *
 * 注入順（manifest content_scripts[].js）:
 *   1. relay-state.js
 *   2. relay-dom.js
 *   3. relay-watchers.js
 *   4. relay-logbook.js
 *   5. relay-ui.js
 *   6. relay-main.js  ← このファイル
 *
 * v3.4.0 変更点:
 *   - _start() 内で logbook / ui の watchers 接続を明示的に実行
 *   - 各サービスの _connectWatchers() を廃止し、ここに集中
 *   - これにより「watchers未登録でスキップ」バグを根絶
 */

(() => {
  'use strict';

  const Relay = globalThis.__RELAY__;
  if (!Relay) { console.error('[Relay] relay-main.js: __RELAY__ not found'); return; }

  // ─── 起動チェック ──────────────────────────────────────────────────────────

  function _checkServices() {
    const required = ['dom', 'watchers', 'logbook', 'ui'];
    const missing  = required.filter(k => !Relay.services[k]);
    if (missing.length > 0) {
      console.error('[Relay] missing services:', missing);
      return false;
    }
    return true;
  }

  // ─── watchers コールバック接続（ここに集中） ─────────────────────────────

  function _connectAllCallbacks() {
    const w  = Relay.services.watchers;
    const lb = Relay.services.logbook;
    const ui = Relay.services.ui;

    // logbook: 安定テキスト → TODO抽出・保存 → バッジ更新
    w.on('onStableAssistant', text => {
      lb.processStableText(text).then(saved => {
        if (saved.length > 0) {
          console.info('[Relay] logbook: saved', saved.length, 'TODOs');
          ui.refreshBadge();
        }
      });
    });

    // ui: 安定テキスト確定 → バッジ更新
    w.on('onStableAssistant', () => ui.refreshBadge());

    // ui: ターン変化 → バッジ更新 + 20ターン警告
    w.on('onTurnChange', turn => {
      ui.refreshBadge();
      if (turn >= Relay.config.turnWarningAt && !Relay.state.warningShown) {
        ui.showTurnWarning(turn);
      }
    });

    console.info('[Relay] all watcher callbacks connected.');
  }

  // ─── 引き継ぎパケット生成 ─────────────────────────────────────────────────

  async function _buildHandoffPacket() {
    const todos    = await Relay.services.logbook.getTodos({ sessionOnly: true });
    const open     = todos.filter(t => !t.done);
    const allMsgs  = Relay.services.dom.getAllMessages();
    const recentMsgs = allMsgs.slice(-6);

    const summary = recentMsgs
      .map(m => `${m.role === 'user' ? 'あなた' : 'Claude'}: ${m.text.slice(0, 200)}`)
      .join('\n\n');

    const todoSection = open.length > 0
      ? `📋 未着手TODO:\n${open.map((t, i) => `  ${i + 1}. ${t.content}`).join('\n')}`
      : '';

    return [
      `[Relay — continuing from ${Relay.state.turnCount} turns]`,
      todoSection,
      summary ? `=== 直前の会話（末尾） ===\n${summary}` : '',
      `Last message: "${recentMsgs.at(-1)?.text?.slice(0, 120) ?? ''}"`,
      '--- Please continue from where we left off.',
    ].filter(Boolean).join('\n\n');
  }

  // ─── 引き継ぎトリガー ─────────────────────────────────────────────────────

  async function triggerHandoff() {
    const packet = await _buildHandoffPacket();
    await Relay.services.dom.copyToClipboard(packet);
    Relay.services.ui.showToast('引き継ぎパケットをコピーしました。新しいチャットに貼り付けてください。', 4000);
    try {
      chrome.runtime.sendMessage({ type: 'RELAY/OPEN_NEW_CHAT', packet }, res => {
        if (chrome.runtime.lastError) window.open('https://claude.ai/new', '_blank');
      });
    } catch (_) {
      window.open('https://claude.ai/new', '_blank');
    }
  }

  Relay.services.handoff = Object.freeze({ trigger: triggerHandoff });

  // ─── popup.js → content script メッセージリスナー ────────────────────────

  chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
    _handleMessage(msg)
      .then(result => sendResponse({ ok: true, ...result }))
      .catch(err   => sendResponse({ ok: false, error: String(err) }));
    return true;
  });

  async function _handleMessage(msg) {
    const lb = Relay.services.logbook;

    switch (msg.type) {

      case 'RELAY_LB_GET_TODOS': {
        const todos = await lb.getTodos({ sessionOnly: false, includeArchived: false });
        return { todos };
      }

      case 'RELAY_LB_ADD_TODO': {
        const rec = await lb.saveTodo(msg.content, 'manual');
        return { record: rec };
      }

      case 'RELAY_LB_ARCHIVE_DONE': {
        const changed = await lb.archiveDone();
        return { changed };
      }

      case 'RELAY_LB_DELETE_TODO': {
        const todos = await lb.getTodos({ includeArchived: true });
        const filtered = todos.filter(t => t.id !== msg.id);
        await _saveAllTodos(filtered);
        return { deleted: true };
      }

      case 'RELAY_LB_COMPLETE_TO_LOG': {
        await lb.toggleDone(msg.id);
        return { done: true };
      }

      case 'RELAY_LB_UPDATE_STATUS': {
        await lb.toggleDone(msg.id);
        return { updated: true };
      }

      case 'RELAY_MANUAL_HANDOFF': {
        await triggerHandoff();
        return { triggered: true };
      }

      case 'RELAY_GET_SUMMARY_FOR_VAULT': {
        const packet = await _buildHandoffPacket();
        return { summary: packet };
      }

      default:
        return { skipped: true, type: msg.type };
    }
  }

  // ─── chrome.storage.local 全件保存ヘルパー ───────────────────────────────

  function _saveAllTodos(todos) {
    return new Promise(resolve => {
      chrome.storage.local.set({ relay_todos: todos }, () => resolve());
    });
  }

  // ─── 起動シーケンス ────────────────────────────────────────────────────────

  function _start() {
    if (!_checkServices()) {
      console.error('[Relay] startup aborted: services not ready.');
      return;
    }

    // watchers 接続を main.js に集中（logbook/ui の _connectWatchers は削除済み）
    _connectAllCallbacks();

    Relay.services.watchers.assistant.start();
    Relay.services.watchers.user.start();
    Relay.services.ui.refreshBadge();
    Relay.state.initialized = true;
    console.info('[Relay] ✅ all services started. session:', Relay.state.sessionId);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', _start);
  } else {
    _start();
  }

})();
