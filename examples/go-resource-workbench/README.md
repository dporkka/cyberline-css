# Syntyr Go Resource Workbench

A runnable **server-rendered** enterprise resource workspace demonstrating how to compose existing Syntyr CSS classes without a frontend runtime. The records are fictional and held in a fixed in-memory slice.

## Run

Requires Go 1.24 or newer. From this directory:

```sh
go test ./...
go run . -addr 127.0.0.1:8767
```

Open http://127.0.0.1:8767/resources. The demo serves the repository's already-built CSS from `../../dist`. Run from `examples/go-resource-workbench/`; if your CSS is elsewhere, pass `-dist /absolute/path/to/dist`.

## Optional browser verification

A maintainer-only Playwright smoke test covers Chromium and Firefox at 320px, 390px and desktop widths, plus 400%-equivalent text size, forced-colors, native no-JS forms, inspector links and bulk previews. Playwright is **not** a runtime dependency of Syntyr CSS or of this Go example.

From `examples/go-resource-workbench/`, with Playwright installed independently:

```sh
node browser-smoke.cjs
```

The test compiles and runs the Go app on localhost, allocates a temporary binary, and cleans it up. Browser executable overrides `SYNTYR_TEST_CHROMIUM_EXECUTABLE` and `SYNTYR_TEST_FIREFOX_EXECUTABLE` are supported for non-standard installs. Text reflow and keyboard/semantic checks are not a substitute for human screen-reader review.

## Working behaviors

- Native GET search over resource name, ID, owner and region; status filtering; explicit name or updated-date sort.
- Three-row, server-owned pagination with bounded page numbers, preserved sort/theme/column options, current-page announcement and native previous/next links. Changing filters starts at page one.
- Column visibility controls (Owner and Region) stored in URL query parameters; resource ID, status and update date remain visible.
- Studio, Grid and Noir tokens selected via a GET control, preserved in inspector and selection-preview links.
- Per-resource detail links that retain current search, column and theme preferences; an inspector never shows a record excluded by the current filter.
- Checked-row bulk **preview** via a native GET form; the server validates IDs, removes duplicates and intersects choices with **the visible filtered page**. It cannot submit hidden rows from another page.
- Explicit "Preview all matching" link spanning **all filtered pages**, not just the current page. It does **not** infer select-all from an empty checkbox form.
- Empty-results and empty-selection screens. Input validation, output escaping, method checks and no-store response headers.

This is a self-contained example, not a new Syntyr CSS component or a full backend. No authentication, tenant isolation, CRUD writes, audit persistence, pagination, virtualization, export or database connections are included. **Do not deploy it as a live multi-tenant business application.** Integrating real data requires server-side tenant/RBAC checks, stable query scope, per-record authorization, CSRF protection for mutations, transaction semantics and audit logs.

Pagination limits each rendered table to three records (to exercise the example); this is not a recommendation for production page size. A request for an invalid or out-of-range page fails with HTTP 400 instead of silently changing selection scope. The `/preview` endpoint only describes a proposed selection. It never changes records. Large paginated selections need a server-owned query snapshot or select-all-except contract; unchecked IDs on unloaded pages cannot be inferred from checkboxes.

## Composition map

| Concern | Syntyr presentation |
| --- | --- |
| Workspace and responsive inspector | `syn-workspace`, `syn-detail-layout`, `syn-detail-main`, `syn-detail-aside` |
| Search/filter/sort/theme controls | `syn-filter-bar`, `syn-filter-field`, `syn-filter-actions` |
| Results and bulk previews | `syn-table`, `syn-table-wrap`, `syn-bulk-actions`, `syn-result-state` |
| Inspector metadata | `syn-record-fields`, `syn-surface--raised` |
| Themes and density | `data-syn-theme`, `data-syn-density` |

The Go application owns every query, state and link. Syntyr CSS only presents them. The same HTML can be adapted to other SSR frameworks.
