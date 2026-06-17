// MoCKA Gateway — Cloudflare Workers Reverse Proxy (TODO_259)
// バックエンド: ngrok経由のローカル gateway.py (port:5010)
// デプロイ先:   mocka-api.nsjpkimura-mocka.workers.dev
//
// 公開エンドポイント:
//   GET  /api/v1/context  — MoCKAコンテキスト取得（X-MoCKA-Keyで認証）
//   GET  /api/v1/todo     — アクティブTODO取得（X-MoCKA-Keyで認証）
//   POST /api/v1/event    — イベント記録（HMAC-SHA256署名必須）
//
// HMAC署名フォーマット (POST /api/v1/event):
//   Header: X-MoCKA-Sig: sha256=<hex>
//   署名対象: `${X-MoCKA-Timestamp}:${bodyText}`
//   秘密鍵: Cloudflare環境変数 MOCKA_HMAC_SECRET
//   有効時間: ±5分（リプレイ攻撃防止）

const BACKEND         = "https://pharmacy-governing-whale-two.trycloudflare.com"; // fallback
const RATE_LIMIT_WINDOW  = 60_000;   // 1分
const RATE_LIMIT_MAX     = 60;       // 最大60リクエスト/分
const HMAC_TIMESTAMP_TTL = 300_000;  // 5分（リプレイ防止ウィンドウ）

const rateLimitMap = new Map();

// ---------- レート制限 ----------

function checkRateLimit(ip) {
  const now = Date.now();
  const entry = rateLimitMap.get(ip) || { count: 0, windowStart: now };
  if (now - entry.windowStart > RATE_LIMIT_WINDOW) {
    entry.count = 0;
    entry.windowStart = now;
  }
  entry.count++;
  rateLimitMap.set(ip, entry);
  return entry.count <= RATE_LIMIT_MAX;
}

// ---------- HMAC-SHA256 検証 ----------

async function verifyHmac(request, secret, bodyText) {
  const sigHeader = request.headers.get("X-MoCKA-Sig") || "";
  const tsHeader  = request.headers.get("X-MoCKA-Timestamp") || "";

  if (!sigHeader.startsWith("sha256=") || !tsHeader) {
    return { ok: false, reason: "X-MoCKA-Sig or X-MoCKA-Timestamp missing" };
  }

  // タイムスタンプ有効期限チェック（リプレイ攻撃防止）
  const ts = parseInt(tsHeader, 10);
  if (isNaN(ts) || Math.abs(Date.now() - ts) > HMAC_TIMESTAMP_TTL) {
    return { ok: false, reason: "timestamp expired or invalid" };
  }

  // 署名検証
  const message   = `${tsHeader}:${bodyText}`;
  const encoder   = new TextEncoder();
  const keyData   = encoder.encode(secret);
  const msgData   = encoder.encode(message);
  const cryptoKey = await crypto.subtle.importKey(
    "raw", keyData, { name: "HMAC", hash: "SHA-256" }, false, ["verify"]
  );
  const sigHex = sigHeader.slice("sha256=".length);
  const sigBuf = hexToUint8Array(sigHex);

  const valid = await crypto.subtle.verify("HMAC", cryptoKey, sigBuf, msgData);
  return valid
    ? { ok: true }
    : { ok: false, reason: "signature mismatch" };
}

function hexToUint8Array(hex) {
  const arr = new Uint8Array(hex.length / 2);
  for (let i = 0; i < arr.length; i++) {
    arr[i] = parseInt(hex.slice(i * 2, i * 2 + 2), 16);
  }
  return arr;
}

// ---------- メインハンドラ ----------

export default {
  async fetch(request, env) {
    const url     = new URL(request.url);
    const backend = env.MOCKA_BACKEND_URL || BACKEND;

    // CORS プリフライト
    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: corsHeaders(),
      });
    }

    // レート制限
    const ip = request.headers.get("CF-Connecting-IP") || "unknown";
    if (!checkRateLimit(ip)) {
      return jsonError("rate limit exceeded", 429);
    }

    // POST /api/v1/event — HMAC認証必須
    if (request.method === "POST" && url.pathname === "/api/v1/event") {
      const secret = env.MOCKA_HMAC_SECRET;
      if (!secret) {
        return jsonError("MOCKA_HMAC_SECRET not configured", 503);
      }
      const bodyText = await request.text();
      const check = await verifyHmac(request, secret, bodyText);
      if (!check.ok) {
        return jsonError(`HMAC verification failed: ${check.reason}`, 401);
      }
      // 検証済みbodyでバックエンドにプロキシ
      return proxyRequest(backend, url, request, bodyText);
    }

    // GET /api/v1/context, /api/v1/todo, /api/v1/phase, etc. — X-MoCKA-Keyで認証
    return proxyRequest(backend, url, request, null);
  },
};

// ---------- バックエンドプロキシ ----------

async function proxyRequest(backend, url, request, bodyOverride) {
  const targetUrl  = backend.replace(/\/$/, "") + url.pathname + url.search;
  const fwdHeaders = new Headers(request.headers);
  fwdHeaders.set("ngrok-skip-browser-warning", "1");

  const proxyReq = new Request(targetUrl, {
    method:  request.method,
    headers: fwdHeaders,
    body:    bodyOverride !== null
             ? bodyOverride
             : (request.method !== "GET" && request.method !== "HEAD" ? request.body : undefined),
  });

  try {
    const res  = await fetch(proxyReq);
    const body = await res.arrayBuffer();
    return new Response(body, {
      status:  res.status,
      headers: {
        ...Object.fromEntries(res.headers),
        ...corsHeaders(),
      },
    });
  } catch (e) {
    return jsonError(`gateway unreachable: ${e.message}`, 502);
  }
}

// ---------- ユーティリティ ----------

function jsonError(message, status) {
  return new Response(JSON.stringify({ error: message }), {
    status,
    headers: { "Content-Type": "application/json", ...corsHeaders() },
  });
}

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, X-MoCKA-Key, X-MoCKA-Sig, X-MoCKA-Timestamp",
  };
}
