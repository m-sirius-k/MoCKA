/*
 * くろこWEB専用：1stパイプライン仮想Synapseシミュレーター（純粋ロジック）
 *
 * Human Gate -> Authorization -> RuntimeGate -> Consequence -> Memory
 * 実環境（mocka_events.db・正本コード）には一切触れない。すべてメモリ内で完結する。
 * 1回の走査ごとに状態を初期化するため、CP-2（認可 0件 -> 1件）は毎回検証できる。
 */
(function (root) {
  'use strict';

  const APPROVER = 'human_authority';

  // 決定的なハッシュ（FNV-1a 32bit）。シミュレーション用であり、暗号学的ではない
  function fnv1a(str) {
    let h = 0x811c9dc5;
    for (let i = 0; i < str.length; i++) {
      h ^= str.charCodeAt(i);
      h = Math.imul(h, 0x01000193) >>> 0;
    }
    return ('00000000' + h.toString(16)).slice(-8);
  }

  // 仕様書 A の mockHumanEvent と同じ値。overrides で一部だけ差し替えられる
  function makeHumanEvent(overrides) {
    return Object.assign({
      event_id: 'evt_hg_20261016_001',
      approved_by: APPROVER,
      scope: 'pipeline_1st_test',
      decision: 'ALLOW',
      timestamp: '2026-10-16T13:00:00Z',
    }, overrides || {});
  }

  // どの接続（Synapse）で遮断されたかを示すエラー
  class EdgeError extends Error {
    constructor(edge, reason, detail) {
      super(edge + ': ' + reason);
      this.name = 'EdgeError';
      this.edge = edge;
      this.reason = reason;
      this.detail = detail === undefined ? null : detail;
    }
  }

  // Step 1: Human Gate 発火（イベントをそのまま次へ渡す。承認者の検証は Step 2 で行う）
  function triggerHumanGate(event, log) {
    log('STEP1 Human Gate', 'Dispatch Approve Event: ' + event.event_id, { approved_by: event.approved_by });
    return event;
  }

  // Step 2: Authorization 生成（承認者と判定を検証し、認可レコードを1件追加する）
  function generateAuthorization(state, humanEvent, log) {
    if (humanEvent.approved_by !== APPROVER) {
      throw new EdgeError('edge_hg_to_auth', 'UNAUTHORIZED_APPROVER', humanEvent.approved_by);
    }
    if (humanEvent.decision !== 'ALLOW') {
      throw new EdgeError('edge_hg_to_auth', 'DECISION_NOT_ALLOW', humanEvent.decision);
    }
    const auth = {
      auth_id: 'auth_' + String(state.authRecords.length + 1).padStart(3, '0'),
      source_event_id: humanEvent.event_id,
      decision: 'ALLOW',
      scope: humanEvent.scope,
    };
    state.authRecords.push(auth);
    log('STEP2 Authorization', 'Generate Record: ' + auth.auth_id + ' (count ' + state.authRecords.length + ')', auth);
    return auth;
  }

  // Step 3: RuntimeGate 検証（認可レコードを探し、ALLOW なら SUPPORTED）
  // 見つからない・不許可のときは UNSUPPORTED を返す（Typed UNKNOWN：理由コードで区別する）
  function validateRuntimeExecution(state, authId, log) {
    const rec = state.authRecords.find((r) => r.auth_id === authId);
    let out;
    if (!rec) {
      out = { result: 'UNSUPPORTED', reason: 'UNKNOWN_NO_AUTHORIZATION', auth_id: authId, run_id: null, scope: null };
    } else if (rec.decision !== 'ALLOW') {
      out = { result: 'UNSUPPORTED', reason: 'DECISION_NOT_ALLOW', auth_id: authId, run_id: null, scope: rec.scope };
    } else {
      out = { result: 'SUPPORTED', reason: 'OK', auth_id: authId, run_id: 'run_' + authId, scope: rec.scope };
    }
    log('STEP3 RuntimeGate', 'Authorize & Execute Check: ' + out.result + ' (' + out.reason + ')', out);
    return out;
  }

  // Step 4: Consequence 捕捉（実行ステータスと output_hash を付与）
  // 受け取った値をそのまま記録する。整合性の確認は Step 5 で行う
  function captureConsequence(exec, log) {
    const executed = exec.result === 'SUPPORTED';
    const payload = { auth_id: exec.auth_id, run_id: exec.run_id, scope: exec.scope || null };
    const consequence = {
      consequence_id: 'cons_' + (exec.run_id || 'none'),
      status: executed ? 'SUCCESS' : 'NOT_EXECUTED',
      auth_id: exec.auth_id,
      run_id: exec.run_id,
      output_hash: fnv1a(JSON.stringify(payload)),
      payload: payload,
    };
    log('STEP4 Consequence', 'Capture Execution Result: ' + consequence.status, { consequence_id: consequence.consequence_id, output_hash: consequence.output_hash });
    return consequence;
  }

  // Step 5: Memory 永続化（ID の連鎖を検証してから保存する）
  // 連鎖：human_event_id -> auth_id -> run_id -> consequence_id
  function commitToMemory(state, trace, log) {
    const rec = state.authRecords.find((r) => r.auth_id === trace.auth_id);
    if (!rec) throw new EdgeError('edge_auth_to_rt', 'AUTH_MISSING', trace.auth_id);
    if (rec.source_event_id !== trace.human_event_id) {
      throw new EdgeError('edge_hg_to_auth', 'EVENT_ID_MISMATCH', { expected: trace.human_event_id, actual: rec.source_event_id });
    }
    const c = trace.consequence;
    if (c.auth_id !== trace.auth_id) {
      throw new EdgeError('edge_rt_to_cons', 'AUTH_ID_MISMATCH', { expected: trace.auth_id, actual: c.auth_id });
    }
    if (c.run_id !== trace.run_id) {
      throw new EdgeError('edge_rt_to_cons', 'RUN_ID_MISMATCH', { expected: trace.run_id, actual: c.run_id });
    }
    if (c.status !== 'SUCCESS') {
      throw new EdgeError('edge_rt_to_cons', 'NOT_EXECUTED', c.status);
    }
    const entry = {
      human_event_id: trace.human_event_id,
      auth_id: trace.auth_id,
      runtime_status: trace.runtime_status,
      run_id: trace.run_id,
      consequence_id: c.consequence_id,
      output_hash: c.output_hash,
    };
    state.memoryStore.push(entry);
    log('STEP5 Memory', 'Persist Trace Log: ' + entry.human_event_id + ' -> ' + entry.auth_id + ' -> ' + entry.run_id + ' -> ' + entry.consequence_id, entry);
    return entry;
  }

  const CP_DEFS = [
    { id: 'CP-1', label: 'Human Gate: approved_by が human_authority' },
    { id: 'CP-2', label: 'Authorization: 認可レコード 0件 -> 1件' },
    { id: 'CP-3', label: 'RuntimeGate: SUPPORTED が返る' },
    { id: 'CP-4', label: 'Consequence: 結果が SUCCESS で捕捉される' },
    { id: 'CP-5', label: 'Memory: 4つのIDが一連の連鎖として保存される' },
  ];

  // 1回の走査（既定：仕様どおりの正常系）
  // opts: humanEvent（上書き）、skipAuth（Step 2 を飛ばす）、consequenceAuthIdOverride（Step 4 に別の auth_id を渡す）
  function runVirtualPipelineTest(opts) {
    opts = opts || {};
    const log = [];
    const logFn = (step, msg, data) => log.push({ step: step, msg: msg, data: data === undefined ? null : data });
    const state = { authRecords: [], memoryStore: [] };
    const edges = {
      edge_hg_to_auth: 'NOT_REACHED',
      edge_auth_to_rt: 'NOT_REACHED',
      edge_rt_to_cons: 'NOT_REACHED',
      edge_cons_to_mem: 'NOT_REACHED',
    };
    const cps = CP_DEFS.map((d) => ({ id: d.id, label: d.label, pass: false, expected: null, actual: 'NOT_REACHED' }));
    const setCp = (id, pass, expected, actual) => {
      const c = cps.find((x) => x.id === id);
      c.pass = !!pass; c.expected = expected; c.actual = actual;
    };

    const humanEvent = makeHumanEvent(opts.humanEvent);
    const before = state.authRecords.length;
    let broken = null;
    let auth = null, exec = null, consequence = null;

    try {
      // Step 1
      triggerHumanGate(humanEvent, logFn);
      setCp('CP-1', humanEvent.approved_by === APPROVER, APPROVER, humanEvent.approved_by);

      // Step 2
      if (opts.skipAuth) {
        logFn('STEP2 Authorization', 'SKIPPED by test option (Test B)', null);
      } else {
        auth = generateAuthorization(state, humanEvent, logFn);
        edges.edge_hg_to_auth = 'VERIFIED';
      }
      const after = state.authRecords.length;
      setCp('CP-2', before === 0 && after === 1, '0 -> 1', before + ' -> ' + after);

      // Step 3（認可が無ければ RuntimeGate が UNSUPPORTED を返し、Auth->RT で遮断される）
      exec = validateRuntimeExecution(state, auth ? auth.auth_id : null, logFn);
      setCp('CP-3', exec.result === 'SUPPORTED', 'SUPPORTED', exec.result + ' (' + exec.reason + ')');
      if (exec.result !== 'SUPPORTED') {
        throw new EdgeError('edge_auth_to_rt', exec.reason, exec);
      }
      edges.edge_auth_to_rt = 'VERIFIED';

      // Step 4（Test C では別の auth_id を渡す）
      const execForConsequence = opts.consequenceAuthIdOverride
        ? Object.assign({}, exec, { auth_id: opts.consequenceAuthIdOverride })
        : exec;
      consequence = captureConsequence(execForConsequence, logFn);
      setCp('CP-4', consequence.status === 'SUCCESS' && !!consequence.output_hash,
        'SUCCESS + output_hash', consequence.status + ' + ' + (consequence.output_hash || 'none'));

      // Step 5
      const entry = commitToMemory(state, {
        human_event_id: humanEvent.event_id,
        auth_id: exec.auth_id,
        runtime_status: exec.result,
        run_id: exec.run_id,
        consequence: consequence,
      }, logFn);
      edges.edge_rt_to_cons = 'VERIFIED';
      edges.edge_cons_to_mem = 'VERIFIED';
      setCp('CP-5', true, 'all 4 IDs chained', [entry.human_event_id, entry.auth_id, entry.run_id, entry.consequence_id].join(' -> '));
    } catch (err) {
      if (!(err instanceof EdgeError)) throw err;
      edges[err.edge] = 'BROKEN';
      broken = { edge: err.edge, reason: err.reason, detail: err.detail };
      logFn('BLOCKED', '[BLOCKED] ' + err.edge + ': ' + err.reason, err.detail);
      // 遮断された後の CP は NOT_REACHED のまま、CP-5 は未通過として明示する
      if (!cps.find((x) => x.id === 'CP-5').pass) {
        setCp('CP-5', false, 'all 4 IDs chained', 'NOT_REACHED');
      }
    }

    // 3D Mapping 連携用フラグ（画面のエッジ色に使う）
    return {
      ok: broken === null,
      broken: broken,
      edges: edges,
      checkpoints: cps,
      log: log,
      authRecords: state.authRecords.slice(),
      memoryStore: state.memoryStore.slice(),
    };
  }

  // 異常系テスト（仕様書 6）
  function runDebugSuite() {
    return {
      testA_invalidApprover: runVirtualPipelineTest({ humanEvent: { approved_by: 'unknown_user' } }),
      testB_missingAuthorization: runVirtualPipelineTest({ skipAuth: true }),
      testC_idMismatch: runVirtualPipelineTest({ consequenceAuthIdOverride: 'auth_999' }),
    };
  }

  const api = {
    APPROVER: APPROVER,
    fnv1a: fnv1a,
    makeHumanEvent: makeHumanEvent,
    EdgeError: EdgeError,
    runVirtualPipelineTest: runVirtualPipelineTest,
    runDebugSuite: runDebugSuite,
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.SynapseSim = api;
  root.runVirtualPipelineTest = runVirtualPipelineTest;
})(typeof window !== 'undefined' ? window : globalThis);
