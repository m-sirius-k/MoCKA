// 実行試験ハーネス（MoCKA 3D Orbit Map）
// 使い方: THREE_JS=<three.min.js> PAGE=<html> node tests/run_browser_check.js
// - 外部通信は全遮断し、Three.js r128 はローカルファイルで代替（隔離）
// - 判定は画面の見え方（表示件数・投影座標・発光の時間変化）で行う
const { chromium } = require('./_browser_env').requireBrowserPrereqs();
const path = require('path');
const fs = require('fs');
const os = require('os');

const LAB = path.resolve(__dirname, '..');
const PAGE = path.resolve(process.env.PAGE || path.join(LAB, 'src', 'mocka_3d.html'));
const THREE_JS = process.env.THREE_JS;
// 期待値の基準データ。DATA=実データJSON を指定すると実データで検証する（既定はフィクスチャ）
const DATA_FILE = path.resolve(process.env.DATA || path.join(LAB, 'tests', 'fixtures', 'fixture_unified.json'));
const FIXTURE = JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
const IS_REAL = !!process.env.DATA;

const idSet = new Set(FIXTURE.nodes.map((n) => n.id));
const expectedDroppedEdges = FIXTURE.edges.filter((e) => !idSet.has(e.from) || !idSet.has(e.to)).length;
// ノードの接続エッジ集約と同じ基準で、特定ステータスを含むノードを数える（画面側のロジックと独立に計算）
const nodesWithEdgeStatus = (st) => FIXTURE.nodes.filter((n) =>
  FIXTURE.edges.some((e) => (e.from === n.id || e.to === n.id) && e.status === st)).map((n) => n.id);
const pendingIds = nodesWithEdgeStatus('PENDING');
const expectedSearchN054Pending = FIXTURE.nodes.filter((n) =>
  [n.id, n.name, n.path, n.note, n.type].filter(Boolean).join(' ').toLowerCase().includes('n054') &&
  pendingIds.includes(n.id)).length;
const expectedSearchN054 = FIXTURE.nodes.filter((n) =>
  [n.id, n.name, n.path, n.note, n.type].filter(Boolean).join(' ').toLowerCase().includes('n054')).length;

async function openPage(browser, file) {
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  const errors = [], external = [];
  await page.route('**/*', (route) => {
    const url = route.request().url();
    if (url.startsWith('file://')) return route.continue();
    if (url.includes('three.min.js')) {
      return route.fulfill({ status: 200, contentType: 'application/javascript', body: fs.readFileSync(THREE_JS) });
    }
    external.push(url);
    return route.abort();
  });
  page.on('pageerror', (e) => errors.push(String(e.message)));
  await page.goto('file://' + file);
  await page.waitForTimeout(1200);
  return { page, errors, external };
}

(async () => {
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'],
  });
  const R = { checks: {}, pageErrors: [], externalRequests: [] };

  // ---- A. 正常系 ----
  const A = await openPage(browser, PAGE);
  const p = A.page;
  R.pageErrors = A.errors;
  R.externalRequests = A.external;

  R.checks.canvasPresent = (await p.locator('canvas').count()) === 1;
  R.checks.metaText = await p.locator('#meta-info').innerText();
  R.checks.fixtureBannerShown = await p.locator('#banner').isVisible();
  R.checks.bannerMatchesDataKind = R.checks.fixtureBannerShown === !IS_REAL;

  // 埋め込みデータがフィクスチャと一致するか
  const embedded = await p.evaluate(() => JSON.parse(document.getElementById('mocka-data').textContent));
  // 埋め込み時に付ける source 欄だけ除外して比較する（それ以外は完全一致が必要）
  const strip = (o) => { const c = Object.assign({}, o); delete c.source; return JSON.stringify(c); };
  R.checks.embeddedMatchesDataFile = strip(embedded) === strip(FIXTURE);

  // 描画件数（フィクスチャ基準）
  const dbg = () => p.evaluate(() => {
    const m = window.__mockaDebug;
    const nodesVisible = [...m.meshes.values()].filter((x) => x.visible).length;
    const edgesVisible = m.edgeObjs.filter((x) => x.line.visible).length;
    return { nodesVisible, edgesVisible, total: m.meshes.size, edgeTotal: m.edgeObjs.length };
  });
  const c0 = await dbg();
  R.checks.nodesDrawn = c0.total;
  R.checks.edgesDrawn = c0.edgeTotal;
  R.checks.expectedNodes = FIXTURE.nodes.length;
  R.checks.expectedEdgesAfterDrop = FIXTURE.edges.length - expectedDroppedEdges;

  // ドラッグ回転: orbit の回転角が変わるか
  const rot = () => p.evaluate(() => [window.__mockaDebug.orbit.rotation.x, window.__mockaDebug.orbit.rotation.y]);
  const r0 = await rot();
  await p.mouse.move(640, 400); await p.mouse.down();
  await p.mouse.move(760, 460, { steps: 10 }); await p.mouse.up();
  await p.waitForTimeout(200);
  const r1 = await rot();
  R.checks.dragRotates = r0[0] !== r1[0] || r0[1] !== r1[1];

  // クリック: 投影座標で N054 を狙ってクリック → 詳細が N054 になるか
  const screen = await p.evaluate(() => {
    const m = window.__mockaDebug;
    const mesh = m.meshes.get('N054');
    const v = mesh.getWorldPosition(new (mesh.position.constructor)());
    v.project(m.camera);
    return { x: (v.x + 1) / 2 * innerWidth, y: (-v.y + 1) / 2 * innerHeight };
  });
  await p.mouse.click(screen.x, screen.y);
  await p.waitForTimeout(150);
  R.checks.clickFocusesN054 = (await p.evaluate(() => window.__mockaDebug.focusId)) === 'N054';
  R.checks.detailShowsN054 = (await p.locator('#detail').innerText()).includes('[N054]');

  // 空白クリックでフォーカス解除
  await p.mouse.click(10, 780);
  await p.waitForTimeout(150);
  R.checks.emptyClickClearsFocus = (await p.evaluate(() => window.__mockaDebug.focusId)) === null;

  // 検索: 'N054' で1件・接続線は0本（N054 の接続はあるが相手が消える）
  await p.fill('#search-q', 'N054');
  await p.waitForTimeout(100);
  const s1 = await dbg();
  R.checks.searchN054Nodes = s1.nodesVisible;
  R.checks.expectedSearchN054 = expectedSearchN054;

  // 検索解除 → フィルタ PENDING（フィクスチャ上の PENDING 件数と一致するか）
  await p.fill('#search-q', '');
  await p.selectOption('#filter-status', 'PENDING');
  await p.waitForTimeout(100);
  const s2 = await dbg();
  R.checks.filterPendingNodes = s2.nodesVisible;
  R.checks.expectedPendingNodes = pendingIds.length;

  // 検索 + フィルタの組み合わせ
  await p.fill('#search-q', 'N054');
  await p.waitForTimeout(100);
  R.checks.searchPlusFilterNodes = (await dbg()).nodesVisible;
  R.checks.expectedSearchPlusFilter = expectedSearchN054Pending;

  // 赤ノード(N061 CONFIRMED_ABSENT)の発光が時間で変化するか
  await p.fill('#search-q', ''); await p.selectOption('#filter-status', '');
  await p.waitForTimeout(50);
  const emi = async () => p.evaluate(() => window.__mockaDebug.meshes.get('N061').material.emissiveIntensity);
  const e1 = await emi(); await p.waitForTimeout(250); const e2 = await emi();
  R.checks.redGlowPulses = Math.abs(e1 - e2) > 0.01;
  R.checks.redGlowNode = 'N061';

  // 1秒あたりフレーム数（参考値：ソフトウェア描画のため性能指標ではない）
  R.checks.fps_softwareRenderer = await p.evaluate(() => new Promise((res) => {
    let n = 0; const t0 = performance.now();
    const f = () => { n++; if (performance.now() - t0 < 2000) requestAnimationFrame(f); else res(Math.round(n / 2)); };
    requestAnimationFrame(f);
  }));
  await A.page.close();

  // ---- B. 失敗系: 壊れたJSONで白画面にならず、理由が出るか ----
  const scratch = fs.mkdtempSync(path.join(process.env.SCRATCH || os.tmpdir(), 'mocka-neg-'));
  const broken = path.join(scratch, 'broken.html');
  fs.writeFileSync(broken, fs.readFileSync(PAGE, 'utf8').replace(
    /<script id="mocka-data" type="application\/json">[\s\S]*?<\/script>/,
    '<script id="mocka-data" type="application/json">{ nodes: [ }</script>'));
  const B = await openPage(browser, broken);
  R.negativeBrokenJson = {
    errorVisible: await B.page.locator('#error').isVisible(),
    errorText: await B.page.locator('#error').innerText(),
    pageErrors: B.errors.length,
  };
  await B.page.close();

  await browser.close();
  console.log(JSON.stringify(R, null, 2));
})().catch((e) => { console.error('TEST HARNESS FAILED:', e); process.exit(2); });
