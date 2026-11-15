-- Apply before enabling Stripe pilot; only signed Stripe webhook events issue credits.
-- The x402 pilot is pay-per-use and never writes durable entitlements before settlement.
CREATE TABLE IF NOT EXISTS stripe_credit_purchases (
  session_id TEXT PRIMARY KEY,
  token_hash TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL CHECK (status IN ('pending', 'paid', 'refunded')),
  credits INTEGER NOT NULL DEFAULT 0 CHECK (credits >= 0 AND credits <= 20),
  payment_intent_id TEXT UNIQUE,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS stripe_credit_purchases_status_idx
  ON stripe_credit_purchases (status);

-- Tombstones make refund/dispute events safe even when webhooks arrive out of order.
CREATE TABLE IF NOT EXISTS stripe_payment_revocations (
  payment_intent_id TEXT PRIMARY KEY,
  reason TEXT NOT NULL,
  observed_at TEXT NOT NULL
);
