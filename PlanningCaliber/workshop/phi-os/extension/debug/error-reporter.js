// error-reporter.js — 未処理エラーの自動収集
'use strict';

const MAX_ERRORS = 100;
const STORAGE_KEY = 'phi_error_log';

/**
 * エラーをchrome.storage.localに保存する
 * @param {object} err
 */
export async function reportError(err) {
  try {
    const stored = await chrome.storage.local.get(STORAGE_KEY);
    const log = stored[STORAGE_KEY] || [];
    log.unshift(err);
    if (log.length > MAX_ERRORS) log.pop();
    await chrome.storage.local.set({ [STORAGE_KEY]: log });
  } catch (e) {
    // storage自体が壊れている場合は諦める
  }
  console.error('[PHI OS Error]', err);
}

/**
 * グローバルエラーハンドラーを登録する
 * content.js / options.js の先頭で呼び出す
 */
export function installGlobalHandlers() {
  window.addEventListener('unhandledrejection', (event) => {
    reportError({
      type:    'UNHANDLED_REJECTION',
      message: event.reason?.message || String(event.reason),
      stack:   event.reason?.stack   || null,
      ts:      Date.now(),
      url:     location.href,
    });
  });

  window.addEventListener('error', (event) => {
    // ResizeObserver loop は無害なブラウザ仕様ノイズのため除外
    if (event.message?.includes('ResizeObserver loop')) return;
    reportError({
      type:    'RUNTIME_ERROR',
      message: event.message,
      stack:   event.error?.stack || null,
      ts:      Date.now(),
      url:     location.href,
      line:    event.lineno,
      col:     event.colno,
    });
  });
}

/**
 * エラーログを取得する（デバッグパネル用）
 * @returns {Promise<Array>}
 */
export async function getErrorLog() {
  try {
    const stored = await chrome.storage.local.get(STORAGE_KEY);
    return stored[STORAGE_KEY] || [];
  } catch (e) {
    return [];
  }
}

/**
 * エラーログをクリアする
 */
export async function clearErrorLog() {
  try {
    await chrome.storage.local.set({ [STORAGE_KEY]: [] });
  } catch (e) {
    // ignore
  }
}
