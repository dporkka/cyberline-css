# One interface, three backends: Go, Rails and Laravel

Syntyr's design system is **ordinary CSS with semantic HTML**. The three
recipes below render the same *Projects* search form and accessible data table
using Go's standard library, Ruby on Rails ERB and Laravel Blade. The CSS
class API, theme, color tokens and HTML semantics do not change by language.

**Zero required Syntyr JavaScript.** Rails may optionally use the host app's
Turbo Frames; Laravel may optionally use Livewire; neither is a Syntyr
dependency. The plain GET search still works with browser JavaScript disabled.

## Compare the integrations

| | Go stdlib | Ruby on Rails | PHP / Laravel |
| --- | --- | --- | --- |
| Server renderer | `html/template` + `embed` | Rails ERB | Laravel Blade |
| Route | `GET /syntyr/projects` | `get "/syntyr/projects"` | `Route::get('/syntyr/projects', ...)` |
| Escaped query value | `{{.Query}}` | `<%= h(@query) %>` | `{{ $query }}` |
| State and authorization | Owned by Go app | Owned by Rails | Owned by Laravel |
| Optional progressive behavior | HTMX (host choice) | Turbo Frames (host choice) | Livewire (host choice) |
| Syntyr runtime dependencies | None | None | None |

The sample rows and search behavior are deliberately identical:
`Station expansion`, `Airport displays`, and `Downtown refresh`.
All three use the **Studio** theme with the same portable surface, form, and
table classes. A search for `airport` yields only `Airport displays`;
an unmatched search yields a readable empty state. Queries are trimmed
and limited, and each renderer escapes displayed user input by default.

## Common HTML and CSS contract

The examples intentionally keep this markup recognizable in every backend:

```html
<body class="syn-root syn-page" data-syn-theme="studio">
  <main class="syn-panel">
    <form class="syn-form" method="get" role="search">
      <label class="syn-label" for="syntyr-project-query">Search projects</label>
      <input class="syn-input" id="syntyr-project-query"
             name="q" type="search" maxlength="100">
      <button class="syn-button syn-button--primary" type="submit">Search</button>
    </form>
    <p class="syn-muted" role="status" aria-live="polite">1 project found</p>
    <div class="syn-table-wrap">
      <table class="syn-table">
        <caption>Projects matching your search</caption>
        <thead><tr><th scope="col">Project</th></tr></thead>
        <tbody><!-- Framework-escaped rows --></tbody>
      </table>
    </div>
  </main>
</body>
```

The markup above is an **illustrative common contract**, not a fourth
copyable application. Actual recipes provide the full three-column table,
server route, search and empty state. Rails uses `<section class="syn-root">`
inside its existing layout rather than duplicating the application's
`<body>` element; this is intentional and keeps Syntyr scoped.

**Self-host the same pinned CSS file** in each application: copy
`dist/syntyr.core.css` into the app's public assets and load it once.
For optional request-loading visuals, load `syntyr.server.css` *after*
core; it does not implement request state or lock controls. Never assume
that an unreleased Syntyr alpha.5 asset is already on npm.

## Run each reference

- **Go:** [Working `net/http` example](../examples/go-stdlib-projects/README.md)
  (`examples/go-stdlib-projects/README.md`). `cd examples/go-stdlib-projects`,
  copy the stylesheet under `public/css/`, then `go test ./...` and
  `go run .`. No nonstandard Go module required.
- **Rails:** [ERB controller, view, and optional Turbo](../examples/rails-hotwire/README.md)
  (`examples/rails-hotwire/README.md`). Copy into an existing Rails app;
  run the included `bin/rails test` integration tests there.
- **Laravel:** [Plain Blade and read-only route](../examples/laravel-blade/README.md)
  (`examples/laravel-blade/README.md`). Copy into an existing Laravel app;
  run the included `php artisan test` feature tests there.

All source examples are MIT licensed. No production authentication, data
storage, payments, or mutation is included. For actual workloads, apply
host-framework authorization and validation, native CSRF protection to
state-changing methods, and normal browser/security testing.

## Adoption and validation boundaries

**Do not confuse identical CSS contracts with identical runtime behavior.**
Each host framework still owns escaping, URL generation, form lifecycle,
focus management, and Turbo/Livewire updates. Go is compiled and tested in
Syntyr's repository; Rails and Laravel example test files must be executed
in actual applications with supported Ruby/PHP versions and framework
dependencies. Native keyboard navigation, zoom/reflow, screen-reader
announcements, and CSS resource requests require browser checks.

For existing apps that use Tailwind or Bootstrap, prefer a narrow
`.syn-root` subtree and explicit `syn-*` classes, test cascade order,
and avoid importing Syntyr's optional semantic mode globally. See the
[full framework integration guide](framework-integrations.md).
