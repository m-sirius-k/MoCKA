/**
 * PHI OS — Shared Validators
 * @version 1.0.0
 * @description 保存前検証・クレンジング。壊れたレコードを隔離し全体停止を防ぐ。
 *
 * Purpose  : 保存・共有・export前のデータ検証と修復
 * Owns     : validate* / sanitize* / quarantine*
 * Must not : chrome API・DOM操作・IndexedDB直接操作
 */

'use strict';

import { ARTIFACT_TYPE, STAGE_STATUS, ROLE, ERROR_CODE } from './constants.js';

// ─── 結果型 ───────────────────────────────────────────────────────────────────

/**
 * @typedef {object} ValidationResult
 * @property {boolean}  ok       検証合否
 * @property {string[]} errors   エラーコードリスト
 * @property {string[]} warnings 警告リスト（保存は可能）
 */
const ok      = ()         => ({ ok: true,  errors: [], warnings: [] });
const fail    = (codes)    => ({ ok: false, errors: codes, warnings: [] });
const warn    = (w, base)  => ({ ...base, warnings: [...(base.warnings ?? []), w] });

// ─── Artifact バリデーション ──────────────────────────────────────────────────

/**
 * Artifact を検証する。
 * @param {object} artifact
 * @returns {ValidationResult}
 */
export function validateArtifact(artifact) {
  if (!artifact || typeof artifact !== 'object') return fail([ERROR_CODE.SCHEMA_INVALID]);

  const errors = [];

  // 必須フィールド
  if (!artifact.artifact_id || typeof artifact.artifact_id !== 'string')
    errors.push(ERROR_CODE.SCHEMA_INVALID);

  if (typeof artifact.content !== 'string')
    errors.push(ERROR_CODE.SCHEMA_INVALID);

  if (artifact.content?.length === 0)
    errors.push(ERROR_CODE.CONTENT_TOO_SHORT);

  // artifact_type チェック
  const validTypes = Object.values(ARTIFACT_TYPE);
  if (artifact.artifact_type && !validTypes.includes(artifact.artifact_type))
    errors.push(ERROR_CODE.SCHEMA_INVALID);

  // status チェック
  const validStatuses = Object.values(STAGE_STATUS);
  if (artifact.status && !validStatuses.includes(artifact.status))
    errors.push(ERROR_CODE.SCHEMA_INVALID);

  // role チェック
  const validRoles = Object.values(ROLE);
  if (artifact.role && !validRoles.includes(artifact.role))
    errors.push(ERROR_CODE.SCHEMA_INVALID);

  if (errors.length > 0) return fail(errors);

  let result = ok();

  // 警告: content が短すぎる
  if (artifact.content.length < 10)
    result = warn('content_very_short', result);

  // 警告: session_id が空
  if (!artifact.session_id)
    result = warn('session_id_missing', result);

  // 警告: タグが配列でない
  if (artifact.tags && !Array.isArray(artifact.tags))
    result = warn('tags_not_array', result);

  return result;
}

// ─── Session バリデーション ───────────────────────────────────────────────────

export function validateSession(session) {
  if (!session || typeof session !== 'object') return fail([ERROR_CODE.SCHEMA_INVALID]);

  const errors = [];
  if (!session.session_id) errors.push(ERROR_CODE.SCHEMA_INVALID);
  if (!session.started_at) errors.push(ERROR_CODE.SCHEMA_INVALID);

  return errors.length ? fail(errors) : ok();
}

// ─── サニタイズ ───────────────────────────────────────────────────────────────

/**
 * Artifact の content を安全な文字列に正規化する。
 * - null/undefined → ''
 * - 異常に長い文字列をトリム
 * - NUL文字除去
 */
export function sanitizeContent(content, maxLen = 100_000) {
  if (content == null) return '';
  let s = String(content);
  s = s.replace(/\u0000/g, '');              // NUL 除去
  s = s.replace(/\uFEFF/g, '');             // BOM 除去
  if (s.length > maxLen) s = s.slice(0, maxLen) + '…[truncated]';
  return s;
}

/**
 * タグ配列をクレンジングする。
 * - 文字列以外を除去
 * - 空文字を除去
 * - 重複を除去
 * - 最大20件
 */
export function sanitizeTags(tags) {
  if (!Array.isArray(tags)) return [];
  return [...new Set(
    tags
      .filter(t => typeof t === 'string' && t.trim().length > 0)
      .map(t => t.trim().toLowerCase().slice(0, 50))
  )].slice(0, 20);
}

// ─── 重複検出 ─────────────────────────────────────────────────────────────────

/**
 * 既存IDセットと照合して重複を検出する。
 * @param {string}     artifactId
 * @param {Set<string>} existingIds
 * @returns {boolean} true = 重複あり
 */
export function isDuplicate(artifactId, existingIds) {
  return existingIds instanceof Set && existingIds.has(artifactId);
}

// ─── エラー隔離 ───────────────────────────────────────────────────────────────

/**
 * 壊れたレコードを隔離オブジェクトに変換する。
 * これにより全体停止を防ぐ。
 * @param {*}             rawData   元データ
 * @param {string[]}      errors    エラーコードリスト
 * @returns {QuarantinedRecord}
 */
export function quarantineRecord(rawData, errors = []) {
  return Object.freeze({
    quarantine_id   : `q_${Date.now().toString(36)}`,
    original_data   : rawData,
    error_codes     : errors,
    quarantined_at  : new Date().toISOString(),
    recoverable     : errors.every(e => e !== ERROR_CODE.SCHEMA_INVALID),
  });
}

// ─── Export 検証 ──────────────────────────────────────────────────────────────

export function validateExportJob(job) {
  if (!job || typeof job !== 'object')   return fail([ERROR_CODE.SCHEMA_INVALID]);
  if (!job.export_id)                    return fail([ERROR_CODE.SCHEMA_INVALID]);
  if (!['json','csv','markdown'].includes(job.format)) return fail([ERROR_CODE.EXPORT_FAIL]);
  if (!['raw','normalized','share-ready'].includes(job.profile)) return fail([ERROR_CODE.EXPORT_FAIL]);
  return ok();
}
