# Optional Rust SaaS Foundation / Askama / HTMX integration

An opt-in Syntyr profile is implemented on the
`feat/optional-syntyr-skin` integration branch of
`dporkka/rust-saas-foundation`. It uses a separate Askama page template,
shares the original `catalog.html` fragment, and does not require npm,
external assets, or any additional runtime JavaScript.

The source adapter is `integrations/rust-saas-foundation/catalog.css`.
It scopes the existing `.wrap`, `.items` and `.item` classes beneath
`.syn-rust-foundation` so the default page is unaffected. Load a pinned
Syntyr core stylesheet first, then the adapter. The optional page sets
`class="syn-root syn-rust-foundation"` and `data-syn-theme="studio"`.

The Rust integration vendors the **published alpha.4 core CSS** and serves
versioned assets from the application binary. It exposes `APP_UI_SKIN=syntyr`
at startup; unknown values are rejected. The backend's identity, tenants,
permissions, PostgreSQL queries and HTMX fragments are not touched.

This demonstrates a public catalog. It does not prove an authenticated admin
flow or certify accessibility. Browser, keyboard, contrast and zoom tests on
real application pages are required before production claims.

## SaaS workspace reference: server-rendered application UI

The [script-free SaaS workspace preview](../examples/saas-workspace.html) combines organization context, member roles and invitations, subscription usage, invoices, API-key presentation, webhooks, audit events, and accessible success/error/empty/loading states. **Every name, amount, event and status is fictional**; the static page does not persist data, change tenants, send invitations, create keys or process payments. Its form controls for writes are disabled intentionally. The example classes and recipes are part of the **unreleased alpha.5 source candidate**, not the already published alpha.4 CSS.

For a concrete server-rendered integration starting point, copy [`integrations/rust-saas-foundation/workspace.askama.html`](https://github.com/dporkka/syntyr-css/blob/main/integrations/rust-saas-foundation/workspace.askama.html) into Rust SaaS Foundation's `templates/workspace.html`, and load locally self-hosted, pinned `syntyr.core.css` and `syntyr.recipes.css` at `/assets/`. The template is **illustrative**, not a connected Rust route or an authenticated end-to-end feature. It uses ordinary Askama-escaped interpolation (`{{ ... }}`), a member loop, conditional notices, native HTML forms, server-selected organization options, and a `<progress>` element. Syntyr itself contains no request or routing logic.

Bind the Askama view model with: `workspace_name`, `accessible_workspaces` (each with `id`, `name`), `members` (each with `name`, `role`, `status`), `plan_name`, `requests_used`, `requests_limit`, `csrf_token`, `can_invite`, `has_error`, `error_message`, `has_notice`, and `notice_message`. Use an `askama::Template` derive with `#[template(path = "workspace.html")]`; render the returned HTML from a route that verifies a session and resolves the active tenant. The template does not include credential secrets, pricing calculations or client-driven permission checks.

### Required Rust SaaS Foundation backend contracts

1. **GET `/workspace`:** Authenticate, derive the current organization from the session, recheck tenant membership, load authorized members and usage, then render the template. Return a real 403/404 when permission checks fail; don't rely on CSS to hide data.
2. **POST `/workspace/switch`:** Validate a session-bound CSRF token, recheck that the submitted `workspace_id` belongs to an accessible organization, set the active tenant server-side, and redirect using POST/redirect/GET. Never accept tenant identity from a hidden input alone.
3. **POST `/workspace/invitations`:** Validate CSRF, authorize the invitation capability, validate the email/allowed role, rate-limit invitations, persist an audit event, and redirect with a server-rendered result. The demo intentionally does not include elevated roles in its public invitation selector.
4. **Subscriptions, API keys and webhooks:** Fetch and authorize server-side. Never return raw API-key material to templates after initial one-time issuance; verify billing provider webhooks using signatures before committing changes. The static UI makes no payment claim.
5. **Accessible state rendering:** Attach `role="alert"` to errors only when present, use `role="status"` for confirmation messages, keep labels and table captions, and use real server-provided progress values (with `requests_limit > 0`). Test keyboard access, 320px reflow, forced colors and zoom on the integrated page.

The copyable template is a **presentation adapter**, not authentication, authorization, CSRF infrastructure, or a production-tested route. It does not alter Rust SaaS Foundation's existing tenant/RLS boundary, and it does not make Syntyr dependent on Rust, Askama or HTMX.
