const enc = new TextEncoder();
export const STRIPE_SKU = 'syntyr-agent-theme-20';
export const STRIPE_CREDITS = 20;

export function stripeReady(env) {
  return env.STRIPE_PILOT_ENABLED === 'true'
    && /^(sk|rk)_test_/.test(env.STRIPE_SECRET_KEY || '')
    && env.STRIPE_WEBHOOK_SECRET?.startsWith('whsec_')
    && /^price_[a-zA-Z0-9]+$/.test(env.STRIPE_PRICE_ID || '')
    && isHttpsUrl(env.STRIPE_SUCCESS_URL)
    && isHttpsUrl(env.STRIPE_CANCEL_URL)
    && Boolean(env.ENTITLEMENTS_DB);
}

function isHttpsUrl(raw) {
  try {
    const url = new URL(raw);
    return url.protocol === 'https:' && !url.username && !url.password;
  } catch {
    return false;
  }
}

export function newAccessToken() {
  return crypto.randomUUID() + '.' + crypto.randomUUID();
}

export async function tokenHash(token) {
  const digest = await crypto.subtle.digest('SHA-256', enc.encode(token));
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

export function bearerToken(request) {
  const raw = request.headers.get('authorization');
  if (raw === null) return null;
  const match = /^Bearer ([0-9a-f-]{36}\.[0-9a-f-]{36})$/i.exec(raw);
  return match ? match[1] : '';
}

export async function beginCheckout(env, fetchImpl = fetch) {
  const accessToken = newAccessToken();
  const hash = await tokenHash(accessToken);
  const form = new URLSearchParams({
    mode: 'payment',
    'line_items[0][price]': env.STRIPE_PRICE_ID,
    'line_items[0][quantity]': '1',
    success_url: env.STRIPE_SUCCESS_URL,
    cancel_url: env.STRIPE_CANCEL_URL,
    client_reference_id: hash,
    'metadata[sku]': STRIPE_SKU,
    // Stripe 2026-09-30.endive supports the custom integration identifier.
    // The suffix is a non-secret, randomized usage-analysis label.
    integration_identifier: 'syntyr-agent-' + Array.from(crypto.getRandomValues(new Uint8Array(8)),
      (n) => String.fromCharCode(97 + n % 26)).join(''),
  });
  const response = await fetchImpl('https://api.stripe.com/v1/checkout/sessions', {
    method: 'POST',
    headers: {
      authorization: 'Bearer ' + env.STRIPE_SECRET_KEY,
      'content-type': 'application/x-www-form-urlencoded',
      'Stripe-Version': '2026-09-30.endive',
      'idempotency-key': crypto.randomUUID(),
    },
    body: form.toString(),
  });
  if (!response.ok) throw new Error('Stripe checkout request failed');
  const session = await response.json();
  if (typeof session.id !== 'string' || !session.id.startsWith('cs_test_')
      || !isHttpsUrl(session.url) || new URL(session.url).hostname !== 'checkout.stripe.com') {
    throw new Error('Stripe returned an invalid test checkout session');
  }
  await env.ENTITLEMENTS_DB.prepare(
    "INSERT INTO stripe_credit_purchases (session_id, token_hash, status, credits, created_at) VALUES (?, ?, 'pending', 0, datetime('now'))"
  ).bind(session.id, hash).run();
  return { checkout_url: session.url, access_token: accessToken, credits_after_payment: STRIPE_CREDITS };
}

export async function verifyWebhook(rawBody, stripeSignature, secret, now = Date.now()) {
  if (typeof stripeSignature !== 'string' || rawBody.length > 1024 * 1024) return false;
  const entries = stripeSignature.split(',').map((part) => part.trim());
  const timestampPart = entries.find((part) => /^t=\d+$/.test(part));
  const signatures = entries.filter((part) => /^v1=[0-9a-f]{64}$/.test(part));
  if (!timestampPart || signatures.length === 0) return false;
  const timestamp = Number(timestampPart.slice(2));
  if (!Number.isSafeInteger(timestamp) || Math.abs(Math.floor(now / 1000) - timestamp) > 300) return false;
  const key = await crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['verify']);
  for (const entry of signatures) {
    const expected = new Uint8Array(entry.slice(3).match(/.{2}/g).map((pair) => parseInt(pair, 16)));
    if (await crypto.subtle.verify('HMAC', key, expected, enc.encode(timestamp + '.' + rawBody))) return true;
  }
  return false;
}

export async function applyStripeEvent(db, event) {
  if (event?.type === 'checkout.session.completed' || event?.type === 'checkout.session.async_payment_succeeded') {
    const session = event.data?.object;
    if (session?.mode !== 'payment' || session?.payment_status !== 'paid'
        || typeof session?.payment_intent !== 'string'
        || session?.metadata?.sku !== STRIPE_SKU
        || !/^[0-9a-f]{64}$/.test(session?.client_reference_id || '')
        || typeof session?.id !== 'string') return 'ignored';
    const result = await db.prepare(
      "UPDATE stripe_credit_purchases SET status = 'paid', credits = ?, payment_intent_id = ? WHERE session_id = ? AND token_hash = ? AND status = 'pending' AND NOT EXISTS (SELECT 1 FROM stripe_payment_revocations WHERE payment_intent_id = ?)"
    ).bind(STRIPE_CREDITS, session.payment_intent, session.id, session.client_reference_id, session.payment_intent).run();
    return result.meta?.changes === 1 ? 'credited' : 'already_processed_or_unknown';
  }
  if (event?.type === 'charge.refunded' || event?.type === 'charge.dispute.created') {
    const intent = event.data?.object?.payment_intent;
    if (typeof intent !== 'string') return 'ignored';
    // Record revocation before updating purchases. This prevents a delayed
    // checkout.session.completed webhook from restoring credits.
    await db.prepare(
      "INSERT OR IGNORE INTO stripe_payment_revocations (payment_intent_id, reason, observed_at) VALUES (?, ?, datetime('now'))"
    ).bind(intent, event.type).run();
    const result = await db.prepare(
      "UPDATE stripe_credit_purchases SET status = 'refunded', credits = 0 WHERE payment_intent_id = ? AND status = 'paid'"
    ).bind(intent).run();
    return result.meta?.changes === 1 ? 'revoked' : 'already_processed_or_unknown';
  }
  return 'ignored';
}

export async function findEntitlement(db, token) {
  const hash = await tokenHash(token);
  return db.prepare('SELECT status, credits FROM stripe_credit_purchases WHERE token_hash = ?')
    .bind(hash).first();
}

export async function redeemCredit(db, token) {
  const hash = await tokenHash(token);
  const result = await db.prepare(
    "UPDATE stripe_credit_purchases SET credits = credits - 1 WHERE token_hash = ? AND status = 'paid' AND credits > 0"
  ).bind(hash).run();
  return result.meta?.changes === 1;
}
