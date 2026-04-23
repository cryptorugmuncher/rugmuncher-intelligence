/**
 * RugMuncher API Gateway Worker
 * Edge-caches API responses, adds security headers, routes traffic,
 * and integrates Cloudflare Workers AI + AI Gateway.
 */

export interface Env {
  API_ORIGIN: string;
  CACHE_TTL_SECONDS: string;
  AI: any; // Workers AI binding
}

const CACHEABLE_PATHS = [
  '/api/v1/health',
  '/api/v1/email/business-emails',
  '/api/v1/status',
  '/api/v1/rag/namespaces',
];

const CACHEABLE_PREFIXES = [
  '/api/v1/profiles/',
  '/api/v1/news',
];

function isCacheable(request: Request): boolean {
  if (request.method !== 'GET') return false;
  const url = new URL(request.url);
  if (CACHEABLE_PATHS.includes(url.pathname)) return true;
  return CACHEABLE_PREFIXES.some((p) => url.pathname.startsWith(p));
}

function getCacheTTL(path: string): number {
  if (path.startsWith('/api/v1/profiles/')) return 60;
  if (path.startsWith('/api/v1/news')) return 300;
  return 30;
}

// ═══════════════════════════════════════════════════════════
// WORKERS AI — Edge Inference
// ═══════════════════════════════════════════════════════════

async function handleWorkersAI(request: Request, env: Env): Promise<Response> {
  const url = new URL(request.url);
  const pathParts = url.pathname.split('/').filter(Boolean);

  // /ai/smart — 🆓 FREE-FIRST smart routing (tries Workers AI first, then fallback)
  if (pathParts[1] === 'smart' && request.method === 'POST') {
    const body = await request.json<{ messages: any[]; model?: string; fallback_provider?: string; fallback_key?: string }>();

    // 1. 🆓 ALWAYS try Workers AI first (FREE)
    try {
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
    } catch (e) {
      // Workers AI failed — try fallback if provided
      if (body.fallback_provider && body.fallback_key) {
        return await handleAIGatewayFallback(body);
      }
      return new Response(JSON.stringify({ error: 'Workers AI failed and no fallback provided', details: String(e) }), {
        status: 503,
        headers: { 'Content-Type': 'application/json' },
      });
    }
  }

  // /ai/chat → text generation (direct Workers AI — FREE)
  if (pathParts[1] === 'chat' && request.method === 'POST') {
    const body = await request.json<{ messages: any[]; model?: string }>();
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
    openrouter: 'openrouter/free',
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
// MAIN HANDLER
// ═══════════════════════════════════════════════════════════

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);
    const origin = env.API_ORIGIN || 'https://api.rugmunch.io';

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

    // Add security headers
    const headers = new Headers(response.headers);
    headers.set('X-Content-Type-Options', 'nosniff');
    headers.set('X-Frame-Options', 'DENY');
    headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
    headers.set('X-Cache', 'MISS');

    // Cache if cacheable
    if (isCacheable(request) && response.status === 200) {
      const ttl = getCacheTTL(url.pathname);
      headers.set('Cache-Control', `public, max-age=${ttl}`);
      ctx.waitUntil(
        cache.put(
          request,
          new Response(responseClone.body, {
            status: responseClone.status,
            headers: {
              ...Object.fromEntries(responseClone.headers),
              'Cache-Control': `public, max-age=${ttl}`,
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
