// Synapse-3D ブリッジの試験（Node）：変換の正しさ・入力を壊さないこと・3D側へ送る形の安全性
// 実行: node --test tests/synapse_bridge.test.js
const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('path');

const base = path.resolve(__dirname, '..', 'src', 'synapse_sim');
const sim = require(path.join(base, 'pipeline.js'));
const bridge = require(path.join(base, 'bridge_to_3d.js'));
const { translateTo3DStyles, toPayload, OVERLAY_KEYS } = bridge.Synapse3DBridge || globalThis.Synapse3DBridge;

test('キーは4経路で、シミュレーターのエッジ名と一致する', () => {
  assert.deepEqual(OVERLAY_KEYS, ['edge_hg_to_auth', 'edge_auth_to_rt', 'edge_rt_to_cons', 'edge_cons_to_mem']);
});

test('正常系：4本とも緑・太線・点滅なし', () => {
  const st = translateTo3DStyles(sim.runVirtualPipelineTest());
  for (const k of OVERLAY_KEYS) {
    assert.equal(st[k].status, 'VERIFIED');
    assert.equal(st[k].color, '#2ecc71');
    assert.equal(st[k].width, 3);
    assert.equal(st[k].highlight, false);
  }
});

test('Test A：HG->Auth が赤・点滅、理由が付き、他は灰色の未到達', () => {
  const st = translateTo3DStyles(sim.runVirtualPipelineTest({ humanEvent: { approved_by: 'unknown_user' } }));
  assert.equal(st.edge_hg_to_auth.status, 'BROKEN');
  assert.equal(st.edge_hg_to_auth.color, '#e74c3c');
  assert.equal(st.edge_hg_to_auth.highlight, true);
  assert.equal(st.edge_hg_to_auth.reason, 'UNAUTHORIZED_APPROVER');
  for (const k of ['edge_auth_to_rt', 'edge_rt_to_cons', 'edge_cons_to_mem']) {
    assert.equal(st[k].status, 'NOT_REACHED');
    assert.equal(st[k].color, '#9a9a9a');
    assert.equal(st[k].highlight, false);
  }
});

test('Test B：Auth->RT が赤・点滅（HG->Auth は未検証のまま灰色）', () => {
  const st = translateTo3DStyles(sim.runVirtualPipelineTest({ skipAuth: true }));
  assert.equal(st.edge_auth_to_rt.status, 'BROKEN');
  assert.equal(st.edge_auth_to_rt.highlight, true);
  assert.equal(st.edge_hg_to_auth.status, 'NOT_REACHED');
});

test('Test C：RT->Cons が赤・点滅、Cons->Mem は未到達', () => {
  const st = translateTo3DStyles(sim.runVirtualPipelineTest({ consequenceAuthIdOverride: 'auth_999' }));
  assert.equal(st.edge_rt_to_cons.status, 'BROKEN');
  assert.equal(st.edge_rt_to_cons.highlight, true);
  assert.equal(st.edge_rt_to_cons.reason, 'AUTH_ID_MISMATCH');
  assert.equal(st.edge_cons_to_mem.status, 'NOT_REACHED');
});

test('入力のシミュレーター結果を変更しない', () => {
  const r = sim.runVirtualPipelineTest({ skipAuth: true });
  const before = JSON.stringify(r);
  translateTo3DStyles(r);
  toPayload(translateTo3DStyles(r));
  assert.equal(JSON.stringify(r), before);
});

test('toPayload：色を送らず、許可された状態だけを通す', () => {
  const p = toPayload({
    edge_hg_to_auth: { color: '#ff00ff', status: 'VERIFIED', width: 3, dash: false, highlight: false, reason: null, extra: 'x' },
    edge_auth_to_rt: { status: 'EVIL', width: 3, highlight: true },
    edge_rt_to_cons: { status: 'BROKEN', width: 999, highlight: true, reason: 'x'.repeat(500) },
    not_an_edge: { status: 'VERIFIED' },
  });
  assert.deepEqual(Object.keys(p).sort(), ['edge_hg_to_auth', 'edge_rt_to_cons']);
  assert.equal(p.edge_hg_to_auth.color, undefined);
  assert.equal(p.edge_hg_to_auth.extra, undefined);
  assert.equal(p.edge_rt_to_cons.width, 8, '太さは 1〜8 に丸める');
  assert.equal(p.edge_rt_to_cons.reason.length, 80, '理由は 80 文字まで');
});

test('toPayload：未知の入力（null / 空）でも落ちない', () => {
  assert.deepEqual(toPayload(null), {});
  assert.deepEqual(toPayload({}), {});
});
