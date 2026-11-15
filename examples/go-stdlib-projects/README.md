# Syntyr + Go standard library: runnable project search

A working server-rendered search demo with the **same form, project data,
accessible table, and results state** as the Rails and Laravel recipes.
It uses `net/http`, `html/template`, and `embed`: **zero Go modules beyond
the standard library, zero JavaScript**. Go 1.22 or newer is required.

From Syntyr's repository root:

```sh
cd examples/go-stdlib-projects
mkdir -p public/css
cp ../../dist/syntyr.core.css public/css/syntyr.core.css
go test ./...
go run .
# Open http://127.0.0.1:8080/syntyr/projects?q=airport
```

The stylesheet is self-hosted at `/css/syntyr.core.css`; the checked-in
example does not duplicate Syntyr's compiled CSS. The local CSS copy is
ignored by Git. Use a pinned Syntyr release or repo revision in production,
not an unversioned CDN.

This is **GET-only** demonstration data, not a database, authentication,
authorization, or a write endpoint. The handler clamps query length, and
Go's `html/template` escapes the user's query and record values. Real apps
should use their normal auth, CSRF protections on mutations, and server
validation. The CSS is presentation only.

See [the cross-backend comparison](../../docs/backend-integration-comparison.md).
Run `go test ./...` for filtering, output escaping, and accessible HTML
smoke checks. Verify browser behavior and screen-reader flows separately.
