# Syntyr Go SaaS example — working HTML-first application

A **runnable, read-only, original SaaS dashboard** using the Go standard library and **published Syntyr CSS v0.3.0-alpha.4**. Unlike the static gallery screens, these routes perform actual server-side rendering, search/filtering and CSV export. No browser JavaScript, no third-party Go dependencies, no build pipeline, no remote fonts or network assets.

## Run it

Requires Go 1.22 or newer:

```sh
cd examples/go-stdlib-saas
go run .
# Open http://127.0.0.1:8080
```

The service binds to **127.0.0.1** only. To run its regression tests:

```sh
cd examples/go-stdlib-saas
go test ./...
go vet ./...
```

Optional real-browser smoke testing requires the example running on localhost in
another terminal. The test-only Python dependency does **not** enter the Go
binary or Syntyr CSS runtime:

```sh
uv run --no-project --with 'playwright==1.65.2' python3 browser_smoke.py --browsers chromium firefox
# Include webkit when the matching browser and its native libraries are available.
```

The smoke test exercises native GET search/status filtering, theme continuity,
customer navigation, filtered CSV responses, script-free markup, and 320px
root-page reflow including a 2× root-font stress case. It is **not** evidence
of actual browser zoom or manual screen-reader accessibility approval.
Chrome/Firefox/WebKit versions and platform dependencies should be recorded
when reviewing a release.

## Try these flows

1. Open **Overview** to see metrics calculated from the in-memory dataset (active accounts alone contribute to illustrative MRR).
2. Choose **Customers**, search by name, ID or plan, and filter by subscription status. The browser submits a normal GET request; the server returns only matching rows and a real empty state when appropriate.
3. Follow a customer link to see its detail page, then navigate back. The selected Studio, Grid or Noir theme travels through links and filter forms in query parameters.
4. Select **Export matching CSV** to download precisely the filtered rows. The exporter uses the Go CSV writer and mitigates common spreadsheet-formula injection risks.

The data is immutable and intentionally synthetic. Contact addresses use `example.invalid`. There are **no write operations, backend authentication, actual billing, production observability, persistence or payment processing**. Do not expose this example as a real client portal. In a production app, integrate session authentication, authorization, storage, CSRF protection for mutations, request limits, error reporting and appropriate cache policies.

## Files

- `main.go` — read-only handlers, filters, CSV export, template rendering, embedded CSS, baseline headers.
- `templates/*.html` — three ordinary `html/template` views and a shared responsive Syntyr shell.
- `assets/syntyr.core.css` — **unaltered published v0.3.0-alpha.4 release CSS**, self-hosted within the binary.
- `main_test.go` — HTTP-level tests for UI, filtering, safe HTML, filter errors, theme continuity, route behavior and CSV export.
- `browser_smoke.py` — opt-in Playwright browser journey for navigation, CSV, filters, themes and narrow text reflow.

Bundled CSS SHA-256: `8d6458bf1f2ae25098a733e7fb88a84260e54b8b285bf05ff07432cccfbdaa6e`.

The bundled Syntyr stylesheet is MIT-licensed; see [the repository's license](../../LICENSE). The copies intentionally use the **published alpha.4 CSS**, not the unreleased alpha.5 source styles. If updating the stylesheet, regenerate it from an immutable release tag, check the checksum, review compatibility and rerun the tests.

## Design boundaries

The accessible navigation, native search form, status labels, responsive table and server-generated theme links show how Syntyr integrates with plain HTTP. This deliberately does **not** invent CSS-only business behavior: the host application implements filtering and CSV export in Go, while Syntyr provides presentation. This example is free, MIT-licensed reference code, not part of the private commercial Console Kit.

This directory is a **local runnable example**. The static Syntyr Cloudflare documentation site does not execute Go, and users should not expect the HTTP routes to function there.
