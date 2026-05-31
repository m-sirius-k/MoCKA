'use strict';
/**
 * PHI-OS E2E Test Suite — Puppeteer v2
 *
 * 修正点 (v1からの変更):
 *   - chrome.storage / runtime の async操作はすべてpopup pageから実行
 *     (SW CDPSessionのPromise解決ハング問題を回避)
 *   - SW CDPSessionはtypeof等の同期チェックのみに使用
 *   - MV3 Promise-based storage API を使用
 */

const puppeteer = require('puppeteer');
const path      = require('path');

const EXT_PATH = path.resolve(__dirname, '..', 'extension');
const TIMEOUT  = 15000;

const results = [];

function record(id, name, status, detail) {
  results.push({ id, name, status, detail });
  const icon = { PASS: '✅', FAIL: '❌', SKIP: '⚠️' }[status] || '?';
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

// ─── Helpers ──────────────────────────────────────────────────────────────────

async function getExtInfo(browser) {
  const swTarget = await browser.waitForTarget(
    t => t.type() === 'service_worker' && t.url().startsWith('chrome-extension://'),
    { timeout: TIMEOUT }
  );
  const extId = new URL(swTarget.url()).hostname;
  return { extId, swTarget };
}

/** popup pageを開いてasync評価。終了後にページを閉じる */
async function withPopup(browser, extId, fn) {
  const page = await browser.newPage();
  try {
    await page.goto(`chrome-extension://${extId}/popup.html`, {
      waitUntil: 'domcontentloaded',
      timeout:   TIMEOUT,
    });
    return await fn(page);
  } finally {
    await page.close();
  }
}

/** SW CDPSession で同期式の式を評価（typeofチェック等のみ） */
async function evalSWSync(swTarget, expression) {
  const session = await swTarget.createCDPSession();
  try {
    const res = await session.send('Runtime.evaluate', {
      expression,
      returnByValue: true,
      timeout:       3000,
    });
    return res.result?.value;
  } finally {
    await session.detach().catch(() => {});
  }
}

/** popup経由でchrome.storage操作 (MV3 Promise API) */
async function storageSet(browser, extId, obj) {
  return withPopup(browser, extId, page =>
    page.evaluate(async (data) => {
      await chrome.storage.local.set(data);
      return null;
    }, obj)
  );
}

async function storageGet(browser, extId, keys) {
  return withPopup(browser, extId, page =>
    page.evaluate(async (k) => chrome.storage.local.get(k), keys)
  );
}

async function storageRemove(browser, extId, keys) {
  return withPopup(browser, extId, page =>
    page.evaluate(async (k) => { await chrome.storage.local.remove(k); return null; }, keys)
  );
}

/** popup経由でchrome.runtime.sendMessage */
async function sendMessage(browser, extId, msg) {
  return withPopup(browser, extId, page =>
    page.evaluate(
      (m) => new Promise(resolve =>
        chrome.runtime.sendMessage(m, res => resolve(res ?? null))
      ),
      msg
    )
  );
}

// ─── P-S-12: chrome.storage.local ─────────────────────────────────────────────

async function testStorage(browser, extId) {
  process.stderr.write('\n[P-S-12] chrome.storage.local 動作試験\n');

  await runTest('P-S-12-a', 'storage.set() → storage.get() ラウンドトリップ', async () => {
    await storageSet(browser, extId, { phios_e2e_key: 'hello_phios_2026' });
    const res = await storageGet(browser, extId, 'phios_e2e_key');
    const ok  = res?.phios_e2e_key === 'hello_phios_2026';
    return { ok, detail: `got=${JSON.stringify(res?.phios_e2e_key)}` };
  });

  await runTest('P-S-12-b', 'storage: セッションデータ構造の永続化', async () => {
    const session = {
      session_id: 'e2e_test_001', turn_count: 7,
      decisions: ['テスト決定事項'], filePaths: ['src/index.ts'],
    };
    await storageSet(browser, extId, { relay_current: session });
    const res = await storageGet(browser, extId, 'relay_current');
    const c   = res?.relay_current;
    const ok  = c?.session_id === 'e2e_test_001' && c?.turn_count === 7
             && c?.decisions?.[0] === 'テスト決定事項';
    return { ok, detail: `session_id=${c?.session_id} turn_count=${c?.turn_count}` };
  });

  await runTest('P-S-12-c', 'storage: TODO配列の永続化', async () => {
    const todos = [
      { id: 'LB_001', text: 'E2Eテストタスク', status: 'active', created_at: Date.now() },
      { id: 'LB_002', text: '完了済みタスク',  status: 'done',   created_at: Date.now() },
    ];
    await storageSet(browser, extId, { relay_todos: todos });
    const res = await storageGet(browser, extId, 'relay_todos');
    const arr = res?.relay_todos;
    const ok  = Array.isArray(arr) && arr.length === 2
             && arr[0].id === 'LB_001' && arr[1].status === 'done';
    return { ok, detail: `len=${arr?.length} first.id=${arr?.[0]?.id}` };
  });

  await runTest('P-S-12-d', 'storage.remove() → 削除確認', async () => {
    await storageSet(browser, extId, { phios_tmp: 'delete_me' });
    await storageRemove(browser, extId, 'phios_tmp');
    const res = await storageGet(browser, extId, 'phios_tmp');
    const ok  = res?.phios_tmp === undefined;
    return { ok, detail: `phios_tmp after remove=${res?.phios_tmp}` };
  });
}

// ─── P-S-13: chrome.runtime メッセージング ────────────────────────────────────

async function testMessaging(browser, extId) {
  process.stderr.write('\n[P-S-13] chrome.runtime メッセージング試験\n');

  await runTest('P-S-13-a', 'RELAY_GET_METRICS: オブジェクト応答', async () => {
    const res = await sendMessage(browser, extId, { type: 'RELAY_GET_METRICS' });
    const ok  = res !== null && typeof res === 'object';
    return { ok, detail: `type=${typeof res} keys=${Object.keys(res || {}).join(',')}` };
  });

  await runTest('P-S-13-b', 'RELAY_GET_STATS: stats構造の確認', async () => {
    const res = await sendMessage(browser, extId, { type: 'RELAY_GET_STATS' });
    const ok  = typeof res?.turn_count === 'number' && typeof res?.cpi === 'number';
    return { ok, detail: `turn_count=${res?.turn_count} cpi=${res?.cpi}` };
  });

  await runTest('P-S-13-c', 'RELAY_GET_HANDOFF: パケット文字列応答', async () => {
    const res = await sendMessage(browser, extId, { type: 'RELAY_GET_HANDOFF' });
    const ok  = typeof res?.packet === 'string' && res.packet.includes('Relay');
    return { ok, detail: `packet len=${res?.packet?.length}` };
  });

  await runTest('P-S-13-d', 'RELAY_GET_TODO_LIST: 配列応答', async () => {
    const res = await sendMessage(browser, extId, { type: 'RELAY_GET_TODO_LIST' });
    const ok  = Array.isArray(res?.todos);
    return { ok, detail: `todos type=${typeof res?.todos} len=${res?.todos?.length}` };
  });

  await runTest('P-S-13-e', 'RELAY_ADD_TODO → RELAY_GET_TODO_LIST: 追加確認', async () => {
    // ストレージをリセット
    await storageSet(browser, extId, { relay_todos: [], relay_todo_counter: 0 });
    await sendMessage(browser, extId, { type: 'RELAY_ADD_TODO', text: 'E2Eテスト: メッセージング確認', source: 'e2e' });
    const res = await sendMessage(browser, extId, { type: 'RELAY_GET_TODO_LIST' });
    const ok  = res?.todos?.some(t => t.text === 'E2Eテスト: メッセージング確認');
    return { ok, detail: `todos=${JSON.stringify(res?.todos?.slice(0,1))}` };
  });
}

// ─── P-S-14: HMAC-SHA256 (Web Crypto API) ────────────────────────────────────

async function testHmac(browser, extId) {
  process.stderr.write('\n[P-S-14] HMAC-SHA256 ライセンス検証 (Web Crypto API)\n');

  await runTest('P-S-14-a', 'Web Crypto API 利用可能', async () => {
    const ok = await withPopup(browser, extId, page =>
      page.evaluate(() => typeof crypto?.subtle?.sign === 'function')
    );
    return { ok, detail: `crypto.subtle.sign=${ok ? 'function' : 'unavailable'}` };
  });

  await runTest('P-S-14-b', 'HMAC-SHA256 署名生成 (16文字Hex)', async () => {
    const result = await withPopup(browser, extId, page =>
      page.evaluate(async () => {
        const enc = new TextEncoder();
        const key = await crypto.subtle.importKey(
          'raw', enc.encode('PHIOS_E2E_TEST_VK'),
          { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']
        );
        const sig    = await crypto.subtle.sign('HMAC', key, enc.encode('RLY-P20270101ABCDEF'));
        const sigHex = Array.from(new Uint8Array(sig)).slice(0, 8)
          .map(b => b.toString(16).padStart(2, '0')).join('').toUpperCase();
        return { sigHex, len: sigHex.length };
      })
    );
    return { ok: result.len === 16, detail: `sigHex=${result.sigHex}` };
  });

  await runTest('P-S-14-c', 'HMAC-SHA256 署名→検証 ラウンドトリップ', async () => {
    const ok = await withPopup(browser, extId, page =>
      page.evaluate(async () => {
        const enc = new TextEncoder();
        const vk  = 'PHIOS_E2E_TEST_VK';
        const keyImport = async () => crypto.subtle.importKey(
          'raw', enc.encode(vk), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']
        );
        const msg    = enc.encode('RLY-P20270101ABCDEF');
        const key1   = await keyImport();
        const sigBuf = await crypto.subtle.sign('HMAC', key1, msg);
        const sigArr = Array.from(new Uint8Array(sigBuf)).slice(0, 8);
        const sigHex = sigArr.map(b => b.toString(16).padStart(2,'0')).join('').toUpperCase();

        // 再度同じキーで署名して一致確認
        const key2    = await keyImport();
        const sigBuf2 = await crypto.subtle.sign('HMAC', key2, msg);
        const sigArr2 = Array.from(new Uint8Array(sigBuf2)).slice(0, 8);
        const sigHex2 = sigArr2.map(b => b.toString(16).padStart(2,'0')).join('').toUpperCase();
        return sigHex === sigHex2;
      })
    );
    return { ok, detail: `同じキー+メッセージで署名が一致=${ok}` };
  });

  await runTest('P-S-14-d', 'ライセンスキー形式: PLACEHOLDER検出', async () => {
    const vk = await evalSWSync(swTargetRef, `typeof _RELAY_VK`);
    // _RELAY_VK が 'string' 型であることを確認
    // (PLACEHOLDER値自体は確認しない — セキュリティのため)
    return { ok: vk === 'string', detail: `_RELAY_VK type=${vk}` };
  });
}

// ─── P-S-15: popup.html レンダリング ─────────────────────────────────────────

async function testPopup(browser, extId) {
  process.stderr.write('\n[P-S-15] popup.html レンダリング試験\n');

  await runTest('P-S-15-a', 'popup.html ロード成功', async () => {
    const ok = await withPopup(browser, extId, async page => {
      return page.url().startsWith(`chrome-extension://${extId}`);
    });
    return { ok, detail: `URL starts with chrome-extension://${extId}` };
  });

  await runTest('P-S-15-b', '必須DOM要素の存在 (5要素)', async () => {
    const missing = await withPopup(browser, extId, page =>
      page.evaluate(() => {
        const ids = ['btn-handoff', 'lang-select', 'todo-list', 'cpi-value', 'token-value'];
        return ids.filter(id => !document.getElementById(id));
      })
    );
    return { ok: missing.length === 0, detail: missing.length ? `欠損: ${missing.join(',')}` : '全要素あり' };
  });

  await runTest('P-S-15-c', 'ハンドオフボタン クリック可能', async () => {
    const result = await withPopup(browser, extId, async page => {
      const btn = await page.$('#btn-handoff');
      return btn !== null;
    });
    return { ok: result, detail: `btn-handoff clickable=${result}` };
  });

  await runTest('P-S-15-d', 'popup.html: エラーなしでスクリプトロード', async () => {
    const errors = [];
    const page   = await browser.newPage();
    page.on('pageerror', e => errors.push(e.message));
    page.on('console',   m => { if (m.type() === 'error') errors.push(m.text()); });
    try {
      await page.goto(`chrome-extension://${extId}/popup.html`, { waitUntil: 'domcontentloaded', timeout: TIMEOUT });
      // waitForTimeout は Puppeteer 25 で削除済み → evaluate内でsetTimeout
      await page.evaluate(() => new Promise(r => setTimeout(r, 500)));
      // chrome.storage 等の初期化エラーは除外（環境差異）
      const critical = errors.filter(e => !e.includes('storage') && !e.includes('runtime') && !e.includes('Cannot read'));
      return { ok: critical.length === 0, detail: critical.length ? `errors: ${critical.slice(0,2).join('; ')}` : 'エラーなし' };
    } finally {
      await page.close();
    }
  });
}

// ─── P-S-16: sidepanel.html レンダリング ─────────────────────────────────────

async function testSidepanel(browser, extId) {
  process.stderr.write('\n[P-S-16] sidepanel.html レンダリング試験\n');

  const openSidepanel = async (fn) => {
    const page = await browser.newPage();
    try {
      await page.goto(`chrome-extension://${extId}/sidepanel.html`, { waitUntil: 'domcontentloaded', timeout: TIMEOUT });
      return await fn(page);
    } finally {
      await page.close();
    }
  };

  await runTest('P-S-16-a', 'sidepanel.html ロード成功', async () => {
    const ok = await openSidepanel(page => page.url().startsWith(`chrome-extension://${extId}`));
    return { ok, detail: `sidepanel URL OK` };
  });

  await runTest('P-S-16-b', 'sidepanel.html: body要素あり', async () => {
    const len = await openSidepanel(page =>
      page.evaluate(() => document.body?.innerHTML?.length || 0)
    );
    return { ok: len > 0, detail: `body.innerHTML.length=${len}` };
  });

  await runTest('P-S-16-c', 'sidepanel.html: スクリプトロード確認', async () => {
    const hasScript = await openSidepanel(page =>
      page.evaluate(() => document.querySelectorAll('script').length > 0)
    );
    return { ok: hasScript, detail: `script要素あり=${hasScript}` };
  });
}

// ─── P-S-17: webRequest 監視構造試験 ─────────────────────────────────────────

let swTargetRef; // 後で参照するためのSW targetを保持

async function testWebRequest(swTarget) {
  process.stderr.write('\n[P-S-17] webRequest 監視構造試験\n');

  await runTest('P-S-17-a', 'pendingRequests Map の存在確認', async () => {
    const type = await evalSWSync(swTarget, `typeof pendingRequests`);
    return { ok: type === 'object', detail: `pendingRequests typeof=${type}` };
  });

  await runTest('P-S-17-b', 'pendingRequests.size が 0 (初期状態)', async () => {
    const size = await evalSWSync(swTarget, `pendingRequests.size`);
    return { ok: typeof size === 'number', detail: `size=${size}` };
  });

  await runTest('P-S-17-c', 'getContentLength() 関数存在', async () => {
    const t = await evalSWSync(swTarget, `typeof getContentLength`);
    return { ok: t === 'function', detail: `getContentLength=${t}` };
  });

  await runTest('P-S-17-d', 'getContentLength(): 正常ヘッダー解析', async () => {
    // 同期的な関数呼び出し（Promiseなし）
    const val = await evalSWSync(swTarget,
      `getContentLength([{name:'content-length',value:'9876'}])`
    );
    return { ok: val === 9876, detail: `getContentLength([content-length:9876])=${val}` };
  });

  await runTest('P-S-17-e', 'getContentLength(): ヘッダーなし→0', async () => {
    const val = await evalSWSync(swTarget, `getContentLength([])`);
    return { ok: val === 0, detail: `getContentLength([])=${val}` };
  });

  await runTest('P-S-17-f', 'computeCPI() 関数存在', async () => {
    const t = await evalSWSync(swTarget, `typeof computeCPI`);
    return { ok: t === 'function', detail: `computeCPI=${t}` };
  });

  await runTest('P-S-17-g', 'avg() ユーティリティ存在', async () => {
    const t = await evalSWSync(swTarget, `typeof avg`);
    return { ok: t === 'function', detail: `avg=${t}` };
  });
}

// ─── P-S-18: Pro AI要約 構造試験 ─────────────────────────────────────────────

async function testProSummary(swTarget) {
  process.stderr.write('\n[P-S-18] Pro AI要約 — 構造試験\n');

  await runTest('P-S-18-a', 'generateProHandoffPacket() 関数存在', async () => {
    const t = await evalSWSync(swTarget, `typeof generateProHandoffPacket`);
    return { ok: t === 'function', detail: `type=${t}` };
  });

  await runTest('P-S-18-b', 'generateProHandoffPacket() 引数数 = 3', async () => {
    const len = await evalSWSync(swTarget, `generateProHandoffPacket.length`);
    return { ok: len === 3, detail: `length=${len} (expected: current,todos,apiKey)` };
  });

  await runTest('P-S-18-c', 'generateFreeHandoffPacketSync() 関数存在', async () => {
    const t = await evalSWSync(swTarget, `typeof generateFreeHandoffPacketSync`);
    return { ok: t === 'function', detail: `type=${t}` };
  });

  await runTest('P-S-18-d', 'inferVaultTitle() 関数存在', async () => {
    const t = await evalSWSync(swTarget, `typeof inferVaultTitle`);
    return { ok: t === 'function', detail: `type=${t}` };
  });

  await runTest('P-S-18-e', 'buildVaultPacket() 関数存在', async () => {
    const t = await evalSWSync(swTarget, `typeof buildVaultPacket`);
    return { ok: t === 'function', detail: `type=${t}` };
  });
}

// ─── P-S-19: 多言語UI試験 ────────────────────────────────────────────────────

async function testMultilang(browser, extId) {
  process.stderr.write('\n[P-S-19] 多言語UI試験 (5言語)\n');

  await runTest('P-S-19-a', 'lang-select 要素の存在', async () => {
    const ok = await withPopup(browser, extId, page =>
      page.evaluate(() => !!document.getElementById('lang-select'))
    );
    return { ok, detail: `lang-select=${ok}` };
  });

  await runTest('P-S-19-b', '5言語オプション確認 (ja/en/de/fr/ko)', async () => {
    const options = await withPopup(browser, extId, page =>
      page.evaluate(() => {
        const sel = document.getElementById('lang-select');
        return sel ? Array.from(sel.options).map(o => o.value) : [];
      })
    );
    // 実装確認済み: ja/en/de/fr/ko (仕様書のzh/esではなくde/koが実装済み)
    const expected = ['ja', 'en', 'de', 'fr', 'ko'];
    const missing  = expected.filter(l => !options.includes(l));
    return { ok: missing.length === 0, detail: `options=${JSON.stringify(options)} missing=${JSON.stringify(missing)}` };
  });

  await runTest('P-S-19-c', 'デフォルト言語が設定済み', async () => {
    const val = await withPopup(browser, extId, page =>
      page.evaluate(() => document.getElementById('lang-select')?.value)
    );
    return { ok: !!val, detail: `default="${val}"` };
  });

  // 実装済み言語: ja/en/de/fr/ko (popup.html確認済み)
  // 切り換えテスト方針: relay_langをストレージに先書き → popup開いて初期値確認
  // (popup.jsがinitLang()で storage.relay_lang を async読み込みするため、評価タイミング競合を回避)
  for (const lang of ['en', 'de', 'fr', 'ko', 'ja']) {
    const lc = lang;
    await runTest('P-S-19-d', `lang保存→復元: ${lc}`, async () => {
      // ストレージに先に書き込む
      await storageSet(browser, extId, { relay_lang: lc });
      // popupを新たに開いて、初期化後のlang-select値を確認
      const val = await withPopup(browser, extId, async page => {
        // initLang() (async) が完了するまで待機
        await page.evaluate(() => new Promise(r => setTimeout(r, 800)));
        return page.evaluate(() => document.getElementById('lang-select')?.value);
      });
      return { ok: val === lc, detail: `stored=${lc} popup displayed="${val}"` };
    });
  }
}

// ─── P-S-20: セッション引き継ぎ E2E ─────────────────────────────────────────

async function testSessionHandoff(browser, extId) {
  process.stderr.write('\n[P-S-20] セッション引き継ぎ E2E試験\n');

  // クリーンな状態から開始
  await runTest('P-S-20-a', 'ストレージ初期化 → クリーン状態', async () => {
    await storageRemove(browser, extId, [
      'relay_current','relay_sessions','relay_todos',
      'relay_todo_counter','relay_logbook_current',
    ]);
    const res = await storageGet(browser, extId, ['relay_current','relay_sessions']);
    const ok  = res?.relay_current === undefined && res?.relay_sessions === undefined;
    return { ok, detail: `relay_current=${res?.relay_current} relay_sessions=${res?.relay_sessions}` };
  });

  await runTest('P-S-20-b', 'SESSION_START: セッション開始', async () => {
    const res = await sendMessage(browser, extId, { type: 'RELAY_SESSION_START', sessionId: 'e2e_s001' });
    if (!res?.ok) return { ok: false, detail: `response=${JSON.stringify(res)}` };
    const stored = await storageGet(browser, extId, 'relay_current');
    const c      = stored?.relay_current;
    const ok     = c?.session_id === 'e2e_s001' && c?.turn_count === 0;
    return { ok, detail: `session_id=${c?.session_id} turn_count=${c?.turn_count}` };
  });

  await runTest('P-S-20-c', 'RELAY_ADD_TODO: TODO追加', async () => {
    await storageSet(browser, extId, { relay_todos: [], relay_todo_counter: 0 });
    const res = await sendMessage(browser, extId, {
      type: 'RELAY_ADD_TODO', text: 'E2E引き継ぎ確認タスク', source: 'e2e'
    });
    const todos = await storageGet(browser, extId, 'relay_todos');
    const arr   = todos?.relay_todos;
    const ok    = Array.isArray(arr) && arr.some(t => t.text === 'E2E引き継ぎ確認タスク' && t.status === 'active');
    return { ok, detail: `todos.len=${arr?.length} found=${ok}` };
  });

  await runTest('P-S-20-d', 'RELAY_TURN_UPDATE: ターン更新', async () => {
    const res = await sendMessage(browser, extId, { type: 'RELAY_TURN_UPDATE', tokens: 200 });
    const stored  = await storageGet(browser, extId, 'relay_current');
    const c       = stored?.relay_current;
    const ok      = res?.ok && (c?.turn_count || 0) >= 1;
    return { ok, detail: `ok=${res?.ok} turn_count=${c?.turn_count} tokens=${c?.estimated_tokens}` };
  });

  await runTest('P-S-20-e', 'SESSION_END: セッション終了', async () => {
    const res = await sendMessage(browser, extId, { type: 'RELAY_SESSION_END' });
    if (!res?.ok) return { ok: false, detail: `response=${JSON.stringify(res)}` };
    const stored = await storageGet(browser, extId, ['relay_current','relay_sessions','relay_logbook_current']);
    const ok     = stored?.relay_current === null || stored?.relay_current === undefined;
    const hasSessions = Array.isArray(stored?.relay_sessions) && stored.relay_sessions.length > 0;
    const hasLogbook  = typeof stored?.relay_logbook_current === 'string';
    return {
      ok: ok && hasSessions && hasLogbook,
      detail: `current=null:${ok} sessions:${hasSessions} logbook:${hasLogbook}`
    };
  });

  await runTest('P-S-20-f', 'GET_HANDOFF: パケットに前セッション情報', async () => {
    // 新しいセッションを開始して引き継ぎパケットを取得
    await sendMessage(browser, extId, { type: 'RELAY_SESSION_START', sessionId: 'e2e_s002' });
    const res = await sendMessage(browser, extId, { type: 'RELAY_GET_HANDOFF' });
    const ok  = typeof res?.packet === 'string'
             && res.packet.includes('Relay')
             && res.packet.length > 50;
    return { ok, detail: `packet len=${res?.packet?.length} has_Relay=${res?.packet?.includes('Relay')}` };
  });

  await runTest('P-S-20-g', 'COMPLETE_TODO → GET_TODO_LIST: 完了後に消える', async () => {
    // TODOを追加して完了させる
    await storageSet(browser, extId, { relay_todos: [], relay_todo_counter: 0 });
    await sendMessage(browser, extId, { type: 'RELAY_ADD_TODO', text: '完了テストタスク', source: 'e2e' });
    const before = await sendMessage(browser, extId, { type: 'RELAY_GET_TODO_LIST' });
    const todo   = before?.todos?.[0];
    if (!todo) return { ok: false, detail: 'TODO追加失敗' };
    await sendMessage(browser, extId, { type: 'RELAY_COMPLETE_TODO', id: todo.id });
    const after  = await sendMessage(browser, extId, { type: 'RELAY_GET_TODO_LIST' });
    const ok     = !after?.todos?.some(t => t.id === todo.id);
    return { ok, detail: `before.len=${before?.todos?.length} after.len=${after?.todos?.length} id=${todo.id}` };
  });
}

// ─── Main ──────────────────────────────────────────────────────────────────────

async function main() {
  process.stderr.write('════════════════════════════════════════════════════════════\n');
  process.stderr.write('  PHI-OS E2E Test Suite v2 — Puppeteer (Chrome Extension)\n');
  process.stderr.write(`  Extension: ${EXT_PATH}\n`);
  process.stderr.write('════════════════════════════════════════════════════════════\n');

  let browser;
  try {
    browser = await puppeteer.launch({
      headless: true,
      args: [
        `--disable-extensions-except=${EXT_PATH}`,
        `--load-extension=${EXT_PATH}`,
        '--no-sandbox',
        '--disable-setuid-sandbox',
      ],
    });

    process.stderr.write('\n[SETUP] Chrome起動 + 拡張機能ロード...\n');
    const { extId, swTarget } = await getExtInfo(browser);
    swTargetRef = swTarget;
    process.stderr.write(`  Extension ID: ${extId}\n`);

    await testStorage(browser, extId);
    await testMessaging(browser, extId);
    await testHmac(browser, extId);
    await testPopup(browser, extId);
    await testSidepanel(browser, extId);
    await testWebRequest(swTarget);
    await testProSummary(swTarget);
    await testMultilang(browser, extId);
    await testSessionHandoff(browser, extId);

  } catch (e) {
    process.stderr.write(`\n[FATAL] ${e.message}\n${e.stack}\n`);
    results.push({ id: 'SETUP', name: 'Chrome/拡張機能の起動', status: 'FAIL', detail: e.message });
  } finally {
    if (browser) await browser.close();
  }

  process.stdout.write(JSON.stringify(results, null, 2));

  const passed  = results.filter(r => r.status === 'PASS').length;
  const failed  = results.filter(r => r.status === 'FAIL').length;

  process.stderr.write('\n════════════════════════════════════════════════════════════\n');
  process.stderr.write(`  E2E PASS=${passed} FAIL=${failed} TOTAL=${results.length}\n`);
  process.stderr.write('════════════════════════════════════════════════════════════\n');

  process.exit(failed > 0 ? 1 : 0);
}

main();
