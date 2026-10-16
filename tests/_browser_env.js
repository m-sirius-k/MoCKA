// ブラウザ試験の共通前提チェック。
// Playwright（PLAYWRIGHT_MODULE または require('playwright')）と Three.js r128（THREE_JS）が無い環境では、
// 理由を出力して SKIP（終了コード0）とする。失敗を合格扱いにはしない。
const fs = require('fs');

function loadChromium() {
  const candidates = [process.env.PLAYWRIGHT_MODULE, 'playwright'].filter(Boolean);
  for (const candidate of candidates) {
    try {
      return require(candidate).chromium;
    } catch (_) {
      // 次の候補を試す
    }
  }
  return null;
}

function requireBrowserPrereqs() {
  const chromium = loadChromium();
  const missing = [];
  if (!chromium) missing.push('playwright (PLAYWRIGHT_MODULE を指定)');
  if (!process.env.THREE_JS || !fs.existsSync(process.env.THREE_JS)) missing.push('THREE_JS (three.min.js r128 のローカルパス)');
  if (missing.length) {
    console.log('SKIP: 必要な前提が無いためブラウザ試験を実行しません: ' + missing.join(', '));
    process.exit(0);
  }
  return { chromium };
}

module.exports = { requireBrowserPrereqs };
