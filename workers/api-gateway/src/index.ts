/**
 * RugMuncher API Gateway Worker
 * Edge-caches API responses, adds security headers, routes traffic,
 * and integrates Cloudflare Workers AI + AI Gateway with FREE-PROVIDER FAILOVER.
 *
 * Free Provider Chain (auto-failover when quota exhausted):
 *   1. Workers AI (CF free tier — 10K req/day)
 *   2. OpenRouter Free models ($0)
 *   3. Gemini Free tier (~1500 req/day)
 *   4. Groq Free Credits ($5 initial)
 *   5. Paid fallback (cheapest available)
 */

export interface Env {
  API_ORIGIN: string;
  CACHE_TTL_SECONDS: string;
  AI: any; // Workers AI binding
  QUOTA_KV: KVNamespace; // KV for tracking provider exhaustion
  OPENROUTER_API_KEY?: string;
  GEMINI_API_KEY?: string;
  GROQ_API_KEY?: string;
}

// ═══════════════════════════════════════════════════════════
// FREE PROVIDER CHAIN CONFIG
// ═══════════════════════════════════════════════════════════

interface FreeProvider {
  name: string;
  type: 'workers-ai' | 'openrouter' | 'gemini' | 'groq';
  priority: number; // lower = tried first
  model: string;
  maxRetries: number;
}

const FREE_PROVIDER_CHAIN: FreeProvider[] = [
  { name: 'workers-ai', type: 'workers-ai', priority: 1, model: '@cf/meta/llama-3.1-8b-instruct', maxRetries: 1 },
  { name: 'openrouter-free', type: 'openrouter', priority: 2, model: 'openrouter/auto', maxRetries: 2 },
  { name: 'gemini-free', type: 'gemini', priority: 3, model: 'gemini-1.5-flash', maxRetries: 2 },
  { name: 'groq-free', type: 'groq', priority: 4, model: 'llama-3.1-8b-instant', maxRetries: 2 },
];

// How long to mark a provider as exhausted in KV (minutes)
const EXHAUSTION_TTL_SECONDS = 3600; // 1 hour

// ═══════════════════════════════════════════════════════════
// CACHE CONFIG — Aggressive edge caching for speed
// ═══════════════════════════════════════════════════════════

const CACHEABLE_PATHS = [
  '/api/v1/health',
  '/api/v1/email/business-emails',
  '/api/v1/status',
  '/api/v1/rag/namespaces',
  '/api/v1/budget/summary',
  '/api/v1/budget/free-quota',
];

const CACHEABLE_PREFIXES = [
  '/api/v1/profiles/',
  '/api/v1/news',
  '/api/v1/crypto/',       // Crypto data
  '/api/v1/mcp/',          // MCP read-only endpoints
  '/api/v1/chain/',        // Chain data
  '/api/v1/token/',        // Token metadata
];

// Crypto API origins we can cache directly at edge
const CRYPTO_EDGE_ORIGINS: Record<string, string> = {
  'coingecko': 'https://api.coingecko.com/api/v3',
  'helius': 'https://mainnet.helius-rpc.com',
};

function isCacheable(request: Request): boolean {
  if (request.method !== 'GET') return false;
  const url = new URL(request.url);
  if (CACHEABLE_PATHS.includes(url.pathname)) return true;
  return CACHEABLE_PREFIXES.some((p) => url.pathname.startsWith(p));
}

function getCacheTTL(path: string): number {
  // Profiles — short cache
  if (path.startsWith('/api/v1/profiles/')) return 60;
  // News — medium cache
  if (path.startsWith('/api/v1/news')) return 300;
  // Crypto prices — 30s cache (prices change fast)
  if (path.startsWith('/api/v1/crypto/prices')) return 30;
  if (path.startsWith('/api/v1/crypto/')) return 120;
  // Token metadata — long cache (rarely changes)
  if (path.startsWith('/api/v1/token/')) return 3600;
  // Chain data — medium cache
  if (path.startsWith('/api/v1/chain/')) return 60;
  // MCP read endpoints — medium cache
  if (path.startsWith('/api/v1/mcp/query') || path.startsWith('/api/v1/mcp/search')) return 300;
  if (path.startsWith('/api/v1/mcp/')) return 60;
  // Budget/quota — short cache
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

  // Performance headers
  headers.set('X-DNS-Prefetch-Control', 'on');

  // Cache headers based on path
  const ttl = getCacheTTL(path);
  if (isCacheable(new Request(path))) {
    headers.set('Cache-Control', `public, max-age=${ttl}, s-maxage=${ttl * 2}`);
  }

  return headers;
}

// ═══════════════════════════════════════════════════════════
// KV QUOTA TRACKING HELPERS
// ═══════════════════════════════════════════════════════════

async function isProviderExhausted(kv: KVNamespace, provider: string): Promise<boolean> {
  const key = `exhausted:${provider}`;
  const value = await kv.get(key);
  return value !== null;
}

async function markProviderExhausted(kv: KVNamespace, provider: string): Promise<void> {
  const key = `exhausted:${provider}`;
  await kv.put(key, 'true', { expirationTtl: EXHAUSTION_TTL_SECONDS });
}

async function clearProviderExhausted(kv: KVNamespace, provider: string): Promise<void> {
  const key = `exhausted:${provider}`;
  await kv.delete(key);
}

// ═══════════════════════════════════════════════════════════
// FREE PROVIDER IMPLEMENTATIONS
// ═══════════════════════════════════════════════════════════

interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

interface ChatResponse {
  content: string;
  provider: string;
  model: string;
  cost?: number;
}

/** 1. Workers AI (FREE) */
async function tryWorkersAI(
  env: Env,
  messages: ChatMessage[],
  model: string
): Promise<ChatResponse | null> {
  try {
    const response = await env.AI.run(model, {
      messages,
      stream: false,
    });
    // Workers AI returns { response: string } for chat
    const text = (response as any).response || JSON.stringify(response);
    return { content: text, provider: 'workers-ai', model, cost: 0 };
  } catch (err: any) {
    const status = err?.status || err?.statusCode || 500;
    // 429 = rate limit / quota exhausted
    if (status === 429 || status === 403) {
      throw new Error(`EXHAUSTED:workers-ai`);
    }
    throw err;
  }
}

/** 2. OpenRouter Free ($0 models) */
async function tryOpenRouter(
  env: Env,
  messages: ChatMessage[],
  model: string
): Promise<ChatResponse | null> {
  const apiKey = env.OPENROUTER_API_KEY;
  if (!apiKey) return null;

  const body = {
    model: model || 'openrouter/auto',
    messages,
    temperature: 0.7,
    max_tokens: 4096,
  };

  const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`,
      'HTTP-Referer': 'https://rugmunch.io',
      'X-Title': 'RugMunch Intelligence',
    },
    body: JSON.stringify(body),
  });

  if (response.status === 429 || response.status === 402) {
    throw new Error(`EXHAUSTED:openrouter-free`);
  }
  if (!response.ok) {
    const err = await response.text();
    throw new Error(`OpenRouter error ${response.status}: ${err}`);
  }

  const data = await response.json() as any;
  const content = data.choices?.[0]?.message?.content || '';
  return { content, provider: 'openrouter-free', model: body.model, cost: 0 };
}

/** 3. Gemini Free tier */
async function tryGemini(
  env: Env,
  messages: ChatMessage[],
  model: string
): Promise<ChatResponse | null> {
  const apiKey = env.GEMINI_API_KEY;
  if (!apiKey) return null;

  // Convert messages to Gemini format
  const geminiModel = model || 'gemini-1.5-flash';
  const systemMsg = messages.find(m => m.role === 'system')?.content || '';
  const chatMessages = messages.filter(m => m.role !== 'system').map(m => ({
    role: m.role === 'user' ? 'user' : 'model',
    parts: [{ text: m.content }],
  }));

  const body = {
    contents: chatMessages,
    systemInstruction: systemMsg ? { parts: [{ text: systemMsg }] } : undefined,
    generationConfig: {
      temperature: 0.7,
      maxOutputTokens: 4096,
    },
  };

  const url = `https://generativelanguage.googleapis.com/v1beta/models/${geminiModel}:generateContent?key=${apiKey}`;
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (response.status === 429 || response.status === 403) {
    throw new Error(`EXHAUSTED:gemini-free`);
  }
  if (!response.ok) {
    const err = await response.text();
    throw new Error(`Gemini error ${response.status}: ${err}`);
  }

  const data = await response.json() as any;
  const content = data.candidates?.[0]?.content?.parts?.[0]?.text || '';
  return { content, provider: 'gemini-free', model: geminiModel, cost: 0 };
}

/** 4. Groq Free Credits */
async function tryGroq(
  env: Env,
  messages: ChatMessage[],
  model: string
): Promise<ChatResponse | null> {
  const apiKey = env.GROQ_API_KEY;
  if (!apiKey) return null;

  const body = {
    model: model || 'llama-3.1-8b-instant',
    messages,
    temperature: 0.7,
    max_tokens: 4096,
  };

  const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`,
    },
    body: JSON.stringify(body),
  });

  if (response.status === 429 || response.status === 402) {
    throw new Error(`EXHAUSTED:groq-free`);
  }
  if (!response.ok) {
    const err = await response.text();
    throw new Error(`Groq error ${response.status}: ${err}`);
  }

  const data = await response.json() as any;
  const content = data.choices?.[0]?.message?.content || '';
  return { content, provider: 'groq-free', model: body.model, cost: 0 };
}

// Map provider types to their try functions
const PROVIDER_TRY_FN: Record<string, (env: Env, messages: ChatMessage[], model: string) => Promise<ChatResponse | null>> = {
  'workers-ai': tryWorkersAI,
  'openrouter': tryOpenRouter,
  'gemini': tryGemini,
  'groq': tryGroq,
};

// ═══════════════════════════════════════════════════════════
// SMART CHAT with FREE-PROVIDER FAILOVER
// ═══════════════════════════════════════════════════════════

async function smartChatWithFailover(
  env: Env,
  messages: ChatMessage[],
  preferredModel?: string
): Promise<Response> {
  const errors: string[] = [];

  for (const provider of FREE_PROVIDER_CHAIN) {
    // Check KV to see if this provider was recently exhausted
    const exhausted = await isProviderExhausted(env.QUOTA_KV, provider.name);
    if (exhausted) {
      errors.push(`${provider.name}: skipped (recently exhausted)`);
      continue;
    }

    const tryFn = PROVIDER_TRY_FN[provider.type];
    if (!tryFn) continue;

    try {
      const result = await tryFn(env, messages, preferredModel || provider.model);
      if (!result) {
        errors.push(`${provider.name}: no API key configured`);
        continue;
      }

      // Success! Clear any exhaustion marker (provider is healthy again)
      await clearProviderExhausted(env.QUOTA_KV, provider.name);

      return new Response(JSON.stringify({
        content: result.content,
        model: result.model,
        provider: result.provider,
        free: true,
        cost: 0,
      }), {
        headers: {
          'Content-Type': 'application/json',
          'X-Edge-AI': result.provider,
          'X-Free-Provider': 'true',
          'X-Cost': '0',
          'X-Provider-Chain': FREE_PROVIDER_CHAIN.map(p => p.name).join(' -> '),
          'X-Provider-Used': result.provider,
        },
      });
    } catch (err: any) {
      const msg = String(err?.message || err);
      if (msg.includes('EXHAUSTED:')) {
        const pname = msg.split(':')[1];
        await markProviderExhausted(env.QUOTA_KV, pname);
        errors.push(`${provider.name}: quota exhausted (cached 1h)`);
      } else {
        errors.push(`${provider.name}: ${msg.slice(0, 200)}`);
      }
    }
  }

  // All free providers exhausted — return error with details
  return new Response(JSON.stringify({
    error: 'All free providers exhausted or unavailable',
    details: errors,
    suggestion: 'Add a fallback_provider + fallback_key to use paid credits, or wait for free quota reset.',
  }), {
    status: 503,
    headers: {
      'Content-Type': 'application/json',
      'X-Free-Provider': 'false',
      'X-All-Exhausted': 'true',
    },
  });
}

// ═══════════════════════════════════════════════════════════
// WORKERS AI — Edge Inference
// ═══════════════════════════════════════════════════════════

async function handleWorkersAI(request: Request, env: Env): Promise<Response> {
  const url = new URL(request.url);
  const pathParts = url.pathname.split('/').filter(Boolean);

  // /ai/smart — 🆓 FREE-FIRST smart routing with cascading failover
  if (pathParts[1] === 'smart' && request.method === 'POST') {
    const body = await request.json<{
      messages: ChatMessage[];
      model?: string;
      fallback_provider?: string;
      fallback_key?: string;
    }>();

    // Try free chain first
    const freeResponse = await smartChatWithFailover(env, body.messages, body.model);
    if (freeResponse.status === 200) {
      return freeResponse;
    }

    // All free exhausted — try paid fallback if provided
    if (body.fallback_provider && body.fallback_key) {
      return await handleAIGatewayFallback(body);
    }

    // Return the free exhaustion error
    return freeResponse;
  }

  // /ai/chat → text generation (direct Workers AI — FREE)
  if (pathParts[1] === 'chat' && request.method === 'POST') {
    const body = await request.json<{ messages: ChatMessage[]; model?: string }>();
    const model = body.model || '@cf/meta/llama-3.1-8b-instruct';
    const response = await env.AI.run(model, {
      messages: body.messages,
      stream: false,
    });
    return new Response(JSON.stringify(response), {
      headers: {
        'Content-Type': 'application/json',
        'X-Edge-AI': 'workers-ai',
        'X-Free-Provider': 'true',
        'X-Cost': '0',
      },
    });
  }

  // /ai/embeddings → edge embeddings (FREE)
  if (pathParts[1] === 'embeddings' && request.method === 'POST') {
    const body = await request.json<{ text: string | string[]; model?: string }>();
    const model = body.model || '@cf/baai/bge-base-en-v1.5';
    const texts = Array.isArray(body.text) ? body.text : [body.text];
    const response = await env.AI.run(model, { text: texts });
    return new Response(JSON.stringify(response), {
      headers: {
        'Content-Type': 'application/json',
        'X-Edge-AI': 'workers-ai',
        'X-Free-Provider': 'true',
        'X-Cost': '0',
      },
    });
  }

  return new Response('Not Found', { status: 404 });
}

async function handleAIGatewayFallback(body: any): Promise<Response> {
  const provider = body.fallback_provider;
  const apiKey = body.fallback_key;
  const config = AI_PROVIDER_CONFIG[provider];
  if (!config) {
    return new Response(JSON.stringify({ error: 'Unknown fallback provider' }), { status: 400, headers: { 'Content-Type': 'application/json' } });
  }
  const payload = {
    model: body.model || _defaultModel(provider),
    messages: body.messages,
    temperature: body.temperature || 0.7,
  };
  const targetUrl = config.baseUrl + '/chat/completions';
  const originHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    'Authorization': config.headerName === 'x-api-key' ? apiKey : `Bearer ${apiKey}`,
  };
  const originRequest = new Request(targetUrl, { method: 'POST', headers: originHeaders, body: JSON.stringify(payload) });
  const response = await fetch(originRequest);
  return new Response(response.body, {
    status: response.status,
    headers: {
      ...Object.fromEntries(response.headers),
      'X-AI-Gateway': provider,
      'X-Free-Provider': 'false',
      'X-Fallback-Used': 'true',
    },
  });
}

function _defaultModel(provider: string): string {
  const defaults: Record<string, string> = {
    openai: 'gpt-4o-mini',
    anthropic: 'claude-3-haiku-20240307',
    groq: 'llama-3.1-8b-instant',
    openrouter: 'openrouter/auto',
    deepseek: 'deepseek-chat',
    fireworks: 'accounts/fireworks/models/llama-v3p1-8b-instruct',
    gemini: 'gemini-1.5-flash',
    mistral: 'mistral-small-latest',
    nvidia: 'meta/llama-3.1-nemotron-70b-instruct',
    kimi: 'kimi-k2.5',
    together: 'meta-llama/Llama-3.3-70B-Instruct-Turbo',
  };
  return defaults[provider] || '';
}

// ═══════════════════════════════════════════════════════════
// AI GATEWAY — Unified AI Provider Proxy with Caching
// ═══════════════════════════════════════════════════════════

const AI_PROVIDER_CONFIG: Record<string, { baseUrl: string; headerName: string; queryParam?: string }> = {
  openai: { baseUrl: 'https://api.openai.com/v1', headerName: 'Authorization' },
  anthropic: { baseUrl: 'https://api.anthropic.com/v1', headerName: 'x-api-key' },
  groq: { baseUrl: 'https://api.groq.com/openai/v1', headerName: 'Authorization' },
  openrouter: { baseUrl: 'https://openrouter.ai/api/v1', headerName: 'Authorization' },
  deepseek: { baseUrl: 'https://api.deepseek.com/v1', headerName: 'Authorization' },
  fireworks: { baseUrl: 'https://api.fireworks.ai/inference/v1', headerName: 'Authorization' },
  gemini: { baseUrl: 'https://generativelanguage.googleapis.com/v1beta/models', headerName: 'Authorization', queryParam: 'key' },
  mistral: { baseUrl: 'https://api.mistral.ai/v1', headerName: 'Authorization' },
  nvidia: { baseUrl: 'https://integrate.api.nvidia.com/v1', headerName: 'Authorization' },
  kimi: { baseUrl: 'https://api.moonshot.cn/v1', headerName: 'Authorization' },
  together: { baseUrl: 'https://api.together.xyz/v1', headerName: 'Authorization' },
};

async function handleAIGateway(request: Request): Promise<Response> {
  const url = new URL(request.url);
  const pathParts = url.pathname.split('/').filter(Boolean);
  const provider = pathParts[2];
  const config = AI_PROVIDER_CONFIG[provider];

  if (!config) {
    return new Response(JSON.stringify({ error: 'Unknown provider', available: Object.keys(AI_PROVIDER_CONFIG) }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  // Get API key from request header
  const apiKey = request.headers.get('X-AI-Key');
  if (!apiKey) {
    return new Response(JSON.stringify({ error: 'Missing X-AI-Key header' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  // Build target URL
  const targetPath = '/' + pathParts.slice(3).join('/');
  const targetUrl = config.baseUrl + targetPath + url.search;

  // Check cache for identical requests
  const cache = caches.default;
  if (request.method === 'POST') {
    const cacheKey = new Request(request.url + '?_hash=' + await hashRequestBody(request.clone()), { method: 'GET' });
    const cached = await cache.match(cacheKey);
    if (cached) {
      return new Response(cached.body, {
        status: cached.status,
        headers: { ...Object.fromEntries(cached.headers), 'X-AI-Gateway-Cache': 'HIT' },
      });
    }
  }

  // Forward to provider
  const originRequest = new Request(targetUrl, {
    method: request.method,
    headers: {
      ...Object.fromEntries(request.headers),
      [config.headerName]: config.headerName === 'x-api-key' ? apiKey : `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: request.body,
  });

  const response = await fetch(originRequest);

  // Cache successful completions
  if (request.method === 'POST' && response.status === 200 && targetPath.includes('/chat/completions')) {
    const responseClone = response.clone();
    const cacheKey = new Request(request.url + '?_hash=' + await hashRequestBody(request.clone()), { method: 'GET' });
    const cacheResponse = new Response(responseClone.body, {
      status: responseClone.status,
      headers: { ...Object.fromEntries(responseClone.headers), 'Cache-Control': 'public, max-age=300' },
    });
    await cache.put(cacheKey, cacheResponse);
  }

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: {
      ...Object.fromEntries(response.headers),
      'X-AI-Gateway': provider,
      'X-AI-Gateway-Cache': 'MISS',
    },
  });
}

async function hashRequestBody(request: Request): Promise<string> {
  const body = await request.text();
  const encoder = new TextEncoder();
  const data = encoder.encode(body);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, '0')).join('').slice(0, 16);
}

// ═══════════════════════════════════════════════════════════
// CRYPTO API PROXY — Edge cache for crypto data
// ═══════════════════════════════════════════════════════════

async function handleCryptoAPI(request: Request, ctx: ExecutionContext): Promise<Response> {
  const url = new URL(request.url);
  const pathParts = url.pathname.split('/').filter(Boolean);
  const source = pathParts[3]; // e.g., 'coingecko', 'helius' (path: /api/v1/crypto/{source}/...)
  const config = CRYPTO_EDGE_ORIGINS[source];

  if (!config) {
    return new Response(JSON.stringify({ error: 'Unknown crypto source' }), { status: 400, headers: { 'Content-Type': 'application/json' } });
  }

  const targetPath = '/' + pathParts.slice(3).join('/');
  const targetUrl = config + targetPath + url.search;

  const cache = caches.default;
  if (request.method === 'GET') {
    const cached = await cache.match(request);
    if (cached) {
      return new Response(cached.body, {
        status: cached.status,
        headers: { ...Object.fromEntries(cached.headers), 'X-Crypto-Cache': 'HIT' },
      });
    }
  }

  const originRequest = new Request(targetUrl, { method: request.method, headers: request.headers });
  const response = await fetch(originRequest);

  // Cache GET responses aggressively
  if (request.method === 'GET' && response.status === 200) {
    const ttl = source === 'coingecko' ? 30 : 60;
    const responseClone = response.clone();
    ctx.waitUntil(
      cache.put(
        request,
        new Response(responseClone.body, {
          status: responseClone.status,
          headers: { ...Object.fromEntries(responseClone.headers), 'Cache-Control': `public, max-age=${ttl}` },
        })
      )
    );
  }

  return new Response(response.body, {
    status: response.status,
    headers: {
      ...Object.fromEntries(response.headers),
      'X-Crypto-Cache': 'MISS',
      'X-Crypto-Source': source,
    },
  });
}

// ═══════════════════════════════════════════════════════════
// MAIN HANDLER
// ═══════════════════════════════════════════════════════════

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);
    const origin = env.API_ORIGIN || 'https://api.rugmunch.io';

    // Route crypto API requests directly at edge (faster than origin)
    if (url.pathname.startsWith('/api/v1/crypto/')) {
      return handleCryptoAPI(request, ctx);
    }

    // Route Workers AI requests
    if (url.pathname.startsWith('/ai/')) {
      if (url.pathname.startsWith('/ai/gateway/')) {
        return handleAIGateway(request);
      }
      return handleWorkersAI(request, env);
    }

    // Security: block common bot patterns
    const ua = (request.headers.get('User-Agent') || '').toLowerCase();
    const blockedUA = ['sqlmap', 'nikto', 'nmap', 'masscan', 'zgrab'];
    if (blockedUA.some((b) => ua.includes(b))) {
      return new Response('Forbidden', { status: 403 });
    }

    // Build origin request
    const originUrl = origin + url.pathname + url.search;
    const originRequest = new Request(originUrl, {
      method: request.method,
      headers: request.headers,
      body: request.body,
    });

    // Try cache for GETs
    const cache = caches.default;
    if (isCacheable(request)) {
      const cached = await cache.match(request);
      if (cached) {
        return new Response(cached.body, {
          status: cached.status,
          headers: {
            ...Object.fromEntries(cached.headers),
            'X-Cache': 'HIT',
          },
        });
      }
    }

    // Fetch from origin
    let response: Response;
    try {
      response = await fetch(originRequest);
    } catch (e) {
      return new Response(JSON.stringify({ error: 'Origin unreachable' }), {
        status: 503,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const responseClone = response.clone();

    // Apply edge-optimized headers (security + performance + cache)
    const headers = getEdgeOptimizedHeaders(response, url.pathname);
    headers.set('X-Cache', 'MISS');

    // Cache if cacheable
    if (isCacheable(request) && response.status === 200) {
      const ttl = getCacheTTL(url.pathname);
      headers.set('Cache-Control', `public, max-age=${ttl}, s-maxage=${ttl * 2}`);
      ctx.waitUntil(
        cache.put(
          request,
          new Response(responseClone.body, {
            status: responseClone.status,
            headers: {
              ...Object.fromEntries(responseClone.headers),
              'Cache-Control': `public, max-age=${ttl}, s-maxage=${ttl * 2}`,
            },
          })
        )
      );
    } else {
      headers.set('Cache-Control', 'no-store');
    }

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers,
    });
  },
};
