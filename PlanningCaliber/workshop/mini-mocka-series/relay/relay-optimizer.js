// relay-optimizer.js — 引き継ぎ最適タイミング検知エンジン（One プラン専用）
// TODO_176  API ゼロ・ローカル処理。密度スコア 0.0〜1.0 で最適タイミングを判定する。
'use strict';

const DENSITY_THRESHOLD = 0.7;  // これ以上で「今が引き継ぎのベストタイミング」通知

// ─── 重要キーワードパターン ───────────────────────────────────────────────────

const KEYWORD_PATTERNS = [
  // ファイルパス系
  /[A-Z]:\\[\w\\.\- ]+/,
  /\/(?:home|Users|var|etc|opt)\/[\w\/.\- ]+/,
  /\b[\w\-]+\.(?:js|py|json|ts|md|yaml|yml|sh|bat|html|css|go|rs)\b/i,
  // TODO/FIXME
  /\bTODO[_\-]?\d*/i,
  /\bFIXME\b/i,
  /\bHACK\b/i,
  // 決定事項（日本語）
  /採用/,
  /却下/,
  /確定/,
  /決定/,
  /にした/,
  /にします/,
  /方針/,
  /設計.*完了/,
  /実装.*完了/,
  // 決定事項（英語）
  /\bfixed\b/i,
  /\bapproved\b/i,
  /\bdecided\b/i,
  /\bconfirmed\b/i,
];

const DECISION_PATTERNS = [
  /採用/, /却下/, /確定/, /決定/, /にした/, /にします/,
  /設計.*完了/, /実装.*完了/,
  /\bfixed\b/i, /\bapproved\b/i, /\bdecided\b/i, /\bconfirmed\b/i,
];

const FILE_PATH_RE = /([A-Z]:\\[\w\\.\- ]+|\/(?:home|Users|var|etc)\/[\w\/.\- ]+|\b[\w\-]+\.(?:js|py|json|ts|md|yaml|yml|sh|bat|html|css|go|rs)\b)/gi;

// ─── 話題転換検知 ────────────────────────────────────────────────────────────

/**
 * 単語集合の Jaccard 距離で話題転換スコアを計算する
 * 直近3ターンが全体と乖離しているほどスコアが高い（話題が変わった）
 */
function calcTopicDivergence(allText, recentText) {
  const toWords = (t) => new Set(
    t.toLowerCase()
      .replace(/[^\w぀-鿿]/g, ' ')
      .split(/\s+/)
      .filter(w => w.length > 2)
  );
  const A = toWords(allText);
  const B = toWords(recentText);
  if (A.size === 0 || B.size === 0) return 0;
  const intersection = [...B].filter(w => A.has(w)).length;
  const union = new Set([...A, ...B]).size;
  const jaccard = intersection / union;
  return Math.round((1 - jaccard) * 100) / 100;
}

// ─── メイン計算 ──────────────────────────────────────────────────────────────

/**
 * メッセージ配列から密度スコア（0.0〜1.0）を計算する
 * @param {Array<{role:string, content:string}>} messages
 * @returns {{ score: number, breakdown: object }}
 */
export function calcDensityScore(messages) {
  if (!messages || messages.length === 0) return { score: 0, breakdown: {} };

  const allText    = messages.map(m => m.content || '').join('\n');
  const recentText = messages.slice(-3).map(m => m.content || '').join('\n');
  const wordCount  = Math.max(allText.split(/\s+/).filter(Boolean).length, 1);

  // 指標1: 重要キーワード出現率
  let kwCount = 0;
  for (const re of KEYWORD_PATTERNS) {
    const hits = allText.match(new RegExp(re.source, (re.flags || '') + 'g')) || [];
    kwCount += hits.length;
  }
  const kwScore = Math.min(kwCount / Math.max(wordCount * 0.05, 1), 1.0);

  // 指標2: ファイルパス検出数
  const filePaths  = allText.match(FILE_PATH_RE) || [];
  const fileScore  = Math.min(filePaths.length / 10, 1.0);

  // 指標3: 決定事項検出数
  let decisionCount = 0;
  for (const re of DECISION_PATTERNS) {
    const hits = allText.match(new RegExp(re.source, (re.flags || '') + 'g')) || [];
    decisionCount += hits.length;
  }
  const decisionScore = Math.min(decisionCount / 5, 1.0);

  // 指標4: 話題転換スコア
  const topicScore = calcTopicDivergence(allText, recentText);

  // 複合スコア（重みつき平均）
  const score = Math.min(
    kwScore       * 0.30 +
    fileScore     * 0.25 +
    decisionScore * 0.25 +
    topicScore    * 0.20,
    1.0
  );

  return {
    score: Math.round(score * 100) / 100,
    breakdown: {
      keyword:        Math.round(kwScore * 100) / 100,
      filePath:       Math.round(fileScore * 100) / 100,
      decision:       Math.round(decisionScore * 100) / 100,
      topicDivergence: Math.round(topicScore * 100) / 100,
      keywordCount:   kwCount,
      filePathCount:  filePaths.length,
      decisionCount,
    },
  };
}

/**
 * 引き継ぎ推奨判定
 * @param {Array} messages
 * @param {number} [threshold]
 * @returns {{ recommend: boolean, score: number, breakdown: object }}
 */
export function shouldHandoff(messages, threshold = DENSITY_THRESHOLD) {
  const { score, breakdown } = calcDensityScore(messages);
  return { recommend: score >= threshold, score, breakdown };
}
