/**
 * RugMuncher API Gateway Worker — CONFIG-DRIVEN
 * =============================================
 * ALL provider configs read from KV at runtime.
 * Adding a new provider = PUT to KV. No redeploy needed.
 */

export interface Env {
  API_ORIGIN: string;
  CACHE_TTL_SECONDS: string;
  AI: any;
  QUOTA_KV: KVNamespace;
  OPENROUTER_API_KEY?: string;
  GEMINI_API_KEY?: string;
  GROQ_API_KEY?: string;
}

// ═══════════════════════════════════════════════════════════
// DEFAULTS (fallback if KV miss)
// ═══════════════════════════════════════════════════════════

const DEFAULT_PROVIDERS: Record<string, any> = {
  "workers-ai": { type: "workers-ai", baseUrl: "", headerName: "", model: "@cf/meta/llama-3.1-8b-instruct", free: true },
  "openrouter-free": { type: "openrouter", baseUrl: "https://openrouter.ai/api/v1", headerName: "Authorization", model: "openrouter/auto", free: true },
  "gemini-free": { type: "gemini", baseUrl: "https://generativelanguage.googleapis.com/v1beta/models", headerName: "Authorization", model: "gemini-1.5-flash", free: true },
  "groq-free": { type: "groq", baseUrl: "https://api.groq.com/openai/v1", headerName: "Authorization", model: "llama-3.1-8b-instant", free: true },
  "deepseek": { type: "deepseek", baseUrl: "https://api.deepseek.com/v1", headerName: "Authorization", model: "deepseek-chat", free: false },
  "openai": { type: "openai", baseUrl: "https://api.openai.com/v1", headerName: "Authorization", model: "gpt-4o-mini", free: false },
  "anthropic": { type: "anthropic", baseUrl: "https://api.anthropic.com/v1", headerName: "x-api-key", model: "claude-3-haiku-20240307", free: false },
  "fireworks": { type: "fireworks", baseUrl: "https://api.fireworks.ai/inference/v1", headerName: "Authorization", model: "accounts/fireworks/models/llama-v3p1-8b-instruct", free: false },
  "mistral": { type: "mistral", baseUrl: "https://api.mistral.ai/v1", headerName: "Authorization", model: "mistral-small-latest", free: false },
  "nvidia": { type: "nvidia", baseUrl: "https://integrate.api.nvidia.com/v1", headerName: "Authorization", model: "meta/llama-3.1-nemotron-70b-instruct", free: false },
  "together": { type: "together", baseUrl: "https://api.together.xyz/v1", headerName: "Authorization", model: "meta-llama/Llama-3.3-70B-Instruct-Turbo", free: false },
  "kimi": { type: "kimi", baseUrl: "https://api.moonshot.cn/v1", headerName: "Authorization", model: "kimi-k2.5", free: false },
};

const DEFAULT_FREE_CHAIN = ["workers-ai", "openrouter-free", "gemini-free", "groq-free"];
const EXHAUSTION_TTL = 3600;

// ═══════════════════════════════════════════════════════════
// CACHE CONFIG
// ═══════════════════════════════════════════════════════════

const CACHEABLE_PATHS = [
  '/api/v1/health', '/api/v1/email/business-emails', '/api/v1/status',
  '/api/v1/rag/namespaces', '/api/v1/budget/summary', '/api/v1/budget/free-quota',
];

const CACHEABLE_PREFIXES = [
  '/api/v1/profiles/', '/api/v1/news', '/api/v1/crypto/',
  '/api/v1/mcp/', '/api/v1/chain/', '/api/v1/token/',
];

const CRYPTO_EDGE_ORIGINS: Record<string, string> = {
  'coingecko': 'https://api.coingecko.com/api/v3',
  'helius': 'https://mainnet.helius-rpc.com',
  'gmgn': 'https://gmgn.ai/api/v1',
};

function isCacheable(request: Request): boolean {
  if (request.method !== 'GET') return false;
  const url = new URL(request.url);
  if (CACHEABLE_PATHS.includes(url.pathname)) return true;
  return CACHEABLE_PREFIXES.some((p) => url.pathname.startsWith(p));
}

function getCacheTTL(path: string): number {
  if (path.startsWith('/api/v1/profiles/')) return 60;
  if (path.startsWith('/api/v1/news')) return 300;
  if (path.startsWith('/api/v1/crypto/prices')) return 30;
  if (path.startsWith('/api/v1/crypto/')) return 120;
  if (path.startsWith('/api/v1/token/')) return 3600;
  if (path.startsWith('/api/v1/chain/')) return 60;
  if (path.startsWith('/api/v1/mcp/query') || path.startsWith('/api/v1/mcp/search')) return 300;
  if (path.startsWith('/api/v1/mcp/')) return 60;
  if (path.startsWith('/api/v1/budget/')) return 30;
  return 30;
}

function getEdgeOptimizedHeaders(response: Response, path: string): Headers {
  const headers = new Headers(response.headers);
  headers.set('X-Content-Type-Options', 'nosniff');
  headers.set('X-Frame-Options', 'DENY');
  headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  headers.set('Strict-Transport-Security', 'max-age=63072000; includeSubDomains; preload');
  headers.set('Permissions-Policy', 'geolocation=(), microphone=(), camera=()');
  headers.set('X-DNS-Prefetch-Control', 'on');
  const ttl = getCacheTTL(path);
  if (isCacheable(new Request(path))) {
    headers.set('Cache-Control', `public, max-age=${ttl}, s-maxage=${ttl * 2}`);
  }
  return headers;
}

// ═══════════════════════════════════════════════════════════
// KV HELPERS
// ═══════════════════════════════════════════════════════════

async function getFreeChain(kv: KVNamespace): Promise<string[]> {
  try { const raw = await kv.get("free_chain"); if (raw) return JSON.parse(raw); } catch (e) {}
  return DEFAULT_FREE_CHAIN;
}

async function isExhausted(kv: KVNamespace, p: string): Promise<boolean> {
  return (await kv.get(`exhausted:${p}`)) !== null;
}

async function markExhausted(kv: KVNamespace, p: string): Promise<void> {
  await kv.put(`exhausted:${p}`, "true", { expirationTtl: EXHAUSTION_TTL });
}

async function clearExhausted(kv: KVNamespace, p: string): Promise<void> {
  await kv.delete(`exhausted:${p}`);
}

// ═══════════════════════════════════════════════════════════
// AI PROVIDER HANDLERS
// ═══════════════════════════════════════════════════════════

interface ChatMessage { role: 'system' | 'user' | 'assistant'; content: string; }

async function tryWorkersAI(env: Env, messages: ChatMessage[], model: string): Promise<any> {
  const response = await env.AI.run(model, { messages, stream: false });
  const text = (response as any).response || JSON.stringify(response);
  return { content: text, provider: "workers-ai", model };
}

async function tryOpenRouter(env: Env, messages: ChatMessage[], model: string): Promise<any> {
  const apiKey = env.OPENROUTER_API_KEY;
  if (!apiKey) return null;
  const body = { model: model || "openrouter/auto", messages, temperature: 0.7, max_tokens: 4096 };
  const res = await fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: { "Content-Type": "application/json", "Authorization": `Bearer ${apiKey}`, "HTTP-Referer": "https://rugmunch.io", "X-Title": "RugMunch Intelligence" },
    body: JSON.stringify(body),
  });
  if (res.status === 429 || res.status === 402) throw new Error("EXHAUSTED:openrouter-free");
  if (!res.ok) throw new Error(`OpenRouter ${res.status}`);
  const data = await res.json() as any;
  return { content: data.choices?.[0]?.message?.content || "", provider: "openrouter-free", model: body.model };
}

async function tryGemini(env: Env, messages: ChatMessage[], model: string): Promise<any> {
  const apiKey = env.GEMINI_API_KEY;
  if (!apiKey) return null;
  const m = model || "gemini-1.5-flash";
  const chatMessages = messages.filter((m: any) => m.role !== "system").map((m: any) => ({ role: m.role === "user" ? "user" : "model", parts: [{ text: m.content }] }));
  const body: any = { contents: chatMessages, generationConfig: { temperature: 0.7, maxOutputTokens: 4096 } };
  const sys = messages.find((m: any) => m.role === "system")?.content;
  if (sys) body.systemInstruction = { parts: [{ text: sys }] };
  const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${m}:generateContent?key=${apiKey}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  if (res.status === 429 || res.status === 403) throw new Error("EXHAUSTED:gemini-free");
  if (!res.ok) throw new Error(`Gemini ${res.status}`);
  const data = await res.json() as any;
  return { content: data.candidates?.[0]?.content?.parts?.[0]?.text || "", provider: "gemini-free", model: m };
}

async function tryGroq(env: Env, messages: ChatMessage[], model: string): Promise<any> {
  const apiKey = env.GROQ_API_KEY;
  if (!apiKey) return null;
  const body = { model: model || "llama-3.1-8b-instant", messages, temperature: 0.7, max_tokens: 4096 };
  const res = await fetch("https://api.groq.com/openai/v1/chat/completions", { method: "POST", headers: { "Content-Type": "application/json", "Authorization": `Bearer ${apiKey}` }, body: JSON.stringify(body) });
  if (res.status === 429 || res.status === 402) throw new Error("EXHAUSTED:groq-free");
  if (!res.ok) throw new Error(`Groq ${res.status}`);
  const data = await res.json() as any;
  return { content: data.choices?.[0]?.message?.content || "", provider: "groq-free", model: body.model };
}

const TRY_FN: Record<string, any> = {
  "workers-ai": tryWorkersAI, "openrouter": tryOpenRouter, "gemini": tryGemini, "groq": tryGroq,
};

// ═══════════════════════════════════════════════════════════
// SMART CHAT with DYNAMIC FAILOVER
// ═══════════════════════════════════════════════════════════

async function smartChat(env: Env, messages: ChatMessage[], preferredModel?: string): Promise<Response> {
  const errors: string[] = [];
  const chain = await getFreeChain(env.QUOTA_KV);
  for (const pname of chain) {
    if (await isExhausted(env.QUOTA_KV, pname)) { errors.push(`${pname}: exhausted`); continue; }
    const cfg = DEFAULT_PROVIDERS[pname];
    if (!cfg) { errors.push(`${pname}: no config`); continue; }
    const fn = TRY_FN[cfg.type];
    if (!fn) { errors.push(`${pname}: no handler`); continue; }
    try {
      const result = await fn(env, messages, preferredModel || cfg.model);
      if (!result) { errors.push(`${pname}: no key`); continue; }
      await clearExhausted(env.QUOTA_KV, pname);
      return new Response(JSON.stringify({ content: result.content, model: result.model, provider: result.provider, free: true, cost: 0 }), {
        headers: { "Content-Type": "application/json", "X-Edge-AI": result.provider, "X-Free-Provider": "true", "X-Cost": "0", "X-Provider-Chain": chain.join(" -> "), "X-Provider-Used": result.provider },
      });
    } catch (err: any) {
      const msg = String(err?.message || err);
      if (msg.includes("EXHAUSTED:")) { await markExhausted(env.QUOTA_KV, msg.split(":")[1]); errors.push(`${pname}: quota exhausted`); }
      else { errors.push(`${pname}: ${msg.slice(0, 200)}`); }
    }
  }
  return new Response(JSON.stringify({ error: "All free providers exhausted", details: errors }), { status: 503, headers: { "Content-Type": "application/json" } });
}

// ═══════════════════════════════════════════════════════════
// AI GATEWAY FALLBACK
// ═══════════════════════════════════════════════════════════

async function handleAIGatewayFallback(body: any): Promise<Response> {
  const provider = body.fallback_provider;
  const apiKey = body.fallback_key;
  const cfg = DEFAULT_PROVIDERS[provider];
  if (!cfg) return new Response(JSON.stringify({ error: "Unknown fallback provider" }), { status: 400, headers: { "Content-Type": "application/json" } });
  const payload = { model: body.model || cfg.model, messages: body.messages, temperature: body.temperature || 0.7 };
  const targetUrl = cfg.baseUrl + "/chat/completions";
  const originHeaders: Record<string, string> = { "Content-Type": "application/json", "Authorization": cfg.headerName === "x-api-key" ? apiKey : `Bearer ${apiKey}` };
  const originRequest = new Request(targetUrl, { method: "POST", headers: originHeaders, body: JSON.stringify(payload) });
  const response = await fetch(originRequest);
  return new Response(response.body, { status: response.status, headers: { ...Object.fromEntries(response.headers), "X-AI-Gateway": provider, "X-Free-Provider": "false", "X-Fallback-Used": "true" } });
}

// ═══════════════════════════════════════════════════════════
// AI GATEWAY PROXY
// ═══════════════════════════════════════════════════════════

async function hashRequestBody(request: Request): Promise<string> {
  const body = await request.text();
  const encoder = new TextEncoder();
  const data = encoder.encode(body);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, "0")).join("").slice(0, 16);
}

async function handleAIGateway(request: Request): Promise<Response> {
  const url = new URL(request.url);
  const pathParts = url.pathname.split("/").filter(Boolean);
  const provider = pathParts[2];
  const cfg = DEFAULT_PROVIDERS[provider];
  if (!cfg) return new Response(JSON.stringify({ error: "Unknown provider", available: Object.keys(DEFAULT_PROVIDERS) }), { status: 400, headers: { "Content-Type": "application/json" } });

  const apiKey = request.headers.get("X-AI-Key");
  if (!apiKey) return new Response(JSON.stringify({ error: "Missing X-AI-Key header" }), { status: 401, headers: { "Content-Type": "application/json" } });

  const targetPath = "/" + pathParts.slice(3).join("/");
  const targetUrl = cfg.baseUrl + targetPath + url.search;

  const cache = caches.default;
  if (request.method === "POST") {
    const cacheKey = new Request(request.url + "?_hash=" + await hashRequestBody(request.clone()), { method: "GET" });
    const cached = await cache.match(cacheKey);
    if (cached) return new Response(cached.body, { status: cached.status, headers: { ...Object.fromEntries(cached.headers), "X-AI-Gateway-Cache": "HIT" } });
  }

  const originRequest = new Request(targetUrl, {
    method: request.method,
    headers: { ...Object.fromEntries(request.headers), [cfg.headerName]: cfg.headerName === "x-api-key" ? apiKey : `Bearer ${apiKey}`, "Content-Type": "application/json" },
    body: request.body,
  });
  const response = await fetch(originRequest);

  if (request.method === "POST" && response.status === 200 && targetPath.includes("/chat/completions")) {
    const responseClone = response.clone();
    const cacheKey = new Request(request.url + "?_hash=" + await hashRequestBody(request.clone()), { method: "GET" });
    await cache.put(cacheKey, new Response(responseClone.body, { status: responseClone.status, headers: { ...Object.fromEntries(responseClone.headers), "Cache-Control": "public, max-age=300" } }));
  }

  return new Response(response.body, { status: response.status, statusText: response.statusText, headers: { ...Object.fromEntries(response.headers), "X-AI-Gateway": provider, "X-AI-Gateway-Cache": "MISS" } });
}

// ═══════════════════════════════════════════════════════════
// CRYPTO PROXY
// ═══════════════════════════════════════════════════════════

async function handleCryptoAPI(request: Request, ctx: ExecutionContext): Promise<Response> {
  const url = new URL(request.url);
  const pathParts = url.pathname.split("/").filter(Boolean);
  const source = pathParts[3]; // /api/v1/crypto/{source}/...
  const config = CRYPTO_EDGE_ORIGINS[source];
  if (!config) return new Response(JSON.stringify({ error: "Unknown crypto source", available: Object.keys(CRYPTO_EDGE_ORIGINS) }), { status: 400, headers: { "Content-Type": "application/json" } });

  const targetPath = "/" + pathParts.slice(4).join("/");
  const targetUrl = config + targetPath + url.search;

  const cache = caches.default;
  if (request.method === "GET") {
    const cached = await cache.match(request);
    if (cached) return new Response(cached.body, { status: cached.status, headers: { ...Object.fromEntries(cached.headers), "X-Crypto-Cache": "HIT" } });
  }

  const originRequest = new Request(targetUrl, { method: request.method, headers: request.headers });
  const response = await fetch(originRequest);

  if (request.method === "GET" && response.status === 200) {
    const ttl = source === "coingecko" ? 30 : source === "gmgn" ? 15 : 60;
    const responseClone = response.clone();
    ctx.waitUntil(cache.put(request, new Response(responseClone.body, { status: responseClone.status, headers: { ...Object.fromEntries(responseClone.headers), "Cache-Control": `public, max-age=${ttl}` } })));
  }

  return new Response(response.body, { status: response.status, headers: { ...Object.fromEntries(response.headers), "X-Crypto-Cache": "MISS", "X-Crypto-Source": source } });
}

// ═══════════════════════════════════════════════════════════
// MAIN HANDLER
// ═══════════════════════════════════════════════════════════

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    try {
      const url = new URL(request.url);
      const origin = env.API_ORIGIN || "https://api.rugmunch.io";

      // Crypto API at edge
      if (url.pathname.startsWith("/api/v1/crypto/")) {
        return await handleCryptoAPI(request, ctx);
      }

      // Workers AI
      if (url.pathname.startsWith("/ai/")) {
        if (url.pathname.startsWith("/ai/gateway/")) {
          return await handleAIGateway(request);
        }
        const pathParts = url.pathname.split("/").filter(Boolean);
        if (pathParts[1] === "smart" && request.method === "POST") {
          const body = await request.json<{ messages: ChatMessage[]; model?: string; fallback_provider?: string; fallback_key?: string }>();
          const freeResponse = await smartChat(env, body.messages, body.model);
          if (freeResponse.status === 200) return freeResponse;
          if (body.fallback_provider && body.fallback_key) return await handleAIGatewayFallback(body);
          return freeResponse;
        }
        if (pathParts[1] === "chat" && request.method === "POST") {
          const body = await request.json<{ messages: ChatMessage[]; model?: string }>();
          const model = body.model || "@cf/meta/llama-3.1-8b-instruct";
          const response = await env.AI.run(model, { messages: body.messages, stream: false });
          return new Response(JSON.stringify(response), { headers: { "Content-Type": "application/json", "X-Edge-AI": "workers-ai", "X-Free-Provider": "true", "X-Cost": "0" } });
        }
        if (pathParts[1] === "embeddings" && request.method === "POST") {
          const body = await request.json<{ text: string | string[]; model?: string }>();
          const model = body.model || "@cf/baai/bge-base-en-v1.5";
          const texts = Array.isArray(body.text) ? body.text : [body.text];
          const response = await env.AI.run(model, { text: texts });
          return new Response(JSON.stringify(response), { headers: { "Content-Type": "application/json", "X-Edge-AI": "workers-ai", "X-Free-Provider": "true", "X-Cost": "0" } });
        }
        return new Response("Not Found", { status: 404 });
      }

      // Bot blocking
      const ua = (request.headers.get("User-Agent") || "").toLowerCase();
      if (["sqlmap", "nikto", "nmap", "masscan", "zgrab"].some(b => ua.includes(b))) {
        return new Response("Forbidden", { status: 403 });
      }

      // Origin proxy with cache
      const originUrl = origin + url.pathname + url.search;
      const originRequest = new Request(originUrl, { method: request.method, headers: request.headers, body: request.body });
      const cache = caches.default;

      if (isCacheable(request)) {
        const cached = await cache.match(request);
        if (cached) return new Response(cached.body, { status: cached.status, headers: { ...Object.fromEntries(cached.headers), "X-Cache": "HIT" } });
      }

      let response: Response;
      try { response = await fetch(originRequest); }
      catch (e) { return new Response(JSON.stringify({ error: "Origin unreachable" }), { status: 503, headers: { "Content-Type": "application/json" } }); }

      const responseClone = response.clone();
      const headers = getEdgeOptimizedHeaders(response, url.pathname);
      headers.set("X-Cache", "MISS");

      if (isCacheable(request) && response.status === 200) {
        const ttl = getCacheTTL(url.pathname);
        headers.set("Cache-Control", `public, max-age=${ttl}, s-maxage=${ttl * 2}`);
        ctx.waitUntil(cache.put(request, new Response(responseClone.body, { status: responseClone.status, headers: { ...Object.fromEntries(responseClone.headers), "Cache-Control": `public, max-age=${ttl}, s-maxage=${ttl * 2}` } })));
      } else {
        headers.set("Cache-Control", "no-store");
      }

      return new Response(response.body, { status: response.status, statusText: response.statusText, headers });
    } catch (e: any) {
      return new Response(JSON.stringify({ error: "Worker error", details: String(e?.message || e) }), { status: 500, headers: { "Content-Type": "application/json" } });
    }
  },
};
