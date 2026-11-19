# Intrinsic layout compositions: inline clusters and sidecars

Syntyr uses scoped native CSS, not a JavaScript layout engine. These patterns
are available in the **unreleased alpha.5 source candidate** under
`dist/syntyr.core.css`. No additional JavaScript or CSS modules are required.

[Open the no-JavaScript composition demo](../examples/composition-adoption.html).

## Use syn-inline for a wrapping cluster

An existing `.syn-inline` is the cluster primitive; Syntyr does **not** add an
identical `.syn-cluster` alias. It wraps naturally and now exposes optional
`--syn-inline-align`, `--syn-inline-justify`, and `--syn-inline-gap` custom
properties.

~~~html
<nav class="syn-inline" aria-label="Contact filters"
     style="--syn-inline-justify:space-between">
  <a href="/contacts?status=active">Active</a>
  <a href="/contacts?status=inactive">Inactive</a>
  <a href="/contacts">All contacts</a>
</nav>
~~~

Use a real `nav` for navigation and a real `form` for filtering inputs.
The class changes layout only; it never implies tab semantics or keyboard
behavior. Existing `.syn-inline` layouts retain their default center
alignment and start justification.

## Use syn-sidecar for an intrinsic main + aside

A two-child `.syn-sidecar` puts the **main content first** and the supplementary
aside second in document and focus order. It wraps on available container width
without viewport breakpoints, JavaScript, or an explicit container query.
A lone child remains the main region and keeps the min-size and
unbroken-text overflow protections.

~~~html
<div class="syn-root syn-sidecar" data-syn-theme="studio">
  <main class="syn-panel">
    <h1>Campaigns</h1>
    <p>The principal content remains first in the accessibility tree.</p>
  </main>
  <aside class="syn-panel" aria-label="Campaign insights">
    <h2>Insights</h2>
    <p>Supplementary context.</p>
  </aside>
</div>
~~~

Custom properties belong on the layout container:

| Property | Default | Effect |
| --- | --- | --- |
| `--syn-sidecar-gap` | `--syn-space-3` | Space between regions |
| `--syn-sidecar-main-min` | `28rem` | Minimum preferred size of the main area before wrapping |
| `--syn-sidecar-aside-width` | `16rem` | Preferred width of the supplementary area |
| `--syn-sidecar-align` | `start` | Cross-axis alignment |

Do not add absolute positioning or hide the aside on small screens. CSS intrinsic
wrapping responds to the *actual available width*, including embedded sidebars,
rather than guessing from the viewport. Content may still overflow if
application-defined children use fixed dimensions; make tables and code blocks
scrollable and keyboard reachable where necessary.

## Import only what you need

For no-build consumers, the preferred option is one self-hosted
`syntyr.core.css` stylesheet. For selective component loading, use the
prebuilt CSS files in order: `components/tokens.css`,
`components/base.css`, then `components/layout.css` and any additional
components. Do not load core and these component files together. The
`form-composition` module also needs `forms`.

The `--syn-inline-*` and `--syn-sidecar-*` properties are public
customization points; they do not require an app-side CSS compiler.
Syntyr's optional [selective builder](selective-builds.md) can assemble
a single stylesheet without scanning templates or purging dynamic classes.

See the [Go server-rendered starter](https://github.com/dporkka/syntyr-css/tree/main/examples/go-htmx) for a
working app whose native GET route can optionally return HTMX fragments.
Application state, accessibility behavior and data authorization always
belong to the host, not to these layout classes.

For optional browser verification, run `python3 tests/composition_adoption_browser.py`
from a checkout with Playwright and browser engines installed. It checks
wide, narrow, and embedded widths; WebKit needs its native system dependencies.
The release CSS and the example itself do not require Playwright.
