/**
 * PHI OS — Shared Schema
 * @version 1.0.0
 * @description 全アプリ共通のデータモデル定義とファクトリ関数。
 *
 * Purpose  : Artifact / Session / Workspace / ExportJob の生成・正規化
 * Owns     : createArtifact / createSession / createWorkspace / normalizeArtifact
 * Must not : DOM操作・chrome API・副作用を持たない。純粋関数のみ。
 */

'use strict';

import {
  PHI_OS_VERSION, SCHEMA_VERSION,
  ARTIFACT_TYPE, STAGE_STATUS, ROLE,
  SOURCE_APP, SOURCE_SERVICE,
} from './constants.js';

// ─── ID生成 ───────────────────────────────────────────────────────────────────

const _genId = (prefix = 'phi') => {
  const ts  = Date.now().toString(36);
  const rnd = Math.random().toString(36).slice(2, 7);
  return `${prefix}_${ts}${rnd}`;
};

// ─── タイムスタンプ ───────────────────────────────────────────────────────────

const _now = () => new Date().toISOString();

// ─── Artifact ─────────────────────────────────────────────────────────────────

/**
 * Artifact を生成する。
 * @param {object} params
 * @param {string} params.content         本文
 * @param {string} [params.role]          user / assistant / system
 * @param {string} [params.artifactType]  ARTIFACT_TYPE のいずれか
 * @param {string} [params.sessionId]     所属セッションID
 * @param {string} [params.workspaceId]   所属ワークスペースID
 * @param {string} [params.sourceApp]     SOURCE_APP のいずれか
 * @param {string[]} [params.tags]        タグ配列
 * @returns {PhiArtifact}
 */
export function createArtifact({
  content       = '',
  role          = ROLE.USER,
  artifactType  = ARTIFACT_TYPE.MESSAGE,
  sessionId     = '',
  workspaceId   = '',
  sourceApp     = SOURCE_APP.ORCHESTRA,
  sourceService = SOURCE_SERVICE.CLAUDE_AI,
  tags          = [],
} = {}) {
  const now = _now();
  return Object.freeze({
    phi_os_version : PHI_OS_VERSION,
    schema_version : SCHEMA_VERSION,
    artifact_id    : _genId('art'),
    artifact_type  : artifactType,
    session_id     : sessionId,
    workspace_id   : workspaceId,
    source: Object.freeze({
      app     : sourceApp,
      service : sourceService,
    }),
    role,
    content,
    tags          : [...tags],
    status        : STAGE_STATUS.DRAFT,
    created_at    : now,
    updated_at    : now,
    hash          : _hashContent(content),
  });
}

/**
 * 既存オブジェクトを PHI OS Artifact に正規化する。
 * 足りないフィールドをデフォルト値で補完する。
 */
export function normalizeArtifact(raw = {}) {
  if (!raw || typeof raw !== 'object') return null;

  const now = _now();
  const content = String(raw.content ?? raw.text ?? raw.message ?? '');

  return {
    phi_os_version : raw.phi_os_version ?? PHI_OS_VERSION,
    schema_version : raw.schema_version ?? SCHEMA_VERSION,
    artifact_id    : raw.artifact_id ?? raw.id ?? raw.messageId ?? _genId('art'),
    artifact_type  : raw.artifact_type ?? ARTIFACT_TYPE.MESSAGE,
    session_id     : raw.session_id ?? raw.sessionId ?? '',
    workspace_id   : raw.workspace_id ?? raw.workspaceId ?? '',
    source: {
      app     : raw.source?.app     ?? raw.app     ?? SOURCE_APP.ORCHESTRA,
      service : raw.source?.service ?? raw.service ?? SOURCE_SERVICE.CLAUDE_AI,
    },
    role       : raw.role ?? ROLE.USER,
    content,
    tags       : Array.isArray(raw.tags) ? [...raw.tags] : [],
    status     : raw.status ?? STAGE_STATUS.DRAFT,
    created_at : raw.created_at ?? raw.timestamp ?? raw.when ?? now,
    updated_at : raw.updated_at ?? now,
    hash       : raw.hash ?? _hashContent(content),
  };
}

// ─── Session ──────────────────────────────────────────────────────────────────

/**
 * Session を生成する。
 * @param {object} params
 */
export function createSession({
  workspaceId  = '',
  sourceApp    = SOURCE_APP.ORCHESTRA,
  title        = '',
  url          = '',
  tags         = [],
} = {}) {
  const now = _now();
  return Object.freeze({
    phi_os_version : PHI_OS_VERSION,
    schema_version : SCHEMA_VERSION,
    session_id     : _genId('sess'),
    workspace_id   : workspaceId,
    source: Object.freeze({
      app     : sourceApp,
      service : SOURCE_SERVICE.CLAUDE_AI,
    }),
    title,
    url,
    tags           : [...tags],
    status         : STAGE_STATUS.DRAFT,
    artifact_count : 0,
    started_at     : now,
    updated_at     : now,
    ended_at       : null,
    shared_at      : null,
  });
}

/**
 * Session の ended_at を確定する。
 */
export function finalizeSession(session) {
  if (!session) return null;
  return { ...session, ended_at: _now(), updated_at: _now() };
}

// ─── Workspace ────────────────────────────────────────────────────────────────

/**
 * Workspace を生成する。
 * 案件・プロジェクト・顧客をworkspace_idで分ける。
 */
export function createWorkspace({
  name        = 'default',
  description = '',
  tags        = [],
} = {}) {
  const now = _now();
  return Object.freeze({
    phi_os_version : PHI_OS_VERSION,
    workspace_id   : _genId('ws'),
    name,
    description,
    tags           : [...tags],
    status         : STAGE_STATUS.DRAFT,
    created_at     : now,
    updated_at     : now,
  });
}

// ─── ExportJob ────────────────────────────────────────────────────────────────

/**
 * ExportJob を生成する。
 * @param {'raw'|'normalized'|'share-ready'} profile
 * @param {'json'|'csv'|'markdown'}          format
 */
export function createExportJob({
  profile     = 'normalized',
  format      = 'json',
  sessionIds  = [],
  workspaceId = '',
  filters     = {},
} = {}) {
  const now = _now();
  return Object.freeze({
    phi_os_version : PHI_OS_VERSION,
    export_id      : _genId('exp'),
    profile,
    format,
    session_ids    : [...sessionIds],
    workspace_id   : workspaceId,
    filters        : { ...filters },
    status         : 'pending',
    created_at     : now,
    completed_at   : null,
    error          : null,
  });
}

// ─── AuditLog Entry ───────────────────────────────────────────────────────────

/**
 * AuditLog エントリを生成する。
 */
export function createAuditEntry({
  action      = '',   // 'save' | 'share' | 'export' | 'archive' | 'delete'
  artifactId  = '',
  sessionId   = '',
  actor       = 'user',
  detail      = {},
} = {}) {
  return Object.freeze({
    audit_id   : _genId('aud'),
    action,
    artifact_id : artifactId,
    session_id  : sessionId,
    actor,
    detail      : { ...detail },
    occurred_at : _now(),
  });
}

// ─── Share-ready フィルタ ─────────────────────────────────────────────────────

/**
 * 内部フィールドを除去した共有用オブジェクトを返す。
 */
export function toShareReady(artifact) {
  if (!artifact) return null;
  const { hash, schema_version, phi_os_version, ...rest } = artifact;
  return rest;
}

// ─── バリデーション用ヘルパー ─────────────────────────────────────────────────

export function isValidArtifact(obj) {
  return (
    obj != null &&
    typeof obj === 'object' &&
    typeof obj.artifact_id  === 'string' && obj.artifact_id.length > 0 &&
    typeof obj.content      === 'string' &&
    typeof obj.session_id   === 'string' &&
    typeof obj.created_at   === 'string'
  );
}

export function isValidSession(obj) {
  return (
    obj != null &&
    typeof obj === 'object' &&
    typeof obj.session_id  === 'string' && obj.session_id.length > 0 &&
    typeof obj.started_at  === 'string'
  );
}

// ─── プライベート: コンテンツハッシュ ────────────────────────────────────────
// 軽量な非暗号学的ハッシュ（重複検出用）

function _hashContent(str = '') {
  let h = 0x811c9dc5;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = (h * 0x01000193) >>> 0;
  }
  return h.toString(16).padStart(8, '0');
}
