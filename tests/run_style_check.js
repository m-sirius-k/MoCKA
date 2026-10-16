// 表示設定の試験: 背景色の変更・保存・既定への復元、接続線の太さ（画面ピクセル）とズーム時の不変性
// 使い方: THREE_JS=<three.min.js> PAGE=<html> DATA=<json> SHOT=<png> node tests/run_style_check.js
const { chromium } = require('./_browser_env').requireBrowserPrereqs();
const path = require('path');
const fs = require('fs');

const PAGE = path.resolve(process.env.PAGE);
const THREE_JS = process.env.THREE_JS;
const SHOT = process.env.SHOT;
const DATA = JSON.parse(fs.readFileSync(path.resolve(process.env.DATA), 'utf8'));

(async () => {
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'],
  });
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } }); // 保存を持たない新規環境
  const page = await context.newPage();
  const errors = [], external = [];
  await page.route('**/*', (route) => {
    const url = route.request().url();
    if (url.startsWith('file://')) return route.continue();
    if (url.includes('three.min.js')) return route.fulfill({ status: 200, contentType: 'application/javascript', body: fs.readFileSync(THREE_JS) });
    external.push(url); return route.abort();
  });
  page.on('pageerror', (e) => errors.push(String(e.message)));
  await page.goto('file://' + PAGE);
  await page.waitForTimeout(1200);

  const R = { checks: {}, pageErrors: errors, externalRequests: external };

  // 1. 既定値
  R.checks.defaultBg = await page.evaluate(() => document.body.style.background);
  R.checks.defaultLightClass = await page.evaluate(() => document.body.classList.contains('light'));
  R.checks.defaultEdgeWidthLabel = await page.locator('#edge-w-val').innerText();

  // 2. 背景色を明るく変更
  await page.locator('#bg-color').fill('#f2f2ee');
  await page.waitForTimeout(100);
  R.checks.lightBgApplied = await page.evaluate(() => document.body.style.background);
  R.checks.lightClassSet = await page.evaluate(() => document.body.classList.contains('light'));
  // 再読み込み後も保持されるか（閲覧者のブラウザ内）
  await page.reload();
  await page.waitForTimeout(1000);
  R.checks.bgPersistedAfterReload = await page.evaluate(() => document.body.style.background);

  // 3. 接続線の太さ：8px に設定し、画面上の太さを測る
  const measurePx = () => page.evaluate(() => {
    const m = window.__mockaDebug;
    const worldPerPx = (m.view.dist * 2 * Math.tan(30 * Math.PI / 180)) / innerHeight;
    const widths = m.edgeObjs.map(({ line }) => (2 * line.scale.x) / worldPerPx);
    return { min: Math.min(...widths), max: Math.max(...widths), n: widths.length };
  });
  await page.locator('#edge-width').fill('8');
  await page.waitForTimeout(150);
  const w8 = await measurePx();
  R.checks.edgeWidth8px = { min: +w8.min.toFixed(2), max: +w8.max.toFixed(2), edges: w8.n };
  R.checks.edgeWidthLabel8 = await page.locator('#edge-w-val').innerText();

  // 4. ズームしても画面上の太さは変わらないか
  const d0 = await page.evaluate(() => window.__mockaDebug.view.dist);
  await page.click('#view-ctrl button[data-act="zoomin"]');
  await page.waitForTimeout(150);
  const d1 = await page.evaluate(() => window.__mockaDebug.view.dist);
  const w8z = await measurePx();
  R.checks.zoomChangedDist = d1 !== d0;
  R.checks.edgeWidthAfterZoomPx = { min: +w8z.min.toFixed(2), max: +w8z.max.toFixed(2) };

  // 5. 背景を既定に戻す
  await page.click('#bg-reset');
  await page.waitForTimeout(100);
  R.checks.resetBg = await page.evaluate(() => document.body.style.background);
  R.checks.resetLightClassCleared = await page.evaluate(() => !document.body.classList.contains('light'));

  // 6. 既存機能の回帰：ノード選択でラベルが出るか、表示件数
  await page.locator('#edge-width').fill('2');
  await page.locator('#bg-color').fill('#f2f2ee');
  await page.waitForTimeout(150);
  const pos = await page.evaluate(() => {
    const m = window.__mockaDebug; const mesh = m.meshes.get('N054');
    const v = mesh.getWorldPosition(new THREE.Vector3()).project(m.camera);
    return { x: (v.x + 1) / 2 * innerWidth, y: (-v.y + 1) / 2 * innerHeight };
  });
  await page.mouse.click(pos.x, pos.y);
  await page.waitForTimeout(250);
  R.checks.labelsStillWork = await page.locator('#labels .lbl').count();
  if (SHOT) await page.screenshot({ path: SHOT });

  await browser.close();
  console.log(JSON.stringify(R, null, 2));
})().catch((e) => { console.error('TEST HARNESS FAILED:', e); process.exit(2); });
