/**
 * commit-engine.js — DNA_v3 Step3
 * セッション終了時に5点を judgement_reason / events へ書き込む。
 *
 * better-sqlite3 は Node v25 でビルド不可のため、
 * db_helper.py を child_process.spawnSync で呼び出してDB操作を行う。
 *
 * 使用方法:
 *   node commit-engine.js                        # 対話形式（stdin JSON）
 *   node commit-engine.js --data '{ ... }'       # CLIから直接渡す
 *   const { commitSession } = require('./commit-engine'); // モジュール利用
 */

'use strict';

const { spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const DB_HELPER = path.join(__dirname, 'db_helper.py');
const EVENTS_DB = String.raw`C:\Users\sirok\MoCKA\data\mocka_events.db`;

// ────────────────────────────────────────────────────
// DB ヘルパー呼び出し
// ────────────────────────────────────────────────────
function dbCall(command, argsObj) {
  const result = spawnSync(
    'python',
    [DB_HELPER, command, JSON.stringify(argsObj)],
    { encoding: 'utf-8', timeout: 15000 }
  );
  if (result.error) throw new Error(`db_helper spawn failed: ${result.error.message}`);
  if (result.status !== 0) throw new Error(`db_helper stderr: ${result.stderr}`);
  try {
    return JSON.parse(result.stdout.trim());
  } catch {
    throw new Error(`db_helper parse error: ${result.stdout}`);
  }
}

// ────────────────────────────────────────────────────
// バリデーション
// ────────────────────────────────────────────────────
function validateCommitData(data) {
  const errors = [];
  if (!data.event_id)      errors.push('event_id が必須');
  if (!data.session_date)  errors.push('session_date が必須');
  if (!data.decision)      errors.push('decision が必須 (採用|却下|保留)');
  if (!data.reason)        errors.push('reason が必須 (WHY)');
  if (data.decision === '却下' && !data.rejected_reason) {
    errors.push('decision=却下 のとき rejected_reason が必須');
  }
  const severity = data.tension_severity ?? 0;
  if (severity < 0 || severity > 5) errors.push('tension_severity は 0〜5');
  return errors;
}

// ────────────────────────────────────────────────────
// 5点コミット
// ────────────────────────────────────────────────────
/**
 * @param {object} payload
 *   event_id        string   — events.db の event_id（参照）
 *   session_date    string   — YYYY-MM-DD
 *   decision        string   — '採用' | '却下' | '保留'
 *   reason          string   — なぜその判断か（WHY）
 *   rejected_reason string?  — 却下理由（decision='却下'時必須）
 *   error_solved    string?  — どのエラーをどう潰したか
 *   tension         string?  — 違和感テキスト
 *   tension_severity number? — 0〜5
 *   tension_at      string?  — ISO8601
 *   source_map      string?  — 例: events.db#E20260528_021
 *   tags            string?  — カンマ区切り
 * @returns {{ ok: boolean, id?: number, errors?: string[] }}
 */
function commitSession(payload) {
  const errors = validateCommitData(payload);
  if (errors.length > 0) {
    return { ok: false, errors };
  }

  const row = {
    event_id:         payload.event_id,
    session_date:     payload.session_date,
    decision:         payload.decision,
    rejected_reason:  payload.rejected_reason ?? null,
    reason:           payload.reason,
    error_solved:     payload.error_solved ?? null,
    tension:          payload.tension ?? null,
    tension_severity: payload.tension_severity ?? 0,
    tension_at:       payload.tension_at ?? null,
    source_map:       payload.source_map ?? null,
    tags:             payload.tags ?? null,
  };

  const result = dbCall('write_judgement', row);
  if (result.error) {
    return { ok: false, errors: [result.error] };
  }
  return { ok: true, id: result.id };
}

// ────────────────────────────────────────────────────
// CLI モード
// ────────────────────────────────────────────────────
function runCli() {
  const args = process.argv.slice(2);
  let payload;

  const dataIdx = args.indexOf('--data');
  if (dataIdx !== -1 && args[dataIdx + 1]) {
    try {
      payload = JSON.parse(args[dataIdx + 1]);
    } catch {
      console.error('[ERROR] --data の JSON パースに失敗');
      process.exit(1);
    }
  } else {
    // stdin から読む
    const raw = fs.readFileSync('/dev/stdin', 'utf-8');
    try {
      payload = JSON.parse(raw);
    } catch {
      console.error('[ERROR] stdin JSON パースに失敗');
      process.exit(1);
    }
  }

  const result = commitSession(payload);
  console.log(JSON.stringify(result, null, 2));
  if (!result.ok) process.exit(1);
}

// ────────────────────────────────────────────────────
// エクスポート / エントリポイント
// ────────────────────────────────────────────────────
if (require.main === module) {
  runCli();
} else {
  module.exports = { commitSession, dbCall };
}
