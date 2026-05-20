/**
 * Relay — relay-watchers.js
 * @version 3.2.0
 * @description DOM監視の集中管理。Observer lifecycle を start/stop/restart で制御。
 *
 * Purpose  : claude.ai DOM変化の監視・安定テキストの state への反映
 * Owns     : Observer の start/stop/restart / stream idle detection
 * Must not : TODO抽出・localStorage・chrome API（state更新とコールバック通知のみ）
 * Inputs   : DOM mutations
 * Outputs  : Relay.state.lastAssistantText / lastStableAssistantText（副作用）
 *            + onStable コールバック呼び出し
 *
 * Known traps:
 *   - Observer を start() せずに stop() しても安全（null チェック済み）
 *   - SPA遷移で Observer が残存する → stop() → restart() で対応
 *   - streamIdleMs が短すぎるとストリーミング途中で処理される（1200ms 推奨）
 *   - 同じ Observer を二重 start() しないよう _isRunning フラグで防止
 */

(() => {
  'use strict';

  const Relay = globalThis.__RELAY__;
  if (!Relay) { console.error('[Relay] relay-watchers.js: __RELAY__ not found'); return; }

  const dom = () => Relay.services.dom;  // 遅延参照（dom.js より後に実行される）

  // ─── コールバックレジストリ ────────────────────────────────────────────────

  const _callbacks = {
    onStableAssistant : [],   // 安定したアシスタントテキストが確定したとき
    onUserMessage     : [],   // 新しいユーザーメッセージが検出されたとき
    onTurnChange      : [],   // ターン数が変化したとき
    onUrlChange       : [],   // SPA遷移でURLが変化したとき（state reset 前に発火）
  };

  function on(event, fn) {
    if (_callbacks[event]) _callbacks[event].push(fn);
  }

  function _emit(event, ...args) {
    (_callbacks[event] ?? []).forEach(fn => {
      try { fn(...args); } catch(e) { console.warn('[Relay] watcher callback error:', e); }
    });
  }

  // ─── Assistant Observer ────────────────────────────────────────────────────

  const _assistant = {
    _obs       : null,
    _isRunning : false,

    start() {
      if (this._isRunning) return;

      const target = document.body;
      if (!target) { console.warn('[Relay] assistantObserver: document.body not ready'); return; }

      this._obs = new MutationObserver(() => this._onMutation());
      this._obs.observe(target, { childList: true, subtree: true, characterData: true });
      this._isRunning = true;
      console.info('[Relay] assistantObserver started.');
    },

    stop() {
      if (this._obs) { this._obs.disconnect(); this._obs = null; }
      clearTimeout(Relay.state.streamIdleTimer);
      this._isRunning = false;
    },

    restart() { this.stop(); this.start(); },

    _onMutation() {
      const text = dom()?.getLatestAssistantText() ?? '';

      // テキストが変化していないなら無視
      if (text === Relay.state.lastAssistantText) return;

      Relay.state.lastAssistantText = text;

      // タイマーリセット: streamIdleMs 間テキストが変化しなければ「安定」と判定
      clearTimeout(Relay.state.streamIdleTimer);
      Relay.state.streamIdleTimer = setTimeout(() => {
        const stable = Relay.state.lastAssistantText;
        if (stable.length < Relay.config.minTodoLen) return;

        // 重複安定化防止（同じ内容を2回処理しない）
        const hash = Relay.utils.hash(stable);
        if (hash === Relay.state.lastSavedHash) return;

        Relay.state.lastStableAssistantText = stable;
        _emit('onStableAssistant', stable);
      }, Relay.config.streamIdleMs);
    },
  };

  // ─── User Observer ────────────────────────────────────────────────────────

  const _user = {
    _obs       : null,
    _isRunning : false,
    _lastTurn  : 0,

    start() {
      if (this._isRunning) return;

      this._obs = new MutationObserver(() => this._onMutation());
      this._obs.observe(document.body, { childList: true, subtree: true });
      this._isRunning = true;
    },

    stop() {
      if (this._obs) { this._obs.disconnect(); this._obs = null; }
      this._isRunning = false;
    },

    restart() { this.stop(); this.start(); },

    _onMutation() {
      const text = dom()?.getLatestUserText() ?? '';
      if (text && text !== Relay.state.lastUserText) {
        Relay.state.lastUserText = text;
        _emit('onUserMessage', text);
      }

      // ターン数変化チェック
      const turn = dom()?.getTurnCount() ?? 0;
      if (turn !== this._lastTurn) {
        this._lastTurn       = turn;
        Relay.state.turnCount = turn;
        _emit('onTurnChange', turn);
      }
    },
  };

  // ─── URL 変化監視（SPA遷移対応）─────────────────────────────────────────────

  let _lastUrl = location.href;

  const _urlWatcher = setInterval(() => {
    const current = location.href;
    if (current === _lastUrl) return;
    _lastUrl = current;

    // SPA遷移: state reset 前に onUrlChange を発火（セッション保存に使う）
    console.info('[Relay] URL changed → restarting observers. url:', current);
    _emit('onUrlChange', current);

    _assistant.restart();
    _user.restart();

    Relay.state.lastAssistantText       = '';
    Relay.state.lastStableAssistantText = '';
    Relay.state.lastUserText            = '';
    Relay.state.turnCount               = 0;
    Relay.state.warningShown            = false;
    Relay.state.lastSavedHash           = '';
  }, 1000);

  // ─── サービスとして登録 ───────────────────────────────────────────────────────

  Relay.services.watchers = Object.freeze({
    on,
    assistant : {
      start   : () => _assistant.start(),
      stop    : () => _assistant.stop(),
      restart : () => _assistant.restart(),
      get isRunning() { return _assistant._isRunning; },
    },
    user: {
      start   : () => _user.start(),
      stop    : () => _user.stop(),
      restart : () => _user.restart(),
      get isRunning() { return _user._isRunning; },
    },
    stopAll() {
      _assistant.stop();
      _user.stop();
      clearInterval(_urlWatcher);
    },
  });

  console.info('[Relay] relay-watchers.js registered.');

})();
