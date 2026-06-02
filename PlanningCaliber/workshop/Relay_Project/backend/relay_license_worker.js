/**
 * relay_license_worker.js  — Relay License Manager
 * TODO_178: Relay Stripe + Cloudflare Workers + Resend 自動キー発給
 *
 * Orchestraパイプライン（orchestra-license worker）の完全流用版。
 * 差分: プレフィックス OPR/ONE → RLY-P/RLY-O、商品名、メール文面のみ。
 *
 * デプロイ先: relay-license.nsjpkimura-mocka.workers.dev
 *
 * 必要な Cloudflare Workers シークレット（wrangler secret put で設定）:
 *   STRIPE_WEBHOOK_SECRET   Stripe Webhook の署名シークレット
 *   HMAC_SECRET             HMAC-SHA256 署名用秘密鍵（keygen.py と同一値）
 *   RESEND_API_KEY          Resend APIキー
 *   KV_NAMESPACE            KV バインディング名（RELAY_KV）
 *
 * wrangler.toml 設定例:
 *   name = "relay-license"
 *   [[kv_namespaces]]
 *   binding = "RELAY_KV"
 *   id = "<your-kv-id>"
 */

// MOCKA_DEV_MODE: KVに登録された開発者GitHub ID
// KV設定: wrangler kv:key put --binding=RELAY_KV DEVELOPER_GITHUB_ID "m-sirius-k"
const DEVELOPER_GITHUB_ID = "m-sirius-k";

// ── ルーティング ───────────────────────────────────────────────────────────────

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // MOCKA_DEV_MODE: x-mocka-dev-id ヘッダーが "m-sirius-k" ならOneプランを即返す
    const devId = request.headers.get("x-mocka-dev-id");
    if (devId && devId === DEVELOPER_GITHUB_ID) {
      return Response.json({ valid: true, planLevel: "one", dev: true });
    }

    if (request.method === "GET" && url.pathname === "/health") {
      return Response.json({
        status: "ok",
        service: "relay-license",
        version: "1.0.0",
        timestamp: new Date().toISOString(),
      });
    }

    if (request.method === "POST" && url.pathname === "/webhook/stripe") {
      return handleStripeWebhook(request, env);
    }

    if (request.method === "GET" && url.pathname === "/verify") {
      return handleVerify(request, env);
    }

    return new Response("relay-license worker", { status: 200 });
  },
};

// ── Stripe Webhook ────────────────────────────────────────────────────────────

async function handleStripeWebhook(request, env) {
  // 署名検証
  const body      = await request.text();
  const sigHeader = request.headers.get("Stripe-Signature");

  const valid = await verifyStripeSignature(body, sigHeader, env.STRIPE_WEBHOOK_SECRET);
  if (!valid) {
    return new Response("Invalid signature", { status: 401 });
  }

  const event = JSON.parse(body);

  // checkout.session.completed のみ処理
  if (event.type !== "checkout.session.completed") {
    return Response.json({ received: true, action: "ignored" });
  }

  const session     = event.data.object;
  const email       = session.customer_details?.email || session.customer_email;
  const amountTotal = session.amount_total; // 単位: cents
  const currency    = session.currency;

  if (!email) {
    return Response.json({ received: true, action: "no_email" });
  }

  // プラン判定（金額ベース。Stripe商品IDを使う場合はline_itemsを展開する）
  //   Pro  : $5/月 = 500 cents
  //   One  : $10/月 = 1000 cents / Launch: $8/月 = 800 cents
  const plan = detectPlan(amountTotal, currency, session);

  if (!plan) {
    console.log("Unknown plan:", amountTotal, currency);
    return Response.json({ received: true, action: "unknown_plan" });
  }

  // ライセンスキー生成
  const licenseKey = await generateLicenseKey(plan, env.HMAC_SECRET);

  // KV に保存（メール → キー のマッピング）
  const kvKey = `relay:${email}:${plan.prefix}`;
  await env.RELAY_KV.put(kvKey, JSON.stringify({
    key:        licenseKey,
    plan:       plan.name,
    email:      email,
    issued_at:  new Date().toISOString(),
    expires_at: plan.expiresAt,
  }));

  // メール送信
  const emailSent = await sendLicenseEmail(email, licenseKey, plan, env.RESEND_API_KEY);

  console.log(`Relay license issued: ${email} → ${plan.name} → ${licenseKey}`);

  return Response.json({
    received:  true,
    action:    "license_issued",
    plan:      plan.name,
    email_sent: emailSent,
  });
}

// ── プラン判定 ────────────────────────────────────────────────────────────────

function detectPlan(amountCents, currency, session) {
  // Stripe商品名で判定（最優先）
  const productName = (session.metadata?.product_name || "").toLowerCase();

  if (productName.includes("relay one") || productName.includes("relay_one")) {
    return buildPlan("ONE", 365);
  }
  if (productName.includes("relay pro") || productName.includes("relay_pro")) {
    return buildPlan("PRO", 30);
  }

  // フォールバック: 金額で判定
  if (currency === "usd") {
    if (amountCents >= 900)  return buildPlan("ONE", 365); // $9以上 = One
    if (amountCents >= 400)  return buildPlan("PRO", 30);  // $4以上 = Pro
  }
  if (currency === "jpy") {
    if (amountCents >= 1300) return buildPlan("ONE", 365);
    if (amountCents >= 600)  return buildPlan("PRO", 30);
  }

  return null;
}

function buildPlan(type, days) {
  const expiresAt = new Date(Date.now() + days * 86400000).toISOString().split("T")[0];
  return {
    type,
    name:      type === "ONE" ? "Relay One" : "Relay Pro",
    prefix:    type === "ONE" ? "RLY-O" : "RLY-P",
    days,
    expiresAt,
  };
}

// ── ライセンスキー生成（HMAC-SHA256）────────────────────────────────────────

async function generateLicenseKey(plan, secret) {
  // キー形式: RLY-P-YYYYMMDD{SERIAL}{SIGNATURE}
  //           RLY-O-YYYYMMDD{SERIAL}{SIGNATURE}
  //
  // keygen.py と同一形式（Orchestraのprefixだけ変えた版）
  const expiry = plan.expiresAt.replace(/-/g, ""); // YYYYMMDD
  const serial = Math.floor(Math.random() * 0xFFFFFF).toString(16).toUpperCase().padStart(6, "0");
  const msg    = plan.prefix + expiry + serial;

  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const sigBuffer = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(msg));
  const sigHex    = Array.from(new Uint8Array(sigBuffer))
    .slice(0, 8)
    .map(b => b.toString(16).padStart(2, "0"))
    .join("")
    .toUpperCase();

  return `${plan.prefix}-${expiry}${serial}${sigHex}`;
}

// ── Stripe 署名検証 ────────────────────────────────────────────────────────

async function verifyStripeSignature(body, sigHeader, webhookSecret) {
  if (!sigHeader || !webhookSecret) return false;
  try {
    const parts     = sigHeader.split(",").reduce((acc, part) => {
      const [k, v] = part.split("=");
      acc[k] = v;
      return acc;
    }, {});
    const timestamp = parts["t"];
    const signature = parts["v1"];
    if (!timestamp || !signature) return false;

    const payload = `${timestamp}.${body}`;
    const key = await crypto.subtle.importKey(
      "raw",
      new TextEncoder().encode(webhookSecret),
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["sign"]
    );
    const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(payload));
    const expected = Array.from(new Uint8Array(sig))
      .map(b => b.toString(16).padStart(2, "0"))
      .join("");

    return expected === signature;
  } catch (e) {
    return false;
  }
}

// ── Resend メール送信 ──────────────────────────────────────────────────────

async function sendLicenseEmail(to, licenseKey, plan, resendApiKey) {
  const subject = plan.type === "ONE"
    ? `Relay One — ライセンスキーをお届けします`
    : `Relay Pro — ライセンスキーをお届けします`;

  const planJa  = plan.type === "ONE" ? "Relay One" : "Relay Pro";
  const feature = plan.type === "ONE"
    ? "AI要約引き継ぎ・Vault文脈注入・タイミング最適化エンジン"
    : "AI要約引き継ぎ・ファイルパスキャプチャ・決定事項抽出";

  const html = `
<!DOCTYPE html>
<html lang="ja">
<head><meta charset="UTF-8"></head>
<body style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:24px;color:#333">
  <h2 style="color:#1a1a2e">Relay — ${planJa} ライセンスキー</h2>

  <p>この度は <strong>${planJa}</strong> をご購入いただきありがとうございます。</p>

  <div style="background:#f8f9fa;border:2px solid #6c63ff;border-radius:8px;
              padding:20px;margin:24px 0;text-align:center">
    <div style="font-size:12px;color:#666;margin-bottom:8px">ライセンスキー</div>
    <div style="font-family:monospace;font-size:18px;font-weight:bold;
                color:#1a1a2e;letter-spacing:1px">${licenseKey}</div>
    <div style="font-size:12px;color:#888;margin-top:8px">
      有効期限: ${plan.expiresAt}
    </div>
  </div>

  <h3>利用可能な機能</h3>
  <p>${feature}</p>

  <h3>設定手順</h3>
  <ol>
    <li>Chrome拡張バーの <strong>Relay</strong> アイコンをクリック</li>
    <li>「Settings」タブを開く</li>
    <li>「License Key」欄に上記キーを貼り付けて「Activate」</li>
    <li>${planJa}の機能が有効になります</li>
  </ol>

  <p style="font-size:12px;color:#888;margin-top:32px;border-top:1px solid #eee;padding-top:16px">
    このメールは自動送信です。ご不明な点は GitHub Issues または
    Gumroadのメッセージ機能よりお問い合わせください。<br>
    Relay は claude.ai 専用のセッション引き継ぎ拡張機能です。
  </p>
</body>
</html>`;

  try {
    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${resendApiKey}`,
        "Content-Type":  "application/json",
      },
      body: JSON.stringify({
        from:    "noreply@nsjp.org",
        to:      [to],
        subject: subject,
        html:    html,
      }),
    });
    return res.ok;
  } catch (e) {
    console.error("Resend error:", e);
    return false;
  }
}

// ── ライセンス検証エンドポイント ──────────────────────────────────────────────

async function handleVerify(request, env) {
  // GET /verify?key=RLY-P-xxxxx
  const url = new URL(request.url);
  const key = url.searchParams.get("key");
  if (!key) return Response.json({ valid: false, error: "key required" }, { status: 400 });

  // HMAC検証（ローカル処理）
  const valid = await verifyKey(key, env.HMAC_SECRET);
  if (!valid) return Response.json({ valid: false });

  // プレフィックスからプラン取得
  const plan = key.startsWith("RLY-O") ? "one" : key.startsWith("RLY-P") ? "pro" : "unknown";

  // 有効期限チェック（キー内にエンコードされているYYYYMMDD）
  const dateStr = key.replace("RLY-O-", "").replace("RLY-P-", "").substring(0, 8);
  const expiry  = `${dateStr.substring(0,4)}-${dateStr.substring(4,6)}-${dateStr.substring(6,8)}`;
  const expired = new Date(expiry) < new Date();

  return Response.json({
    valid:   !expired,
    plan,
    expires: expiry,
    expired,
  });
}

async function verifyKey(key, secret) {
  try {
    // RLY-P- or RLY-O- を除去してメッセージ部分を取得
    const prefixMatch = key.match(/^(RLY-[PO])-(\w{8})(\w{6})(\w{16})$/);
    if (!prefixMatch) return false;
    const [, prefix, expiry, serial, sig] = prefixMatch;
    const msg = `${prefix}${expiry}${serial}`;

    const hmacKey = await crypto.subtle.importKey(
      "raw", new TextEncoder().encode(secret),
      { name: "HMAC", hash: "SHA-256" }, false, ["sign"]
    );
    const sigBuffer = await crypto.subtle.sign("HMAC", hmacKey, new TextEncoder().encode(msg));
    const expected  = Array.from(new Uint8Array(sigBuffer))
      .slice(0, 8)
      .map(b => b.toString(16).padStart(2, "0"))
      .join("")
      .toUpperCase();

    return expected === sig;
  } catch (e) {
    return false;
  }
}
