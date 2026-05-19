/**
 * Relay - relay-ui.js
 * @version 3.5.0
 * @description バッジ・トースト・警告ポップアップ。
 *
 * Purpose  : 視覚フィードバック全般
 * Owns     : #relay-badge / #relay-toast / 警告ポップアップ
 * Must not : DOM監視・TODO抽出・chrome API・state直接書き込み
 *
 * v3.5.0 変更:
 *   - refreshBadge() をターンカウント常時表示に修正
 *     TODOゼロでもバッジを表示 (例: 5/20、5/20 📋3)
 *   - 色: 0-49%=緑, 50-79%=オレンジ, 80-99%=赤, 100%超=赤点滅
 *   - バッジクリックで引き継ぎポップアップを即表示
 */

(() => {
  'use strict';

  const Relay = globalThis.__RELAY__;
  if (!Relay) { console.error('[Relay] relay-ui.js: __RELAY__ not found'); return; }

  const BADGE_ID = 'relay-badge';
  const TOAST_ID = 'relay-toast';

  // ─── バッジ生成 ──────────────────────────────────────────────────────────

  function _ensureBadge() {
    let badge = document.getElementById(BADGE_ID);
    if (badge) return badge;

    badge = document.createElement('div');
    badge.id = BADGE_ID;
    Object.assign(badge.style, {
      position   : 'fixed',
      bottom     : '20px',
      right      : '20px',
      zIndex     : '2147483647',
      background : '#1a1a2e',
      color      : '#e2c97e',
      border     : '1.5px solid #e2c97e',
      borderRadius: '12px',
      padding    : '4px 10px',
      fontSize   : '12px',
      fontFamily : 'monospace',
      fontWeight : 'bold',
      cursor     : 'pointer',
      userSelect : 'none',
      transition : 'opacity 0.2s',
      display    : 'none',
    });

    badge.addEventListener('click', () => {
      Relay.services.ui?.showTurnWarning(Relay.state.turnCount ?? 0);
    });

    document.body.appendChild(badge);
    return badge;
  }

  // ─── バッジ更新（ターンカウント常時表示）────────────────────────────────

  async function refreshBadge() {
    if (!document.body) return;
    const badge = _ensureBadge();

    const turn  = Relay.state.turnCount ?? 0;
    const limit = Relay.config?.turnWarningAt ?? 20;

    // TODO件数取得
    let openCount = 0;
    try {
      const todos = await Relay.services.logbook?.getTodos({ sessionOnly: true }) ?? [];
      openCount = todos.filter(t => !t.done).length;
    } catch (_) {}

    // テキスト組み立て
    const turnText = `${turn}/${limit}`;
    const todoText = openCount > 0 ? ` 📋${openCount}` : '';
    badge.textContent = turnText + todoText;

    // 色・点滅
    const ratio = limit > 0 ? turn / limit : 0;
    badge.style.animation = '';
    if (ratio >= 1.0) {
      badge.style.color       = '#ef4444';
      badge.style.borderColor = '#ef4444';
      badge.style.animation   = 'relay-blink 0.8s step-end infinite';
    } else if (ratio >= 0.8) {
      badge.style.color       = '#ef4444';
      badge.style.borderColor = '#ef4444';
    } else if (ratio >= 0.5) {
      badge.style.color       = '#f97316';
      badge.style.borderColor = '#f97316';
    } else {
      badge.style.color       = '#22c55e';
      badge.style.borderColor = '#22c55e';
    }

    // 点滅CSS（未挿入なら挿入）
    if (!document.getElementById('relay-blink-style')) {
      const style = document.createElement('style');
      style.id = 'relay-blink-style';
      style.textContent = `@keyframes relay-blink { 50% { opacity: 0; } }`;
      document.head.appendChild(style);
    }

    badge.style.display = 'block';
  }

  // ─── トースト ────────────────────────────────────────────────────────────

  function showToast(message, durationMs = 3000, type = 'info') {
    let toast = document.getElementById(TOAST_ID);
    if (!toast) {
      toast = document.createElement('div');
      toast.id = TOAST_ID;
      Object.assign(toast.style, {
        position     : 'fixed',
        bottom       : '60px',
        right        : '20px',
        zIndex       : '2147483647',
        background   : '#1a1a2e',
        color        : '#e2c97e',
        border       : '1px solid #e2c97e',
        borderRadius : '8px',
        padding      : '8px 14px',
        fontSize     : '12px',
        fontFamily   : 'monospace',
        maxWidth     : '280px',
        pointerEvents: 'none',
      });
      document.body.appendChild(toast);
    }

    toast.textContent  = message;
    toast.style.display = 'block';
    toast.style.opacity = '1';

    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => { toast.style.display = 'none'; }, 300);
    }, durationMs);
  }

  // ─── 引き継ぎ警告ポップアップ ────────────────────────────────────────────

  async function showTurnWarning(turn) {
    const existing = document.getElementById('relay-warning-popup');
    if (existing) existing.remove();

    // TODO取得
    let todoPart = '';
    try {
      const todos = await Relay.services.logbook?.getTodos({ sessionOnly: true }) ?? [];
      const open  = todos.filter(t => !t.done);
      if (open.length > 0) {
        todoPart = `<div style="margin-top:8px;font-size:11px;color:#94a3b8">
          未完了TODO: ${open.slice(0, 3).map(t => `<br>・${t.content.slice(0, 40)}`).join('')}
          ${open.length > 3 ? `<br>他 ${open.length - 3} 件` : ''}
        </div>`;
      }
    } catch (_) {}

    const popup = document.createElement('div');
    popup.id = 'relay-warning-popup';
    Object.assign(popup.style, {
      position     : 'fixed',
      bottom       : '60px',
      right        : '20px',
      zIndex       : '2147483647',
      background   : '#0d0d1a',
      border       : '1.5px solid #e2c97e',
      borderRadius : '12px',
      padding      : '16px',
      width        : '260px',
      fontFamily   : 'monospace',
      boxShadow    : '0 4px 20px rgba(0,0,0,0.5)',
    });

    popup.innerHTML = `
      <div style="color:#e2c97e;font-size:13px;font-weight:bold;margin-bottom:6px">
        ⚡ Relay: ${turn}ターンに達しました
      </div>
      <div style="color:#94a3b8;font-size:11px;line-height:1.6">
        コンテキストが長くなっています。<br>新しいチャットへ引き継ぐことを推奨します。
      </div>
      ${todoPart}
      <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:12px">
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

  // ─── サービスとして登録 ──────────────────────────────────────────────────

  Relay.services.ui = Object.freeze({
    refreshBadge,
    showToast,
    showTurnWarning,
  });

  console.info('[Relay] relay-ui.js registered. v3.5.0');

})();
