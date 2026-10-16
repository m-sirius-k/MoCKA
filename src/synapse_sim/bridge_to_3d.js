/**
 * Synapse-3D Bridge Module
 * シミュレーターの結果（edges / broken）を 3D Mapping のオーバーレイ経路の描画指示に変換する。
 *
 * 注意：3Dマップの実データのエッジ（E001〜E128）には、シミュレーターの経路に対応するものが無い。
 * そのため、経路は 3D 側が持つ「Synapse オーバーレイ」（mocka_3d.html の SYNAPSE_PATH）として描く。
 * 本モジュールの出力キーは、シミュレーターのエッジ名そのもの（edge_hg_to_auth など）とする。
 */
(function (global) {
  'use strict';

  // 3D側のオーバーレイ経路のキー（mocka_3d.html の SYNAPSE_PATH と一致させること）
  const OVERLAY_KEYS = ['edge_hg_to_auth', 'edge_auth_to_rt', 'edge_rt_to_cons', 'edge_cons_to_mem'];

  // 3D側へ送ってよい状態の一覧（ここに無い状態は送らない）
  const ALLOWED_STATUS = ['VERIFIED', 'BROKEN', 'NOT_REACHED'];

  const STYLE_BY_STATUS = {
    VERIFIED:    { color: '#2ecc71', width: 3, dash: false },  // 緑の実線（太）：実証済み
    BROKEN:      { color: '#e74c3c', width: 4, dash: true },   // 赤の警告線（点滅）：遮断箇所
    NOT_REACHED: { color: '#9a9a9a', width: 1, dash: false },  // 灰色の細線：未到達
  };

  /**
   * シミュレーターの結果を、経路ごとの描画スタイルに変換する（入力は変更しない）
   * @param {Object} simResult - SynapseSim.runVirtualPipelineTest() の戻り値
   * @returns {Object} { [edgeKey]: { color, width, dash, status, highlight, reason } }
   */
  function translateTo3DStyles(simResult) {
    const styles = {};
    const edges = (simResult && simResult.edges) || {};

    for (const key of OVERLAY_KEYS) {
      const status = edges[key] || 'NOT_REACHED';
      const base = STYLE_BY_STATUS[status] || STYLE_BY_STATUS.NOT_REACHED;
      styles[key] = { color: base.color, width: base.width, dash: base.dash, status: status, highlight: false };
    }

    // 遮断箇所はハイライト（点滅）し、理由を付ける
    if (simResult && !simResult.ok && simResult.broken && styles[simResult.broken.edge]) {
      styles[simResult.broken.edge].highlight = true;
      styles[simResult.broken.edge].reason = simResult.broken.reason;
    }
    return styles;
  }

  /**
   * 3D側へ送るための安全な形に整える（許可された項目だけを残す）
   * 色は 3D 側が状態から決めるため、送らない。
   */
  function toPayload(styles) {
    const payload = {};
    for (const key of OVERLAY_KEYS) {
      const s = styles && styles[key];
      if (!s || ALLOWED_STATUS.indexOf(s.status) === -1) continue;
      payload[key] = {
        status: s.status,
        width: Math.min(8, Math.max(1, Number(s.width) || 1)),
        highlight: s.highlight === true,
        reason: typeof s.reason === 'string' ? s.reason.slice(0, 80) : null,
      };
    }
    return payload;
  }

  global.Synapse3DBridge = {
    OVERLAY_KEYS: OVERLAY_KEYS,
    ALLOWED_STATUS: ALLOWED_STATUS,
    translateTo3DStyles: translateTo3DStyles,
    toPayload: toPayload,
  };
})(typeof window !== 'undefined' ? window : globalThis);
