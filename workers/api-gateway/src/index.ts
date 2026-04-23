/**
 * RugMuncher API Gateway Worker
 * Edge-caches API responses, adds security headers, and routes traffic.
 */

export interface Env {
  API_ORIGIN: string;
  CACHE_TTL_SECONDS: string;
}

const CACHEABLE_PATHS = [
  '/api/v1/health',
  '/api/v1/email/business-emails',
  '/api/v1/status',
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

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);
    const origin = env.API_ORIGIN || 'https://api.rugmunch.io';

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
        const resp = new Response(cached.body, {
          status: cached.status,
          headers: {
            ...Object.fromEntries(cached.headers),
            'X-Cache': 'HIT',
          },
        });
        return resp;
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

    // Clone for cache
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
