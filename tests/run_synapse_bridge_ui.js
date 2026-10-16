// Synapse-3D ブリッジの画面試験：シミュレーターの操作が、iframe の 3D マップの線に反映されるか
// 使い方: THREE_JS=<three.min.js> PAGE=<synapse_sim/index.html> SHOT=<png> node tests/run_synapse_bridge_ui.js
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
  await page.waitForTimeout(2500); // iframe（3Dマップ）の読み込みと ready の往復を待つ

  const R = { checks: {}, pageErrors: errors, externalRequests: external };
  const frame = () => page.frames().find((f) => f.url().includes('mocka_3d.html'));
  // 3D 側の経路線の状態を読む（色は 16 進文字列）
  const overlay = () => frame().evaluate(() => {
    const out = {};
    window.__mockaDebug.synapseEdges.forEach((line, key) => {
      out[key] = { status: line.userData.status, color: line.material.color.getHexString(), highlight: line.userData.highlight, widthPx: line.userData.widthPx, opacity: line.material.opacity };
    });
    return out;
  });
  const chainBroken = () => page.locator('#chain .link.BROKEN').count();

  // 1. 起動時：4本とも VERIFIED（緑）
  let o = await overlay();
  R.checks.startVerified = Object.keys(o).length === 4 && Object.values(o).every((v) => v.status === 'VERIFIED' && v.color === '2ecc71');

  // 2. Test B：Auth->RT が赤・点滅、HG->Auth は灰色
  await page.click('#btn-b');
  await page.waitForTimeout(300);
  o = await overlay();
  R.checks.testB_authToRtBrokenRed = o.edge_auth_to_rt.status === 'BROKEN' && o.edge_auth_to_rt.color === 'e74c3c' && o.edge_auth_to_rt.highlight === true;
  R.checks.testB_hgToAuthGrey = o.edge_hg_to_auth.status === 'NOT_REACHED' && o.edge_hg_to_auth.color === '9a9a9a';
  R.checks.testB_chainBrokenCount = await chainBroken();

  // 3. 点滅しているか（不透明度が時間で変わる）
  const op1 = (await overlay()).edge_auth_to_rt.opacity;
  await page.waitForTimeout(170);
  const op2 = (await overlay()).edge_auth_to_rt.opacity;
  R.checks.blinkingHighlight = Math.abs(op1 - op2) > 0.01;

  // 4. Test A：HG->Auth が赤に変わる
  await page.click('#btn-a');
  await page.waitForTimeout(300);
  o = await overlay();
  R.checks.testA_hgToAuthBrokenRed = o.edge_hg_to_auth.status === 'BROKEN' && o.edge_hg_to_auth.color === 'e74c3c';

  // 5. Test C：RT->Cons が赤
  await page.click('#btn-c');
  await page.waitForTimeout(300);
  o = await overlay();
  R.checks.testC_rtToConsBrokenRed = o.edge_rt_to_cons.status === 'BROKEN' && o.edge_rt_to_cons.highlight === true;
  R.checks.testC_consToMemNotReached = o.edge_cons_to_mem.status === 'NOT_REACHED';

  // 6. 正常系へ戻すと、4本とも緑に戻る
  await page.click('#btn-run');
  await page.waitForTimeout(300);
  o = await overlay();
  R.checks.runBackToAllVerified = Object.values(o).every((v) => v.status === 'VERIFIED' && v.highlight === false);

  // 7. ready の往復：iframe を読み直しても、現在の状態が送り直される
  await page.click('#btn-b');
  await page.waitForTimeout(200);
  await page.reload();
  await page.waitForTimeout(2500);
  // 再読み込み後は起動時の正常系が送られる（ready→現在の状態）
  o = await overlay();
  R.checks.afterReloadStateRestored = Object.values(o).every((v) => v.status === 'VERIFIED');

  // 8. 3D の実データ（ノード・エッジ数）は変わっていない
  const counts = await frame().evaluate(() => ({ nodes: window.__mockaDebug.meshes.size, edges: window.__mockaDebug.edgeObjs.length }));
  R.checks.realDataUnchanged = counts.nodes === 104 && counts.edges === 128;

  if (SHOT) await page.screenshot({ path: SHOT, fullPage: true });
  await browser.close();
  console.log(JSON.stringify(R, null, 2));
})().catch((e) => { console.error('TEST HARNESS FAILED:', e); process.exit(2); });
