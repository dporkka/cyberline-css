# Syntyr agent commerce — isolated, disabled-by-default pilot

**Privately deployed to Cloudflare staging, but not publicly routed or approved for real-money use.** Syntyr's current CSS, documentation,
themes, and examples remain MIT-licensed and free. There is no premium asset
available for purchase. The sole demonstration product is a *service*: generation
of original, machine-readable accessible theme token suggestions.

This directory is a **separate Cloudflare Worker**. Nothing here is part of
`@syntyr/css`, its runtime dependencies, the static Cloudflare Pages output,
or the immutable CSS CDN. The static site never receives Stripe secrets,
wallet keys, or paid resource source.

## Local tests

```sh
cd commerce
npm ci
npm test
```

The Node test suite verifies an actual x402 v2 payment challenge and uses
in-memory fakes for Stripe's API and D1 boundaries. It does **not** claim
to have settled any testnet payments or made live Stripe transactions.

## API

| Endpoint | Purpose | Auth |
| --- | --- | --- |
| `GET /v1/catalog` | Versioned public JSON catalog with input schema and disabled/enabled rails | None |
| `GET /.well-known/agent-commerce.json` | Agent-readable discovery metadata | None |
| `GET /v1/agent/theme?accent=%2379e3ed&surface=%23111827` | JSON tokens with measured text contrast | x402 testnet payment **or** one prepaid Stripe credit |
| `POST /v1/checkout` | Stripe **test-mode** 20-credit checkout, returns checkout URL and opaque buyer token | Disabled unless configured |
| `GET /v1/credits` | Buyer token balance | `Authorization: Bearer <token>` |
| `POST /v1/webhooks/stripe` | Signed Stripe test webhooks for completion/refunds/disputes | Valid Stripe-Signature |

The token returned by `POST /v1/checkout` must be stored securely by the
buyer **before** visiting the Checkout URL. There is no customer-account
recovery, dashboard, team license, or production identity flow yet. The API
stores only SHA-256 hashes of buyer tokens, not the tokens themselves.

## Isolated staging deployment

1. The dedicated Cloudflare D1 database `syntyr-agent-commerce-staging`
   already exists, and its credit and revocation schema has been applied and
   verified. **Do not create a replacement database or reapply migrations
   without checking the current schema.** No production customer data is used.
2. The separate Worker `syntyr-agent-commerce-staging` is already
   deployed, with version `1820f02a-c60d-4559-a37b-0ae463159362` active
   at 100%. **Both `workers.dev` and preview URLs are disabled**, as are
   both payment rails. This version contains the tested Syntyr implementation,
   not an HTTP placeholder. The remote version has D1 and safe plain-text
   flags, but not the Cloudflare rate-limit bindings; do not enable payment
   flags on it. For the next release, use `wrangler.toml.example`, whose
   rate-limit bindings are complete, and deploy only after exact-head CI and
   configuration review.
3. Supply an explicitly designated **Base Sepolia** receiving address with
   `X402_PAY_TO`; set `X402_TESTNET_ENABLED=true` for a supervised x402
   sandbox test. Network is hardcoded to `eip155:84532`, and the fee is
   `$0.25` *testnet-denominated*, not a live-dollar transaction.
4. Create a **Stripe test-mode** one-time price for **20 calls**, then set
   the following **staging-only** values: `STRIPE_PRICE_ID`,
   `STRIPE_SUCCESS_URL`, `STRIPE_CANCEL_URL`. Add
   `STRIPE_SECRET_KEY` (prefer a scoped `rk_test_` restricted key) and
   `STRIPE_WEBHOOK_SECRET` through Wrangler
   secrets; both are mandatory. Add `STRIPE_PILOT_ENABLED=true` only after
   the webhook endpoint is registered in Stripe and migration checks pass.
5. Configure the webhook endpoint for `checkout.session.completed`,
   `checkout.session.async_payment_succeeded`, `charge.refunded`, and
   `charge.dispute.created`. Stripe signatures are checked with WebCrypto
   HMAC-SHA256, a 5-minute tolerance, and the unmodified raw request body.
6. Keep the `IP_RATE_LIMITER` and `CHECKOUT_RATE_LIMITER` Cloudflare
   rate-limit bindings configured. The Worker responds with HTTP 503 on
   protected endpoints when the binding or Cloudflare client IP is
   missing. The bindings limit requests to approximately 60/min/IP for
   paid resource/balance queries and 5/min/IP for new checkout sessions.
   These counters are **approximate per Cloudflare location** and cannot
   guarantee strict global limits. Add Cloudflare WAF rate-limit rules,
   bot protections and alerting before wider exposure; never trust
   client-supplied `X-Forwarded-For`.
7. Exercise the paid route with a funded *testnet* agent wallet and a Stripe
   test card. Confirm: 402 challenge, payment verification and settlement,
   Stripe webhook credit, idempotent redelivery, refund/dispute revocation,
   rate limiting, and operator reconciliation. Reconcile receipts against
   Stripe's dashboard and the testnet explorer before broader access.

## Safety boundaries and next release gates

- **No mainnet:** x402 requires `X402_TESTNET_ENABLED=true` and uses
  Base Sepolia only. Stripe accepts `sk_test_...` only.
- **No price injection:** checkout uses a trusted server-side Stripe Price ID;
  the request cannot choose arbitrary prices, redirect URLs, or credit counts.
- **Fail closed:** missing D1, webhook secret, wallet address, or flags disables
  the corresponding paid route. No token-bearing or payment-bearing requests
  fall back to free access.
- **Webhook replay:** only a paid, expected Stripe session grants credits.
  D1 conditionally credits once; refunds/disputes leave tombstones so
  reordered event delivery cannot recredit a purchase.
- **Privacy-first logs:** optional structured request logs contain only
  a fresh request ID, fixed route label, HTTP method, and status. Do not
  log the path query, buyer tokens, blockchain payment payloads or keys.
  Logs and traces are explicitly enabled in the staging template.
- **Abuse resistance:** protect Stripe checkout creation and paid API requests using Cloudflare rate-limit bindings, with 429 on excess and fail-closed 503 on missing bindings. Counts are approximate, not a substitute for WAF or financial reconciliation.
- **No API security by CSS:** the gate lives server-side. The public static
  build allowlists only documentation, not any commerce executable or secrets.
- **Before production:** independent security review, WAF/rate limits and
  bot-abuse prevention, Stripe account and customer recovery, financial
  reconciliation, taxes, commercial licensing review, privacy policy,
  monitoring, entitlement repair tooling, staging tests with real payment
  providers, and an explicit live-payment launch decision.

The optional x402 and Stripe methods share a single protected resource
boundary, but payment accounting differs: Stripe grants durable prepaid
credits; x402 authorizes a single request after SDK verification/settlement.
The pilot deliberately does **not** mint permanent licenses from testnet
payments. Avoid presenting this as a finished subscription product.

See `../docs/agent-commerce.md` for public-facing integration notes.

## Safe smoke and rollout sequence

From `commerce/`, with the Worker running locally or available at an
explicitly isolated staging origin:

```sh
npm run smoke -- http://127.0.0.1:8787 disabled
npm run smoke -- https://YOUR-ISOLATED-STAGING-ORIGIN disabled
```

Once an authorized operator has installed a Base Sepolia wallet, set
`X402_TESTNET_ENABLED=true` and verify the unpaid v2 challenge without
transferring funds:

```sh
npm run smoke -- https://YOUR-ISOLATED-STAGING-ORIGIN testnet
```

This smoke performs only safe public requests, malformed-color requests,
and a Stripe-disabled checkout attempt. On November 15, 2026, the
`disabled` mode ran successfully against the hosted Worker: health 200,
catalog 200, invalid input 400, gated theme 503 and checkout 503.
The public `workers.dev` route was disabled immediately afterward and
verified disabled. It **never signs, submits or
settles** a testnet payment. A real funded test-wallet settlement and
Stripe sandbox webhook round-trip still require separate E2E testing.

Before any future Worker redeployment, use a reviewed, restricted Cloudflare API token
in the maintainer's local secret store or CI secret vault and configure
`wrangler.toml` as an ignored local file. The template is deliberately
inert: no public Worker URL, paid route or wallet is enabled by default.
The existing staging deployment was created using the authorized Cloudflare
connection; the Wrangler CLI on Gertrude remains unauthenticated. Do not
deploy by copying unrelated application tokens or production credentials
from other repos.
