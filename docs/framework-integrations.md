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

For accessible advanced menus, comboboxes and toasts, see the [optional headless interaction guide](headless-interactions.md). All framework JavaScript remains application-owned.

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
request classes on enclosing HTMX/LiveView forms. It never manages
`aria-busy`, disabled state, network requests, focus, announcements,
morphing, DOM lifecycle, or retries. Native disabled buttons retain
their disabled cursor; visual feedback does not block double submissions.

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
element. Turbo toggles `turbo-frame[busy]` while it fetches a replacement.
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

**Verification scope:** the optional bridge and the copyable templates
are statically tested with Python's standard library; the repository's
existing HTMX demo has integration coverage. These examples are not a
claim that Phoenix, Laravel, Rails, or Go runtime tests have run. Add
framework-owned end-to-end tests when you adopt a template in an app.

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

## Vue 3 / Nuxt

[Runnable Vue 3 + Vite starter](https://github.com/dporkka/syntyr-css/tree/main/examples/vue)
uses the local Syntyr CSS package and a normal `<script setup>` component.
Run `npm install && npm run dev` from `examples/vue`; production compilation
is `npm run build`. The CSS import belongs in `src/main.js`, once:

```js
import '@syntyr/css/core.css';
```

```vue
<script setup>
import { ref } from 'vue';
const name = ref('');
</script>

<template>
  <section class="syn-root" data-syn-theme="studio">
    <label class="syn-label" for="campaign-name">Campaign</label>
    <input id="campaign-name" class="syn-input" v-model="name" />
    <p aria-live="polite">{{ name }}</p>
  </section>
</template>
```

Vue owns `v-model`, `@submit.prevent`, computed state, disabling buttons,
ARIA values and network requests. Syntyr never mutates Vue's DOM. Keep
`.syn-root` on a stable ancestor when toggling conditional children;
scope `.syn-semantic` to native HTML elements you intentionally opt in.
In Nuxt, configure global CSS once in `nuxt.config.ts` via its `css`
array; do not import the same bundle in each component. When using SSR,
match the initial theme on server and client to prevent hydration mismatches.

## Svelte 5 / SvelteKit

[Runnable Svelte 5 + Vite starter](https://github.com/dporkka/syntyr-css/tree/main/examples/svelte)
uses native Svelte 5 runes, `bind:value`, `onsubmit`, state-driven
`aria-invalid`, and disabled/pending states. Run `npm install && npm run dev`
from `examples/svelte`; production compilation is `npm run build`.
Import CSS once in `src/main.js` (or `src/routes/+layout.svelte` for SvelteKit):

```js
import '@syntyr/css/core.css';
```

```svelte
<script>
  let name = $state('');
</script>

<section class="syn-root" data-syn-theme="studio">
  <label class="syn-label" for="campaign-name">Campaign</label>
  <input id="campaign-name" class="syn-input" bind:value={name} />
  <p aria-live="polite">{name}</p>
</section>
```

Svelte owns reactivity, validation, events and requests. Syntyr provides
no Svelte actions, stores or hydration hook. In SvelteKit, keep the root
and initial theme consistent across server rendering and hydration.
The two runnable starters use a **local-only campaign list** and an
explicitly simulated delay; they are examples of application-owned state,
not real API persistence.

## Java / Spring MVC + Thymeleaf

[Copyable Thymeleaf view](https://github.com/dporkka/syntyr-css/blob/main/examples/server-rendered/spring-thymeleaf.html)
and [Spring MVC controller](https://github.com/dporkka/syntyr-css/blob/main/examples/server-rendered/CampaignSearchController.java)
demonstrate a real GET handler and escaped server-rendered campaign search.
See the [Java/.NET copy guide](https://github.com/dporkka/syntyr-css/blob/main/examples/server-rendered/README-java-dotnet.md).
Copy `dist/syntyr.core.css` to
`src/main/resources/static/css/syntyr.core.css`, the view to
`src/main/resources/templates/campaigns.html`, and the controller to
your application's Java package. Spring Web and Thymeleaf are host dependencies
only. The view uses `th:text` and `th:value`, never unescaped `th:utext`.

Use Spring MVC binding and Bean Validation for mutating forms; if you
enable Spring Security, retain its CSRF protections. Syntyr cannot
validate requests, encode controller data or submit forms on your behalf.
HTMX or other partial responses should retain the outer theme root.
Syntyr styles browser HTML, not Java Swing or JavaFX desktop widgets.
Vaadin web components may use Shadow DOM; inherited tokens alone do not
style internal elements unless exposed through supported `::part()`/theme
APIs. Avoid assuming the Spring MVC example applies to Vaadin internals.

## C# / ASP.NET Core Razor Pages

[Copyable Razor view and PageModel](https://github.com/dporkka/syntyr-css/tree/main/examples/server-rendered/dotnet/Pages)
demonstrate a read-only GET search with HTML-encoded Razor output.
See the [Java/.NET copy guide](https://github.com/dporkka/syntyr-css/blob/main/examples/server-rendered/README-java-dotnet.md).
Copy the CSS to `wwwroot/css/syntyr.core.css`; copy `Campaigns.cshtml`
and `Campaigns.cshtml.cs` into your app's `Pages` directory and adjust the
namespace. The example enables MVC Tag Helpers explicitly, so
`asp-append-version="true"` cache-busts the CSS asset.

Razor `@Model.Query` and list entries are HTML encoded; avoid `Html.Raw` on
untrusted content. Use ASP.NET Core antiforgery, authorization and model
validation for mutations. Blazor also renders normal HTML `class` attributes,
but its component lifecycle, state and hydration remain Blazor's responsibility;
host CSS through the app layout or static asset pipeline.
Syntyr does not style native WPF, WinUI, or .NET MAUI controls; it is a
browser CSS system. Blazor component CSS isolation and third-party component
Shadow DOM still require normal CSS cascade/part-boundary testing.

**Verification boundary:** Vue and Svelte starter production builds can run
with Node and their optional example-only dependencies. The Java/C# sources
have static contract tests but are not claimed to compile or run on hosts
without Java/Spring and .NET toolchains. Syntyr itself adds no framework
dependency, Java library or NuGet package.

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
