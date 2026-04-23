/**
 * RugMuncher Frontend Edge Worker
 * Adds security headers, geo-redirects, and basic bot protection.
 */

export default {
  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);

    // Block bad bots
    const ua = (request.headers.get('User-Agent') || '').toLowerCase();
    const badBots = ['sqlmap', 'nikto', 'nmap', 'masscan', 'zgrab', 'scrapy'];
    if (badBots.some((b) => ua.includes(b))) {
      return new Response('Forbidden', { status: 403 });
    }

    // Fetch from origin (Caddy/static server)
    const response = await fetch(request);

    const headers = new Headers(response.headers);
    headers.set('X-Frame-Options', 'DENY');
    headers.set('X-Content-Type-Options', 'nosniff');
    headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
    headers.set('Permissions-Policy', 'geolocation=(), microphone=(), camera=()');

    // Cache static assets aggressively
    if (url.pathname.match(/\.(js|css|png|jpg|jpeg|webp|gif|ico|svg|woff|woff2|ttf)$/)) {
      headers.set('Cache-Control', 'public, max-age=86400, immutable');
    }

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers,
    });
  },
};
