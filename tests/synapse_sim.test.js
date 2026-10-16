// 仮想Synapseシミュレーターの試験（Node の組み込みテストランナー）
// 実行: node --test tests/synapse_sim.test.js
const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('path');

const sim = require(path.resolve(__dirname, '..', 'src', 'synapse_sim', 'pipeline.js'));

const VERIFIED_ALL = {
  edge_hg_to_auth: 'VERIFIED',
  edge_auth_to_rt: 'VERIFIED',
  edge_rt_to_cons: 'VERIFIED',
  edge_cons_to_mem: 'VERIFIED',
};

test('仕様の mockHumanEvent と同じ値になる', () => {
  assert.deepEqual(sim.makeHumanEvent(), {
    event_id: 'evt_hg_20261016_001',
    approved_by: 'human_authority',
    scope: 'pipeline_1st_test',
    decision: 'ALLOW',
    timestamp: '2026-10-16T13:00:00Z',
  });
});

test('正常系：Step 1〜5 がすべて通り、全エッジが VERIFIED', () => {
  const r = sim.runVirtualPipelineTest();
  assert.equal(r.ok, true);
  assert.equal(r.broken, null);
  assert.deepEqual(r.edges, VERIFIED_ALL);
  assert.ok(r.checkpoints.every((c) => c.pass), 'すべての CP が通過すること');
  assert.equal(r.authRecords.length, 1);
  assert.equal(r.memoryStore.length, 1);
  assert.deepEqual(
    [r.memoryStore[0].human_event_id, r.memoryStore[0].auth_id, r.memoryStore[0].run_id, r.memoryStore[0].consequence_id],
    ['evt_hg_20261016_001', 'auth_001', 'run_auth_001', 'cons_run_auth_001']
  );
});

test('CP-2：認可レコードが 0件 -> 1件 に推移する', () => {
  const r = sim.runVirtualPipelineTest();
  const cp2 = r.checkpoints.find((c) => c.id === 'CP-2');
  assert.equal(cp2.pass, true);
  assert.equal(cp2.actual, '0 -> 1');
});

test('Test A（無効な承認者）：Authorization が生成されず、HG->Auth で遮断', () => {
  const r = sim.runVirtualPipelineTest({ humanEvent: { approved_by: 'unknown_user' } });
  assert.equal(r.ok, false);
  assert.equal(r.broken.edge, 'edge_hg_to_auth');
  assert.equal(r.broken.reason, 'UNAUTHORIZED_APPROVER');
  assert.equal(r.authRecords.length, 0);
  assert.equal(r.edges.edge_hg_to_auth, 'BROKEN');
  assert.equal(r.edges.edge_auth_to_rt, 'NOT_REACHED');
  assert.equal(r.checkpoints.find((c) => c.id === 'CP-2').pass, false);
  assert.equal(r.memoryStore.length, 0);
});

test('Test B（認可情報の欠損）：RuntimeGate が UNSUPPORTED を返し、Auth->RT で遮断', () => {
  const r = sim.runVirtualPipelineTest({ skipAuth: true });
  assert.equal(r.ok, false);
  assert.equal(r.broken.edge, 'edge_auth_to_rt');
  assert.equal(r.broken.reason, 'UNKNOWN_NO_AUTHORIZATION');
  assert.equal(r.edges.edge_hg_to_auth, 'NOT_REACHED', 'Step 2 を飛ばしたので HG->Auth は未検証のまま');
  assert.equal(r.edges.edge_auth_to_rt, 'BROKEN');
  assert.equal(r.checkpoints.find((c) => c.id === 'CP-3').pass, false);
  assert.equal(r.memoryStore.length, 0);
});

test('Test C（ID不一致）：Memory 結合で「トレース切れ」を検知し、RT->Cons で遮断', () => {
  const r = sim.runVirtualPipelineTest({ consequenceAuthIdOverride: 'auth_999' });
  assert.equal(r.ok, false);
  assert.equal(r.broken.edge, 'edge_rt_to_cons');
  assert.equal(r.broken.reason, 'AUTH_ID_MISMATCH');
  assert.deepEqual(r.broken.detail, { expected: 'auth_001', actual: 'auth_999' });
  assert.equal(r.edges.edge_rt_to_cons, 'BROKEN');
  assert.equal(r.edges.edge_cons_to_mem, 'NOT_REACHED');
  assert.equal(r.checkpoints.find((c) => c.id === 'CP-4').pass, true, 'Consequence 自体は捕捉される');
  assert.equal(r.checkpoints.find((c) => c.id === 'CP-5').pass, false);
  assert.equal(r.memoryStore.length, 0);
});

test('遮断時のログに、どの接続で止まったかが出る', () => {
  const r = sim.runVirtualPipelineTest({ consequenceAuthIdOverride: 'auth_999' });
  const blocked = r.log.find((l) => l.step === 'BLOCKED');
  assert.ok(blocked, 'BLOCKED のログがあること');
  assert.match(blocked.msg, /\[BLOCKED\] edge_rt_to_cons: AUTH_ID_MISMATCH/);
});

test('走査を重ねても状態は持ち越されない（毎回 0 -> 1 を検証できる）', () => {
  const first = sim.runVirtualPipelineTest();
  const second = sim.runVirtualPipelineTest();
  assert.equal(first.authRecords.length, 1);
  assert.equal(second.authRecords.length, 1);
  assert.equal(second.checkpoints.find((c) => c.id === 'CP-2').actual, '0 -> 1');
});

test('デバッグ一括実行は A / B / C を返す', () => {
  const s = sim.runDebugSuite();
  assert.equal(s.testA_invalidApprover.broken.edge, 'edge_hg_to_auth');
  assert.equal(s.testB_missingAuthorization.broken.edge, 'edge_auth_to_rt');
  assert.equal(s.testC_idMismatch.broken.edge, 'edge_rt_to_cons');
});

test('ハッシュは決定的（同じ入力は同じ output_hash）', () => {
  const a = sim.runVirtualPipelineTest().memoryStore[0].output_hash;
  const b = sim.runVirtualPipelineTest().memoryStore[0].output_hash;
  assert.equal(a, b);
  assert.match(a, /^[0-9a-f]{8}$/);
});
