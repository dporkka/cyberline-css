# Syntyr CSS integration guide: server-rendered HTML and frontend stacks

Syntyr is a **CSS presentation layer**, not a state manager, request client, or component runtime.
It has no JavaScript initialization, no required build tool, and no runtime dependency.
Every example uses the same `syn-` classes, CSS tokens and standard HTML.

## Choose one styling mode

1. **Explicit classes (recommended for apps):** load `syntyr.core.css`, use
   `.syn-root` on a stable ancestor, then `.syn-button`, `.syn-panel`, `.syn-input`, etc.
2. **Optional semantic HTML:** additionally load `syntyr.semantic.css` after core and
   add `.syn-semantic` to a scoped ancestor. Unclassed HTML receives semantic styles.
   For an element that an interaction framework will add classes to, opt it in once
   with `data-syn-semantic`. This preserves semantic styling while host-managed
   classes such as `htmx-request` are added and removed.

```html
<section class="syn-root syn-semantic" data-syn-theme="studio">
  <button data-syn-semantic hx-get="/status" hx-target="#status">Check status</button>
  <div id="status" aria-live="polite"></div>
</section>
```

**Host isolation:** Loading the CSS alone does not style a `.syn-button`,
`.syn-panel`, or other Syntyr class outside `.syn-root`. Existing host UI
components and CSS retain their presentation. Put `.syn-root` on the actual
Syntyr subtree (or on the component itself); do not assume a globally
scoped component class creates its own theme root. Syntyr uses native CSS
nesting for this boundary, so test embedding in each target browser.

The marker is only considered **inside** `.syn-semantic`, so it does not style
elements elsewhere. Do not put it on elements styled by a separate component
library unless you explicitly want Syntyr semantic styling there. Prefer
`.syn-button` for already-classed controls. The marker does **not** make the
control stateful, disabled, or accessible by itself.

## HTMX: progressive enhancement

A complete example with a real stdlib Python HTTP server is at:
[examples/htmx.html](https://github.com/dporkka/syntyr-css/blob/main/examples/htmx.html),
[examples/htmx_server.py](https://github.com/dporkka/syntyr-css/blob/main/examples/htmx_server.py), and
[examples/htmx.css](https://github.com/dporkka/syntyr-css/blob/main/examples/htmx.css).
These links lead to source files, not a live Cloudflare demonstration.

From the repository root:

```sh
python3 examples/htmx_server.py
# open http://127.0.0.1:8765/examples/htmx.html
```

The optional demo loads **pinned HTMX 2.0.8** from a third-party CDN. The CSS
library doesn't load HTMX automatically. Production applications should
self-host the pinned HTMX asset for control over performance, integrity, and CSP.

The search form uses a real `action` and `method=get`. When HTMX sends
`HX-Request: true`, the server returns only the result fragment. Ordinary
navigation gets a complete HTML document. The server emits `Vary: HX-Request`
to keep caches from mixing the representations, and escapes user-controlled
query text before inserting it in HTML.

For best results:

- Put `.syn-root` and `data-syn-theme` **outside** the swapped element.
- Swap the narrowest stable target (normally `innerHTML` inside a results container).
- Give labels and inputs stable IDs; preserve native form submission as a fallback.
- Use the framework's `hx-indicator` and `hx-disabled-elt` when appropriate;
  `aria-busy` does **not** block duplicate submissions by itself.
- Do not create a permanent Syntyr HTMX runtime or register Syntyr lifecycle events.
- For strict CSP, use `includeIndicatorStyles: false` and an external stylesheet.
  The demo shows this pattern with a small **application-owned** `htmx.css`.
- Test initial document, request state, swapped fragment, form fallback, and
  failure paths in an actual browser.

The demo server intentionally exposes only four static assets and one GET route,
listens on localhost, and is **not** included in the Cloudflare static-site build.
A static host cannot serve its dynamic search endpoint without a backend.


## Server-driven HTML: optional request-state bridge

**No adapter is necessary to render Syntyr components.** Serve core CSS from
your application and output the same `syn-` classes in HEEx, Blade, ERB, templ,
Jinja, Twig or Razor. You only need a second CSS file if you want native
framework loading classes and attributes to show Syntyr's progress cursor:

```html
<link rel="stylesheet" href="/css/syntyr.core.css">
<link rel="stylesheet" href="/css/syntyr.server.css">
```

Or, when using a CSS-aware package build system, import
`@syntyr/css/core.css` followed by `@syntyr/css/server.css`.
The optional `syntyr.server.css` is included in `syntyr.all.css`, but not core.
The npm package is an unreleased alpha.5 candidate; self-host prebuilt
files or a pinned release until that version is actually published.

The bridge is **presentation-only**. It styles the cursor on Syntyr buttons
during `data-loading`, `.htmx-request`, `.phx-click-loading`,
`.phx-submit-loading`, `.phx-change-loading`, or
`[data-syn-state="loading"]`. It also supports `turbo-frame[busy]` and
request classes on enclosing HTMX/LiveView forms, plus `form[aria-busy="true"]`
when Turbo submits a form targeting a sibling frame. It never manages
`aria-busy`, disabled state, network requests, focus, announcements,
morphing, DOM lifecycle, or retries. Busy submit buttons can temporarily be disabled by Livewire or LiveView;
the bridge still uses a progress cursor while the native loading attribute is
present. Ordinary disabled buttons keep their disabled cursor. CSS feedback
and `aria-busy` do not prevent duplicate submissions.

Keep `.syn-root` and `data-syn-theme` on a stable ancestor **outside**
the element that Turbo/HTMX replaces or that LiveView/Livewire morphs.
Prefer stable, unique input and form IDs. A server-rendered validation
message must use an associated `aria-describedby` and `aria-invalid`
on the input. Do not use `phx-update="ignore"` or `wire:ignore` just to
make styling survive framework patches.

## Phoenix LiveView (HEEx)

[Copyable HEEx form](https://github.com/dporkka/syntyr-css/blob/main/examples/server-rendered/liveview.heex)
uses the normal `phx-change` and `phx-submit` handlers. Server assigns
control the value and validation error:

```heex
<section class="syn-root" data-syn-theme="studio">
  <form id="campaign-form" class="syn-form" phx-change="validate" phx-submit="save">
    <label class="syn-label" for="campaign-name">Campaign</label>
    <input id="campaign-name" class="syn-input" name="campaign[name]"
           value={@name} aria-invalid={if @error, do: "true", else: "false"} />
    <button class="syn-button syn-button--primary" type="submit"
            phx-disable-with="Saving...">Save</button>
  </form>
</section>
```

LiveView adds `phx-submit-loading`, `phx-click-loading`, and
`phx-change-loading` to the relevant element or form while awaiting the
server. Its own `phx-disable-with` and form behavior handle interaction
locking; Syntyr never duplicates that logic. Include LiveView's ordinary
JavaScript bootstrap in your Phoenix application, not in Syntyr.

## Laravel Livewire (Blade)

[Copyable Blade form](https://github.com/dporkka/syntyr-css/blob/main/examples/server-rendered/livewire.blade.php)
uses `wire:submit`, `wire:model.live`, and Blade validation messages:

```blade
<section class="syn-root" data-syn-theme="studio">
  <form class="syn-form" wire:submit="save">
    <label class="syn-label" for="campaign-name">Campaign</label>
    <input id="campaign-name" class="syn-input" wire:model.live="name"
           aria-invalid="{{ $errors->has('name') ? 'true' : 'false' }}" />
    <button class="syn-button syn-button--primary" type="submit">Save</button>
  </form>
</section>
```

**Livewire 4** automatically adds `data-loading` to request-triggering
elements. Syntyr's optional CSS recognizes it without Tailwind. In
**Livewire 3**, use `wire:loading`, `wire:loading.attr="disabled"`,
or your own native `aria-busy`/`data-syn-state` binding where needed;
do not assume the v4 automatic attribute exists. For loading text,
prefer Livewire's own `wire:loading` and `wire:target` controls. Its
client runtime comes from the Laravel application.

## Rails Hotwire / Turbo Frames

[Copyable Turbo form](https://github.com/dporkka/syntyr-css/blob/main/examples/server-rendered/turbo.html)
uses a normal GET form to update only a matching frame:

```html
<section class="syn-root" data-syn-theme="studio">
  <form action="/campaigns" method="get" data-turbo-frame="campaign-results">
    <label for="q">Campaign</label>
    <input id="q" class="syn-input" name="q">
    <button class="syn-button" type="submit">Search</button>
  </form>
  <turbo-frame id="campaign-results"></turbo-frame>
</section>
```

The server must return a matching `<turbo-frame id="campaign-results">`
element. Turbo toggles `turbo-frame[busy]` while it fetches a replacement and
`aria-busy` on the submitting form; when the frame is a sibling of the form,
the form state (not the frame state) styles the submit button.
Turbo Streams and full-page visits must keep the Syntyr root appropriately
scoped. Forms with mutations still need application-owned authentication,
CSRF protection and server validation. This recipe does not ship Turbo.

## Go templ and other server template engines

[Copyable Go templ search template](https://github.com/dporkka/syntyr-css/blob/main/examples/server-rendered/search.templ)
shows a native GET form with escaped templ values. Serve the same CSS
from Go's static assets. The request handler performs the search and
renders the next HTML response; Syntyr does not add a Go dependency.

Django/Jinja, Symfony/Twig, ASP.NET Razor, Spring Thymeleaf, Hugo/Zola,
and other HTML renderers need no special integration: render actual
`<label>`, `<input>`, `<button>` and `<form>` elements with `syn-`
classes, apply `aria-invalid` and `aria-describedby` from server
validation, and keep static assets versioned. Choose framework-native
partials/components and anti-CSRF mechanisms.

**Verification scope (November 15, 2026):** the bridge and copyable
templates have standard-library contract tests. For computed CSS,
run the optional cross-browser smoke test after installing Playwright
and its chosen browsers in a *test environment*:

```sh
python3 tests/server_framework_browser.py --browsers chromium,firefox,webkit
```

The standalone CSS tests passed in Chromium, Firefox and WebKit. We also
tested the Blade form in a disposable Laravel 12.72 / Livewire 4.4.8 app:
server-side form validation (9 assertions), and a Chromium session exercising
live invalid/valid submissions, request state and input focus. A disposable
Phoenix 1.8.16 / LiveView 1.2.13 app passed an actual `Phoenix.LiveViewTest`
for `phx-change`, `phx-submit`, validation and successful server rendering.
Those *framework-app test harnesses* are not included in the Syntyr source
distribution; this is evidence for the tested versions, not a universal
compatibility certification.

Full LiveView browser-client behavior, Rails Turbo navigation, and
other framework versions still require application-owned end-to-end tests.
Syntyr does not bundle or initialize these frameworks.

## Lit / Web Components

Syntyr works with Lit but does not depend on it. Lit components using light DOM
can use ordinary `.syn-*` classes within a Syntyr root. Components with Shadow
DOM need local internal styles consuming inherited `--syn-*` tokens, and may
expose supported styling surfaces with `::part()`. Stylesheets in the page do
not automatically style the inside of a shadow root. See the
[Lit integration guide](lit-integration.md), [optional runnable example](https://github.com/dporkka/syntyr-css/tree/main/examples/lit)
and [component-authoring conventions](component-authoring.md).

## Alpine.js

Use native attributes for real state, and Syntyr classes for presentation:

```html
<div class="syn-root" x-data="{ selected: false }">
  <button class="syn-button" type="button"
          :aria-pressed="String(selected)" @click="selected = !selected">
    Toggle details
  </button>
</div>
```

Mount Alpine once in the host app. For `x-cloak`, define a tiny application
rule `[x-cloak] { display: none !important; }` before Alpine initializes.
Syntyr doesn't manage Alpine state.

## Datastar

Bind standard `aria-*`, `data-syn-state`, and class attributes to Datastar
signals. Style the resulting HTML as ordinary DOM. Keep the Syntyr theme root
outside morph targets, and let Datastar own request and signal behavior.
No Syntyr Datastar plugin is needed.

## React / Next.js

```jsx
import "./syntyr.core.css";

export function StatusCard({ status }) {
  return (
    <section className="syn-root" data-syn-theme="studio">
      <article className="syn-panel">
        <h2 className="syn-heading">Operations</h2>
        <p>{status}</p>
      </article>
    </section>
  );
}
```

Import CSS once from the app entry point (or root layout, as supported by
the framework). No Syntyr provider, hooks, hydration, or dependency on React.

## Vue / Nuxt and Svelte / SvelteKit

Import the same CSS once. Bind native classes, `aria-*`, and
`data-syn-state` using each framework's built-in template syntax.
Do not wrap simple visual classes in additional runtime components unless the
application benefits from reusable semantic component boundaries.

## Astro, Hugo, Zola, Django, Rails, Go/templ and Rust templates

Serve `syntyr.core.css` as a normal static asset. Write HTML partials
with real headings, forms and links. Optional interactive islands can use
HTMX, Alpine, Datastar, React or native browser elements without changing
Syntyr's HTML/CSS contract. In Rails, Hotwire/Turbo updates have the same
theme-root and swap-boundary considerations as HTMX.

## Existing Tailwind or component-library applications

- Syntyr's `.syn-root` scope and `@layer syn.*` layers limit unintended
  interference, but Tailwind Preflight can still change global element defaults.
- Prefer explicit Syntyr classes. Apply `.syn-semantic` only to designated
  regions, not to a whole React/Headless UI component tree.
- Override public `--syn-*` tokens in application CSS; avoid copying or
  rebuilding utility frameworks inside Syntyr.
- Test cascade ordering, focus rings, dark/light color schemes, zoom and
  third-party components after integration.

## Performance and compatibility contract

- CSS bytes are tracked by `python3 scripts/asset_report.py` with optional JSON baseline comparisons; no arbitrary gzip release gate.
- Syntyr runtime JS: **zero**. HTMX/Alpine/React are host-app dependencies.
- Self-host assets on the app's own origin when practical; pin external CDN
  versions. Don't load both `syntyr.all.css` and its constituent stylesheets.
- Use Playwright or equivalent browser automation to verify dynamic class
  changes, HTMX fragments, responsiveness and accessibility.
- Avoid large DOM swaps, expensive decorative effects on scrolling tables,
  and unnecessary hydration. Measure actual page LCP, CLS and INP.
