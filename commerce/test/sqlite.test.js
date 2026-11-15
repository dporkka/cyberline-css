import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { DatabaseSync } from 'node:sqlite';
import test from 'node:test';
import { createApp } from '../src/app.js';

class SqliteD1 {
  constructor() {
    this.db = new DatabaseSync(':memory:');
    this.db.exec(readFileSync(new URL('../schema.sql', import.meta.url), 'utf8'));
  }
  prepare(query) {
    const stmt = this.db.prepare(query);
    return { bind: (...args) => ({
      run: async () => ({ meta: { changes: stmt.run(...args).changes } }),
      first: async () => stmt.get(...args) ?? null,
    }) };
  }
}

const limiter = { async limit() { return { success: true }; } };
function send(app, path, options = {}) {
  return app.request(path, {
    ...options,
    headers: { 'cf-connecting-ip': '203.0.113.12', ...options.headers },
  });
}

function configuredEnv(db) {
  return {
    STRIPE_PILOT_ENABLED: 'true',
    STRIPE_SECRET_KEY: 'sk_test_local',
    STRIPE_WEBHOOK_SECRET: 'whsec_local',
    STRIPE_PRICE_ID: 'price_local',
    STRIPE_SUCCESS_URL: 'https://syntyr.example/success',
    STRIPE_CANCEL_URL: 'https://syntyr.example/cancel',
    ENTITLEMENTS_DB: db,
    IP_RATE_LIMITER: limiter,
    CHECKOUT_RATE_LIMITER: limiter,
  };
}

async function signedWebhook(app, event) {
  const body = JSON.stringify(event);
  const ts = Math.floor(Date.now() / 1000);
  const key = await crypto.subtle.importKey('raw', new TextEncoder().encode('whsec_local'), {
    name: 'HMAC', hash: 'SHA-256',
  }, false, ['sign']);
  const mac = new Uint8Array(await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(ts + '.' + body)));
  const signature = [...mac].map((n) => n.toString(16).padStart(2, '0')).join('');
  return send(app, '/v1/webhooks/stripe', {
    method: 'POST', body,
    headers: { 'stripe-signature': 't=' + ts + ',v1=' + signature },
  });
}

test('real SQLite schema atomically prevents overspending 20 paid Stripe credits', async () => {
  const db = new SqliteD1();
  const app = createApp(configuredEnv(db), {
    fetchImpl: async () => Response.json({
      id: 'cs_test_sqlite',
      url: 'https://checkout.stripe.com/c/pay/cs_test_sqlite',
    }),
  });
  const checkout = await send(app, '/v1/checkout', { method: 'POST' });
  assert.equal(checkout.status, 201);
  const { access_token: token } = await checkout.json();
  const hash = db.db.prepare('SELECT token_hash FROM stripe_credit_purchases').get().token_hash;
  const evt = {
    type: 'checkout.session.completed',
    data: { object: {
      id: 'cs_test_sqlite', mode: 'payment', payment_status: 'paid',
      metadata: { sku: 'syntyr-agent-theme-20' },
      payment_intent: 'pi_sqlite', client_reference_id: hash,
    } },
  };
  assert.equal((await signedWebhook(app, evt)).status, 200);
  const headers = { authorization: 'Bearer ' + token };
  const requests = Array.from({ length: 30 }, () => send(app, '/v1/agent/theme', { headers }));
  const responses = await Promise.all(requests);
  assert.equal(responses.filter((r) => r.status === 200).length, 20);
  assert.equal(responses.filter((r) => r.status === 403).length, 10);
  assert.equal(db.db.prepare('SELECT credits FROM stripe_credit_purchases').get().credits, 0);

  assert.equal((await signedWebhook(app, evt)).status, 200);
  assert.equal(db.db.prepare('SELECT credits FROM stripe_credit_purchases').get().credits, 0);
  db.db.close();
});

test('SQLite revocation tombstone survives refund preceding checkout settlement', async () => {
  const db = new SqliteD1();
  const app = createApp(configuredEnv(db), {
    fetchImpl: async () => Response.json({
      id: 'cs_test_refund',
      url: 'https://checkout.stripe.com/c/pay/cs_test_refund',
    }),
  });
  await send(app, '/v1/checkout', { method: 'POST' });
  const hash = db.db.prepare('SELECT token_hash FROM stripe_credit_purchases').get().token_hash;

  assert.equal((await signedWebhook(app, {
    type: 'charge.refunded', data: { object: { payment_intent: 'pi_refund' } },
  })).status, 200);
  assert.equal((await signedWebhook(app, {
    type: 'checkout.session.completed', data: { object: {
      id: 'cs_test_refund', mode: 'payment', payment_status: 'paid',
      metadata: { sku: 'syntyr-agent-theme-20' }, payment_intent: 'pi_refund',
      client_reference_id: hash,
    } },
  })).status, 200);
  assert.equal(db.db.prepare('SELECT credits FROM stripe_credit_purchases').get().credits, 0);
  db.db.close();
});
