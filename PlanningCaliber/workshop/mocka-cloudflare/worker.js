/**
 * MoCKA MCP Worker v1.0.0
 * Cloudflare Workers で MoCKA データを GitHub API 経由で配信
 * エンドポイント: /mcp (MCP protocol) /health /overview /todos /events /search
 */

const GITHUB_OWNER = "m-sirius-k";
const GITHUB_REPO  = "MoCKA";
const DATA_PREFIX  = "data";          // リポジトリ内のデータディレクトリ
const CACHE_TTL    = 300;             // GitHub API キャッシュ秒数

const TOOLS = [
  {
    name: "mocka_get_overview",
    description: "MOCKA_OVERVIEW.json を返す（プロジェクト全体像）",
    inputSchema: { type: "object", properties: {}, required: [] },
  },
  {
    name: "mocka_get_essence",
    description: "lever_essence.json の INCIDENT/PHILOSOPHY/OPERATION を返す",
    inputSchema: { type: "object", properties: {}, required: [] },
  },
  {
    name: "mocka_get_todo",
    description: "MOCKA_TODO.json を返す（現在のTODO一覧）",
    inputSchema: { type: "object", properties: {}, required: [] },
  },
  {
    name: "mocka_list_events",
    description: "最新 N 件のイベントを返す",
    inputSchema: {
      type: "object",
      properties: { n: { type: "integer", default: 20 } },
      required: [],
    },
  },
  {
    name: "mocka_search",
    description: "MoCKA データ全体を横断検索する",
    inputSchema: {
      type: "object",
      properties: { query: { type: "string" } },
      required: ["query"],
    },
  },
];

// ── GitHub API ヘルパー ──────────────────────────────────────────────────────

async function fetchGitHub(env, path) {
  const cacheKey = `https://github-cache.mocka/${path}`;
  const cache    = caches.default;

  const cached = await cache.match(cacheKey);
  if (cached) return cached.json();

  const url = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${path}`;
  const res  = await fetch(url, {
    headers: {
      Authorization: `token ${env.GITHUB_TOKEN}`,
      Accept:        "application/vnd.github.v3+json",
      "User-Agent":  "mocka-mcp-worker/1.0",
    },
  });

  if (!res.ok) {
    throw new Error(`GitHub API error: ${res.status} ${url}`);
  }

  const meta    = await res.json();
  const content = atob(meta.content.replace(/\n/g, ""));
  const decoded = JSON.parse(content);

  // Cloudflare Cache API に保存
  const cacheRes = new Response(JSON.stringify(decoded), {
    headers: { "Content-Type": "application/json", "Cache-Control": `max-age=${CACHE_TTL}` },
  });
  await cache.put(cacheKey, cacheRes);

  return decoded;
}

async function getOverview(env) { return fetchGitHub(env, `${DATA_PREFIX}/MOCKA_OVERVIEW.json`); }
async function getTodo(env)     { return fetchGitHub(env, `${DATA_PREFIX}/MOCKA_TODO.json`); }
async function getEssence(env)  {
  const raw = await fetchGitHub(env, `${DATA_PREFIX}/lever_essence.json`);
  return {
    INCIDENT:   raw.INCIDENT   ?? "",
    PHILOSOPHY: raw.PHILOSOPHY ?? "",
    OPERATION:  raw.OPERATION  ?? "",
  };
}
async function getEvents(env) {
  try {
    return fetchGitHub(env, `${DATA_PREFIX}/events_latest.json`);
  } catch {
    return [];
  }
}

// ── 検索ヘルパー ─────────────────────────────────────────────────────────────

function deepSearch(obj, query, path = "") {
  const hits = [];
  const q    = query.toLowerCase();
  if (typeof obj === "string") {
    if (obj.toLowerCase().includes(q)) hits.push({ path, snippet: obj.slice(0, 200) });
  } else if (Array.isArray(obj)) {
    obj.forEach((item, i) => hits.push(...deepSearch(item, query, `${path}[${i}]`)));
  } else if (obj && typeof obj === "object") {
    for (const [k, v] of Object.entries(obj)) {
      hits.push(...deepSearch(v, query, path ? `${path}.${k}` : k));
    }
  }
  return hits;
}

async function searchAll(env, query) {
  const [overview, todo, essence, events] = await Promise.allSettled([
    getOverview(env), getTodo(env), getEssence(env), getEvents(env),
  ]);
  const results = {};
  if (overview.status === "fulfilled")
    results.overview = deepSearch(overview.value, query, "overview").slice(0, 10);
  if (todo.status === "fulfilled")
    results.todos = deepSearch(todo.value, query, "todos").slice(0, 10);
  if (essence.status === "fulfilled")
    results.essence = deepSearch(essence.value, query, "essence").slice(0, 10);
  if (events.status === "fulfilled")
    results.events = deepSearch(events.value, query, "events").slice(0, 10);
  return results;
}

// ── MCP ツール実行 ────────────────────────────────────────────────────────────

async function executeTool(env, name, args) {
  switch (name) {
    case "mocka_get_overview": {
      const data = await getOverview(env);
      return JSON.stringify(data, null, 2);
    }
    case "mocka_get_essence": {
      const data = await getEssence(env);
      return JSON.stringify(data, null, 2);
    }
    case "mocka_get_todo": {
      const data = await getTodo(env);
      return JSON.stringify(data, null, 2);
    }
    case "mocka_list_events": {
      const events = await getEvents(env);
      const n      = parseInt(args?.n ?? 20, 10);
      const slice  = Array.isArray(events) ? events.slice(-n) : events;
      return JSON.stringify({ count: Array.isArray(slice) ? slice.length : 0, events: slice }, null, 2);
    }
    case "mocka_search": {
      const query   = args?.query ?? "";
      const results = await searchAll(env, query);
      return JSON.stringify({ query, results }, null, 2);
    }
    default:
      return JSON.stringify({ error: `unknown tool: ${name}` });
  }
}

// ── CORS ヘルパー ─────────────────────────────────────────────────────────────

function corsHeaders(origin) {
  const allowed = ["https://claude.ai", "https://www.claude.ai"];
  const o       = allowed.includes(origin) ? origin : "https://claude.ai";
  return {
    "Access-Control-Allow-Origin":  o,
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization, mcp-session-id",
    "Access-Control-Max-Age":       "86400",
  };
}

function json(data, status = 200, extra = {}) {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...extra },
  });
}

// ── ルーティング ──────────────────────────────────────────────────────────────

export default {
  async fetch(request, env) {
    const origin  = request.headers.get("Origin") ?? "";
    const cors    = corsHeaders(origin);
    const url     = new URL(request.url);
    const method  = request.method.toUpperCase();

    // OPTIONS プリフライト
    if (method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }

    try {
      // ── /health ─────────────────────────────────────────────
      if (url.pathname === "/health") {
        return json(
          {
            status:  "ok",
            version: "1.0.0",
            source:  `github:${GITHUB_OWNER}/${GITHUB_REPO}/${DATA_PREFIX}`,
            tools:   TOOLS.map((t) => t.name),
            ts:      new Date().toISOString(),
          },
          200,
          cors
        );
      }

      // ── /overview ───────────────────────────────────────────
      if (url.pathname === "/overview") {
        const data = await getOverview(env);
        return json(data, 200, cors);
      }

      // ── /todos ──────────────────────────────────────────────
      if (url.pathname === "/todos") {
        const data = await getTodo(env);
        return json(data, 200, cors);
      }

      // ── /events ─────────────────────────────────────────────
      if (url.pathname === "/events") {
        const events = await getEvents(env);
        const n      = parseInt(url.searchParams.get("n") ?? "20", 10);
        const slice  = Array.isArray(events) ? events.slice(-n) : events;
        return json({ count: Array.isArray(slice) ? slice.length : 0, events: slice }, 200, cors);
      }

      // ── /search ─────────────────────────────────────────────
      if (url.pathname === "/search") {
        const query = url.searchParams.get("q") ?? "";
        if (!query) return json({ error: "q parameter required" }, 400, cors);
        const results = await searchAll(env, query);
        return json({ query, results }, 200, cors);
      }

      // ── /mcp (MCP JSON-RPC) ──────────────────────────────────
      if (url.pathname === "/mcp") {
        if (method === "GET") {
          return json(
            { name: "mocka-mcp-worker", version: "1.0.0", description: "MoCKA via Cloudflare Workers" },
            200,
            cors
          );
        }

        if (method !== "POST") {
          return json({ error: "method not allowed" }, 405, cors);
        }

        const body   = await request.json();
        const rpcId  = body.id ?? null;
        const rpcMethod = body.method ?? "";
        const params = body.params ?? {};

        let result;
        if (rpcMethod === "initialize") {
          result = {
            protocolVersion: "2024-11-05",
            capabilities:    { tools: {} },
            serverInfo:      { name: "mocka-mcp-worker", version: "1.0.0" },
          };
        } else if (rpcMethod === "tools/list") {
          result = { tools: TOOLS };
        } else if (rpcMethod === "tools/call") {
          const text = await executeTool(env, params.name ?? "", params.arguments ?? {});
          result = { content: [{ type: "text", text }], isError: false };
        } else if (rpcMethod === "notifications/initialized") {
          // クライアント通知はレスポンス不要
          return new Response(null, { status: 204, headers: cors });
        } else {
          return json(
            { jsonrpc: "2.0", id: rpcId, error: { code: -32601, message: `unknown method: ${rpcMethod}` } },
            200,
            cors
          );
        }

        return json({ jsonrpc: "2.0", id: rpcId, result }, 200, cors);
      }

      // ── 404 ─────────────────────────────────────────────────
      return json(
        { error: "not found", endpoints: ["/health", "/overview", "/todos", "/events", "/search", "/mcp"] },
        404,
        cors
      );
    } catch (err) {
      return json({ error: err.message ?? "internal error" }, 500, cors);
    }
  },
};
