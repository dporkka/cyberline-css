import assert from 'node:assert/strict';
import test from 'node:test';
import { runStagingSmoke } from '../scripts/smoke.mjs';
import { createApp } from '../src/app.js';

test('staging smoke verifies disabled payment endpoints without sending funds', async () => {
  const app = createApp({});
  const results = await runStagingSmoke('http://localhost:8791', {
    request: (url, options) => app.request(url, options),
    mode: 'disabled',
  });
  assert.deepEqual(results.map((x) => x.status), [200, 200, 400, 503, 503]);
});

test('staging smoke verifies x402 challenge without constructing payment payload', async () => {
  const app = createApp({
    X402_TESTNET_ENABLED: 'true',
    X402_PAY_TO: '0x' + 'a'.repeat(40),
    IP_RATE_LIMITER: { async limit() { return { success: true }; } },
  });
  const results = await runStagingSmoke('http://localhost:8791', {
    request: (url, options = {}) => app.request(url, {
      ...options, headers: { ...options.headers, 'cf-connecting-ip': '192.0.2.44' },
    }),
    mode: 'testnet',
  });
  assert.deepEqual(results.map((x) => x.status), [200, 200, 400, 402, 503]);
});

test('smoke rejects non-HTTPS remote URLs, credentials, and query injection', async () => {
  await assert.rejects(() => runStagingSmoke('http://syntyr.example'), /HTTPS/);
  await assert.rejects(() => runStagingSmoke('https://user:pass@syntyr.example'), /credentials/);
  await assert.rejects(() => runStagingSmoke('https://syntyr.example/?a=1'), /query/);
});
