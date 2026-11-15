import { Hono } from 'hono';
import { paymentMiddleware, x402ResourceServer } from '@x402/hono';
import { ExactEvmScheme } from '@x402/evm/exact/server';
import { HTTPFacilitatorClient } from '@x402/core/server';
import { generateTheme } from './theme.js';
import { checkRateLimit } from './abuse.js';
import {
  stripeReady, bearerToken, beginCheckout, verifyWebhook,
  applyStripeEvent, findEntitlement, redeemCredit,
} from './stripe.js';

const TESTNET = 'eip155:84532';
const PRICE = '$0.25';

function x402Ready(env) {
  if (env.X402_TESTNET_ENABLED !== 'true' || !/^0x[0-9a-fA-F]{40}$/.test(env.X402_PAY_TO || '')) return false;
  if (!env.X402_FACILITATOR_URL) return true;
  try {
    const url = new URL(env.X402_FACILITATOR_URL);
    return url.protocol === 'https:' && !url.username && !url.password;
  } catch {
    return false;
  }
}

function x402Gate(env) {
  const facilitator = new HTTPFacilitatorClient({
    url: env.X402_FACILITATOR_URL || 'https://x402.org/facilitator',
    timeoutMs: 15000,
  });
  const resourceServer = new x402ResourceServer(facilitator)
    .register(TESTNET, new ExactEvmScheme());
  return paymentMiddleware({
    'GET /v1/agent/theme': {
      accepts: [{
        scheme: 'exact',
        price: PRICE,
        network: TESTNET,
        payTo: env.X402_PAY_TO,
      }],
      description: 'Generate accessible Syntyr theme tokens from two hex colors (testnet pilot)',
      mimeType: 'application/json',
    },
  }, resourceServer);
}

async function readBoundedBody(request, maxBytes) {
  const declared = request.headers.get('content-length');
  if (declared && Number(declared) > maxBytes) return null;
  if (!request.body) return '';
  const reader = request.body.getReader();
  const chunks = [];
  let total = 0;
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    total += value.byteLength;
    if (total > maxBytes) {
      await reader.cancel();
      return null;
    }
    chunks.push(value);
  }
  const body = new Uint8Array(total);
  let offset = 0;
  for (const chunk of chunks) {
    body.set(chunk, offset);
    offset += chunk.byteLength;
  }
  return new TextDecoder('utf-8', { fatal: true }).decode(body);
}

function noStore(c, body, status = 200) {
  c.header('Cache-Control', 'no-store');
  c.header('X-Content-Type-Options', 'nosniff');
  return c.json(body, status);
}

export function createApp(env = {}, deps = {}) {
  const app = new Hono();
  const loggedRoutes = new Set([
    '/v1/health', '/v1/catalog', '/.well-known/agent-commerce.json',
    '/v1/agent/theme', '/v1/checkout', '/v1/credits',
    '/v1/webhooks/stripe',
  ]);
  app.use('*', async (c, next) => {
    const requestId = crypto.randomUUID();
    try {
      await next();
    } finally {
      c.header('X-Request-ID', requestId);
      if (env.LOG_REQUESTS === 'true') {
        // Fixed route labels only. Never log query strings, bodies, payment
        // headers, client IPs, wallet payloads, buyer bearer tokens or keys.
        const event = {
          service: 'syntyr-agent-commerce',
          request_id: requestId,
          route: loggedRoutes.has(c.req.path) ? c.req.path : 'unknown',
          method: c.req.method,
          status: c.res.status,
        };
        try {
          (deps.logger || console).info(JSON.stringify(event));
        } catch {
          // A logging outage must never break settlement or fulfillment.
        }
      }
    }
  });

  app.onError(() => noStoreFallback());
  function noStoreFallback() {
    return new Response(JSON.stringify({ error: 'internal_error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' },
    });
  }

  app.get('/v1/health', (c) => noStore(c, { status: 'ok', service: 'syntyr-agent-commerce', live_payments: false }));

  app.get('/v1/catalog', (c) => noStore(c, {
    schema_version: 1,
    service: 'syntyr-agent-commerce',
    live_payments: false,
    products: [
      {
        id: 'syntyr-css',
        name: 'Syntyr MIT CSS',
        license: 'MIT',
        price_usd: '0',
        url: 'https://github.com/dporkka/syntyr-css',
      },
      {
        id: 'agent-theme-tokens',
        name: 'Generated accessible theme tokens (pilot)',
        status: 'testnet_only',
        input_schema: {
          type: 'object',
          properties: {
            accent: { type: 'string', pattern: '^#[0-9a-fA-F]{6}$', default: '#79e3ed' },
            surface: { type: 'string', pattern: '^#[0-9a-fA-F]{6}$', default: '#111827' },
          },
          additionalProperties: false,
        },
        output: 'application/json',
        endpoint: '/v1/agent/theme',
        x402: { enabled: x402Ready(env), network: TESTNET, amount_usd: '0.25', mode: 'testnet' },
        stripe: { enabled: stripeReady(env), checkout_endpoint: '/v1/checkout', credits: 20, mode: 'test' },
      },
    ],
  }));

  app.get('/.well-known/agent-commerce.json', (c) => noStore(c, {
    schema_version: 1,
    name: 'Syntyr agent commerce pilot',
    catalog: '/v1/catalog',
    resources: [{ method: 'GET', path: '/v1/agent/theme', payment_options: ['x402-v2-base-sepolia', 'stripe-test-credits'] }],
    notes: 'Preview only. Live charging and premium kit sales are not enabled.',
  }));

  app.get('/v1/agent/theme', async (c, next) => {
    let theme;
    try {
      theme = generateTheme({
        accent: c.req.query('accent'),
        surface: c.req.query('surface'),
      });
    } catch {
      return noStore(c, { error: 'invalid_hex_color', message: 'accent and surface must be six-digit #RRGGBB values' }, 400);
    }
    c.set('generatedTheme', theme);
    const limited = await checkRateLimit(c, env, 'agent-theme');
    if (limited) return limited;
    const token = bearerToken(c.req.raw);
    if (token !== null) {
      if (!stripeReady(env)) return noStore(c, { error: 'stripe_credits_unavailable' }, 503);
      if (!token) return noStore(c, { error: 'invalid_token' }, 401);
      const purchased = await redeemCredit(env.ENTITLEMENTS_DB, token);
      if (!purchased) return noStore(c, { error: 'no_valid_stripe_credits' }, 403);
      c.set('paymentMethod', 'stripe');
      return next();
    }
    if (!x402Ready(env)) return noStore(c, { error: 'x402_unavailable' }, 503);
    c.set('paymentMethod', 'x402');
    const middleware = deps.makeX402Gate ? deps.makeX402Gate(env) : x402Gate(env);
    return middleware(c, next);
  }, (c) => noStore(c, { ...c.get('generatedTheme'), payment_method: c.get('paymentMethod') }));

  app.post('/v1/checkout', async (c) => {
    if (!stripeReady(env)) return noStore(c, { error: 'stripe_checkout_unavailable' }, 503);
    const limited = await checkRateLimit(c, env, 'checkout');
    if (limited) return limited;
    try {
      const checkout = await beginCheckout(env, deps.fetchImpl || fetch);
      return noStore(c, checkout, 201);
    } catch {
      return noStore(c, { error: 'checkout_unavailable' }, 502);
    }
  });

  app.get('/v1/credits', async (c) => {
    if (!stripeReady(env)) return noStore(c, { error: 'stripe_credits_unavailable' }, 503);
    const limited = await checkRateLimit(c, env, 'credit-status');
    if (limited) return limited;
    const token = bearerToken(c.req.raw);
    if (!token) return noStore(c, { error: 'invalid_token' }, 401);
    const entitlement = await findEntitlement(env.ENTITLEMENTS_DB, token);
    if (!entitlement) return noStore(c, { error: 'invalid_token' }, 401);
    return noStore(c, { status: entitlement.status, credits_remaining: entitlement.credits });
  });

  app.post('/v1/webhooks/stripe', async (c) => {
    if (!stripeReady(env)) return noStore(c, { error: 'stripe_webhook_unavailable' }, 503);
    let raw;
    try {
      raw = await readBoundedBody(c.req.raw, 1024 * 1024);
    } catch {
      return noStore(c, { error: 'invalid_encoding' }, 400);
    }
    if (raw === null) return noStore(c, { error: 'payload_too_large' }, 413);
    if (!await verifyWebhook(raw, c.req.header('stripe-signature'), env.STRIPE_WEBHOOK_SECRET)) {
      return noStore(c, { error: 'invalid_signature' }, 400);
    }
    let event;
    try {
      event = JSON.parse(raw);
    } catch {
      return noStore(c, { error: 'invalid_payload' }, 400);
    }
    const result = await applyStripeEvent(env.ENTITLEMENTS_DB, event);
    return noStore(c, { received: true, result });
  });

  return app;
}
