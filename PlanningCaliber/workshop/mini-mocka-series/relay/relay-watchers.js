// relay-watchers.js — DOM 変化監視（MutationObserver）
'use strict';

window.RelayWatchers = (() => {
  let _observer   = null;
  let _seenIds    = new Set();
  let _onNewTurn  = null;

  /**
   * DOM 監視を開始する
   * @param {Function} onNewTurn  新ターン発見時のコールバック
   */
  function start(onNewTurn) {
    _onNewTurn = onNewTurn;
    if (_observer) return;

    const target = RelayDOM.getMainTarget();
    _observer = new MutationObserver(_handleMutations);
    _observer.observe(target, { childList: true, subtree: true });
    _scanExisting();  // 初回スキャン
  }

  function stop() {
    _observer?.disconnect();
    _observer = null;
  }

  function _handleMutations() {
    _scanExisting();
  }

  function _scanExisting() {
    const turns = RelayDOM.getAllTurns();
    turns.forEach(el => {
      const turn = RelayDOM.extractTurn(el);
      if (!turn.id || _seenIds.has(turn.id)) return;
      if (!turn.content) return;
      _seenIds.add(turn.id);
      _onNewTurn?.(turn);
    });
  }

  function reset() {
    _seenIds.clear();
  }

  return { start, stop, reset };
})();
