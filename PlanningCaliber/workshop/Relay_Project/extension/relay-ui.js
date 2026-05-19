/**
 * Relay — relay-ui.js
 * @version 3.3.0
 * @description バッジ・トースト・20ターン警告ポップアップ・引き継ぎUI。
 *
 * Purpose  : UI要素の生成・表示・更新
 * Owns     : バッジDOM / トーストDOM / 警告ポップアップ / バッジカウント更新
 * Must not : TODO抽出・MutationObserver・chrome.storage直接読み書き
 * Inputs   : logbook.getTodos() / state.turnCount
 * Outputs  : DOM要素の挿入・更新
 *
 * v3.3.0 変更点:
 *   - _connectWatchers() を削除。watchers 接続は relay-main.js に集中。
 *
 * Known traps:
 *   - claude.ai のスタイル変更でバッジが隠れることがある → z-index:2147483647 固定
 *   - ポップアップを重複生成しないよう id で一意化する
 *   - トーストは自動で消えるが、警告ポップアップはユーザー操作で閉じる
 */

(() => {
  'use strict';

  const Relay = globalThis.__RELAY__;
  if (!Relay) { console.error('[Relay] relay-ui.js: __RELAY__ not found'); return; }

  // ─── 定数 ─────────────────────────────────────────────────────────────────

  const BADGE_ID   = 'relay-badge';
  const TOAST_ID   = 'relay-toast';
  const POPUP_ID   = 'relay-warning-popup';
  const Z_TOP      = 2147483647;

  // ─── バッジ ───────────────────────────────────────────────────────────────

  function _ensureBadge() {
    if (document.getElementById(BADGE_ID)) return document.getElementById(BADGE_ID);

    const badge = document.createElement('div');
    badge.id = BADGE_ID;
    Object.assign(badge.style, {
      position     : 'fixed',
      bottom       : '20px',
      right        : '20px',
      zIndex       : String(Z_TOP),
      background   : '#1a1a2e',
      color        : '#e2c97e',
      border       : '1.5px solid #e2c97e',
      borderRadius : '12px',
      padding      : '4px 10px',
      fontSize     : '12px',
      fontFamily   : 'monospace',
      fontWeight   : 'bold',
      cursor       : 'pointer',
      userSelect   : 'none',
      transition   : 'opacity .2s',
      display      : 'none',
    });

    badge.title = 'Relay: TODO一覧を開く';
    badge.addEventListener('click', () => _openPopup());
    document.body.appendChild(badge);
    return badge;
  }

  async function refreshBadge() {
    if (!document.body) return;
    const badge = _ensureBadge();
    try {
      const todos = await Relay.services.logbook?.getTodos({ sessionOnly: true }) ?? [];
      const open  = todos.filter(t => !t.done);
      if (open.length === 0) {
        badge.style.display = 'none';
      } else {
        badge.style.display = 'block';
        badge.textContent   = `📋 ${open.length}`;
      }
    } catch (_) {
      badge.style.display = 'none';
    }
  }

  // ─── トースト ─────────────────────────────────────────────────────────────

  function showToast(message, durationMs = 3000, type = 'info') {
    let toast = document.getElementById(TOAST_ID);
    if (!toast) {
      toast = document.createElement('div');
      toast.id = TOAST_ID;
      Object.assign(toast.style, {
        position     : 'fixed',
        bottom       : '60px',
        right        : '20px',
        zIndex       : String(Z_TOP),
        borderRadius : '8px',
        padding      : '8px 14px',
        fontSize     : '13px',
        fontFamily   : 'monospace',
        fontWeight   : '500',
        maxWidth     : '320px',
        pointerEvents: 'none',
        transition   : 'opacity .3s',
      });
      document.body.appendChild(toast);
    }

    const palette = {
      info  : { bg: '#1a1a2e', color: '#e2c97e', border: '#e2c97e' },
      warn  : { bg: '#2e1a1a', color: '#f0a070', border: '#f0a070' },
      error : { bg: '#3b0000', color: '#ff6b6b', border: '#ff4444' },
    };
    const p = palette[type] ?? palette.info;
    Object.assign(toast.style, {
      background : p.bg,
      color      : p.color,
      border     : `1.5px solid ${p.border}`,
      opacity    : '1',
    });

    toast.textContent = message;

    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => {
      toast.style.opacity = '0';
    }, durationMs);
  }

  // ─── 20ターン警告ポップアップ ─────────────────────────────────────────────

  async function showTurnWarning(turnCount) {
    if (document.getElementById(POPUP_ID)) return;

    const todos = await Relay.services.logbook?.getTodos({ sessionOnly: true }) ?? [];
    const todoPart = todos.filter(t => !t.done)
      .slice(0, 5)
      .map((t, i) => `${i + 1}. ${t.content}`)
      .join('\n');

    const popup = document.createElement('div');
    popup.id = POPUP_ID;
    Object.assign(popup.style, {
      position     : 'fixed',
      top          : '50%',
      left         : '50%',
      transform    : 'translate(-50%, -50%)',
      zIndex       : String(Z_TOP),
      background   : '#0d0d1a',
      border       : '2px solid #e2c97e',
      borderRadius : '12px',
      padding      : '24px',
      width        : '380px',
      maxWidth     : '90vw',
      fontFamily   : 'monospace',
      color        : '#e2c97e',
      boxShadow    : '0 8px 32px rgba(0,0,0,.6)',
    });

    popup.innerHTML = `
      <div style="font-size:15px;font-weight:bold;margin-bottom:12px">
        ⚡ Relay: ${turnCount}ターンに達しました
      </div>
      <div style="font-size:12px;color:#aaa;margin-bottom:14px;line-height:1.6">
        コンテキストが長くなっています。<br>新しいチャットへ引き継ぐことを推奨します。
      </div>
      ${todoPart ? `
        <div style="font-size:11px;color:#888;margin-bottom:6px">未完了TODO（引き継ぎに含まれます）</div>
        <div style="font-size:12px;background:#1a1a2e;border:1px solid #333;border-radius:6px;
                    padding:8px;margin-bottom:14px;max-height:100px;overflow-y:auto;
                    white-space:pre-wrap;line-height:1.6">${todoPart}</div>
      ` : ''}
      <div style="display:flex;gap:10px;justify-content:flex-end">
        <button id="relay-popup-dismiss"
          style="background:none;border:1px solid #555;color:#888;border-radius:6px;
                 padding:6px 14px;cursor:pointer;font-size:12px">
          後で
        </button>
        <button id="relay-popup-handoff"
          style="background:#e2c97e;border:none;color:#0d0d1a;border-radius:6px;
                 padding:6px 14px;cursor:pointer;font-size:12px;font-weight:bold">
          新しいチャットへ →
        </button>
      </div>
    `;

    document.body.appendChild(popup);

    document.getElementById('relay-popup-dismiss')?.addEventListener('click', () => {
      popup.remove();
      Relay.state.warningShown = true;
    });

    document.getElementById('relay-popup-handoff')?.addEventListener('click', async () => {
      popup.remove();
      Relay.state.warningShown = true;
      await Relay.services.handoff?.trigger?.();
    });
  }

  // ─── サービスとして登録 ───────────────────────────────────────────────────
  // NOTE: watchers 接続は relay-main.js の _connectAllCallbacks() で行う。
  //       ここでは接続しない（タイミング競合を防ぐため）。

  Relay.services.ui = Object.freeze({
    refreshBadge,
    showToast,
    showTurnWarning,
  });

  console.info('[Relay] relay-ui.js registered.');

})();
