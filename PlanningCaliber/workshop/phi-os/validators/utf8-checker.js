'use strict';
// utf8-checker.js — UTF-8完全性検証（TODO_155）
// cp932由来の危険文字を検出する。Chrome拡張・Node.js両対応。

// C1制御文字（0x80-0x9F）: cp932テキストをUTF-8として誤解釈した時に混入しやすい
// 文字化け置換文字 (U+FFFD): デコード失敗の証拠
// 半角カナ (U+FF61-U+FF9F): 意図的使用以外は禁止
const BANNED_PATTERNS = [
  { pattern: /[-]/, name: 'C1制御文字', code: 'C1_CONTROL' },
  { pattern: /�/,          name: '置換文字(文字化け)', code: 'REPLACEMENT_CHAR' },
  { pattern: /[｡-ﾟ]/, name: '半角カナ',    code: 'HALFWIDTH_KANA' },
];

function _scanText(text) {
  const issues = [];
  for (const { pattern, name, code } of BANNED_PATTERNS) {
    const matches = [...text.matchAll(new RegExp(pattern.source, 'g'))];
    if (matches.length > 0) {
      issues.push({
        code,
        name,
        count: matches.length,
        positions: matches.slice(0, 5).map(m => m.index),
      });
    }
  }
  return { ok: issues.length === 0, issues };
}

async function _readFile(filePath) {
  // Chrome拡張環境: fetch で extension URL 経由
  if (typeof globalThis.chrome !== 'undefined' && chrome.runtime?.getURL) {
    try {
      const url = chrome.runtime.getURL(filePath);
      const res = await fetch(url);
      if (!res.ok) throw new Error(`fetch ${res.status}`);
      return await res.text();
    } catch {
      // extension URL でない場合は fallback
    }
  }

  // Node.js 環境: fs.promises
  if (typeof globalThis.process !== 'undefined') {
    try {
      const { readFile } = await import('fs/promises');
      return await readFile(filePath, 'utf-8');
    } catch (err) {
      throw new Error(`Node.js readFile failed: ${err.message}`);
    }
  }

  // ブラウザ環境: fetch (相対URLのみ)
  try {
    const res = await fetch(filePath);
    if (!res.ok) throw new Error(`fetch ${res.status}`);
    return await res.text();
  } catch (err) {
    throw new Error(`UTF8Checker: ファイル読み込み失敗 (${filePath}): ${err.message}`);
  }
}

export const UTF8Checker = {
  /**
   * ファイルパスを指定してUTF-8検証を行う。
   * @param {string} filePath
   * @returns {Promise<{ ok: boolean, issues: Array }>}
   */
  async verify(filePath) {
    try {
      const text = await _readFile(filePath);
      return _scanText(text);
    } catch (err) {
      // ファイル読み込み失敗時は「検証不能」として ok: false を返す
      return {
        ok: false,
        issues: [{ code: 'READ_ERROR', name: '読み込みエラー', message: err.message, count: 1, positions: [] }],
      };
    }
  },

  /**
   * テキスト内容を直接検証する（ファイルアクセス不要）。
   * @param {string} text
   * @returns {{ ok: boolean, issues: Array }}
   */
  scanContent(text) {
    return _scanText(String(text));
  },

  /**
   * 禁止パターン一覧を返す。
   * @returns {Array<{ pattern: RegExp, name: string, code: string }>}
   */
  getBannedPatterns() {
    return BANNED_PATTERNS.map(p => ({ ...p }));
  },
};
