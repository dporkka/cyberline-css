/**
 * Read-only staging smoke: NEVER provides payment credentials or settles funds.
 * Designed for isolated testnet/demo deployments, not production gateways.
 */
import { pathToFileURL } from 'node:url';

function assertOrigin(raw) {
  const url = new URL(raw);
  if (url.username || url.password) throw new Error('URL credentials are forbidden');
  if (url.search || url.hash) throw new Error('URL query/fragment is forbidden');
  if (url.pathname !== '/' && url.pathname !== '') throw new Error('URL must be an origin');
  if (url.protocol !== 'https:' &&
      !(url.protocol === 'http:' && ['localhost', '127.0.0.1', '[::1]'].includes(url.hostname))) {
    throw new Error('HTTPS is required for remote smoke targets');
  }
  return url.origin;
}

function requireStatus(response, expected, path) {
  if (response.status !== expected) throw new Error(path + ': expected ' + expected + ', received ' + response.status);
}

export async function runStagingSmoke(origin, { request = fetch, mode = 'disabled' } = {}) {
  const base = assertOrigin(origin);
  if (!['disabled', 'testnet'].includes(mode)) throw new Error('Mode must be disabled or testnet');
  const results = [];
  async function check(path, expected, options) {
    const response = await request(base + path, options);
    requireStatus(response, expected, path);
    results.push({ path, status: response.status });
    return response;
  }

  const health = await (await check('/v1/health', 200)).json();
  if (health.status !== 'ok' || health.live_payments !== false) {
    throw new Error('Health endpoint no longer identifies itself as a non-live pilot');
  }
  const catalog = await (await check('/v1/catalog', 200)).json();
  if (catalog?.products?.[0]?.license !== 'MIT' ||
      catalog.products[0].price_usd !== '0' ||
      catalog.products[1].x402.enabled !== (mode === 'testnet') ||
      catalog.products[1].stripe.enabled !== false) {
    throw new Error('Catalog does not match expected testnet-only commercial gate');
  }
  await check('/v1/agent/theme?accent=javascript%3Abad', 400);
  const payment = await check('/v1/agent/theme?accent=%23ffcc00', mode === 'testnet' ? 402 : 503);
  if (mode === 'testnet') {
    const header = payment.headers.get('PAYMENT-REQUIRED');
    if (!header) throw new Error('Missing x402 v2 PAYMENT-REQUIRED header');
    const challenge = JSON.parse(Buffer.from(header, 'base64').toString('utf8'));
    if (challenge.x402Version !== 2 || challenge.accepts?.[0]?.network !== 'eip155:84532') {
      throw new Error('Unexpected payment protocol or network');
    }
  }
  await check('/v1/checkout', 503, { method: 'POST' });
  return results;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const [origin, mode = 'disabled'] = process.argv.slice(2);
  if (!origin) {
    console.error('Usage: node scripts/smoke.mjs https://staging.example disabled|testnet');
    process.exitCode = 2;
  } else {
    runStagingSmoke(origin, { mode })
      .then((results) => console.log('PASS staging smoke:', results.map((r) => r.path + '=' + r.status).join(', ')))
      .catch((error) => { console.error('FAIL staging smoke:', error.message); process.exitCode = 1; });
  }
}
