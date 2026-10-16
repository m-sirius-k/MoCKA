// 創造演算エンジンの試験（Node）：LE-1〜LE-4、試験X（断絶）、試験Y（循環）、実データの不変条件
// 実行: node --test tests/logic_engine.test.js
// 注意：合成グラフ（fixture）は演算の単体試験用。実データの検証は末尾の実データ節で行う。
const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('path');
const fs = require('fs');

const L = require(path.resolve(__dirname, '..', 'src', 'synapse_sim', 'logic_engine.js')).LogicEngine
  || require(path.resolve(__dirname, '..', 'src', 'synapse_sim', 'logic_engine.js'));
const { awaken, detectUnknowns, pairKey } = L;

// 合成グラフ：A(L1)–C(L3)–B(L2) が強い接続で、A と B は未接続。
// B には関係未確定の線（B–D, UNKNOWN＝β）を付け、B をホワイトスペースの端にする。
// UNKNOWN×3 が無ければ AND は動かない（仕様どおり）ので、この β が燃料になる。
const chain = () => ({
  nodes: [
    { id: 'A', layer: 'L1' }, { id: 'B', layer: 'L2' }, { id: 'C', layer: 'L3' }, { id: 'D', layer: 'L4' },
  ],
  edges: [
    { from: 'A', to: 'C', status: 'CODE_CONFIRMED' },
    { from: 'C', to: 'B', status: 'CODE_CONFIRMED' },
    { from: 'B', to: 'D', status: 'UNKNOWN' },
  ],
});

test('LE-1：UNKNOWN×3（α/β/ζ）が正確に抽出される', () => {
  const g = {
    nodes: [
      { id: 'X', layer: 'L1' },                 // 接続なし → α
      { id: 'Y', layer: 'L2' },                 // 全接続が UNKNOWN → α
      { id: 'Z', layer: 'Pending' },            // 判断未決 → ζ
      { id: 'W', layer: 'L1' }, { id: 'V', layer: 'L3' }, // PARTIAL の線 → β
    ],
    edges: [
      { from: 'Y', to: 'Z', status: 'UNKNOWN' },
      { from: 'W', to: 'V', status: 'PARTIAL' },
    ],
  };
  const u = detectUnknowns(g.nodes, g.edges);
  // Z は「接続が全て UNKNOWN」なので α。かつ Pending 層なので ζ。定義どおり両方に入る
  assert.deepEqual(u.alpha.sort(), ['X', 'Y', 'Z']);
  assert.deepEqual(u.zeta, ['Z']);
  assert.deepEqual(u.beta.slice().sort(), [pairKey('V', 'W'), pairKey('Y', 'Z')].sort());
  assert.ok(u.whitespace > 0, 'ホワイトスペースが抽出されること');
});

test('LE-2：AND により、共通の強い接続先を持つ異層の対に横のつながりが生まれる', () => {
  const r = awaken(chain());
  assert.equal(r.status, 'CONVERGED');
  assert.equal(r.laterals.length, 1);
  const l = r.laterals[0];
  assert.equal(pairKey(l.from, l.to), pairKey('A', 'B'));
  assert.deepEqual(l.branches, ['C']);
  assert.equal(l.state, 'SYNTHESIZED');
  assert.equal(l.kind, 'lateral');
});

test('LE-2：同層の対からは横のつながりを作らない', () => {
  const g = chain();
  g.nodes[1].layer = 'L1'; // B を A と同層にする
  assert.equal(awaken(g).laterals.length, 0);
});

test('LE-3：NOT により、断絶（CONFIRMED_ABSENT）の脚を通る経路は除外され、制約として残る', () => {
  const g = chain();
  g.edges[1].status = 'CONFIRMED_ABSENT'; // C–B が絶対不在（edges[1] は C–B）
  const r = awaken(g);
  assert.equal(r.laterals.length, 0, '断絶を通る経路では横のつながりを作らない');
  const c = r.constraints.find((x) => x.reason === 'NOT_ABSENT_LEG');
  assert.ok(c, 'NOT_ABSENT_LEG の制約が残ること');
  assert.equal(c.via, 'C');
});

test('LE-3：直接の絶対不在の対は、制約として明示され、横のつながりにならない', () => {
  const g = {
    nodes: [{ id: 'D', layer: 'L1' }, { id: 'E', layer: 'L2' }],
    edges: [{ from: 'D', to: 'E', status: 'CONFIRMED_ABSENT' }],
  };
  const r = awaken(g);
  assert.equal(r.laterals.length, 0);
  assert.ok(r.constraints.some((x) => x.reason === 'DIRECT_ABSENT' && pairKey(x.from, x.to) === pairKey('D', 'E')));
});

test('LE-4：REM が不正な候補（自己ループ・既存・同層・絶対不在・支持なし・重複）を刈り込む', () => {
  const g = chain();
  g.nodes.push({ id: 'P', layer: 'L1' }, { id: 'Q', layer: 'L1' }, { id: 'E', layer: 'L2' });
  g.edges.push({ from: 'P', to: 'E', status: 'CONFIRMED_ABSENT' });
  const injected = [
    { from: 'A', to: 'A', branches: ['C'], score: 1 },            // 自己ループ
    { from: 'A', to: 'C', branches: ['B'], score: 1 },            // 既存の線と重複
    { from: 'P', to: 'Q', branches: ['C'], score: 1 },            // 同層
    { from: 'P', to: 'E', branches: ['C'], score: 1 },            // 絶対不在の対（P–E は不在の線がある）
    { from: 'P', to: 'B', branches: [], score: 0 },               // 支持なし
    { from: 'A', to: 'B', branches: ['C'], score: 1 },            // 正規の候補との重複
    { from: 'ZZ', to: 'B', branches: ['C'], score: 1 },           // 存在しないノード
  ];
  const r = awaken(g, { injectCandidates: injected });
  const reasons = new Set(r.pruned.map((p) => p.reason));
  for (const want of ['SELF_LOOP', 'EXISTING_PAIR', 'SAME_LAYER', 'ABSENT_PAIR', 'NO_SUPPORT', 'DUPLICATE', 'UNKNOWN_NODE']) {
    assert.ok(reasons.has(want), 'REM が ' + want + ' で刈ること');
  }
  assert.equal(r.laterals.length, 1, '正規の横のつながり A–B だけが残る');
  assert.equal(pairKey(r.laterals[0].from, r.laterals[0].to), pairKey('A', 'B'));
});

test('試験X（完全な断絶空間）：証拠が無くても暴走せず、UNKNOWN×3 のまま安全に止まる', () => {
  const g = {
    nodes: [{ id: 'n1', layer: 'L1' }, { id: 'n2', layer: 'L2' }, { id: 'n3', layer: 'L3' }, { id: 'n4', layer: 'Pending' }],
    edges: [],
  };
  const r = awaken(g);
  assert.equal(r.status, 'NO_RESONANCE');
  assert.equal(r.laterals.length, 0);
  assert.equal(r.unknown.alpha, 4, '全ノードが α（データ欠損）');
  assert.equal(r.unknown.zeta, 1, 'Pending 層が ζ');
  assert.ok(r.rounds <= 3);
});

test('試験Y（循環）：AND と NOT が競合して往復しても、REM が循環を検知して禁止する', () => {
  const r = awaken(chain(), { injectFlipPair: pairKey('A', 'B'), maxRounds: 5 });
  assert.equal(r.status, 'CYCLE_PRUNED', '循環を検知して停止すること');
  assert.equal(r.laterals.length, 0, '往復していた対は残らない');
  assert.ok(r.pruned.some((p) => p.reason === 'CYCLE' && pairKey(p.from, p.to) === pairKey('A', 'B')));
  assert.ok(r.rounds <= 3, '無限ループせず早期に止まる（rounds=' + r.rounds + '）');
});

test('試験Y対照：循環を注入しなければ、同じグラフは収束する', () => {
  const r = awaken(chain(), { maxRounds: 5 });
  assert.equal(r.status, 'CONVERGED');
  assert.equal(r.laterals.length, 1);
});

test('入力のグラフは変更しない', () => {
  const g = chain();
  const before = JSON.stringify(g);
  awaken(g);
  assert.equal(JSON.stringify(g), before);
});

test('同じ入力は同じ結果（決定的）', () => {
  const a = JSON.stringify(awaken(chain()));
  const b = JSON.stringify(awaken(chain()));
  assert.equal(a, b);
});

// ---- 実データ（104ノード・128エッジ）の不変条件 ----
test('実データ：横のつながりは全て、異層・既存線なし・全経路が強い接続で裏付けられる', () => {
  const data = JSON.parse(fs.readFileSync(path.resolve(__dirname, '..', 'data', 'mocka_unified.json'), 'utf8'));
  const r = awaken({ nodes: data.nodes, edges: data.edges });
  const layerOf = new Map(data.nodes.map((n) => [n.id, n.layer]));
  const strong = (a, b) => data.edges.some((e) => ((e.from === a && e.to === b) || (e.from === b && e.to === a)) && L.STRONG.has(e.status));
  const exists = (a, b) => data.edges.some((e) => (e.from === a && e.to === b) || (e.from === b && e.to === a));
  const absent = (a, b) => data.edges.some((e) => e.status === 'CONFIRMED_ABSENT' && ((e.from === a && e.to === b) || (e.from === b && e.to === a)));
  assert.ok(['CONVERGED', 'MAX_ROUNDS', 'CYCLE_PRUNED', 'NO_RESONANCE'].includes(r.status));
  for (const l of r.laterals) {
    assert.notEqual(layerOf.get(l.from), layerOf.get(l.to), '異層であること: ' + l.id);
    assert.ok(!exists(l.from, l.to), '既存の線ではないこと: ' + l.id);
    assert.ok(!absent(l.from, l.to), '絶対不在の対ではないこと: ' + l.id);
    for (const c of l.branches) {
      assert.ok(strong(l.from, c) && strong(c, l.to), '経路が強い接続で裏付けられること: ' + l.id + ' via ' + c);
    }
  }
  assert.ok(r.laterals.length <= 30, '刈り込みにより爆発しないこと（' + r.laterals.length + ' 件）');
});

test('実データ：結果は再現する（同じ入力から同じ横のつながり）', () => {
  const data = JSON.parse(fs.readFileSync(path.resolve(__dirname, '..', 'data', 'mocka_unified.json'), 'utf8'));
  const a = awaken({ nodes: data.nodes, edges: data.edges }).laterals.map((l) => l.from + '|' + l.to).join(';');
  const b = awaken({ nodes: data.nodes, edges: data.edges }).laterals.map((l) => l.from + '|' + l.to).join(';');
  assert.equal(a, b);
});
