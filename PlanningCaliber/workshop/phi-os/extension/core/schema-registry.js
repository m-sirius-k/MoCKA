// schema-registry.js — データ構造定義・バージョン管理
'use strict';

export const SCHEMA_VERSION = '1.0.0';

export const SCHEMAS = {
  commit: {
    commit_id:  'string',
    trigger:    'string',   // UNLOAD|VISIBILITY|TURN_THRESHOLD|IDLE|MANUAL
    ts:         'number',
    facts:      'array',    // ファイルパス等
    decisions:  'array',    // 決定事項
    todos:      'array',    // 未完了タスク
    tensions:   'array',    // 違和感 { text, tag }
    next_hook:  'object',   // { last_file, last_decision, pending_todos[] }
  },
  session: {
    session_id:       'string',
    started_at:       'number',
    ended_at:         'number',
    turn_count:       'number',
    estimated_tokens: 'number',
  },
};

export async function ensureSchemaVersion() {
  try {
    const { phi_schema_version } = await chrome.storage.local.get('phi_schema_version');
    if (phi_schema_version !== SCHEMA_VERSION) {
      await chrome.storage.local.set({ phi_schema_version: SCHEMA_VERSION });
    }
  } catch (e) {
    // graceful — non-critical
  }
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
