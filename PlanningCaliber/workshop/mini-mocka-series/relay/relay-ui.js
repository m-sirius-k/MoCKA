// relay-ui.js — 引き継ぎ最適タイミング通知バナー（One プラン）
// Task 2: relay-optimizer.js の判定結果を受けてバナーを表示/非表示する
'use strict';

const BANNER_ID   = 'relay-optimizer-banner';
const STORAGE_KEY = 'relay_optimizer_dismissed';

// ─── バナー生成 ───────────────────────────────────────────────────────────────

function createBanner() {
  const el = document.createElement('div');
  el.id = BANNER_ID;
  el.style.cssText = `
    position: fixed;
    bottom: 24px;
    right: 24px;
    z-index: 99999;
    background: #1a1a2e;
    border: 1px solid #00d4ff;
    border-radius: 10px;
    padding: 14px 18px;
    color: #c9d1d9;
    font-family: 'Noto Sans JP', sans-serif;
    font-size: 13px;
    box-shadow: 0 4px 20px rgba(0,212,255,0.2);
    min-width: 280px;
    max-width: 340px;
    animation: relay-slide-in 0.3s ease;
  `;
  el.innerHTML = `
    <style>
      @keyframes relay-slide-in {
        from { opacity:0; transform: translateY(16px); }
        to   { opacity:1; transform: translateY(0); }
      }
    </style>
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
      <span style="font-size:18px;">💡</span>
      <span style="font-weight:700;color:#00d4ff;font-size:14px;">引き継ぎ最適タイミング検知</span>
    </div>
    <div id="${BANNER_ID}-score-bar" style="background:#0d1117;border-radius:4px;height:8px;margin-bottom:8px;overflow:hidden;">
      <div id="${BANNER_ID}-score-fill" style="height:100%;border-radius:4px;background:linear-gradient(90deg,#00d4ff,#bc8cff);transition:width .5s;width:0%;"></div>
    </div>
    <div style="display:flex;justify-content:space-between;font-size:12px;color:#8b949e;margin-bottom:12px;">
      <span>密度スコア: <strong id="${BANNER_ID}-score-val" style="color:#c9d1d9;">--%</strong></span>
      <span>ターン: <strong id="${BANNER_ID}-turns" style="color:#c9d1d9;">--</strong></span>
      <span>重要決定: <strong id="${BANNER_ID}-decisions" style="color:#c9d1d9;">--</strong>件</span>
    </div>
    <div style="display:flex;gap:8px;">
      <button id="${BANNER_ID}-now" style="flex:1;padding:6px;background:#00d4ff;color:#07090f;border:none;border-radius:6px;font-weight:700;cursor:pointer;font-size:12px;">今すぐ引き継ぎ</button>
      <button id="${BANNER_ID}-later" style="flex:1;padding:6px;background:#1e2d3d;color:#8b949e;border:1px solid #2a3f52;border-radius:6px;cursor:pointer;font-size:12px;">あと5ターン</button>
      <button id="${BANNER_ID}-close" style="padding:6px 10px;background:transparent;color:#8b949e;border:none;cursor:pointer;font-size:16px;line-height:1;">✕</button>
    </div>
  `;
  return el;
}

// ─── バナー操作 ───────────────────────────────────────────────────────────────

function updateBanner(score, breakdown, turnCount) {
  const pct = Math.round(score * 100);
  const fill = document.getElementById(`${BANNER_ID}-score-fill`);
  const val  = document.getElementById(`${BANNER_ID}-score-val`);
  const turns = document.getElementById(`${BANNER_ID}-turns`);
  const decs  = document.getElementById(`${BANNER_ID}-decisions`);
  if (fill)  fill.style.width = `${pct}%`;
  if (val)   val.textContent  = `${pct}%`;
  if (turns) turns.textContent = String(turnCount);
  if (decs)  decs.textContent  = String(breakdown?.decisionCount ?? 0);
}

/**
 * バナーを表示する（未表示の場合のみ）
 * @param {{ score:number, breakdown:object }} result
 * @param {number} turnCount
 * @param {{ onHandoffNow: Function, onLater: Function }} callbacks
 */
export function showBanner(result, turnCount, { onHandoffNow, onLater } = {}) {
  if (document.getElementById(BANNER_ID)) {
    updateBanner(result.score, result.breakdown, turnCount);
    return;
  }
  const banner = createBanner();
  document.body.appendChild(banner);
  updateBanner(result.score, result.breakdown, turnCount);

  document.getElementById(`${BANNER_ID}-now`)?.addEventListener('click', () => {
    hideBanner();
    onHandoffNow?.();
  });
  document.getElementById(`${BANNER_ID}-later`)?.addEventListener('click', () => {
    hideBanner();
    onLater?.();
  });
  document.getElementById(`${BANNER_ID}-close`)?.addEventListener('click', hideBanner);
}

export function hideBanner() {
  document.getElementById(BANNER_ID)?.remove();
}
