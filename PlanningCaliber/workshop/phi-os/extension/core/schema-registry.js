// schema-registry.js — データ構造定義・バージョン管理（TODO_187）
'use strict';

export const SCHEMA_VERSION  = '1.0.0';
export const PHI_OS_VERSION  = '1.0.0';

// artifact_type 一覧（PHI OS 共通）
export const ARTIFACT_TYPES = ['message', 'decision', 'todo', 'note', 'export', 'share'];

// artifact stage 一覧
export const ARTIFACT_STAGES = ['draft', 'reviewed', 'shared', 'archived'];

export const SCHEMAS = {
  commit: {
    commit_id:      'string',
    trigger:        'string',   // UNLOAD|VISIBILITY|TURN_THRESHOLD|IDLE|MANUAL
    ts:             'number',
    facts:          'array',    // ファイルパス等
    decisions:      'array',    // 決定事項
    todos:          'array',    // 未完了タスク
    tensions:       'array',    // 違和感 { text, tag }
    next_hook:      'object',   // { last_file, last_decision, pending_todos[] }
    phi_os_version: 'string',
  },
  session: {
    session_id:       'string',
    started_at:       'number',
    ended_at:         'number',
    turn_count:       'number',
    estimated_tokens: 'number',
    phi_os_version:   'string',
  },
  artifact: {
    artifact_id:    'string',
    artifact_type:  'string',   // message|decision|todo|note|export|share
    stage:          'string',   // draft|reviewed|shared|archived
    product:        'string',   // relay|orchestra|memory|...
    content:        'string',
    ts:             'number',
    phi_os_version: 'string',
  },
};

// バージョン migration テーブル（v1→v2 対応準備）
export const MIGRATIONS = {
  '1.0.0': null,   // 初版 — migration 不要
  // '1.1.0': migrateV1toV1_1,
  // '2.0.0': migrateV1toV2,
};

export async function ensureSchemaVersion() {
  try {
    const stored = await chrome.storage.local.get(['phi_schema_version', 'phi_os_version']);
    if (stored.phi_schema_version !== SCHEMA_VERSION) {
      await _runMigrations(stored.phi_schema_version);
      await chrome.storage.local.set({
        phi_schema_version: SCHEMA_VERSION,
        phi_os_version:     PHI_OS_VERSION,
      });
    }
  } catch (e) {
    // graceful — non-critical
  }
}

async function _runMigrations(fromVersion) {
  // 将来のバージョン間 migration をここで実行する
  // 現在は v1.0.0 のみのため migration なし
}

/**
 * 与えられたオブジェクトがスキーマに準拠しているか簡易チェック
 * @param {string} schemaName
 * @param {object} obj
 * @returns {boolean}
 */
export function validate(schemaName, obj) {
  const schema = SCHEMAS[schemaName];
  if (!schema) return false;
  for (const [key, type] of Object.entries(schema)) {
    if (!(key in obj)) return false;
    if (type === 'array'  && !Array.isArray(obj[key])) return false;
    if (type === 'object' && (typeof obj[key] !== 'object' || Array.isArray(obj[key]))) return false;
    if (type === 'string' && typeof obj[key] !== 'string') return false;
    if (type === 'number' && typeof obj[key] !== 'number') return false;
  }
  return true;
}
