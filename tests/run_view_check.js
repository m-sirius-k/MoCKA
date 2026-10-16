// 表示範囲の試験: 全ノードが回転のどの角度でも画面内に入るか、パン・ズーム・全体表示が効くか
// 使い方: THREE_JS=<three.min.js> PAGE=<html> DATA=<json> SHOT=<png> node tests/run_view_check.js
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

  // 全ノードのうち画面外にあるものの数（NDCで |x|,|y| > 1 または手前外）
  const offscreen = () => page.evaluate(() => {
    const m = window.__mockaDebug;
    m.orbit.updateMatrixWorld(true);
    let out = 0; const total = m.meshes.size;
    const v = new THREE.Vector3();
    m.meshes.forEach((mesh) => {
      mesh.getWorldPosition(v).project(m.camera);
      if (Math.abs(v.x) > 1 || Math.abs(v.y) > 1 || v.z > 1) out++;
    });
    return { out, total };
  });
  const state = () => page.evaluate(() => {
    const v = window.__mockaDebug.view;
    return { tx: v.target.x, ty: v.target.y, tz: v.target.z, dist: v.dist, fit: v.fitDist };
  });

  const R = { checks: {}, pageErrors: errors, externalRequests: external };

  // 1. 回転を変えても全ノードが画面内か（最も厳しい角度を含む）
  let worst = 0; const samples = [];
  for (const ry of [0, Math.PI / 4, Math.PI / 2, Math.PI, 3 * Math.PI / 2]) {
    for (const rx of [-1.2, -0.6, 0, 0.6, 1.2]) {
      const r = await page.evaluate(([y, x]) => { window.__mockaDebug.orbit.rotation.set(x, y, 0); return null; }, [ry, rx]);
      await page.waitForTimeout(60);
      const o = await offscreen();
      samples.push({ ry: +ry.toFixed(2), rx, out: o.out });
      worst = Math.max(worst, o.out);
    }
  }
  R.checks.rotationSweepMaxOffscreen = worst;
  R.checks.rotationSweepSamples = samples.length;
  await page.evaluate(() => window.__mockaDebug.orbit.rotation.set(0, 0, 0));
  await page.waitForTimeout(60);

  // 2. ボタン・キーボード・ホイール・Shift+ドラッグ
  const s0 = await state();
  await page.click('#view-ctrl button[data-act="up"]');
  const s1 = await state();
  R.checks.upButtonMovesTargetY = s1.ty > s0.ty;
  await page.click('#view-ctrl button[data-act="left"]');
  const s2 = await state();
  R.checks.leftButtonMovesTargetX = s2.tx < s1.tx;
  await page.click('#view-ctrl button[data-act="zoomin"]');
  const s3 = await state();
  R.checks.zoomInReducesDist = s3.dist < s2.dist;
  await page.keyboard.press('ArrowRight');
  const s4 = await state();
  R.checks.arrowRightMovesTargetX = s4.tx > s3.tx;
  await page.mouse.move(600, 400); await page.mouse.wheel(0, 300);
  await page.waitForTimeout(80);
  const s5 = await state();
  R.checks.wheelZoomOutIncreasesDist = s5.dist > s4.dist;
  await page.keyboard.down('Shift');
  await page.mouse.move(600, 400); await page.mouse.down();
  await page.mouse.move(640, 430, { steps: 6 }); await page.mouse.up();
  await page.keyboard.up('Shift');
  const s6 = await state();
  R.checks.shiftDragPans = (s6.tx !== s5.tx) || (s6.ty !== s5.ty);

  // 3. 全体表示で元に戻る
  await page.click('#view-ctrl button[data-act="reset"]');
  const s7 = await state();
  R.checks.resetRestoresView = s7.tx === 0 && s7.ty === 0 && s7.tz === 0 && Math.abs(s7.dist - s7.fit) < 1e-6;
  const o = await offscreen();
  R.checks.afterResetOffscreen = `${o.out}/${o.total}`;
  R.checks.afterResetAllVisible = o.out === 0;

  if (SHOT) await page.screenshot({ path: SHOT });
  await browser.close();
  console.log(JSON.stringify(R, null, 2));
})().catch((e) => { console.error('TEST HARNESS FAILED:', e); process.exit(2); });
