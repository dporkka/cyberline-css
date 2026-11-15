# Agent commerce: x402 and Stripe pilot

Syntyr's CSS framework, downloadable modules, themes, examples, and
documentation are **free and MIT-licensed**. There is no paid Syntyr kit for
sale. This page describes an **optional, unpublished payment integration
pilot** for a separate theme-token generation service; it does not add
payment requirements or JavaScript to Syntyr CSS.

## Why two rails?

Stripe Checkout is suitable for humans purchasing prepaid API credits.
x402 v2 enables HTTP-native pay-per-use requests from AI coding agents,
without requiring a Syntyr account. A common resource handler accepts
either a valid prepaid Stripe credit or a verified x402 testnet payment.

The pilot uses Base Sepolia (`eip155:84532`) and Stripe **test mode**.
The optional Worker now enforces Cloudflare rate limiting on paid endpoints,
and logs only fixed endpoint labels and random request IDs (never customer
tokens or wallet payloads). Those limits are approximate and per-location,
not a substitute for WAF protection or transaction reconciliation.
It has **not** been deployed or connected to a live receiving wallet.
The sample price is **$0.25 per generated token response** for the x402
testnet demo, or a separately configured Stripe test price for 20 calls.
Neither option is a current commercial offering.

## Discovery and integration

When the standalone Worker is configured and deployed to a staging hostname,
agents can inspect these self-describing HTTP endpoints:

| HTTP path | Purpose |
| --- | --- |
| `GET /v1/catalog` | Versioned machine-readable product and input schema |
| `GET /.well-known/agent-commerce.json` | Agent discovery document |
| `GET /v1/agent/theme` | Paid token-generation example (HTTP 402 without payment) |
| `POST /v1/checkout` | Stripe test Checkout URL and secret prepaid-token issuance |
| `GET /v1/credits` | Credit balance for a bearer token |

For the theme endpoint, agents can supply optional hex color query parameters:
`accent=%2379e3ed&surface=%23111827`. The JSON response contains CSS
custom-property suggestions plus measured contrast values. The generator is
a service; it does **not** sell access to existing MIT CSS files.

The official x402 v2 SDK constructs the `PAYMENT-REQUIRED` header and
validates/settles requests. Do not attempt to pay by placing an arbitrary
transaction hash or forged receipt in headers. Stripe buyer tokens are
secrets; they are not license IDs or public payment proofs.

## Licensing and release boundary

The MIT core never moves behind a paywall. A future separately authored
premium template could have its own reviewed commercial license, but such
a product has not been released. No premium asset is published by the
commerce prototype. The standalone Worker is excluded from the Cloudflare
Pages static asset allowlist.

**Implementation and security notes:** [commerce/README.md](https://github.com/dporkka/syntyr-css/blob/main/commerce/README.md).

Before enabling real funds, Syntyr needs identity and account recovery,
supplier and tax verification, operator reconciliation, transaction
monitoring, refund and chargeback policies, a licensed commercial product,
and tests with real settlement providers. A production payment rail is not
enabled simply by configuring a wallet address.

## Staging verification

The isolated D1 staging database and its credit/revocation tables have
been verified. The complete commerce Worker is **deployed privately** with
both payment rails disabled. Its public `workers.dev` and preview URLs are
disabled; this is not a public checkout service. A temporary hosted smoke
check confirmed health and catalog access, invalid-input rejection,
and fail-closed disabled payment endpoints. Local Cloudflare workerd testing
confirmed the x402 v2 challenge and rate-limit enforcement. The hosted
version does not yet include the mandatory paid-route rate-limit bindings,
so payment modes must remain disabled. Use `npm run smoke -- <staging-origin> disabled`
from the optional `commerce/` package to verify a disabled staging
deployment and `npm run smoke -- <staging-origin> testnet` to verify a
Base Sepolia unpaid challenge. Neither command transfers funds. See the
[commerce runbook](https://github.com/dporkka/syntyr-css/blob/main/commerce/README.md)
for remaining payment-provider E2E and operational release gates.
