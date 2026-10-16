// 仮想Synapseシミュレーター画面の試験（ブラウザ）：各ボタンの結果が期待どおり画面に出るか
// 使い方: PAGE=<index.html> node tests/run_synapse_ui_check.js
const { chromium } = require('./_browser_env').requireBrowserPrereqs();
const path = require('path');

const PAGE = path.resolve(process.env.PAGE);

(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const page = await browser.newPage();
  const errors = [], external = [];
  await page.route('**/*', (route) => {
    const url = route.request().url();
    if (url.startsWith('file://')) return route.continue();
    external.push(url); return route.abort();
  });
  page.on('pageerror', (e) => errors.push(String(e.message)));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto('file://' + PAGE);
  await page.waitForTimeout(300);

  const R = { checks: {}, pageErrors: errors, externalRequests: external };
  const verdict = () => page.locator('#verdict').innerText();
  const edges = () => page.locator('#edges').innerText();
  const cpRows = () => page.locator('#cps tr').allInnerTexts();

  R.checks.startupVerdictPass = (await verdict()).includes('合格');
  R.checks.startupAllVerified = ((await edges()).match(/= VERIFIED/g) || []).length === 4;

  await page.click('#btn-a');
  R.checks.testA = (await verdict()).includes('edge_hg_to_auth') && (await verdict()).includes('UNAUTHORIZED_APPROVER');
  await page.click('#btn-b');
  R.checks.testB = (await verdict()).includes('edge_auth_to_rt') && (await verdict()).includes('UNKNOWN_NO_AUTHORIZATION');
  await page.click('#btn-c');
  R.checks.testC = (await verdict()).includes('edge_rt_to_cons') && (await verdict()).includes('AUTH_ID_MISMATCH');
  R.checks.testCLogHasBlocked = (await page.locator('#log').innerText()).includes('[BLOCKED] edge_rt_to_cons');
  R.checks.testCCpFailCount = (await cpRows()).filter((r) => r.includes('FAIL')).length;

  await page.click('#btn-all');
  R.checks.allSummaryHasThree = ((await verdict()).match(/遮断 edge_/g) || []).length === 3;

  await page.click('#btn-run');
  R.checks.runPass = (await verdict()).includes('合格');
  R.checks.runCpAllPass = (await cpRows()).filter((r) => r.includes('PASS')).length === 5;

  await page.screenshot({ path: process.env.SHOT || '/dev/null' }).catch(() => {});
  await browser.close();
  console.log(JSON.stringify(R, null, 2));
})().catch((e) => { console.error('TEST HARNESS FAILED:', e); process.exit(2); });
