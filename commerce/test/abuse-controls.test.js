import assert from 'node:assert/strict';
import test from 'node:test';
import { createApp } from '../src/app.js';

const address = '0x' + 'a'.repeat(40);
const rateIp = '192.0.2.12';
const rateHeader = { 'cf-connecting-ip': rateIp };
const limiter = {
  calls: [],
  async limit({ key }) {
    this.calls.push(key);
    return { success: true };
  },
};

function reset() { limiter.calls.length = 0; }
function readyEnv(override = {}) {
  return {
    X402_TESTNET_ENABLED: 'true',
    X402_PAY_TO: address,
    IP_RATE_LIMITER: limiter,
    CHECKOUT_RATE_LIMITER: limiter,
    ...override,
  };
}
function doRequest(app, path, options = {}) {
  return app.request(path, { ...options, headers: { ...rateHeader, ...options.headers } });
}

test('testnet request refuses to call payment facilitator if rate limiter binding is missing', async () => {
  let paymentCalls = 0;
  const app = createApp(readyEnv({ IP_RATE_LIMITER: undefined }), {
    makeX402Gate: () => async (_c, next) => { paymentCalls++; return next(); },
  });
  const response = await doRequest(app, '/v1/agent/theme');
  assert.equal(response.status, 503);
  assert.equal(paymentCalls, 0);
});

test('Cloudflare client address is required for abuse guard; forwarded-for is ignored', async () => {
  const app = createApp(readyEnv(), {
    makeX402Gate: () => async (_c, next) => next(),
  });
  const response = await app.request('/v1/agent/theme', { headers: { 'x-forwarded-for': rateIp } });
  assert.equal(response.status, 503);
});

test('rate limited x402 request returns 429 before payment middleware and no charges', async () => {
  let paymentCalls = 0;
  const app = createApp(readyEnv({
    IP_RATE_LIMITER: { limit: async () => ({ success: false }) },
  }), {
    makeX402Gate: () => async (_c, next) => { paymentCalls++; return next(); },
  });
  const response = await doRequest(app, '/v1/agent/theme');
  assert.equal(response.status, 429);
  assert.equal(response.headers.get('retry-after'), '60');
  assert.equal(paymentCalls, 0);
  assert.equal(response.headers.get('cache-control'), 'no-store');
});

test('per-path client keys are separate; private user agent headers do not affect rate identity', async () => {
  reset();
  const app = createApp(readyEnv(), {
    makeX402Gate: () => async (_c, next) => next(),
  });
  assert.equal((await doRequest(app, '/v1/agent/theme')).status, 200);
  assert.deepEqual(limiter.calls, ['agent-theme:' + rateIp]);
});

test('fail closed on rate limiting service failures instead of falling back to paid route', async () => {
  const app = createApp(readyEnv({
    IP_RATE_LIMITER: { limit: async () => { throw new Error('limiter unavailable'); } },
  }), {
    makeX402Gate: () => async (_c, next) => next(),
  });
  const response = await doRequest(app, '/v1/agent/theme');
  assert.equal(response.status, 503);
  assert.deepEqual(await response.json(), { error: 'rate_limiter_unavailable' });
});

test('checkout refuses requests without dedicated checkout limiter binding', async () => {
  const app = createApp({
    STRIPE_PILOT_ENABLED: 'true',
    STRIPE_SECRET_KEY: 'sk_test_fake',
    STRIPE_WEBHOOK_SECRET: 'whsec_fake',
    STRIPE_PRICE_ID: 'price_test123',
    STRIPE_SUCCESS_URL: 'https://syntyr.example/success',
    STRIPE_CANCEL_URL: 'https://syntyr.example/cancel',
    ENTITLEMENTS_DB: {},
    IP_RATE_LIMITER: limiter,
  });
  const response = await doRequest(app, '/v1/checkout', { method: 'POST' });
  assert.equal(response.status, 503);
  assert.deepEqual(await response.json(), { error: 'rate_limiter_unavailable' });
});

test('staging request log includes safe route and request ID, never bearer data', async () => {
  const logs = [];
  const app = createApp({ LOG_REQUESTS: 'true' }, {
    logger: { info: (line) => logs.push(line) },
  });
  const secret = 'Bearer private-token-must-never-log';
  const response = await app.request('/v1/catalog?access_token=secret-in-query', {
    headers: { authorization: secret },
  });
  assert.equal(response.status, 200);
  assert.match(response.headers.get('x-request-id'), /^[0-9a-f-]{36}$/);
  assert.equal(logs.length, 1);
  const logged = JSON.parse(logs[0]);
  assert.equal(logged.route, '/v1/catalog');
  assert.equal(logged.status, 200);
  assert.equal(logged.request_id, response.headers.get('x-request-id'));
  assert.equal(logged.method, 'GET');
  assert.doesNotMatch(logs[0], /private-token|secret-in-query|Bearer|authorization/);
});
