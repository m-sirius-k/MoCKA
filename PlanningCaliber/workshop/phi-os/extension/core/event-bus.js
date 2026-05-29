// event-bus.js — PHI OS 製品間メッセージング
// chrome.runtime.sendMessage の Extension ID 問題を回避するため
// chrome.storage.local をイベントバスとして使用する
'use strict';

import { reportError } from '../debug/error-reporter.js';

const BUS_KEY    = 'phi_event_bus';
const MAX_EVENTS = 50;

/**
 * イベントを発行する
 * @param {string} type   イベント種別
 * @param {object} payload
 */
export async function emit(type, payload = {}) {
  try {
    const stored = await chrome.storage.local.get(BUS_KEY);
    const bus    = stored[BUS_KEY] || [];
    bus.unshift({ type, payload, ts: Date.now(), id: `EVT_${Date.now()}` });
    if (bus.length > MAX_EVENTS) bus.pop();
    await chrome.storage.local.set({ [BUS_KEY]: bus });
  } catch (e) {
    await reportError({ type: 'EVENT_BUS_EMIT_ERROR', message: e.message, eventType: type, ts: Date.now() });
  }
}

/**
 * 未処理イベントを取得して消費する
 * @param {string[]} types  フィルターする種別（省略時は全件）
 * @returns {Promise<Array>}
 */
export async function consume(types = []) {
  try {
    const stored = await chrome.storage.local.get(BUS_KEY);
    const bus    = stored[BUS_KEY] || [];
    const matched   = types.length ? bus.filter(e => types.includes(e.type)) : [...bus];
    const remaining = types.length ? bus.filter(e => !types.includes(e.type)) : [];
    await chrome.storage.local.set({ [BUS_KEY]: remaining });
    return matched;
  } catch (e) {
    await reportError({ type: 'EVENT_BUS_CONSUME_ERROR', message: e.message, ts: Date.now() });
    return [];
  }
}

/**
 * storage.onChanged を利用してリアルタイムにイベントを購読する
 * @param {string[]} types
 * @param {Function} callback
 * @returns {Function} unsubscribe関数
 */
export function subscribe(types, callback) {
  const handler = (changes, area) => {
    if (area !== 'local' || !changes[BUS_KEY]) return;
    const newBus = changes[BUS_KEY].newValue || [];
    const oldBus = changes[BUS_KEY].oldValue || [];
    const newEvents = newBus.filter(e =>
      !oldBus.some(o => o.id === e.id) &&
      (types.length === 0 || types.includes(e.type))
    );
    newEvents.forEach(callback);
  };
  chrome.storage.onChanged.addListener(handler);
  return () => chrome.storage.onChanged.removeListener(handler);
}
