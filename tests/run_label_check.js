// ラベル試験: ノードをクリックすると、そのノードと接続先のファイル名が画面上に出るか
// 使い方: THREE_JS=<three.min.js> PAGE=<html> DATA=<json> SHOT=<png> node tests/run_label_check.js
const { chromium } = require('./_browser_env').requireBrowserPrereqs();
const path = require('path');
const fs = require('fs');

const PAGE = path.resolve(process.env.PAGE);
const THREE_JS = process.env.THREE_JS;
const DATA = JSON.parse(fs.readFileSync(path.resolve(process.env.DATA), 'utf8'));
const SHOT = process.env.SHOT;
const TARGET = process.env.TARGET || 'N054';

// 期待値：対象ノードと接続先（重複なし）
const incident = DATA.edges.filter((e) => e.from === TARGET || e.to === TARGET);
const expectedIds = [...new Set([TARGET, ...incident.map((e) => (e.from === TARGET ? e.to : e.from))])].sort();
const tnode = DATA.nodes.find((n) => n.id === TARGET);
const base = (tnode.path || '').split(/[\\/]/).pop();

(async () => {
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'],
  });
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
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

  const R = { checks: {}, pageErrors: errors, externalRequests: external, expectedLabelIds: expectedIds.length };

  // 対象ノードを画面上の位置でクリック
  const pos = await page.evaluate((id) => {
    const m = window.__mockaDebug;
    const mesh = m.meshes.get(id);
    const v = mesh.getWorldPosition(new THREE.Vector3()).project(m.camera);
    return { x: (v.x + 1) / 2 * innerWidth, y: (-v.y + 1) / 2 * innerHeight };
  }, TARGET);
  await page.mouse.click(pos.x, pos.y);
  await page.waitForTimeout(250);

  const shown = await page.evaluate(() => {
    const els = [...document.querySelectorAll('#labels .lbl')];
    return els.map((el) => ({ text: el.textContent, display: el.style.display, focus: el.classList.contains('focus') }));
  });
  const ids = shown.map((s) => s.text.split(' · ')[0]).sort();
  R.checks.labelIdsMatchFocusPlusNeighbors = JSON.stringify(ids) === JSON.stringify(expectedIds);
  R.checks.labelCount = shown.length;
  R.checks.labelsOnScreen = shown.filter((s) => s.display === 'block').length;
  R.checks.focusLabelText = (shown.find((s) => s.focus) || {}).text || null;
  R.checks.focusLabelShowsFileName = !!base && (((shown.find((s) => s.focus) || {}).text) || '').includes(base);

  // 空白クリックでラベルが消えるか
  await page.mouse.click(10, 780);
  await page.waitForTimeout(200);
  R.checks.labelsClearedOnEmptyClick = (await page.locator('#labels .lbl').count()) === 0;

  if (SHOT) {
    await page.mouse.click(pos.x, pos.y);
    await page.waitForTimeout(250);
    await page.screenshot({ path: SHOT });
  }
  await browser.close();
  console.log(JSON.stringify(R, null, 2));
})().catch((e) => { console.error('TEST HARNESS FAILED:', e); process.exit(2); });
