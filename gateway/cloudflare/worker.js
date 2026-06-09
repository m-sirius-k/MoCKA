// MoCKA Gateway — Cloudflare Workers Reverse Proxy
// バックエンド: ngrok経由のローカル gateway.py (port:5010)
// デプロイ先:   mocka-api.nsjpkimura-mocka.workers.dev

const BACKEND = "https://pharmacy-governing-whale-two.trycloudflare.com"; // fallback
const RATE_LIMIT_WINDOW = 60_000;    // 1分
const RATE_LIMIT_MAX    = 60;        // 1AI/分 最大60リクエスト

const rateLimitMap = new Map();

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

export default {
  async fetch(request, env) {
    const url     = new URL(request.url);
    const backend = env.MOCKA_BACKEND_URL || BACKEND;

    // レート制限
    const ip = request.headers.get("CF-Connecting-IP") || "unknown";
    if (!checkRateLimit(ip)) {
      return new Response(JSON.stringify({ error: "rate limit exceeded" }), {
        status: 429,
        headers: { "Content-Type": "application/json" },
      });
    }

    // CORS プリフライト
    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: corsHeaders(),
      });
    }

    // バックエンドへプロキシ
    const targetUrl = backend.replace(/\/$/, "") + url.pathname + url.search;
    const fwdHeaders = new Headers(request.headers);
    fwdHeaders.set("ngrok-skip-browser-warning", "1");

    const proxyReq  = new Request(targetUrl, {
      method:  request.method,
      headers: fwdHeaders,
      body:    request.method !== "GET" && request.method !== "HEAD"
               ? request.body : undefined,
    });

    try {
      const res = await fetch(proxyReq);
      const body = await res.arrayBuffer();
      return new Response(body, {
        status:  res.status,
        headers: {
          ...Object.fromEntries(res.headers),
          ...corsHeaders(),
        },
      });
    } catch (e) {
      return new Response(JSON.stringify({ error: "gateway unreachable", detail: e.message }), {
        status: 502,
        headers: { "Content-Type": "application/json", ...corsHeaders() },
      });
    }
  },
};

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, X-MoCKA-Key, X-MoCKA-Sig",
  };
}
