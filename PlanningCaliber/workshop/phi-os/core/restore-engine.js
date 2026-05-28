/**
 * restore-engine.js — DNA_v3 Step4
 * 4層 (Fact/State/Causality/Intent) から関連データを検索・圧縮し
 * restore_packet.json を生成する。
 *
 * 出力先: C:\Users\sirok\MoCKA\data\storage\infield\PACKET\restore_packet.json
 *
 * 疑念004 解決: max_chars=3000。trimToMaxChars()で超過時にトリム。
 * 疑念002 解決: CommitトリガーはRelay引き継ぎボタン。
 */
/*
 * IMMUTABLE層への書き込みは禁止。
 * Decay/Promotionの最終昇格はきむら博士のHuman Gate承認後のみ実施。
 * このエンジンはREAD ONLYでIMMUTABLE層を参照する。
 */

'use strict';

const { spawnSync } = require('child_process');
const path  = require('path');
const fs    = require('fs');

const DB_HELPER   = path.join(__dirname, 'db_helper.py');
const PACKET_OUT  = String.raw`C:\Users\sirok\MoCKA\data\storage\infield\PACKET\restore_packet.json`;

// ────────────────────────────────────────────────────
// DB ヘルパー呼び出し（commit-engine と共有）
// ────────────────────────────────────────────────────
function dbCall(command, argsObj) {
  const result = spawnSync(
    'python',
    [DB_HELPER, command, JSON.stringify(argsObj)],
    { encoding: 'utf-8', timeout: 20000 }
  );
  if (result.error) throw new Error(`db_helper spawn failed: ${result.error.message}`);
  if (result.status !== 0) throw new Error(`db_helper stderr: ${result.stderr}`);
  return JSON.parse(result.stdout.trim());
}

// ────────────────────────────────────────────────────
// 文字数制限（疑念004 解決: max_chars=3000 確定）
// ────────────────────────────────────────────────────
const RESTORE_PACKET_MAX_CHARS = 3000;

function trunc(str, max) {
  if (!str) return '';
  return str.length > max ? str.slice(0, max) + '…' : str;
}

function trimToMaxChars(packet) {
  let text = JSON.stringify(packet, null, 2);
  if (text.length <= RESTORE_PACKET_MAX_CHARS) return packet;

  const r = packet.restore_5points;

  // トリム優先順位: active_work → decisions → tensions → IMMUTABLEは削除しない
  if (text.length > RESTORE_PACKET_MAX_CHARS && r['3_active_work']) {
    r['3_active_work'] = r['3_active_work'].substring(0, 100) + '...（省略）';
    text = JSON.stringify(packet, null, 2);
  }
  if (text.length > RESTORE_PACKET_MAX_CHARS && r['5_recent_decisions']) {
    r['5_recent_decisions'] = r['5_recent_decisions'].slice(0, 2);
    text = JSON.stringify(packet, null, 2);
  }
  if (text.length > RESTORE_PACKET_MAX_CHARS && r['4_tensions']) {
    r['4_tensions'] = r['4_tensions'].slice(0, 2);
  }
  // IMMUTABLE層は削除しない
  return packet;
}

// ────────────────────────────────────────────────────
// Restore Packet 生成
// ────────────────────────────────────────────────────
/**
 * @param {object} opts
 *   session_context  string  — 今日の作業テーマキーワード（30文字以内）
 *   limit_tensions   number  — 取得する tension 件数（default: 5）
 *   limit_decisions  number  — 取得する decisions 件数（default: 5）
 * @returns {object} restore_packet
 */
function generateRestorePacket(opts = {}) {
  const {
    session_context  = '未設定',
    limit_tensions   = 5,
    limit_decisions  = 5,
  } = opts;

  // 4層データを一括取得
  const raw = dbCall('read_restore_data', { limit_tensions, limit_decisions });

  // ── IMMUTABLE 層（先頭固定）──
  const immutable = raw.immutable || {
    philosophy: ['できないのはやらないからだ', '記録なき作業はMoCKAとして存在しない', 'AIを信じるな、システムで縛れ'],
    forbidden:  ['PowerShell環境でPythonコードを直接実行させない', 'PHL記録なき変更を行わない'],
    values:     ['違和感は次の発明のシード', '失敗は資産になる', '判断根拠を必ず残す'],
  };

  // ── 5点: 1_personality ──
  const personality = trunc(raw.philosophy_summary || '', 200);

  // ── 5点: 2_current_goal ──
  const currentGoal = (raw.active_todos || [])
    .filter(t => t.priority === '最高' || t.priority === '高')
    .slice(0, 3)
    .map(t => ({ todo_id: t.todo_id, title: t.title, priority: t.priority }));

  // ── 5点: 3_active_work（直近イベント要約） ──
  const activeWork = (raw.recent_events || [])
    .slice(0, 6)
    .map(e => `[${e.what_type}] ${trunc(e.title, 40)} (${(e.when_ts || '').slice(0, 10)})`)
    .join(' / ');

  // ── 5点: 4_tensions ──
  const tensions = (raw.active_tensions || []).map(t => ({
    text:       trunc(t.tension, 100),
    severity:   t.tension_severity,
    tension_at: t.tension_at || null,
    tags:       t.tags || '',
    source_map: t.source_map || null,
  }));

  // ── 5点: 5_recent_decisions ──
  const decisions = (raw.recent_decisions || []).map(d => ({
    decision:        d.decision,
    reason:          trunc(d.reason, 80),
    rejected_reason: d.rejected_reason ? trunc(d.rejected_reason, 60) : null,
    error_solved:    d.error_solved ? trunc(d.error_solved, 60) : null,
    source_map:      d.source_map || null,
  }));

  const packet = {
    $schema:         'DNA_v3_restore_packet_v1.0',
    version:         '3.0',
    generated_at:    new Date().toISOString(),
    session_context: trunc(session_context, 30),
    immutable,
    restore_5points: {
      '1_personality':       personality,
      '2_current_goal':      currentGoal,
      '3_active_work':       trunc(activeWork, 300),
      '4_tensions':          tensions,
      '5_recent_decisions':  decisions,
    },
  };

  return trimToMaxChars(packet);
}

// ────────────────────────────────────────────────────
// パケット保存
// ────────────────────────────────────────────────────
function savePacket(packet) {
  const dir = path.dirname(PACKET_OUT);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(PACKET_OUT, JSON.stringify(packet, null, 2), 'utf-8');
  return PACKET_OUT;
}

// ────────────────────────────────────────────────────
// CLI モード
// ────────────────────────────────────────────────────
function runCli() {
  const args = process.argv.slice(2);
  const ctxIdx = args.indexOf('--context');
  const sessionContext = (ctxIdx !== -1 && args[ctxIdx + 1])
    ? args[ctxIdx + 1]
    : '手動実行';

  console.error(`[restore-engine] session_context="${sessionContext}" でパケット生成中...`);

  let packet;
  try {
    packet = generateRestorePacket({ session_context: sessionContext });
  } catch (err) {
    console.error('[restore-engine] データ取得失敗 — v2フォールバックへ');
    console.error(err.message);
    process.exit(1);
  }

  const outPath = savePacket(packet);
  console.error(`[restore-engine] 保存完了: ${outPath}`);

  // stdout にパケット JSON を出力（サーバーからの呼び出し用）
  console.log(JSON.stringify(packet, null, 2));
}

// ────────────────────────────────────────────────────
// エクスポート / エントリポイント
// ────────────────────────────────────────────────────
if (require.main === module) {
  runCli();
} else {
  module.exports = { generateRestorePacket, savePacket, dbCall };
}
