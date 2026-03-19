/**
 * UT Sub-Hub 16: Distributed Fetcher
 *
 * Routes LinkedIn fetches through a Cloudflare Tunnel proxy
 * that exits via a residential IP. LinkedIn sees a normal home connection.
 *
 * Architecture:
 *   CF Worker → tunnel → local proxy (residential IP) → LinkedIn
 *
 * Tunnel hostname: linkedin-proxy.insuranceinformatic.agency
 */

export interface FetcherConfig {
  /** Proxy URL (Cloudflare Tunnel endpoint) */
  proxyUrl: string;
  /** Auth secret for the proxy */
  proxySecret: string;
  /** Request timeout in ms (default: 30000) */
  timeoutMs: number;
}

export interface FetchResult {
  url: string;
  status: number;
  body: string;
  fetchedAt: string;
  durationMs: number;
  residential: boolean;
  error: string | null;
}

const DEFAULT_CONFIG: FetcherConfig = {
  proxyUrl: 'https://linkedin-proxy.insuranceinformatic.agency',
  proxySecret: 'linkedin-proxy-2026',
  timeoutMs: 30_000,
};

/**
 * Fetch a LinkedIn URL through the residential proxy tunnel.
 */
export async function fetchUrl(
  url: string,
  config: Partial<FetcherConfig> = {},
): Promise<FetchResult> {
  const cfg = { ...DEFAULT_CONFIG, ...config };
  const start = Date.now();

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), cfg.timeoutMs);

    const response = await fetch(`${cfg.proxyUrl}/fetch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${cfg.proxySecret}`,
      },
      body: JSON.stringify({ url }),
      signal: controller.signal,
    });

    clearTimeout(timeout);

    const data = await response.json() as {
      url: string;
      status: number;
      body: string;
      durationMs: number;
      residential: boolean;
      error?: string;
    };

    if (data.error) {
      return {
        url,
        status: 0,
        body: '',
        fetchedAt: new Date().toISOString(),
        durationMs: Date.now() - start,
        residential: false,
        error: data.error,
      };
    }

    return {
      url,
      status: data.status,
      body: data.body,
      fetchedAt: new Date().toISOString(),
      durationMs: Date.now() - start,
      residential: data.residential,
      error: null,
    };
  } catch (err) {
    return {
      url,
      status: 0,
      body: '',
      fetchedAt: new Date().toISOString(),
      durationMs: Date.now() - start,
      residential: false,
      error: err instanceof Error ? err.message : String(err),
    };
  }
}
