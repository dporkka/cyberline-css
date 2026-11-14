# MIT-licensed composition recipes

These original Syntyr recipes are free to copy, edit, commercialize, and distribute under MIT. No Tailwind Plus source or premium assets were copied. For live examples see [the gallery](index.html), the [Grid console](../examples/console.html), and the [Noir pricing layout](../examples/pricing.html).

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


## Optional render deferral for independent long sections

Load `dist/syntyr.core.css` and **then** `dist/syntyr.recipes.css`.
For large **below-the-fold** sections that do not need immediate painting,
apply `.syn-defer-section` to an outer, independent section:

```html
<section class="syn-defer-section" style="--syn-defer-size: 30rem" aria-labelledby="history-heading">
  <h2 id="history-heading">Historical campaign report</h2>
  <!-- A large, normally rendered HTML report -->
</section>
```

This progressively enhances browsers supporting `content-visibility: auto`
with an estimated intrinsic block size, while keeping HTML and accessibility
semantics intact. Print styles force the contents visible. **The section is
not virtualized**: all DOM nodes still exist and application state updates
still run. Use only where deferred painting is acceptable.

**Avoid on** above-the-fold content, live regions, overlays, sticky panels,
critical inputs, individual table rows, and sections requiring exact initial
height. Choose `--syn-defer-size` close to the rendered section height
(default 36rem) to reduce scroll-position shifts. Validate find-in-page,
keyboard navigation, scroll anchoring, printing, and CLS with real content.
If a section grows unpredictably or causes jumps, omit this class.

### Reproduce performance observations

Syntyr has a developer-only, offline Chromium harness:

```sh
# Install Playwright in a separate developer environment, not in the app.
python3 scripts/perf_benchmark.py --runs 7 --rows 700 --sections 40 \
  --output /tmp/syntyr-performance.json
```

The script compares **the same markup** using no CSS, core, core+recipes,
the full library, and core+recipes with opt-in deferred sections. It reports
median local navigation time and forced theme-restyle measurements using Chrome
DevTools `RecalcStyleDuration` / `LayoutDuration`. A first warmup sample is
discarded. No network or remote fonts are used. Browser installation is
optional; the distributed CSS remains zero-JavaScript.

On Gertrude, headless Chromium 156 (700 rows, 40 independent sections,
seven measured runs with rotated variant order) recorded **31.50 ms/toggle**
without deferred sections versus **22.24 ms/toggle** with deferral (about
29% lower). The cumulative restyle measurement over 10 toggles fell from
290.86 ms to 200.99 ms. These are synthetic, device-dependent measurements;
they are **not Core Web Vitals**, CDN results, benchmarks against other
frameworks, or evidence that all Syntyr pages become faster. Use repeatable
runs on a representative app before enabling the class.

The frozen "/v/0.3.0-alpha.4/" CSS snapshot does **not** include this new
recipe; pin a subsequent release after it is published.
