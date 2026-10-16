/*
 * 創造演算エンジン（Synapse Awakening & Logic Engine）
 *
 * UNKNOWN×3（α/β/ζ）の検出 → AND / OR / NOT による候補生成 → REM による刈り込み、
 * を複数ラウンドで回す。生成された横のつながり（lateral）は次ラウンドの強い接続として扱う。
 *
 * 定義（指示書の記述に基づく。論文本文との突き合わせは未了）：
 *   α：データ欠損 … 接続が 1 本も無いノード、または全接続が UNKNOWN のノード
 *   β：関係未確定 … UNKNOWN / PENDING / PARTIAL の線（関係が確定していない）
 *   ζ：文脈未定義 … layer が Pending のノード（判断が未決）
 *   ホワイトスペース：上の α/β/ζ に触れ、かつ未接続な異層のノード対
 *   AND：異層の対で、共通の強い接続先 C（A–C も C–B も強い）があること
 *   OR ：共通の接続先が複数なら、経路（branch）を全部保持する
 *   NOT：A–C か C–B が CONFIRMED_ABSENT の経路は除外し、制約として記録する
 *   REM：自己ループ・既存線との重複・同層・絶対不在・支持なし・循環で禁止された対を刈り込む
 *   横のつながりは仮説：次ラウンドでは「既存の線」として重複を防ぐが、根拠（強い接続）にはしない
 *
 * 入力の graph は変更しない。外部データ・DB には触れない。
 */
(function (root) {
  'use strict';

  // 横のつながり（SYNTHESIZED）は仮説であり、次の根拠（強い接続）にはしない（証拠なき連鎖を防ぐ）
const STRONG = new Set(['CODE_CONFIRMED', 'RUNTIME_VERIFIED', 'DATA_FLOW_CONFIRMED', 'FS_CONFIRMED']);
  const ABSENT = 'CONFIRMED_ABSENT';
  const UNRESOLVED = new Set(['UNKNOWN', 'PENDING', 'PARTIAL']);

  const pairKey = (a, b) => (a < b ? a + '|' + b : b + '|' + a);

  // 同じ対に複数の状態があれば、それらをまとめて持つ
  function buildIndex(nodes, edges) {
    const layerOf = new Map(nodes.map((n) => [n.id, n.layer]));
    const pairStatus = new Map(); // key -> [status...]
    const adj = new Map(nodes.map((n) => [n.id, new Set()]));
    for (const e of edges) {
      if (!layerOf.has(e.from) || !layerOf.has(e.to) || e.from === e.to) continue;
      const k = pairKey(e.from, e.to);
      if (!pairStatus.has(k)) pairStatus.set(k, []);
      pairStatus.get(k).push(e.status);
      adj.get(e.from).add(e.to);
      adj.get(e.to).add(e.from);
    }
    return { layerOf, pairStatus, adj };
  }

  const hasStrong = (idx, a, b) => (idx.pairStatus.get(pairKey(a, b)) || []).some((s) => STRONG.has(s));
  const hasAbsent = (idx, a, b) => (idx.pairStatus.get(pairKey(a, b)) || []).some((s) => s === ABSENT);
  const hasAnyEdge = (idx, a, b) => idx.pairStatus.has(pairKey(a, b));

  // UNKNOWN×3 の検出
  function detectUnknowns(nodes, edges) {
    const idx = buildIndex(nodes, edges);
    const alpha = [], zeta = [], betaEnds = new Set(), beta = [];
    for (const n of nodes) {
      const nbs = idx.adj.get(n.id);
      const onlyUnknown = nbs.size > 0 && [...nbs].every((o) => {
        const st = idx.pairStatus.get(pairKey(n.id, o)) || [];
        return st.every((s) => s === 'UNKNOWN');
      });
      if (nbs.size === 0 || onlyUnknown) alpha.push(n.id);
      if (n.layer === 'Pending') zeta.push(n.id);
    }
    for (const e of edges) {
      if (UNRESOLVED.has(e.status) && idx.layerOf.has(e.from) && idx.layerOf.has(e.to)) {
        beta.push(pairKey(e.from, e.to));
        betaEnds.add(e.from); betaEnds.add(e.to);
      }
    }
    const wsEnds = new Set([...alpha, ...zeta, ...betaEnds]);
    let whitespace = 0;
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const a = nodes[i].id, b = nodes[j].id;
        if (nodes[i].layer === nodes[j].layer) continue;
        if (hasAnyEdge(idx, a, b)) continue;
        if (wsEnds.has(a) || wsEnds.has(b)) whitespace++;
      }
    }
    return { idx, alpha, beta, zeta, betaEnds, wsEnds, whitespace };
  }

  // AND / OR / NOT による候補生成（1ラウンド分）
  function deriveCandidates(nodes, edges, unk, log) {
    const idx = unk.idx;
    const candidates = [], constraints = [];
    // NOT：直接の絶対不在は、その対を制約として明示する
    for (const [k, sts] of idx.pairStatus) {
      if (sts.indexOf(ABSENT) !== -1) {
        const [from, to] = k.split('|');
        constraints.push({ from, to, kind: 'constraint', reason: 'DIRECT_ABSENT', via: null });
      }
    }
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const a = nodes[i].id, b = nodes[j].id;
        if (nodes[i].layer === nodes[j].layer) continue;      // AND：異層間のみ
        if (hasAnyEdge(idx, a, b)) continue;                    // 既存の線は対象外
        if (!unk.wsEnds.has(a) && !unk.wsEnds.has(b)) continue; // ホワイトスペースのみ
        const branches = [];
        for (const c of idx.adj.get(a)) {
          if (c === b || !idx.adj.get(b).has(c)) continue;
          if (hasAbsent(idx, a, c) || hasAbsent(idx, c, b)) {
            constraints.push({ from: a, to: b, kind: 'constraint', reason: 'NOT_ABSENT_LEG', via: c });
            continue;
          }
          if (hasStrong(idx, a, c) && hasStrong(idx, c, b)) branches.push(c);
        }
        if (branches.length > 0) {
          candidates.push({ from: a, to: b, branches, score: branches.length, multiPath: branches.length > 1 });
        }
      }
    }
    log('AND', '共通の強い接続先がある異層の対: ' + candidates.length + ' 件');
    const multi = candidates.filter((c) => c.multiPath).length;
    log('OR', '複数経路を持つ候補: ' + multi + ' 件（経路は全て保持）');
    log('NOT', '制約（隠れた境界）: ' + constraints.length + ' 件');
    return { candidates, constraints };
  }

  // REM：候補を刈り込み、理由を残す
  // policy: { hubDegree（これを超える接続数のノードだけで支持される対は刈る）, maxPerRound（1ラウンドの上限） }
  function prune(cands, idx, blacklist, policy) {
    policy = policy || {};
    const hubDegree = policy.hubDegree || 8;
    const maxPerRound = policy.maxPerRound || 10;
    const kept = [], pruned = [];
    const seenInBatch = new Set();
    for (const c of cands) {
      const k = pairKey(c.from, c.to);
      let reason = null;
      if (c.from === c.to) reason = 'SELF_LOOP';
      else if (!idx.layerOf.has(c.from) || !idx.layerOf.has(c.to)) reason = 'UNKNOWN_NODE';
      else if (idx.layerOf.get(c.from) === idx.layerOf.get(c.to)) reason = 'SAME_LAYER';
      else if (hasAbsent(idx, c.from, c.to)) reason = 'ABSENT_PAIR';
      else if (hasAnyEdge(idx, c.from, c.to)) reason = 'EXISTING_PAIR';
      else if (blacklist.has(k)) reason = 'BLACKLISTED_CYCLE';
      else if (!(c.score >= 1) || !Array.isArray(c.branches) || c.branches.length < 1) reason = 'NO_SUPPORT';
      else if (seenInBatch.has(k)) reason = 'DUPLICATE';
      else if (!c.multiPath && c.branches.every((h) => idx.adj.get(h) && idx.adj.get(h).size > hubDegree)) reason = 'HUB_ONLY';
      if (reason) { pruned.push({ from: c.from, to: c.to, reason }); continue; }
      seenInBatch.add(k);
      kept.push(c);
    }
    // 上限：スコアの高い（経路の多い）ものから残す。同点は対の名前順で決める（決定的）
    kept.sort((x, y) => (y.score - x.score) || (pairKey(x.from, x.to) < pairKey(y.from, y.to) ? -1 : 1));
    while (kept.length > maxPerRound) {
      const c = kept.pop();
      pruned.push({ from: c.from, to: c.to, reason: 'CAP_EXCEEDED' });
    }
    return { kept, pruned };
  }

  const stateKey = (set) => [...set].sort().join(',');

  /**
   * 創造演算を実行する
   * @param {Object} input - { nodes: [{id, layer}], edges: [{from, to, status}] }
   * @param {Object} opts  - { maxRounds, injectCandidates（REM試験用）, injectFlipPair（循環の注入試験用） }
   */
  function awaken(input, opts) {
    opts = opts || {};
    const maxRounds = opts.maxRounds || 3;
    const nodes = (input.nodes || []).map((n) => ({ id: n.id, layer: n.layer }));
    const baseEdges = (input.edges || []).map((e) => ({ from: e.from, to: e.to, status: e.status }));
    const log = [];
    const L = (step, msg, data) => log.push({ step, msg, data: data === undefined ? null : data });

    // 1) UNKNOWN×3（基底グラフ）
    const unk0 = detectUnknowns(nodes, baseEdges);
    L('UNKNOWN×3', 'α=' + unk0.alpha.length + ' β=' + unk0.beta.length + ' ζ=' + unk0.zeta.length + ' / ホワイトスペース=' + unk0.whitespace,
      { alpha: unk0.alpha, zeta: unk0.zeta });

    const state = new Map();     // key -> lateral（現在採用中）
    const blacklist = new Set();
    const constraints = [];
    const pruned = [];
    const history = [new Set()]; // ラウンドごとの採用状態（循環検出に使う）
    let nextId = 1;
    let status = null;
    let rounds = 0;

    for (let r = 1; r <= maxRounds && status === null; r++) {
      rounds = r;
      // 採用中の横のつながりを、次ラウンドの強い接続として加える（フィードバック）
      const laterals = [...state.values()].map((l) => ({ from: l.from, to: l.to, status: 'SYNTHESIZED' }));
      const edgesR = baseEdges.concat(laterals);
      const unk = detectUnknowns(nodes, edgesR);
      const d = deriveCandidates(nodes, edgesR, unk, (s, m) => L(s, '[r' + r + '] ' + m));
      constraints.push(...d.constraints);

      const injected = r === 1 ? (opts.injectCandidates || []) : [];
      const rem = prune(d.candidates.concat(injected), unk.idx, blacklist, opts.policy);
      rem.pruned.forEach((p) => pruned.push(Object.assign({ round: r }, p)));
      L('REM', '[r' + r + '] 採用 ' + rem.kept.length + ' 件 / 刈り込み ' + rem.pruned.length + ' 件', rem.pruned);

      // 注入された循環（試験用）：前ラウンドで採用された対を、NOT が打ち消す
      if (opts.injectFlipPair && state.has(opts.injectFlipPair)) {
        state.delete(opts.injectFlipPair);
        L('NOT', '[r' + r + '] [FAULT-INJECTED] 採用中の対を打ち消す: ' + opts.injectFlipPair);
      }

      for (const c of rem.kept) {
        const k = pairKey(c.from, c.to);
        if (!state.has(k)) {
          state.set(k, { id: 'lat_' + String(nextId++).padStart(3, '0'), from: c.from, to: c.to, kind: 'lateral', state: 'SYNTHESIZED', branches: c.branches.slice(), round: r });
          L('AND', '[r' + r + '] 横のつながり生成: ' + c.from + ' ↔ ' + c.to + ' (経路 ' + c.branches.length + ')', { branches: c.branches });
        }
      }

      const key = stateKey(state.keys());
      const prevKey = stateKey(history[history.length - 1]);
      if (key === prevKey) { status = 'CONVERGED'; break; }
      const earlier = history.findIndex((h) => stateKey(h) === key);
      if (earlier !== -1) {
        // 循環：その区間で出入りした対を禁止し、安定した共通部分だけを残す
        const seg = history.slice(earlier).concat([state.keys()]).map((s) => new Set(s));
        const union = new Set(), inter = new Set(seg[0]);
        seg.forEach((s) => s.forEach((k) => union.add(k)));
        seg.forEach((s) => { for (const k of [...inter]) if (!s.has(k)) inter.delete(k); });
        for (const k of union) if (!inter.has(k)) {
          blacklist.add(k);
          const [from, to] = k.split('|');
          pruned.push({ round: r, from, to, reason: 'CYCLE' });
        }
        for (const k of [...state.keys()]) if (!inter.has(k)) state.delete(k);
        L('REM', '[r' + r + '] 循環を検知：往復していた対を禁止し、安定部分 ' + inter.size + ' 件のみ残す', [...union].filter((k) => !inter.has(k)));
        status = 'CYCLE_PRUNED';
        break;
      }
      history.push(new Set(state.keys()));
      if (r === maxRounds) status = 'MAX_ROUNDS';
    }
    if (status === null) status = 'CONVERGED';
    if (status !== 'CYCLE_PRUNED' && state.size === 0) status = 'NO_RESONANCE';

    const laterals = [...state.values()].sort((x, y) => (x.id < y.id ? -1 : 1));
    L('RESULT', 'status=' + status + ' / 横のつながり ' + laterals.length + ' 件 / ラウンド ' + rounds);

    return {
      ok: true,
      status: status,
      rounds: rounds,
      unknown: { alpha: unk0.alpha.length, beta: unk0.beta.length, zeta: unk0.zeta.length, whitespace: unk0.whitespace },
      laterals: laterals,
      constraints: dedupeConstraints(constraints),
      pruned: pruned,
      log: log,
    };
  }

  function dedupeConstraints(list) {
    const seen = new Set(), out = [];
    for (const c of list) {
      const k = c.from + '|' + c.to + '|' + c.reason + '|' + (c.via || '');
      if (!seen.has(k)) { seen.add(k); out.push(c); }
    }
    return out;
  }

  const api = { awaken: awaken, detectUnknowns: detectUnknowns, prune: prune, pairKey: pairKey, STRONG: STRONG };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.LogicEngine = api;
})(typeof window !== 'undefined' ? window : globalThis);
