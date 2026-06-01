// permission-manager.js — 拡張ID管理・認証・権限レベル管理（TODO_187）
// chrome.runtime.id を動的に使用し、ハードコードを排除する
'use strict';

import { get, set } from './state-store.js';
import { reportError } from '../debug/error-reporter.js';

const KNOWN_PRODUCTS = ['relay', 'orchestra', 'memory', 'prism', 'vault'];

// 権限レベル: read のみ < read/write < 全操作
export const PERMISSION_LEVELS = Object.freeze({
  read:  'read',
  write: 'write',
  admin: 'admin',
});

// 製品ごとのデフォルト権限
const DEFAULT_PERMISSIONS = {
  relay:    PERMISSION_LEVELS.write,
  orchestra: PERMISSION_LEVELS.write,
  memory:   PERMISSION_LEVELS.write,
  prism:    PERMISSION_LEVELS.read,
  vault:    PERMISSION_LEVELS.read,
};

/**
 * 自身のExtension IDを取得する
 * @returns {string}
 */
export function getSelfId() {
  return chrome.runtime.id;
}

/**
 * 製品のExtension IDを登録する
 * 各製品は起動時に自己申告でIDを登録する
 * @param {string} productName
 * @param {string} extensionId
 */
export async function registerProduct(productName, extensionId) {
  if (!KNOWN_PRODUCTS.includes(productName)) return;
  await set(`phi_product_id_${productName}`, extensionId);
  console.log('[PHI OS PermissionManager] Registered:', productName, extensionId);
}

/**
 * 登録済み製品のExtension IDを取得する
 * @param {string} productName
 * @returns {Promise<string|null>}
 */
export async function getProductId(productName) {
  return get(`phi_product_id_${productName}`, null);
}

/**
 * 全登録済み製品の情報を返す
 * @returns {Promise<object>}
 */
export async function getAllProducts() {
  const result = {};
  for (const name of KNOWN_PRODUCTS) {
    result[name] = await getProductId(name);
  }
  return result;
}

// ─── 権限レベル管理 ──────────────────────────────────────────────────────────

/**
 * 製品の権限レベルを設定する（admin のみが他製品の権限を変更できる）
 * @param {string} productName
 * @param {string} level  'read' | 'write' | 'admin'
 */
export async function setPermissionLevel(productName, level) {
  if (!KNOWN_PRODUCTS.includes(productName)) return;
  if (!Object.values(PERMISSION_LEVELS).includes(level)) return;
  await set(`phi_permission_${productName}`, level);
}

/**
 * 製品の現在の権限レベルを返す
 * @param {string} productName
 * @returns {Promise<string>}
 */
export async function getPermissionLevel(productName) {
  return get(`phi_permission_${productName}`, DEFAULT_PERMISSIONS[productName] ?? PERMISSION_LEVELS.read);
}

/**
 * 操作が許可されているか確認する
 * @param {string} productName
 * @param {'read'|'write'|'admin'} requiredLevel
 * @returns {Promise<boolean>}
 */
export async function hasPermission(productName, requiredLevel) {
  const level = await getPermissionLevel(productName);
  const levels = [PERMISSION_LEVELS.read, PERMISSION_LEVELS.write, PERMISSION_LEVELS.admin];
  return levels.indexOf(level) >= levels.indexOf(requiredLevel);
}

/**
 * 不正アクセスを mocka-bridge.js 経由で記録する
 * @param {string} productName
 * @param {string} attemptedAction
 */
export async function recordUnauthorizedAccess(productName, attemptedAction) {
  try {
    await reportError({
      type: 'UNAUTHORIZED_ACCESS',
      product: productName,
      action: attemptedAction,
      ts: Date.now(),
    });
  } catch {
    // 記録失敗は無視
  }
}
