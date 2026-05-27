// Relay License Worker — Cloudflare Workers
// Stripe Webhook → キー生成 → Resendでメール送信
//
// ⚠️  デプロイ前に以下の環境変数をCloudflare Workerダッシュボードで設定すること
//    RELAY_SECRET      … HMAC署名キー (background.jsの _RELAY_VK と完全一致)
//    RELAY_KV          … KV Namespaceバインディング
//    RESEND_API_KEY    … Resend APIキー
//    RELAY_WEBHOOK_SECRET … Stripe Webhook署名シークレット (オプション検証用)
//
// ⚠️  Orchestraのworker.jsは上書き禁止。本ファイルはRelay専用の独立ファイル。
//
// Cloudflare デプロイ手順:
//   1. wrangler.toml を作成して KV namespace binding を設定
//   2. wrangler deploy relay-license-worker.js --name relay-license
//   3. Stripe Webhook URL = https://relay-license.<your-subdomain>.workers.dev/relay/checkout
//   4. Relay健全性確認 = GET /relay/health

// ── HMAC-SHA256 署名生成 ────────────────────────────────────────────────────────

async function hmacSign(prefix, expiryStr, serialHex, secret) {
  const enc = new TextEncoder();
  const keyMaterial = await crypto.subtle.importKey(
    'raw', enc.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']
  );
  const msg    = enc.encode(prefix + expiryStr + serialHex);
  const sigBuf = await crypto.subtle.sign('HMAC', keyMaterial, msg);
  const sigArr = Array.from(new Uint8Array(sigBuf)).slice(0, 8);
  return sigArr.map(b => b.toString(16).padStart(2, '0')).join('').toUpperCase();
}

// ── 有効期限計算 (30日後) ───────────────────────────────────────────────────────

function calcExpiry() {
  const expiry = new Date();
  expiry.setDate(expiry.getDate() + 30);
  const y = expiry.getFullYear();
  const m = String(expiry.getMonth() + 1).padStart(2, '0');
  const d = String(expiry.getDate()).padStart(2, '0');
  return `${y}${m}${d}`;
}

// ── シリアル番号管理 (KV使用) ────────────────────────────────────────────────────

async function nextSerial(env) {
  const current = parseInt(await env.RELAY_KV.get('relay_serial') || '0');
  const next    = current + 1;
  await env.RELAY_KV.put('relay_serial', String(next));
  return next.toString(16).padStart(6, '0').toUpperCase();
}

// ── Relayキー生成 ───────────────────────────────────────────────────────────────
// 形式: RLY-P-{YYYYMMDD:8}{serial:6}{sig:16}
//       RLY-O-{YYYYMMDD:8}{serial:6}{sig:16}

async function generateRelayKey(plan, env) {
  const prefix    = plan === 'one' ? 'RLY-O' : 'RLY-P';
  const expiryStr = calcExpiry();
  const serialHex = await nextSerial(env);
  const sigHex    = await hmacSign(prefix, expiryStr, serialHex, env.RELAY_SECRET);
  const key       = `${prefix}-${expiryStr}${serialHex}${sigHex}`;
  const expiryDisplay = `${expiryStr.slice(0,4)}/${expiryStr.slice(4,6)}/${expiryStr.slice(6,8)}`;
  return { key, expiryStr, expiryDisplay, serialHex };
}

// ── ランダムサフィックス生成 (Web Crypto) ──
function generateRandomSuffix(len) {
  const arr = new Uint8Array(Math.ceil(len / 2));
  crypto.getRandomValues(arr);
  return Array.from(arr).map(b => b.toString(16).padStart(2, '0')).join('').toUpperCase().slice(0, len);
}

// ── Stripeクーポン作成 ──
async function createStripeCoupon(couponCode, env) {
  const res = await fetch('https://api.stripe.com/v1/coupons', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${env.STRIPE_SECRET_KEY}`,
      'Content-Type':  'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
      'id':              couponCode,
      'percent_off':     '20',
      'duration':        'once',
      'max_redemptions': '1',
      'redeem_by':       String(Math.floor(Date.now() / 1000) + 30 * 24 * 60 * 60),
    }),
  });
  return res.ok;
}

// ── クロスクーポン HTMLブロック (Relayテーマ) ──
function buildCouponHtml(couponCode, sisterProduct, targetUrl) {
  return `
    <hr style="border:none;border-top:1px solid #1e3a5f;margin:20px 0;">
    <div style="background:#111827;border:1px solid #38bdf8;border-radius:6px;padding:18px;">
      <p style="margin:0 0 10px;color:#38bdf8;font-size:13px;font-weight:bold;">🎁 姉妹製品を20% OFFでお試しください</p>
      <p style="margin:0 0 12px;color:#94a3b8;font-size:12px;">${sisterProduct}をご購入いただいた感謝として特別価格をご提供します。</p>
      <div style="background:#0a0e1a;border-radius:4px;padding:10px 14px;margin-bottom:12px;">
        <p style="margin:0 0 4px;color:#64748b;font-size:11px;letter-spacing:1px;">クーポンコード</p>
        <p style="margin:0;font-size:14px;letter-spacing:2px;color:#38bdf8;">${couponCode}</p>
      </div>
      <p style="margin:0 0 14px;color:#64748b;font-size:11px;">有効期限: 30日間 / 1回限り有効</p>
      <a href="${targetUrl}?coupon=${couponCode}" style="display:inline-block;background:#38bdf8;color:#000;padding:10px 20px;border-radius:4px;text-decoration:none;font-size:12px;font-weight:bold;">${sisterProduct}を試す（20% OFF）</a>
    </div>`;
}

// ── Resendでライセンスキーをメール送信 ───────────────────────────────────────────

async function sendRelayKeyEmail(toEmail, plan, key, expiryDisplay, env, couponHtml = '') {
  const planName = plan === 'one' ? 'Relay One' : 'Relay Pro';
  const planFeatures = plan === 'one'
    ? '• AI引き継ぎ要約 (Claude API)\n• 密度スコアリングエンジン\n• Vault（無制限Logbook）\n• コンテキスト自動注入'
    : '• AI引き継ぎ要約 (Claude API)\n• Logbook履歴 (5件)';

  const body = {
    from:    'Relay <noreply@nsjp.org>',
    to:      [toEmail],
    subject: `Relay ライセンスキーのご案内 — ${planName}`,
    html: `
      <div style="font-family:ui-monospace,'Cascadia Code',monospace;background:#0a0e1a;color:#e2e8f0;padding:32px;border-radius:10px;max-width:480px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px;">
          <div style="font-size:22px;color:#38bdf8;font-weight:800;">RELAY</div>
          <div style="font-size:12px;color:#38bdf8;background:rgba(56,189,248,.1);border:1px solid rgba(56,189,248,.3);border-radius:4px;padding:2px 8px;letter-spacing:1px;">${plan.toUpperCase()}</div>
        </div>
        <p style="color:#94a3b8;margin-bottom:20px;">ご購入ありがとうございます。以下のライセンスキーで ${planName} の機能が有効になります。</p>
        <div style="background:#111827;border:1px solid #38bdf8;border-radius:6px;padding:16px;margin-bottom:16px;">
          <p style="margin:0 0 8px;color:#64748b;font-size:11px;letter-spacing:1px;">ライセンスキー</p>
          <p style="margin:0;font-size:13px;letter-spacing:1.5px;color:#38bdf8;word-break:break-all;">${key}</p>
        </div>
        <p style="color:#22c55e;margin-bottom:16px;">✓ 有効期限: ${expiryDisplay}（30日間）</p>
        <div style="background:#111827;border:1px solid #1e3a5f;border-radius:6px;padding:14px;margin-bottom:20px;">
          <p style="margin:0 0 8px;color:#64748b;font-size:11px;letter-spacing:1px;">有効になる機能</p>
          <pre style="margin:0;color:#94a3b8;font-size:12px;line-height:1.7;">${planFeatures}</pre>
        </div>
        <hr style="border:none;border-top:1px solid #1e3a5f;margin:16px 0;">
        <p style="color:#64748b;font-size:12px;line-height:1.7;">
          有効化の手順:<br>
          1. Chromeの拡張機能アイコンからRelayを開く<br>
          2. 上部の設定パネルを開く<br>
          3. プランを「Pro」または「One」に切り替え<br>
          4. ライセンスキーを貼り付けて「認証」をクリック
        </p>
        <p style="color:#334155;font-size:11px;margin-top:16px;">
          更新は有効期限前に再購入するだけです。残り日数は加算されます。<br>
          お問い合わせ: noreply@nsjp.org
        </p>
        ${couponHtml}
      </div>
    `,
  };

  const res = await fetch('https://api.resend.com/emails', {
    method:  'POST',
    headers: {
      'Authorization': `Bearer ${env.RESEND_API_KEY}`,
      'Content-Type':  'application/json',
    },
    body: JSON.stringify(body),
  });
  return res.ok;
}

// ── メインハンドラー ─────────────────────────────────────────────────────────────

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    const corsHeaders = {
      'Access-Control-Allow-Origin':  '*',
      'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, stripe-signature',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    // ── /relay/checkout: Stripe Webhook処理 ────────────────────────────────────
    if (url.pathname === '/relay/checkout' && request.method === 'POST') {
      const rawBody = await request.text();

      let event;
      try {
        event = JSON.parse(rawBody);
      } catch (e) {
        return new Response('Invalid JSON', { status: 400 });
      }

      if (event.type !== 'checkout.session.completed') {
        return new Response('OK', { status: 200 });
      }

      const session = event.data.object;
      const email   = session.customer_details?.email;
      if (!email) return new Response('No email', { status: 400 });

      // Stripeの商品メタデータからRelayプランを判定
      // Payment Link作成時に metadata: { plan: 'pro' } / { plan: 'one' } を設定すること
      const meta = session.metadata?.plan || '';
      const plan  = meta.includes('one') ? 'one' : 'pro';

      const { key, expiryDisplay } = await generateRelayKey(plan, env);

      // クロスクーポン生成（Orchestra向け、冪等性チェック付き）
      let couponHtml = '';
      if (event.id) {
        const idempotencyKey = `coupon_issued:${event.id}`;
        const alreadyIssued  = await env.RELAY_KV.get(idempotencyKey);
        if (!alreadyIssued) {
          const couponCode = `ORCH20-${generateRandomSuffix(8)}`;
          const orchLink   = env.ORCHESTRA_PAYMENT_LINK || 'PLACEHOLDER_REPLACE_ME';
          const couponOk   = await createStripeCoupon(couponCode, env);
          if (couponOk) {
            await env.RELAY_KV.put(idempotencyKey, couponCode, { expirationTtl: 60 * 60 * 24 * 7 });
            couponHtml = buildCouponHtml(couponCode, 'Orchestra', orchLink);
            console.log(`[Relay] Cross-coupon issued: ${couponCode} → ${email}`);
          }
        }
      }

      // KVに発行記録を保存（60日TTL）
      await env.RELAY_KV.put(
        `relay_issued:${key}`,
        JSON.stringify({ email, plan, issued_at: new Date().toISOString() }),
        { expirationTtl: 60 * 60 * 24 * 60 }
      );

      const sent = await sendRelayKeyEmail(email, plan, key, expiryDisplay, env, couponHtml);

      console.log(`[Relay] Key issued: ${key} → ${email} (sent: ${sent})`);
      return new Response(JSON.stringify({ ok: true, sent }), {
        headers: { 'Content-Type': 'application/json', ...corsHeaders },
      });
    }

    // ── /relay/health: 死活確認 ────────────────────────────────────────────────
    if (url.pathname === '/relay/health') {
      return new Response(
        JSON.stringify({ ok: true, service: 'relay-license', ts: new Date().toISOString() }),
        { headers: { 'Content-Type': 'application/json', ...corsHeaders } }
      );
    }

    return new Response('Relay License Service', { headers: corsHeaders });
  },
};
