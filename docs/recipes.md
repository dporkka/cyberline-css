# MIT-licensed composition recipes

For copyable input groups, labeled fields, container-responsive settings forms and optional headless UI styling, see [form composition recipes](component-recipes.md) and the [Radix adapter](radix-integration.md). For layered depth, incident-detail layouts, command presentation, timelines, and editorial product sections, see [premium compositions](premium-compositions.md).

These original Syntyr recipes are free to copy, edit, commercialize, and distribute under MIT. No Tailwind Plus source or premium assets were copied. For live examples see [the gallery](index.html), the [Grid console](../examples/console.html), and the [Noir pricing layout](../examples/pricing.html).

## Optional vertical flow

Use `.syn-flow` from `syntyr.recipes.css` on a content group to add
consistent gaps between adjacent **direct children**. The flex-column
composition stacks both inline and block elements, without overriding a
child component's own display. It does not globally reset margins or modify
unwrapped host markup. When children already have vertical margins, adjust
them at the application level to avoid unexpectedly large combined spacing.
For prose with heading rhythm, prefer the existing `.syn-prose` class.

```html
<section class="syn-root" data-syn-theme="studio">
  <div class="syn-flow" style="--syn-flow-gap: 1.5rem">
    <h2 class="syn-section-heading">A native-first design system</h2>
    <p>Readable content with consistent configurable vertical rhythm.</p>
    <a href="/documentation">Read the documentation</a>
  </div>
</section>
```

`.syn-flow` is an opt-in composition, not part of the minimal core.
All spacing remains controlled by ordinary CSS custom properties.

## 1. Responsive telemetry cards

The `.syn-region` element establishes a **named inline-size container**. Unlike media queries, the cards respond to the width of the enclosing widget/sidebar. This is a native browser feature; no JavaScript observer is needed.

```html
<section class="syn-root syn-region" data-syn-theme="grid" aria-label="Network telemetry">
  <div class="syn-stats">
    <article class="syn-stat"><span class="syn-stat-label">UPTIME</span><p class="syn-stat-value">99.8%</p></article>
    <article class="syn-stat"><span class="syn-stat-label">NODES</span><p class="syn-stat-value">24</p></article>
    <article class="syn-stat"><span class="syn-stat-label">ALERTS</span><p class="syn-stat-value">02</p></article>
  </div>
</section>
```

## 2. Accessible empty state

```html
<section class="syn-empty" aria-labelledby="empty-heading">
  <p class="syn-eyebrow">QUEUE / EMPTY</p>
  <h2 id="empty-heading">No pending actions</h2>
  <p class="syn-muted">New items appear here once submitted.</p>
  <a class="syn-button syn-button--primary" href="/new">Create an item</a>
</section>
```

This is a *visual composition*, not a live queue implementation. Preserve real links, meaningful labels, and server-side behavior.

## 3. Three-card pricing display

```html
<section class="syn-root syn-region" data-syn-theme="noir" aria-label="Illustrative plans">
  <div class="syn-pricing">
    <article class="syn-price-card">
      <h2>Personal</h2>
      <p class="syn-price-value">$19<small> / month</small></p>
      <ul class="syn-feature-list"><li>One project</li><li>Basic support</li></ul>
      <a class="syn-button" href="/contact">Contact us</a>
    </article>
    <article class="syn-price-card" data-syn-featured>
      <h2>Studio</h2>
      <p class="syn-price-value">$49<small> / month</small></p>
      <ul class="syn-feature-list"><li>Unlimited projects</li><li>Team seats</li></ul>
      <a class="syn-button syn-button--primary" href="/contact">Contact us</a>
    </article>
    <article class="syn-price-card">
      <h2>Enterprise</h2>
      <p class="syn-price-value">Custom</p>
      <ul class="syn-feature-list"><li>Security review</li><li>Dedicated support</li></ul>
      <a class="syn-button" href="/contact">Contact us</a>
    </article>
  </div>
</section>
```

## 4. Stateful native button (host controlled)

```html
<button type="button" class="syn-button" aria-pressed="true">Grid view</button>
<button type="button" class="syn-button" aria-busy="true">Syncing status</button>
```

`aria-pressed="true"` conveys a real toggle state to accessibility APIs; set it only when a toggle actually is pressed. `aria-busy` signals that updates are in progress; it **does not** disable a button or create loading logic. The UI state must come from your application/server. If a state is only decorative, use `data-syn-state="active"` instead of misusing ARIA.

## Token-only custom theme

```css
/* Unlayered application CSS intentionally overrides Syntyr's layered tokens. */
.syn-root[data-syn-theme="custom"] {
  --syn-bg: #0b1019;
  --syn-surface: #192333;
  --syn-accent: #82f9d1;
  --syn-on-accent: #09120e;
  --syn-text: #eefbf7;
  --syn-muted: #bbd4ce;
  --syn-frame: #496b68;
}
```

For custom themes, test *every* textual token pairing and important state for WCAG contrast. The example overrides only a subset of the available color tokens and is not an accessibility certification.

## CRM and vertical SaaS patterns (alpha.5 source candidate)

Load `syntyr.core.css` and then optional `syntyr.recipes.css`. See the [complete CRM example](../examples/crm.html), which uses ordinary HTML and requires no JavaScript.

- **Filter bar:** `.syn-filter-bar` arranges labelled `.syn-filter-field` controls and a wrapping `.syn-filter-actions` group. Use `.syn-filter-field--query` for a wider search field. A `method="get"` form remains usable without JavaScript; the application must apply filters and preserve query values.
- **Pipeline:** `.syn-pipeline` contains named `section.syn-pipeline-lane` columns; each lane contains a semantic `ul.syn-pipeline-list` of `li.syn-pipeline-card`. Set `tabindex="0"` and an accessible name on the scrollable board so keyboard users can reach overflow. Links inside cards remain ordinary links. Drag-and-drop, permissions, saved filters, counts, and stage transitions must be implemented by the host application.
- **Record metadata:** `dl.syn-record-fields` groups each `dt` and `dd` in a direct child `div` for readable, responsive key/value pairs. Use a real `time` element for dates.
- **Density:** `data-syn-density="compact"` compresses control, row and card spacing without shrinking type. `data-syn-density="comfortable"` restores default metrics inside compact ancestors. `data-syn-density="spacious"` provides larger controls and rows for review-heavy screens. These attributes may be on `.syn-root` or nested elements. `comfortable` is the default when density is unspecified.

```html
<section class="syn-root" data-syn-theme="studio" data-syn-density="compact">
  <form class="syn-filter-bar" method="get" action="/opportunities">
    <label class="syn-label syn-filter-field syn-filter-field--query" for="crm-query">
      Search
      <input class="syn-input" id="crm-query" name="query" type="search">
    </label>
    <div class="syn-filter-actions">
      <button class="syn-button syn-button--primary" type="submit">Search</button>
    </div>
  </form>
  <div class="syn-pipeline" tabindex="0" aria-label="Opportunity stages">
    <section class="syn-pipeline-lane" aria-labelledby="crm-stage">
      <h2 id="crm-stage">Qualified</h2>
      <ul class="syn-pipeline-list">
        <li class="syn-pipeline-card"><a href="/opportunities/123">Example account</a></li>
      </ul>
    </section>
  </div>
  <section data-syn-density="spacious" aria-label="Opportunity details">
    <dl class="syn-record-fields">
      <div><dt>Owner</dt><dd>Account team</dd></div>
    </dl>
  </section>
</section>
```

The styles are layout primitives, not a grid widget or CRM engine. Keep keyboard focus visible, do not imply drag interactions, and render truthful stage counts. Preserve authorization and validate any user-controlled query parameters on the server.

## Reusing recipes across stacks

- **Go / templ, PHP, Django, Rust templates:** Make recipes server-rendered partials and pass content as arguments.
- **HTMX / Datastar:** Use the same classes on server-returned fragments. Their JavaScript, if chosen, is outside the CSS library.
- **React / Vue / Astro:** Wrap the exact markup in framework components only when the host application calls for it.

Favor stable component classes and CSS variables over copying long lists of generated utilities. See [contract](components.md) and [Tailwind research](tailwind-research.md).

## Accessible navigation and loading placeholders

Breadcrumbs use a real ordered list inside a labeled navigation landmark. The separator is a CSS border rather than spoken punctuation:

```html
<nav class="syn-breadcrumbs" aria-label="Breadcrumb">
  <ol>
    <li><a href="/">Home</a></li>
    <li><span aria-current="page">Reports</span></li>
  </ol>
</nav>
```

Page controls are **real links**, not inert buttons. Match the selected page to the actual URL, and label any symbol-only links:

```html
<nav class="syn-pagination" aria-label="Results pages">
  <a class="syn-page-link" href="?page=1">1</a>
  <a class="syn-page-link" href="?page=2" aria-current="page">2</a>
  <a class="syn-page-link" href="?page=3">3</a>
</nav>
```

Skeletons are deliberately static. Hide the visual placeholder from assistive technology and announce loading outside it with application-owned state. Do not leave an infinite loading message or use fake progress values:

```html
<section aria-busy="true" aria-label="Reports">
  <p role="status">Loading reports…</p>
  <span class="syn-skeleton" aria-hidden="true"></span>
  <span class="syn-skeleton syn-skeleton--short" aria-hidden="true"></span>
</section>
```

When loading finishes, the application replaces the placeholders with content and clears `aria-busy`. The CSS library does not implement fetching or state changes.

## Server-rendered SaaS filter and settings patterns

The [SaaS workflow demonstration](../examples/saas-workflows.html) shows how to combine standard HTML search forms, a table, navigation landmarks, native settings disclosures and no-JavaScript placeholders. The page's data is illustrative and **is not filtered**; the following behavior belongs to the host application:

- Parse and validate `query`, `status`, `owner` and `page` on the server, apply authorization before filtering, paginate the results, and escape all rendered user input.
- Preserve submitted form values and `aria-current` based on the actual result page, and emit a truthful result count plus empty-state or error message.
- Persist preferences in the server's settings endpoint, with CSRF protection for changes; the static demo intentionally has no save button.
- When using HTMX, Datastar or another enhancement layer, keep GET filters, ordinary links and form labels working without client-side JavaScript.

The scoped `examples/saas-workflows.css` stylesheet contains layout glue only and is **not** added to the distributed core or all-in-one bundle.


## Intrinsic responsive layouts (optional recipes CSS)

Load `syntyr.core.css` plus `syntyr.recipes.css`. The layout primitives are
scoped to `.syn-root` and require no JavaScript, framework or viewport media
queries. Their children are ordinary semantic HTML.

```html
<section class="syn-root">
  <div class="syn-sidebar" style="--syn-sidebar-width: 14rem">
    <aside>Navigation or filters</aside>
    <main>Main content</main>
  </div>
  <div class="syn-switcher" style="--syn-switcher-threshold: 42rem">
    <article>First card</article>
    <article>Second card</article>
    <article>Third card</article>
  </div>
</section>
```

`.syn-sidebar` expects **exactly two** direct children: sidebar first,
content second. Defaults: sidebar 16rem, content minimum 28rem (capped at
100% of available width). In narrow containers they stack, and neither
child is forced wider than the container by the layout primitive. Content
with long unbreakable text should still use appropriate wrapping.

`.syn-switcher` treats all direct children uniformly. Above the 40rem
default threshold they share a row; below it every child stacks. Override
`--syn-switcher-threshold` per instance. This differs from `.syn-grid`,
which can display different numbers of columns at intermediate widths.

Use opt-in fluid type classes `.syn-fluid-display`, `.syn-fluid-lede` and
`.syn-reading`. The CSS custom properties `--syn-fluid-display-size`,
`--syn-type-lede` and `--syn-reading-width` can be overridden in plain
application CSS. Keep real document headings and reading order.

See [the working minimalist demo](../examples/minimalist-patterns.html).


## Collection workspaces and error recovery (source candidate)

The optional recipes stylesheet contains `.syn-collection-toolbar`, `.syn-collection-actions`,
`.syn-bulk-actions`, `.syn-table--compact`, `.syn-result-state` and
`.syn-error-summary`. They extend the existing `.syn-filter-bar`, `.syn-table`,
`.syn-detail-layout` and base form classes; they do not ship a JS data grid.

[Static resource and error example](../examples/resource-workspace.html) demonstrates:
- A native GET search form with named query parameters (disabled in the static demo so it cannot navigate to an unimplemented route). Implement `/resources` on your server; the static example route does not filter results.
- A titled table, an optional dense presentation, explicit result states, and disabled bulk-action preview. The backend must enforce selection, authorization, CSRF and idempotency for mutations.
- A server-rendered error summary with field-anchor links, `aria-invalid`, and an `aria-describedby` reference to a visible field error. Preserve entered values and ensure the server response moves keyboard focus to the error summary after a failed submission (or sends an equivalent heading-focused full-page response). Never claim client-side styling performs validation.
- Preserve search/filter/sort state in URL parameters. Announce actual result counts, not sample counts. Display no-result or service-error state only when it is true.

The example is illustrative, **not a configured server**. Avoid relying on color alone to convey status. Test with a keyboard, screen reader, 320 CSS-pixel viewport, text zoom and forced-colors mode.

## Task-page layout with native error recovery

For a complete CSS-first account/task composition, see [the intrinsic task-page example](../examples/intrinsic-task-page.html).
It combines the existing opt-in `.syn-sidebar`, core `.syn-region`, `.syn-field-row`,
`.syn-error-summary` and `.syn-empty` patterns instead of introducing another dashboard API.
The error summary reuses the collection-workspace pattern above; no second summary component is added.

The optional `.syn-cover` layout in `syntyr.recipes.css` reserves vertical
space for an empty state, login step or onboarding task. Put the content in a
direct child with `.syn-cover-main`; header and footer are optional:

```html
<section class="syn-root">
  <div class="syn-cover" style="--syn-cover-min-size: 20rem">
    <header><h2>Approval inbox</h2></header>
    <div class="syn-cover-main">
      <p>No requests need your approval.</p>
      <a href="/requests">Review all requests</a>
    </div>
    <footer>Updated when the server renders a new response.</footer>
  </div>
</section>
```

The default minimum block size is 22rem; override `--syn-cover-min-size`
when embedding in smaller contexts. Content can grow beyond that minimum.
Only opt-in recipe CSS is needed. No script or viewport breakpoint is added.

**Form error recovery:** the example deliberately shows a server-rendered
form error state, with a summary link to the invalid input, a matching label
and `aria-invalid="true"` plus `aria-describedby` for the field error.
On a real failed submission, the server must preserve submitted values,
report errors in text, and show the summary only when errors are present.
After a valid submission, do not keep the stale invalid markup. No CSS
class performs validation, authorizes actions or changes application data.
