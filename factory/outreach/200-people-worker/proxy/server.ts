/**
 * LinkedIn Proxy — Local server behind Cloudflare Tunnel
 *
 * Runs on this machine (residential IP). CF Worker sends LinkedIn URLs
 * to this proxy via the tunnel. The proxy fetches using the residential IP.
 *
 * Usage: npx tsx proxy/server.ts
 * Listens on: localhost:3456
 * Tunnel hostname: linkedin-proxy.insuranceinformatic.agency
 */

import http from 'node:http';

const PORT = 3456;

const USER_AGENTS = [
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Safari/605.1.15',
];

function pickRandom<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

function readBody(req: http.IncomingMessage): Promise<string> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    req.on('data', (chunk) => chunks.push(chunk));
    req.on('end', () => resolve(Buffer.concat(chunks).toString()));
    req.on('error', reject);
  });
}

function jsonResponse(res: http.ServerResponse, data: unknown, status = 200) {
  res.writeHead(status, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(data));
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url || '/', `http://localhost:${PORT}`);

  // Health check
  if (url.pathname === '/health') {
    return jsonResponse(res, { status: 'ok', proxy: 'linkedin-proxy', residential: true });
  }

  // Proxy endpoint
  if (url.pathname === '/fetch' && req.method === 'POST') {
    try {
      const auth = req.headers['authorization'];
      if (auth !== `Bearer ${process.env.PROXY_SECRET || 'linkedin-proxy-2026'}`) {
        return jsonResponse(res, { error: 'Unauthorized' }, 401);
      }

      const raw = await readBody(req);
      const body = JSON.parse(raw) as { url: string };

      if (!body.url || !body.url.includes('linkedin.com')) {
        return jsonResponse(res, { error: 'Only LinkedIn URLs allowed' }, 400);
      }

      const start = Date.now();
      const response = await fetch(body.url, {
        headers: {
          'User-Agent': pickRandom(USER_AGENTS),
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Language': 'en-US,en;q=0.9',
          'Connection': 'keep-alive',
          'Upgrade-Insecure-Requests': '1',
          'Cache-Control': 'no-cache',
        },
        redirect: 'follow',
      });

      const html = await response.text();

      return jsonResponse(res, {
        url: body.url,
        status: response.status,
        body: html,
        durationMs: Date.now() - start,
        residential: true,
      });
    } catch (err) {
      return jsonResponse(res, {
        error: err instanceof Error ? err.message : String(err),
      }, 500);
    }
  }

  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('LinkedIn Proxy\n\nGET /health\nPOST /fetch { url: "..." }');
});

server.listen(PORT, () => {
  console.log(`LinkedIn proxy running on http://localhost:${PORT}`);
  console.log('Tunnel: linkedin-proxy.insuranceinformatic.agency');
});
