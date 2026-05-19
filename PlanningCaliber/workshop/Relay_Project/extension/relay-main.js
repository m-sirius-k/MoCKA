/**
 * Relay — relay-main.js
 * @version 3.2.0
 * @description 起動順制御・引き継ぎパケット生成・new chat誘導。
 *              manifest の content_scripts[].js に最後に注入する。
 *
 * Purpose  : 全サービスの起動順制御・引き継ぎ機能
 * Owns     : 起動シーケンス / handoff trigger / サービス依存チェック
 * Must not : DOM監視・TODO抽出・state 直接書き込み（サービス経由のみ）
 *
 * 注入順（manifest content_scripts[].js）:
 *   1. relay-state.js   ← globalThis.__RELAY__ を初期化
 *   2. relay-dom.js     ← services.dom を登録
 *   3. relay-watchers.js ← services.watchers を登録
 *   4. relay-logbook.js ← services.logbook を登録
 *   5. relay-ui.js      ← services.ui を登録
 *   6. relay-main.js    ← 全サービスを起動（このファイル）
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

  // ─── 引き継ぎパケット生成 ─────────────────────────────────────────────────

  async function _buildHandoffPacket() {
    const todos   = await Relay.services.logbook.getTodos({ sessionOnly: true });
    const open    = todos.filter(t => !t.done);
    const allMsgs = Relay.services.dom.getAllMessages();

    // 最後の N ターンをサマリーとして含める
    const recentMsgs = allMsgs.slice(-6);
    const summary = recentMsgs
      .map(m => `${m.role === 'user' ? 'あなた' : 'Claude'}: ${m.text.slice(0, 200)}`)
      .join('\n\n');

    const todoSection = open.length > 0
      ? `📋 未着手TODO:\n${open.map((t, i) => `  ${i + 1}. ${t.content}`).join('\n')}`
      : '';

    const parts = [
      `[Relay — continuing from ${Relay.state.turnCount} turns]`,
      todoSection,
      summary ? `=== 直前の会話（末尾） ===\n${summary}` : '',
      `Last message: "${recentMsgs.at(-1)?.text?.slice(0, 120) ?? ''}"`,
      '--- Please continue from where we left off.',
    ].filter(Boolean);

    return parts.join('\n\n');
  }

  // ─── 引き継ぎトリガー ─────────────────────────────────────────────────────

  async function triggerHandoff() {
    const packet = await _buildHandoffPacket();

    // クリップボードにコピー
    await Relay.services.dom.copyToClipboard(packet);
    Relay.services.ui.showToast('引き継ぎパケットをコピーしました。新しいチャットに貼り付けてください。', 4000);

    // background.js に新チャットを開くよう依頼
    try {
      chrome.runtime.sendMessage({ type: 'RELAY/OPEN_NEW_CHAT', packet }, res => {
        if (chrome.runtime.lastError) {
          // background 未起動の場合は直接遷移
          window.open('https://claude.ai/new', '_blank');
        }
      });
    } catch (_) {
      window.open('https://claude.ai/new', '_blank');
    }
  }

  Relay.services.handoff = Object.freeze({ trigger: triggerHandoff });

  // ─── 起動シーケンス ────────────────────────────────────────────────────────

  function _start() {
    if (!_checkServices()) {
      console.error('[Relay] startup aborted: services not ready.');
      return;
    }

    // Observers 起動
    Relay.services.watchers.assistant.start();
    Relay.services.watchers.user.start();

    // 初回バッジ更新
    Relay.services.ui.refreshBadge();

    Relay.state.initialized = true;
    console.info('[Relay] ✅ all services started. session:', Relay.state.sessionId);
  }

  // ─── DOM ready 後に起動 ────────────────────────────────────────────────────

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', _start);
  } else {
    _start();
  }

})();
