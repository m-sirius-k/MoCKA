// 創造演算の画面試験：Synapse Awakening・試験X・試験Y が画面に出るか、3Dに紫の横のつながりが実体化するか
// 使い方: THREE_JS=<three.min.js> PAGE=<synapse_sim/index.html> SHOT=<png> node tests/run_awakening_ui.js
const { chromium } = require('./_browser_env').requireBrowserPrereqs();
const path = require('path');
const fs = require('fs');

const PAGE = path.resolve(process.env.PAGE);
const THREE_JS = process.env.THREE_JS;
const SHOT = process.env.SHOT;

(async () => {
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'],
  });
  const page = await browser.newPage({ viewport: { width: 1280, height: 1000 } });
  const errors = [], external = [];
  await page.route('**/*', (route) => {
    const url = route.request().url();
    if (url.startsWith('file://')) return route.continue();
    if (url.includes('three.min.js')) return route.fulfill({ status: 200, contentType: 'application/javascript', body: fs.readFileSync(THREE_JS) });
    external.push(url); return route.abort();
  });
  page.on('pageerror', (e) => errors.push(String(e.message)));
  await page.goto('file://' + PAGE);
  await page.waitForTimeout(2500);

  const R = { checks: {}, pageErrors: errors, externalRequests: external };
  const frame = () => page.frames().find((f) => f.url().includes('mocka_3d.html'));
  const summary = () => page.locator('#aw-summary').innerText();
  const latRows = () => page.locator('#aw-laterals tbody tr').count();

  // 1. Synapse Awakening（3D の実データに対して演算）
  await page.click('#btn-awaken');
  await page.waitForTimeout(2500);
  const s1 = await summary();
  R.checks.awakenStatusConverged = s1.includes('status=CONVERGED');
  R.checks.awakenLateralCount11 = /横のつながり\s*11 件/.test(s1);
  R.checks.awakenTableRows11 = (await latRows()) === 11;
  R.checks.awakenLog = (await page.locator('#aw-log').innerText()).includes('[RESULT]');
  const lat = await frame().evaluate(() => window.__mockaDebug.laterals());
  R.checks.threeLateralCount11 = lat.length === 11;
  R.checks.threeLateralPurple = lat.length > 0 && lat.every((l) => l.color === 'd08cff');
  R.checks.threeLateralIdsMatchTable = lat.map((l) => l.id).sort().join(',') === (await page.locator('#aw-laterals .lat-id').allInnerTexts()).sort().join(',');
  R.checks.realDataUnchanged = await frame().evaluate(() => window.__mockaDebug.meshes.size === 104 && window.__mockaDebug.edgeObjs.length === 128);

  // 2. 試験X（完全な断絶空間）：安全に止まる
  await page.click('#btn-x');
  await page.waitForTimeout(200);
  const sx = await summary();
  R.checks.testX_noResonance = sx.includes('status=NO_RESONANCE') && sx.includes('横のつながり 0 件');

  // 3. 試験Y（循環の注入）：循環を検知して止まる
  await page.click('#btn-y');
  await page.waitForTimeout(200);
  const sy = await summary();
  R.checks.testY_cyclePruned = sy.includes('status=CYCLE_PRUNED');
  R.checks.testY_logHasCycle = (await page.locator('#aw-log').innerText()).includes('循環を検知');
  // 表示の健全性：どの結果にも「[object Object]」が出ないこと、刈り込みは件数で出ること
  R.checks.noRawObjectText = ![s1, sx, sy].some((t) => t.includes('[object Object]'));
  R.checks.pruneShownAsCounts = sy.includes('刈り込み：') && !sy.includes('[object');

  if (SHOT) await page.screenshot({ path: SHOT, fullPage: true });
  await browser.close();
  console.log(JSON.stringify(R, null, 2));
})().catch((e) => { console.error('TEST HARNESS FAILED:', e); process.exit(2); });
