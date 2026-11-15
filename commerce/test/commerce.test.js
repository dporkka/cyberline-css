import assert from 'node:assert/strict';
import test from 'node:test';
import { createApp } from '../src/app.js';
import { generateTheme } from '../src/theme.js';

function request(app, url, options = {}) {
  return app.request('http://syntyr.test' + url, {
    ...options,
    headers: { 'cf-connecting-ip': '198.51.100.3', ...options.headers },
  });
}
const rateLimiter = { async limit() { return { success: true }; } };


test('public catalog is readable without auth, clearly separates free and pilot products', async () => {
  const response = await request(createApp({}), '/v1/catalog');
  assert.equal(response.status, 200);
  const catalog = await response.json();
  assert.equal(catalog.schema_version, 1);
  assert.equal(catalog.products[0].license, 'MIT');
  assert.equal(catalog.products[0].price_usd, '0');
  assert.equal(catalog.products[1].x402.enabled, false);
  assert.equal(catalog.products[1].stripe.enabled, false);
  assert.equal(response.headers.get('cache-control'), 'no-store');
});

test('x402 route fails closed without validated testnet configuration', async () => {
  const response = await request(createApp({ X402_TESTNET_ENABLED: 'true' }), '/v1/agent/theme');
  assert.equal(response.status, 503);
  assert.match((await response.json()).error, /unavailable/);
});

test('invalid custom colors are rejected before a payment attempt', async () => {
  const app = createApp({
    X402_TESTNET_ENABLED: 'true',
    X402_PAY_TO: '0x' + 'a'.repeat(40),
    IP_RATE_LIMITER: rateLimiter,
  }, { makeX402Gate: () => async () => { throw new Error('should not charge'); } });
  const response = await request(app, '/v1/agent/theme?accent=javascript:alert(1)');
  assert.equal(response.status, 400);
});

test('successful x402-gated theme is generated with readable contrast and bounded CSS', async () => {
  let gated = 0;
  const app = createApp({
    X402_TESTNET_ENABLED: 'true',
    X402_PAY_TO: '0x' + 'a'.repeat(40),
    IP_RATE_LIMITER: rateLimiter,
  }, { makeX402Gate: () => async (_c, next) => { gated++; return next(); } });
  const response = await request(app, '/v1/agent/theme?accent=%23ffcc00&surface=%23111222');
  assert.equal(response.status, 200);
  const body = await response.json();
  assert.equal(body.payment_method, 'x402');
  assert.equal(body.tokens['--syn-accent'], '#ffcc00');
  assert.ok(body.accessibility.accent_text_contrast >= 4.5);
  assert.equal(gated, 1);
  assert.equal(response.headers.get('cache-control'), 'no-store');
});

test('theme token generator rejects invalid input and produces accessible contrasting text', () => {
  assert.throws(() => generateTheme({ accent: '#1234' }), /accent/);
  assert.ok(generateTheme({ accent: '#f0f0f0' }).accessibility.accent_text_contrast >= 4.5);
  assert.ok(generateTheme({ accent: '#001122' }).accessibility.accent_text_contrast >= 4.5);
});

test('Stripe checkout is disabled unless complete explicit configuration and DB exist', async () => {
  const app = createApp({ STRIPE_PILOT_ENABLED: 'true' });
  const response = await request(app, '/v1/checkout', { method: 'POST' });
  assert.equal(response.status, 503);
  assert.match((await response.json()).error, /unavailable/);
});

test('Stripe webhook cannot grant credits without a valid signed request', async () => {
  const response = await request(createApp({
    STRIPE_PILOT_ENABLED: 'true',
    STRIPE_SECRET_KEY: 'sk_test_local',
    STRIPE_WEBHOOK_SECRET: 'whsec_test',
    STRIPE_PRICE_ID: 'price_1234',
    STRIPE_SUCCESS_URL: 'https://syntyr.example/success',
    STRIPE_CANCEL_URL: 'https://syntyr.example/cancel',
    ENTITLEMENTS_DB: {},
    IP_RATE_LIMITER: rateLimiter,
    CHECKOUT_RATE_LIMITER: rateLimiter,
  }), '/v1/webhooks/stripe', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ type: 'checkout.session.completed', data: { object: { id: 'cs_fake', payment_status: 'paid' } } }),
  });
  assert.equal(response.status, 400);
});

test('real x402 v2 adapter returns a payment challenge without exposing tokens', async () => {
  const response = await request(createApp({
    X402_TESTNET_ENABLED: 'true',
    X402_PAY_TO: '0x' + 'a'.repeat(40),
    IP_RATE_LIMITER: rateLimiter,
  }), '/v1/agent/theme');
  assert.equal(response.status, 402);
  const header = response.headers.get('payment-required');
  assert.ok(header);
  const challenge = JSON.parse(Buffer.from(header, 'base64').toString('utf8'));
  assert.equal(challenge.x402Version, 2);
  assert.equal(challenge.accepts[0].network, 'eip155:84532');
  assert.equal(challenge.accepts[0].payTo, '0x' + 'a'.repeat(40));
});

class FakeD1 {
  constructor() { this.rows = new Map(); this.revocations = new Set(); }
  prepare(query) {
    return { bind: (...args) => ({
      run: async () => {
        if (query.startsWith('INSERT INTO stripe_credit_purchases')) {
          const [sessionId, hash] = args;
          if (this.rows.has(sessionId)) throw new Error('duplicate session');
          this.rows.set(sessionId, { hash, status: 'pending', credits: 0, payment_intent: null });
          return { meta: { changes: 1 } };
        }
        if (query.startsWith('INSERT OR IGNORE INTO stripe_payment_revocations')) {
          this.revocations.add(args[0]);
          return { meta: { changes: 1 } };
        }
        if (query.includes("status = 'paid', credits = ?")) {
          const [credits, paymentIntent, sessionId, hash] = args;
          const row = this.rows.get(sessionId);
          if (!row || row.hash !== hash || row.status !== 'pending' || this.revocations.has(paymentIntent)) return { meta: { changes: 0 } };
          Object.assign(row, { status: 'paid', credits, payment_intent: paymentIntent });
          return { meta: { changes: 1 } };
        }
        if (query.includes("status = 'refunded'")) {
          const [paymentIntent] = args;
          const row = [...this.rows.values()].find((row) => row.payment_intent === paymentIntent && row.status === 'paid');
          if (!row) return { meta: { changes: 0 } };
          Object.assign(row, { status: 'refunded', credits: 0 });
          return { meta: { changes: 1 } };
        }
        if (query.includes('credits = credits - 1')) {
          const [hash] = args;
          const row = [...this.rows.values()].find((r) => r.hash === hash && r.status === 'paid' && r.credits > 0);
          if (!row) return { meta: { changes: 0 } };
          row.credits--;
          return { meta: { changes: 1 } };
        }
        throw new Error('Unknown test SQL: ' + query);
      },
      first: async () => {
        const [hash] = args;
        const row = [...this.rows.values()].find((r) => r.hash === hash);
        return row ? { status: row.status, credits: row.credits } : null;
      },
    }) };
  }
}

function stripeEnv(db) {
  return {
    STRIPE_PILOT_ENABLED: 'true',
    STRIPE_SECRET_KEY: 'sk_test_local_only',
    STRIPE_WEBHOOK_SECRET: 'whsec_local_test',
    STRIPE_PRICE_ID: 'price_local123',
    STRIPE_SUCCESS_URL: 'https://syntyr.example/complete',
    STRIPE_CANCEL_URL: 'https://syntyr.example/cancel',
    ENTITLEMENTS_DB: db,
    IP_RATE_LIMITER: rateLimiter,
    CHECKOUT_RATE_LIMITER: rateLimiter,
  };
}

async function signedStripeWebhook(app, event, secret = 'whsec_local_test') {
  const body = JSON.stringify(event);
  const timestamp = Math.floor(Date.now() / 1000);
  const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(secret),
    { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const sig = new Uint8Array(await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(timestamp + '.' + body)));
  const hex = [...sig].map((n) => n.toString(16).padStart(2, '0')).join('');
  return request(app, '/v1/webhooks/stripe', {
    method: 'POST',
    headers: { 'stripe-signature': 't=' + timestamp + ',v1=' + hex },
    body,
  });
}

test('Stripe test checkout grants 20 atomic credits only after webhook; duplicate delivery cannot reset credits', async () => {
  const db = new FakeD1();
  let requestCount = 0;
  const app = createApp(stripeEnv(db), {
    fetchImpl: async (url, options) => {
      requestCount++;
      assert.equal(url, 'https://api.stripe.com/v1/checkout/sessions');
      const form = new URLSearchParams(options.body);
      assert.equal(form.get('line_items[0][price]'), 'price_local123');
      assert.equal(form.get('mode'), 'payment');
      assert.equal(form.get('line_items[0][quantity]'), '1');
      assert.equal(options.headers['Stripe-Version'], '2026-09-30.endive');
      assert.match(form.get('integration_identifier'), /^syntyr-agent-[a-z]{8}$/);
      return new Response(JSON.stringify({
        id: 'cs_test_abc',
        url: 'https://checkout.stripe.com/c/pay/cs_test_abc',
      }), { status: 200 });
    },
  });

  const checkout = await request(app, '/v1/checkout', { method: 'POST' });
  assert.equal(checkout.status, 201);
  assert.equal(requestCount, 1);
  assert.equal(checkout.headers.get('cache-control'), 'no-store');
  const created = await checkout.json();
  assert.equal(created.credits_after_payment, 20);
  assert.match(created.access_token, /^[\da-f-]{36}\.[\da-f-]{36}$/);
  assert.doesNotMatch(JSON.stringify([...db.rows.values()]), /[\da-f-]{36}\.[\da-f-]{36}/);
  const auth = { authorization: 'Bearer ' + created.access_token };

  let credits = await request(app, '/v1/credits', { headers: auth });
  assert.deepEqual(await credits.json(), { status: 'pending', credits_remaining: 0 });
  let attempt = await request(app, '/v1/agent/theme', { headers: auth });
  assert.equal(attempt.status, 403);

  const hash = [...db.rows.values()][0].hash;
  const event = {
    id: 'evt_test_abc',
    type: 'checkout.session.completed',
    data: { object: {
      id: 'cs_test_abc',
      mode: 'payment',
      payment_status: 'paid',
      metadata: { sku: 'syntyr-agent-theme-20' },
      client_reference_id: hash,
      payment_intent: 'pi_test_abc',
    } },
  };
  let webhook = await signedStripeWebhook(app, event);
  assert.equal(webhook.status, 200);
  assert.equal((await webhook.json()).result, 'credited');

  attempt = await request(app, '/v1/agent/theme?accent=%23123456', { headers: auth });
  assert.equal(attempt.status, 200);
  assert.equal((await attempt.json()).payment_method, 'stripe');

  webhook = await signedStripeWebhook(app, event);
  assert.equal((await webhook.json()).result, 'already_processed_or_unknown');
  credits = await request(app, '/v1/credits', { headers: auth });
  assert.deepEqual(await credits.json(), { status: 'paid', credits_remaining: 19 });

  const invalid = await request(app, '/v1/agent/theme?accent=not-a-color', { headers: auth });
  assert.equal(invalid.status, 400);
  credits = await request(app, '/v1/credits', { headers: auth });
  assert.equal((await credits.json()).credits_remaining, 19);

  webhook = await signedStripeWebhook(app, {
    type: 'charge.refunded',
    data: { object: { payment_intent: 'pi_test_abc' } },
  });
  assert.equal((await webhook.json()).result, 'revoked');
  credits = await request(app, '/v1/credits', { headers: auth });
  assert.deepEqual(await credits.json(), { status: 'refunded', credits_remaining: 0 });
  attempt = await request(app, '/v1/agent/theme', { headers: auth });
  assert.equal(attempt.status, 403);
});

test('Stripe rejects malformed or stale signed payloads, and never exposes errors', async () => {
  const db = new FakeD1();
  const env = stripeEnv(db);
  const app = createApp(env);
  const missing = await request(app, '/v1/webhooks/stripe', { method: 'POST', body: '{}' });
  assert.equal(missing.status, 400);

  const wrong = await signedStripeWebhook(app, { type: 'checkout.session.completed' }, 'whsec_wrong');
  assert.equal(wrong.status, 400);
  assert.equal(db.rows.size, 0);
});

test('Bearer token without Stripe configuration never falls back to free access', async () => {
  const response = await request(createApp({
    X402_TESTNET_ENABLED: 'true',
    X402_PAY_TO: '0x' + 'a'.repeat(40),
    IP_RATE_LIMITER: rateLimiter,
  }), '/v1/agent/theme', { headers: { authorization: 'Bearer invalid' } });
  assert.equal(response.status, 503);
});

test('out-of-order Stripe refund cannot allow a later completion to re-credit the purchase', async () => {
  const db = new FakeD1();
  const app = createApp(stripeEnv(db), {
    fetchImpl: async () => new Response(JSON.stringify({
      id: 'cs_test_refunded_early',
      url: 'https://checkout.stripe.com/c/pay/cs_test_refunded_early',
    })),
  });
  const response = await request(app, '/v1/checkout', { method: 'POST' });
  assert.equal(response.status, 201);
  const { access_token } = await response.json();
  const hash = [...db.rows.values()][0].hash;

  let webhook = await signedStripeWebhook(app, {
    type: 'charge.refunded',
    data: { object: { payment_intent: 'pi_test_early' } },
  });
  assert.equal(webhook.status, 200);

  webhook = await signedStripeWebhook(app, {
    type: 'checkout.session.completed',
    data: { object: {
      id: 'cs_test_refunded_early',
      mode: 'payment',
      payment_status: 'paid',
      metadata: { sku: 'syntyr-agent-theme-20' },
      client_reference_id: hash,
      payment_intent: 'pi_test_early',
    } },
  });
  assert.equal(webhook.status, 200);

  const credits = await request(app, '/v1/credits', {
    headers: { authorization: 'Bearer ' + access_token },
  });
  assert.notEqual((await credits.json()).credits_remaining, 20);
});

test('Stripe webhook refuses oversized request bodies before attempting verification', async () => {
  const app = createApp(stripeEnv(new FakeD1()));
  const response = await request(app, '/v1/webhooks/stripe', {
    method: 'POST',
    body: 'x'.repeat(1024 * 1024 + 1),
    headers: { 'stripe-signature': 't=1,v1=' + '0'.repeat(64) },
  });
  assert.equal(response.status, 413);
});

test('Stripe accepts test-only restricted keys, never live keys', async () => {
  const { stripeReady } = await import('../src/stripe.js');
  const props = stripeEnv(new FakeD1());
  assert.equal(stripeReady({ ...props, STRIPE_SECRET_KEY: 'rk_test_restricted' }), true);
  assert.equal(stripeReady({ ...props, STRIPE_SECRET_KEY: 'rk_live_not_allowed' }), false);
  assert.equal(stripeReady({ ...props, STRIPE_SECRET_KEY: 'sk_live_not_allowed' }), false);
});
