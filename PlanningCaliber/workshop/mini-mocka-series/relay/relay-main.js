// relay-main.js — Relay エントリポイント（One プラン: 最適タイミング検知を統合）
// Task 2: relay-optimizer 起動タイミング管理
'use strict';

import { shouldHandoff } from './relay-optimizer.js';
import { showBanner, hideBanner } from './relay-ui.js';

// ─── 設定 ───────────────────────────────────────────────────────────────────

const FREE_TURN_WARN = 20;   // Free: 警告ターン数
const CHECK_INTERVAL = 3;    // 3ターンごとに密度スコアを計算

// ─── 状態 ───────────────────────────────────────────────────────────────────

let _messages      = [];
let _turnCount     = 0;
let _extraTurns    = 0;   // 「あと5ターン」で延長した回数
let _planLevel     = 'free';  // 'free' | 'pro' | 'one'

// ─── メッセージ追加（DOM watcher が呼び出す） ────────────────────────────────

export function addMessage(role, content) {
  _messages.push({ role, content });
  _turnCount++;
  _onTurnAdded();
}

// ─── ターン追加時の処理 ──────────────────────────────────────────────────────

function _onTurnAdded() {
  // Free: 固定ターン数警告
  if (_planLevel === 'free') {
    if (_turnCount >= FREE_TURN_WARN) {
      _notifyFreeWarning();
    }
    return;
  }

  // One: 密度スコアによる最適タイミング検知
  if (_planLevel === 'one') {
    if (_turnCount % CHECK_INTERVAL === 0) {
      _checkOptimizerThreshold();
    }
    return;
  }

  // Pro: AI要約トグル + ファイルパスキャプチャ（実装済み部分は維持）
}

// ─── Free: 固定ターン警告 ───────────────────────────────────────────────────

function _notifyFreeWarning() {
  // ルールベース引き継ぎ通知（バナーなしのシンプル通知）
  const banner = document.getElementById('relay-free-warning');
  if (banner) return;
  const el = document.createElement('div');
  el.id = 'relay-free-warning';
  el.style.cssText = 'position:fixed;bottom:24px;right:24px;z-index:99999;background:#1a1a2e;border:1px solid #d29922;border-radius:8px;padding:12px 16px;color:#c9d1d9;font-size:13px;';
  el.innerHTML = `⚠️ <strong>${_turnCount}ターン</strong>に達しました。引き継ぎを推奨します。`;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 8000);
}

// ─── One: 最適タイミング検知 ────────────────────────────────────────────────

function _checkOptimizerThreshold() {
  const result = shouldHandoff(_messages);
  if (result.recommend) {
    showBanner(result, _turnCount, {
      onHandoffNow: _triggerHandoffNow,
      onLater:      _snoozeOptimizer,
    });
  }
}

function _triggerHandoffNow() {
  // 引き継ぎ処理（relay-logbook.js の handoff と連携）
  window.dispatchEvent(new CustomEvent('relay:handoff-request', {
    detail: { source: 'optimizer', turnCount: _turnCount, messages: _messages },
  }));
}

function _snoozeOptimizer() {
  _extraTurns += 5;
  // 5ターン後に再チェック
  const targetTurn = _turnCount + 5;
  const checkFn = () => {
    if (_turnCount >= targetTurn) {
      _checkOptimizerThreshold();
    }
  };
  window.addEventListener('relay:turn-added', checkFn, { once: true });
}

// ─── 初期化 ─────────────────────────────────────────────────────────────────

export function init(planLevel = 'free') {
  _planLevel = planLevel;
  _messages  = [];
  _turnCount = 0;

  // NOTE(LB_005修正): init() から notifySessionStart は呼ばない。
  // notifySessionStart はセッション開始イベント（別パス）でのみ呼ぶ。
  // 旧実装でここに残留していた呼び出しがレースコンディションを引き起こしていた。
}

export function getState() {
  return { turnCount: _turnCount, planLevel: _planLevel, messageCount: _messages.length };
}
