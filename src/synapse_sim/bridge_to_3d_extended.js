/**
 * Synapse-3D Bridge（拡張）：創造演算の横のつながり（lateral）を 3D 描画指示へ変換する
 * 前提：bridge_to_3d.js を先に読み込んでおくこと（Synapse3DBridge を拡張する）
 *
 * 横のつながりは「仮説」。3D では紫の閃光で示し、色は受信側が決める（送られてきた色は使わない）。
 */
(function (global) {
  'use strict';

  const NODE_ID = /^N\d{3}$/;
  const LAT_ID = /^lat_\d{3}$/;
  const MAX_LATERALS = 50;
  const MAX_BRANCHES = 8;

  /**
   * 創造演算の結果から、3D に描く横のつながりだけを取り出す（許可された形のみ）
   * @param {Object} awakenResult - LogicEngine.awaken() の戻り値
   * @returns {Array<{id, from, to, branches, round}>}
   */
  function translateLateralTo3D(awakenResult) {
    const out = [];
    const list = (awakenResult && Array.isArray(awakenResult.laterals)) ? awakenResult.laterals : [];
    for (const l of list) {
      if (out.length >= MAX_LATERALS) break;
      if (!l || typeof l.id !== 'string' || !LAT_ID.test(l.id)) continue;
      if (!NODE_ID.test(l.from) || !NODE_ID.test(l.to) || l.from === l.to) continue;
      const branches = (Array.isArray(l.branches) ? l.branches : [])
        .filter((b) => typeof b === 'string' && NODE_ID.test(b))
        .slice(0, MAX_BRANCHES);
      out.push({ id: l.id, from: l.from, to: l.to, branches: branches, round: Number(l.round) || 1 });
    }
    return out;
  }

  /**
   * 3D 側の描画用：色と太さを状態から決める（受信側で決めるため、ここでは状態だけを付ける）
   */
  function toLateralStyles(list) {
    return list.map((l) => ({ id: l.id, from: l.from, to: l.to, status: 'SYNTHESIZED', width: 3, highlight: true }));
  }

  if (!global.Synapse3DBridge) global.Synapse3DBridge = {};
  Object.assign(global.Synapse3DBridge, {
    translateLateralTo3D: translateLateralTo3D,
    toLateralStyles: toLateralStyles,
    MAX_LATERALS: MAX_LATERALS,
  });
})(typeof window !== 'undefined' ? window : globalThis);
