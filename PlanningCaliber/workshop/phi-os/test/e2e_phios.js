'use strict';
/**
 * PHI-OS E2E Test Suite — Puppeteer
 * PHI OS v1.0.0 Chrome拡張のブラウザ環境依存テスト
 *
 * 対象: extension/ (PHI OS Persistent History Interface)
 */

const puppeteer = require('puppeteer');
const path      = require('path');

const EXT_PATH = path.resolve(__dirname, '..', 'extension');
const TIMEOUT  = 15000;
const results  = [];

function record(id, name, status, detail) {
  results.push({ id, name, status, detail });
  process.stderr.write(`  [${status}] ${id}: ${name}\n`);
  if (status !== 'PASS') process.stderr.write(`         ${detail}\n`);
}

async function runTest(id, name, fn) {
  try {
    const { ok, detail } = await Promise.race([
      fn(),
      new Promise((_, rej) => setTimeout(() => rej(new Error('TIMEOUT')), TIMEOUT)),
    ]);
    record(id, name, ok ? 'PASS' : 'FAIL', detail);
  } catch (e) {
    record(id, name, 'FAIL', `EXCEPTION: ${e.message}`);
  }
}

async function getExtInfo(browser) {
  const swTarget = await browser.waitForTarget(
    t => t.type() === 'service_worker' && t.url().startsWith('chrome-extension://'),
    { timeout: TIMEOUT }
  );
  return { extId: new URL(swTarget.url()).hostname, swTarget };
}

async function withPage(browser, extId, relPath, fn) {
  const page = await browser.newPage();
  try {
    await page.goto(`chrome-extension://${extId}/${relPath}`, {
      waitUntil: 'domcontentloaded', timeout: TIMEOUT
    });
    return await fn(page);
  } finally {
    await page.close();
  }
}

async function storageSet(browser, extId, obj) {
  return withPage(browser, extId, 'ui/options.html', page =>
    page.evaluate(async d => { await chrome.storage.local.set(d); return null; }, obj)
  );
}

async function storageGet(browser, extId, keys) {
  return withPage(browser, extId, 'ui/options.html', page =>
    page.evaluate(async k => chrome.storage.local.get(k), keys)
  );
}

async function storageRemove(browser, extId, keys) {
  return withPage(browser, extId, 'ui/options.html', page =>
    page.evaluate(async k => { await chrome.storage.local.remove(k); return null; }, keys)
  );
}

async function sendMsg(browser, extId, msg) {
  return withPage(browser, extId, 'ui/options.html', page =>
    page.evaluate(m => new Promise(resolve =>
      chrome.runtime.sendMessage(m, res => resolve(res ?? null))
    ), msg)
  );
}

async function evalSWSync(swTarget, expression) {
  const session = await swTarget.createCDPSession();
  try {
    const res = await session.send('Runtime.evaluate', {
      expression, returnByValue: true, timeout: 3000
    });
    return res.result?.value;
  } finally {
    await session.detach().catch(() => {});
  }
}

// ─── P-S-11: chrome.storage (PHI OS keys) ───────────────────────────────────

async function testStorage(browser, extId) {
  process.stderr.write('\n[P-S-11] chrome.storage.local (PHI OS phi_* keys)\n');

  await runTest('P-S-11-a', 'storage set/get ラウンドトリップ', async () => {
    await storageSet(browser, extId, { phios_e2e_test: 'phi_os_2026' });
    const res = await storageGet(browser, extId, 'phios_e2e_test');
    const ok  = res?.phios_e2e_test === 'phi_os_2026';
    return { ok, detail: `got=${JSON.stringify(res?.phios_e2e_test)}` };
  });

  await runTest('P-S-11-b', 'phi_schema_version の読み書き', async () => {
    await storageSet(browser, extId, { phi_schema_version: '1.0.0' });
    const res = await storageGet(browser, extId, 'phi_schema_version');
    return { ok: res?.phi_schema_version === '1.0.0', detail: `got=${res?.phi_schema_version}` };
  });

  await runTest('P-S-11-c', 'phi_commit_index 配列の永続化', async () => {
    const idx = ['commit_001', 'commit_002'];
    await storageSet(browser, extId, { phi_commit_index: idx });
    const res = await storageGet(browser, extId, 'phi_commit_index');
    const ok  = JSON.stringify(res?.phi_commit_index) === JSON.stringify(idx);
    return { ok, detail: `got=${JSON.stringify(res?.phi_commit_index)}` };
  });

  await runTest('P-S-11-d', 'storage.remove() 削除確認', async () => {
    await storageSet(browser, extId, { phi_tmp_test: 'delete_me' });
    await storageRemove(browser, extId, 'phi_tmp_test');
    const res = await storageGet(browser, extId, 'phi_tmp_test');
    return { ok: res?.phi_tmp_test === undefined, detail: `after remove=${res?.phi_tmp_test}` };
  });
}

// ─── P-S-12: chrome.runtime メッセージング ──────────────────────────────────

async function testMessaging(browser, extId) {
  process.stderr.write('\n[P-S-12] chrome.runtime メッセージング試験\n');

  await runTest('P-S-12-a', 'PHI_HEARTBEAT → ok:true,ts', async () => {
    const res = await sendMsg(browser, extId, { type: 'PHI_HEARTBEAT' });
    const ok  = res?.ok === true && typeof res?.ts === 'number';
    return { ok, detail: `ok=${res?.ok} ts=${res?.ts}` };
  });

  await runTest('P-S-12-b', 'PHI_GET_STATUS → commit_count,last_commit_ts', async () => {
    const res = await sendMsg(browser, extId, { type: 'PHI_GET_STATUS' });
    const ok  = typeof res?.commit_count === 'number';
    return { ok, detail: `commit_count=${res?.commit_count} last_ts=${res?.last_commit_ts}` };
  });

  await runTest('P-S-12-c', 'PHI_REGISTER_PRODUCT → ok:true', async () => {
    const res = await sendMsg(browser, extId, {
      type: 'PHI_REGISTER_PRODUCT', product: 'relay', extensionId: 'test_ext_id'
    });
    return { ok: res?.ok === true, detail: `ok=${res?.ok}` };
  });

  await runTest('P-S-12-d', 'PHI_PANEL_MODE_CHANGED (sidepanel) → ok:true', async () => {
    const res = await sendMsg(browser, extId, {
      type: 'PHI_PANEL_MODE_CHANGED', mode: 'sidepanel'
    });
    return { ok: res?.ok === true, detail: `ok=${res?.ok}` };
  });

  await runTest('P-S-12-e', 'PHI_PANEL_MODE_CHANGED (popup) → ok:true', async () => {
    const res = await sendMsg(browser, extId, {
      type: 'PHI_PANEL_MODE_CHANGED', mode: 'popup'
    });
    return { ok: res?.ok === true, detail: `ok=${res?.ok}` };
  });

  await runTest('P-S-12-f', 'PHI_CLEAR_OLD_DATA → ok:true,deleted', async () => {
    const res = await sendMsg(browser, extId, { type: 'PHI_CLEAR_OLD_DATA' });
    const ok  = res?.ok === true && typeof res?.deleted === 'number';
    return { ok, detail: `ok=${res?.ok} deleted=${res?.deleted}` };
  });

  await runTest('P-S-12-g', '不明typeはerrorを返す', async () => {
    const res = await sendMsg(browser, extId, { type: 'PHI_UNKNOWN_9999' });
    const ok  = res !== null && (res?.error !== undefined || res?.ok === false);
    return { ok, detail: `res=${JSON.stringify(res)}` };
  });
}

// ─── P-S-13: ui/options.html レンダリング ───────────────────────────────────

async function testOptionsPage(browser, extId) {
  process.stderr.write('\n[P-S-13] ui/options.html レンダリング試験\n');

  await runTest('P-S-13-a', 'ui/options.html ロード成功', async () => {
    const ok = await withPage(browser, extId, 'ui/options.html', page =>
      page.url().startsWith(`chrome-extension://${extId}`)
    );
    return { ok, detail: `URL starts with chrome-extension://${extId}` };
  });

  await runTest('P-S-13-b', 'PHI-OS ダッシュボード必須要素確認', async () => {
    const missing = await withPage(browser, extId, 'ui/options.html', page =>
      page.evaluate(() => {
        const ids = ['btn-panel', 'lang-select', 'app'];
        return ids.filter(id => !document.getElementById(id));
      })
    );
    return { ok: missing.length === 0, detail: missing.length ? `欠損: ${missing.join(',')}` : '全要素あり' };
  });

  await runTest('P-S-13-c', 'lang-select: 5言語オプション (ja/en/zh/ko/es)', async () => {
    const options = await withPage(browser, extId, 'ui/options.html', page =>
      page.evaluate(() => {
        const sel = document.getElementById('lang-select');
        return sel ? Array.from(sel.options).map(o => o.value) : [];
      })
    );
    const expected = ['ja', 'en', 'zh', 'ko', 'es'];
    const missing  = expected.filter(l => !options.includes(l));
    return {
      ok: missing.length === 0,
      detail: `options=${JSON.stringify(options)} missing=${JSON.stringify(missing)}`
    };
  });

  await runTest('P-S-13-d', 'PHI-OS ロゴ/ヘッダー存在確認', async () => {
    const ok = await withPage(browser, extId, 'ui/options.html', page =>
      page.evaluate(() => {
        const header = document.querySelector('.phi-header, .phi-logo, header');
        return !!header;
      })
    );
    return { ok, detail: `PHI OS ヘッダーあり=${ok}` };
  });
}

// ─── P-S-14: ui/sidepanel.html レンダリング ─────────────────────────────────

async function testSidepanel(browser, extId) {
  process.stderr.write('\n[P-S-14] ui/sidepanel.html レンダリング試験\n');

  await runTest('P-S-14-a', 'ui/sidepanel.html ロード成功', async () => {
    const ok = await withPage(browser, extId, 'ui/sidepanel.html', page =>
      page.url().startsWith(`chrome-extension://${extId}`)
    );
    return { ok, detail: `URL=${ok}` };
  });

  await runTest('P-S-14-b', 'sidepanel: body要素あり', async () => {
    const len = await withPage(browser, extId, 'ui/sidepanel.html', page =>
      page.evaluate(() => document.body?.innerHTML?.length || 0)
    );
    return { ok: len > 0, detail: `body.innerHTML.length=${len}` };
  });

  await runTest('P-S-14-c', 'sidepanel: スクリプトまたはリンクあり', async () => {
    const count = await withPage(browser, extId, 'ui/sidepanel.html', page =>
      page.evaluate(() => document.querySelectorAll('script,link').length)
    );
    return { ok: count > 0, detail: `script/link count=${count}` };
  });
}

// ─── P-S-15: Service Worker 関数構造 ────────────────────────────────────────

async function testSWStructure(swTarget) {
  process.stderr.write('\n[P-S-15] Service Worker 関数構造試験\n');

  const fns = [
    ['ensureSchemaVersion', 'ensureSchemaVersion'],
    ['registerProduct',     'registerProduct'],
    ['handleMessage',       'handleMessage'],
  ];
  for (const [name, expr] of fns) {
    const n = name;
    await runTest('P-S-15', `SW関数: ${n}()`, async () => {
      const t = await evalSWSync(swTarget, `typeof ${expr}`);
      return { ok: t === 'function', detail: `${expr} typeof=${t}` };
    });
  }

  await runTest('P-S-15-d', 'SCHEMA_VERSION = "1.0.0"', async () => {
    const v = await evalSWSync(swTarget, `SCHEMA_VERSION`);
    return { ok: v === '1.0.0', detail: `SCHEMA_VERSION=${v}` };
  });

  await runTest('P-S-15-e', 'KNOWN_PRODUCTS 配列長 = 3', async () => {
    const len = await evalSWSync(swTarget, `KNOWN_PRODUCTS.length`);
    return { ok: len === 3, detail: `KNOWN_PRODUCTS.length=${len}` };
  });

  await runTest('P-S-15-f', "KNOWN_PRODUCTS に 'relay' 含む", async () => {
    const ok = await evalSWSync(swTarget, `KNOWN_PRODUCTS.includes('relay')`);
    return { ok: ok === true, detail: `includes('relay')=${ok}` };
  });
}

// ─── P-S-16: スキーマバージョン初期化 E2E ────────────────────────────────────

async function testSchemaInit(browser, extId) {
  process.stderr.write('\n[P-S-16] スキーマバージョン初期化 E2E\n');

  await runTest('P-S-16-a', 'phi_schema_version: 拡張起動後に設定済み', async () => {
    // 拡張が起動したので、schemaバージョンが設定されているはず
    const res = await storageGet(browser, extId, 'phi_schema_version');
    const ok  = res?.phi_schema_version === '1.0.0';
    return { ok, detail: `phi_schema_version=${res?.phi_schema_version}` };
  });

  await runTest('P-S-16-b', 'PHI_GET_STATUS: commit_count は数値', async () => {
    const res = await sendMsg(browser, extId, { type: 'PHI_GET_STATUS' });
    const ok  = typeof res?.commit_count === 'number' && res.commit_count >= 0;
    return { ok, detail: `commit_count=${res?.commit_count}` };
  });

  await runTest('P-S-16-c', 'phi_product_id_relay 登録後に読み取り可能', async () => {
    await sendMsg(browser, extId, {
      type: 'PHI_REGISTER_PRODUCT', product: 'relay', extensionId: 'e2e_relay_id'
    });
    const res = await storageGet(browser, extId, 'phi_product_id_relay');
    const ok  = res?.phi_product_id_relay === 'e2e_relay_id';
    return { ok, detail: `phi_product_id_relay=${res?.phi_product_id_relay}` };
  });
}

// ─── Main ────────────────────────────────────────────────────────────────────

async function main() {
  process.stderr.write('════════════════════════════════════════════════════════════\n');
  process.stderr.write('  PHI-OS E2E Test Suite — Puppeteer (PHI OS v1.0.0)\n');
  process.stderr.write(`  Extension: ${EXT_PATH}\n`);
  process.stderr.write('════════════════════════════════════════════════════════════\n');

  let browser;
  try {
    // PUPPETEER_HEADLESS=false の場合は非ヘッドレス
    // macOS CI では Google Chrome がheadless+extension で SW を登録しないため
    const useHeadless = process.env.PUPPETEER_HEADLESS !== 'false';
    const launchOptions = {
      headless: useHeadless,
      args: [
        `--disable-extensions-except=${EXT_PATH}`,
        `--load-extension=${EXT_PATH}`,
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
      ],
    };
    if (process.env.PUPPETEER_EXECUTABLE_PATH) {
      launchOptions.executablePath = process.env.PUPPETEER_EXECUTABLE_PATH;
    }
    process.stderr.write(`  headless=${useHeadless} exec=${launchOptions.executablePath || 'bundled'}\n`);
    browser = await puppeteer.launch(launchOptions);
    process.stderr.write('\n[SETUP] Chrome起動 + PHI OS 拡張ロード...\n');

    const { extId, swTarget } = await getExtInfo(browser);
    process.stderr.write(`  Extension ID: ${extId}\n`);

    await testStorage(browser, extId);
    await testMessaging(browser, extId);
    await testOptionsPage(browser, extId);
    await testSidepanel(browser, extId);
    await testSWStructure(swTarget);
    await testSchemaInit(browser, extId);

  } catch (e) {
    process.stderr.write(`\n[FATAL] ${e.message}\n${e.stack}\n`);
    results.push({ id: 'SETUP', name: 'Chrome/拡張起動', status: 'FAIL', detail: e.message });
  } finally {
    if (browser) await browser.close();
  }

  process.stdout.write(JSON.stringify(results, null, 2));

  const passed = results.filter(r => r.status === 'PASS').length;
  const failed = results.filter(r => r.status === 'FAIL').length;
  process.stderr.write('\n════════════════════════════════════════════════════════════\n');
  process.stderr.write(`  E2E PASS=${passed} FAIL=${failed} TOTAL=${results.length}\n`);
  process.stderr.write('════════════════════════════════════════════════════════════\n');

  process.exit(failed > 0 ? 1 : 0);
}

main();
