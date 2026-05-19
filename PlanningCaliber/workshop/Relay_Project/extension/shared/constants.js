/**
 * PHI OS — Shared Constants
 * @version 1.0.0
 * @description 全アプリ（Relay/Orchestra）共通定数。変更時はスキーマバージョンを上げること。
 *
 * Purpose  : 全アプリで参照する定数の唯一の真実源
 * Must not : ここに関数・状態・副作用を置かない
 */

'use strict';

// ─── バージョン ──────────────────────────────────────────────────────────────

export const PHI_OS_VERSION = '1.0.0';
export const SCHEMA_VERSION = 1;

// ─── Artifact Type ───────────────────────────────────────────────────────────

export const ARTIFACT_TYPE = Object.freeze({
  MESSAGE   : 'message',
  DECISION  : 'decision',
  TODO      : 'todo',
  NOTE      : 'note',
  EXPORT    : 'export',
  SHARE     : 'share',
  SESSION   : 'session',
});

// ─── Stage Status ─────────────────────────────────────────────────────────────

export const STAGE_STATUS = Object.freeze({
  DRAFT    : 'draft',
  REVIEWED : 'reviewed',
  SHARED   : 'shared',
  ARCHIVED : 'archived',
});

// ─── Role ─────────────────────────────────────────────────────────────────────

export const ROLE = Object.freeze({
  USER      : 'user',
  ASSISTANT : 'assistant',
  SYSTEM    : 'system',
});

// ─── Source App ───────────────────────────────────────────────────────────────

export const SOURCE_APP = Object.freeze({
  RELAY      : 'Relay',
  ORCHESTRA  : 'Orchestra',
  PRISM      : 'Prism',
});

export const SOURCE_SERVICE = Object.freeze({
  CLAUDE_AI  : 'claude.ai',
});

// ─── Export Profile ───────────────────────────────────────────────────────────

export const EXPORT_PROFILE = Object.freeze({
  RAW         : 'raw',          // 取得そのまま
  NORMALIZED  : 'normalized',   // PHI OS schema 準拠
  SHARE_READY : 'share-ready',  // 内部フィールド除去済み
});

// ─── Feature Flags ────────────────────────────────────────────────────────────

export const FEATURE = Object.freeze({
  SHARE       : 'share',
  EXPORT      : 'export',
  VAULT       : 'vault',
  DEBUG       : 'debug',
  BUILTIN_AI  : 'builtin_ai',
  DIAGNOSTICS : 'diagnostics',
});

// ─── Storage Keys ─────────────────────────────────────────────────────────────

export const STORAGE_KEY = Object.freeze({
  SESSIONS          : 'phi_sessions',
  ARTIFACTS         : 'phi_artifacts',
  WORKSPACES        : 'phi_workspaces',
  EXPORT_JOBS       : 'phi_export_jobs',
  AUDIT_LOG         : 'phi_audit_log',
  ERROR_QUARANTINE  : 'phi_error_quarantine',
  FEATURE_FLAGS     : 'phi_feature_flags',
  SCHEMA_VERSION    : 'phi_schema_version',
});

// ─── IndexedDB ────────────────────────────────────────────────────────────────

export const DB_NAME    = 'phi_os_db';
export const DB_VERSION = 1;

export const DB_STORE = Object.freeze({
  ARTIFACTS        : 'artifacts',
  SESSIONS         : 'sessions',
  AUDIT_LOG        : 'audit_log',
  ERROR_QUARANTINE : 'error_quarantine',
});

// ─── メッセージプロトコル ─────────────────────────────────────────────────────

export const MSG = Object.freeze({
  // PHI OS 共通
  PHI_SAVE_ARTIFACT   : 'PHI/SAVE_ARTIFACT',
  PHI_GET_ARTIFACTS   : 'PHI/GET_ARTIFACTS',
  PHI_EXPORT          : 'PHI/EXPORT',
  PHI_DIAGNOSTICS_GET : 'PHI/DIAGNOSTICS_GET',
  PHI_SCHEMA_MIGRATE  : 'PHI/SCHEMA_MIGRATE',

  // Relay 固有
  RELAY_SESSION_SAVE  : 'RELAY/SESSION_SAVE',
  RELAY_TODO_LIST     : 'RELAY/TODO_LIST',
  RELAY_TODO_ADD      : 'RELAY/TODO_ADD',
  RELAY_TODO_ARCHIVE  : 'RELAY/TODO_ARCHIVE',
  RELAY_HANDOFF       : 'RELAY/HANDOFF_TRIGGER',
  RELAY_OPEN_NEW_CHAT : 'RELAY/OPEN_NEW_CHAT',

  // Orchestra 固有
  ORCH_SAVE_MESSAGE   : 'ORCH/SAVE_MESSAGE',
  ORCH_SEARCH         : 'ORCH/SEARCH',
  ORCH_EXPORT         : 'ORCH/EXPORT',
  ORCH_SHARE          : 'ORCH/SHARE',
});

// ─── エラーコード ─────────────────────────────────────────────────────────────

export const ERROR_CODE = Object.freeze({
  SCHEMA_INVALID      : 'E001',
  DUPLICATE_ID        : 'E002',
  STORAGE_WRITE_FAIL  : 'E003',
  STORAGE_READ_FAIL   : 'E004',
  EXPORT_FAIL         : 'E005',
  SHARE_FAIL          : 'E006',
  MIGRATION_FAIL      : 'E007',
  SELECTOR_MISS       : 'E008',
  OBSERVER_DUPLICATE  : 'E009',
  CONTENT_TOO_SHORT   : 'E010',
});

// ─── Selector Registry ────────────────────────────────────────────────────────
// claude.ai DOM変化に備えてセレクタを集中管理
// confidence: high=安定 / medium=要監視 / low=フォールバック

export const SELECTORS = Object.freeze({
  assistantMessage: [
    { sel: '.font-claude-message',               confidence: 'high',   updated: '2026-05-19' },
    { sel: '[data-testid="assistant-message"]',  confidence: 'medium', updated: '2026-05-19' },
    { sel: '.font-claude-response',              confidence: 'low',    updated: '2026-05-19' },
  ],
  userMessage: [
    { sel: '[data-testid="user-message"]',       confidence: 'high',   updated: '2026-05-19' },
    { sel: '.font-user-message',                 confidence: 'medium', updated: '2026-05-19' },
  ],
  inputBox: [
    { sel: 'div[contenteditable="true"][data-placeholder]', confidence: 'high',   updated: '2026-05-19' },
    { sel: 'div[contenteditable="true"].ProseMirror',       confidence: 'medium', updated: '2026-05-19' },
    { sel: 'textarea',                                       confidence: 'low',    updated: '2026-05-19' },
  ],
  sendButton: [
    { sel: 'button[aria-label="Send message"]',  confidence: 'high',   updated: '2026-05-19' },
    { sel: 'button[type="submit"]',              confidence: 'low',    updated: '2026-05-19' },
  ],
  newChatLink: [
    { sel: 'a[href="/new"]',                     confidence: 'high',   updated: '2026-05-19' },
  ],
});

// ─── Stream Stability ─────────────────────────────────────────────────────────

export const STREAM = Object.freeze({
  IDLE_MS         : 1200,   // この時間テキスト変化なし → 安定と判定
  MIN_LENGTH      : 30,     // この文字数未満は処理しない
  DEBOUNCE_MS     : 300,    // MutationObserver の間引き間隔
});
