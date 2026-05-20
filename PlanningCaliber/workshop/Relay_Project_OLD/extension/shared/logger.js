/**
 * PHI OS — Shared Logger
 * @version 1.0.0
 * @description 全アプリ共通の統一ロガー。diagnosticsパネルへの記録も担う。
 *
 * Purpose  : ログの統一出力・diagnostics連動・silent failure の可視化
 * Must not : chrome.storage への直接書き込み（diagnostics経由のみ）
 */

'use strict';

import { FEATURE } from './constants.js';

// ─── ログレベル ───────────────────────────────────────────────────────────────

export const LOG_LEVEL = Object.freeze({
  DEBUG : 0,
  INFO  : 1,
  WARN  : 2,
  ERROR : 3,
});

// ─── Diagnostics 記録用バッファ ───────────────────────────────────────────────
// background.js 起動前でも使えるよう、メモリバッファに蓄積する

const _diagnosticsBuffer = {
  lastSave      : null,
  lastExport    : null,
  lastSelectorHit : null,
  lastError     : null,
  observerActive : false,
  events        : [],   // 直近50件
};

const _MAX_EVENTS = 50;

function _pushEvent(level, tag, message, detail) {
  _diagnosticsBuffer.events.push({
    level, tag, message, detail,
    ts: new Date().toISOString(),
  });
  if (_diagnosticsBuffer.events.length > _MAX_EVENTS) {
    _diagnosticsBuffer.events.shift();
  }
  if (level >= LOG_LEVEL.ERROR) {
    _diagnosticsBuffer.lastError = { message, detail, ts: new Date().toISOString() };
  }
}

// ─── ロガー実装 ───────────────────────────────────────────────────────────────

class PhiLogger {
  constructor(tag = 'PHI') {
    this._tag       = tag;
    this._minLevel  = LOG_LEVEL.INFO;
    this._debugMode = false;
  }

  /** feature flags から debug モードを設定する */
  setDebug(enabled) {
    this._debugMode = !!enabled;
    this._minLevel  = enabled ? LOG_LEVEL.DEBUG : LOG_LEVEL.INFO;
  }

  debug(message, detail) {
    if (this._minLevel > LOG_LEVEL.DEBUG) return;
    console.debug(`[${this._tag}] ${message}`, detail ?? '');
    _pushEvent(LOG_LEVEL.DEBUG, this._tag, message, detail);
  }

  info(message, detail) {
    if (this._minLevel > LOG_LEVEL.INFO) return;
    console.info(`[${this._tag}] ${message}`, detail ?? '');
    _pushEvent(LOG_LEVEL.INFO, this._tag, message, detail);
  }

  warn(message, detail) {
    console.warn(`[${this._tag}] ⚠ ${message}`, detail ?? '');
    _pushEvent(LOG_LEVEL.WARN, this._tag, message, detail);
  }

  error(message, detail) {
    console.error(`[${this._tag}] ✖ ${message}`, detail ?? '');
    _pushEvent(LOG_LEVEL.ERROR, this._tag, message, detail);
  }

  // Diagnostics 専用記録
  recordSave(detail)        { _diagnosticsBuffer.lastSave         = { ...detail, ts: new Date().toISOString() }; }
  recordExport(detail)      { _diagnosticsBuffer.lastExport       = { ...detail, ts: new Date().toISOString() }; }
  recordSelectorHit(detail) { _diagnosticsBuffer.lastSelectorHit  = { ...detail, ts: new Date().toISOString() }; }
  setObserverActive(v)      { _diagnosticsBuffer.observerActive   = !!v; }

  /** Diagnostics パネル向けスナップショットを返す */
  getDiagnostics() {
    return {
      lastSave        : _diagnosticsBuffer.lastSave,
      lastExport      : _diagnosticsBuffer.lastExport,
      lastSelectorHit : _diagnosticsBuffer.lastSelectorHit,
      lastError       : _diagnosticsBuffer.lastError,
      observerActive  : _diagnosticsBuffer.observerActive,
      recentEvents    : [..._diagnosticsBuffer.events],
    };
  }
}

// ─── シングルトンエクスポート ─────────────────────────────────────────────────

export const logger = new PhiLogger('PHI_OS');

/** アプリごとのタグ付きロガーを作る */
export function createLogger(tag) {
  return new PhiLogger(tag);
}
