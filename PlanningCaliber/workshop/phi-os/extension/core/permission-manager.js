// permission-manager.js — 拡張ID管理・認証
// chrome.runtime.id を動的に使用し、ハードコードを排除する
'use strict';

import { get, set } from './state-store.js';

const KNOWN_PRODUCTS = ['relay', 'orchestra', 'memory'];

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
