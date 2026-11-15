# Syntyr CSS component and token contract

Status: **experimental v0.3-alpha**, not yet released to a package registry. All CSS and markup are original to this repository; no upstream source code was copied.

Native elements such as `search`, `figure`, `figcaption`, `kbd`, `mark`, `output`, `meter`, and `pre` are styled only in the optional semantic mode. See [the no-JS native example](../examples/native-elements.html). The regular component-class API and HTML outside `.syn-root` are unchanged.

## Loading and scoping

For the explicitly classed API (no automatic unclassed element styles):

```html
<link rel="stylesheet" href="syntyr.core.css">
<body class="syn-root syn-page" data-syn-theme="grid">
  <button class="syn-button syn-button--primary">Run</button>
</body>
```

For Pico-like semantic markup, add the optional file **after** core and mark the subtree. Unclassed elements style automatically; opt in class-changing elements with `data-syn-semantic`:

```html
<link rel="stylesheet" href="syntyr.core.css">
<link rel="stylesheet" href="syntyr.semantic.css">
<section class="syn-root syn-semantic" data-syn-theme="studio">
  <article>
    <label for="id">Operator <input id="id" name="id" required></label>
    <button data-syn-semantic>Continue</button>
  </article>
</section>
```

Class-based components, recipes, effects, and geometry apply only to elements
inside a Syntyr root, including classes attached directly to the root itself.
A bare Syntyr class on an unrelated host element is deliberately ignored, so
framework-owned components and existing application CSS are not restyled.
The root boundary is enforced through modern native CSS nesting with
a zero-specificity selector rather than a global reset. Checkboxes and
radio controls using the explicit styling API retain a minimum 24 CSS px box;
the surrounding label should provide additional activation area.

For optional effects, load `syntyr.effects.css`. `syntyr.css` is the convenient core + effects entry point. `syntyr.all.css` combines everything (semantic styling still requires `.syn-semantic`). `syn-root` should wrap any themed subtree; nested `data-syn-theme` overrides color tokens. The separate `data-syn-intensity="quiet|standard|cinematic"` attribute controls decorative strength on a root or nested region. Load `syntyr.geometry.css` for a `.syn-frame` with one shape and optional `.syn-frame--accent`. See the [visual-intensity guide](visual-intensity.md).

## Components

| Area | CSS API | Semantic alternative |
| --- | --- | --- |
| Buttons | `.syn-button`, `.syn-button--primary`, `.syn-button--outline`, `.syn-button--danger`, `.syn-button--small`, `.syn-button--ghost` | unclassed `button` |
| Panels | `.syn-panel`, `.syn-panel--cut` | unclassed `article` |
| Layout | `.syn-page` (viewport-height opt-in), `.syn-shell`, `.syn-header`, `.syn-grid`, `.syn-layout`, `.syn-inline`, `.syn-stack` | normal CSS layout |
| Typography | `.syn-logo`, `.syn-eyebrow`, `.syn-title`, `.syn-section-heading`, `.syn-heading`, `.syn-lede`, `.syn-mono`, `.syn-caption`, `.syn-muted` | native heading/text |
| Status | `.syn-badge`, `.syn-badge--accent`, `.syn-status` and semantic variants, `.syn-alert`, `.syn-alert--danger`, `.syn-meter` on `progress` | native `progress` |
| Forms | `.syn-form`, `.syn-label`, `.syn-input`, `.syn-select`, `.syn-textarea`, `.syn-check`, `.syn-fieldset`, `.syn-help`, `.syn-error` | unclassed form controls |
| Form compositions | `.syn-field`, `.syn-field-row`, `.syn-field-body`, `.syn-input-group`, `.syn-input-addon`, `.syn-error-summary` | native `form`, `label`, `input`, `button` |
| Overlays | `.syn-popover` on `[popover]`, `.syn-dialog` on `dialog`, `.syn-details` on `details` | browser defaults |
| Data | `.syn-table-wrap`, `.syn-table`, `.syn-cell--wrap`, `.syn-cell--numeric`, `.syn-description-list`, `.syn-description-actions` | unclassed `table`, native `dl` |
| Navigation | `.syn-breadcrumbs`, `.syn-pagination`, `.syn-page-link` | native `<nav>`, `<ol>`, links and `aria-current` |
| Loading | `.syn-skeleton`, `.syn-skeleton--short` | decorative placeholders; announce status separately |
| Effects (optional) | `.syn-grid-effect`, `.syn-glow`, `.syn-scanlines` | none |

### Optional composition utilities and component overrides

Load `syntyr.utilities.css` in addition to core to use finite helpers:
`syn-u-w-full`, `syn-u-max-reading`, `syn-u-overflow-auto`,
`syn-u-text-center`, `syn-u-min-w-0` and `syn-u-wrap`. These classes
work only inside `.syn-root` and do not require a class generator.
The existing flex/grid/spacing helpers are unchanged. Load the optional
module only when it is needed.

Customize individual components with custom properties rather than a new
set of modifiers:

```html
<article class="syn-panel"
         style="--syn-panel-padding:1.5rem; --syn-panel-radius:.75rem;
                --syn-panel-border-width:2px">
  <button class="syn-button"
          style="--syn-button-padding-inline:1.25rem;
                 --syn-button-border-width:2px">Open</button>
</article>
```

Defaults preserve the previous appearance: fluid panel padding, square
panel corners, and 1px borders; button inline padding defaults to 1rem.
These values are local CSS custom properties, not compile-time settings.
Inspect `metadata/syntyr-api.json` for the machine-readable API index,
or use the [editor integration instructions](editor-integration.md).

Use native button `popovertarget="id"` to control a popover and `commandfor="id" command="show-modal"` to open a dialog in supporting browsers. This last native dialog invoker API has newer browser support; provide alternate ways to reach important content where needed. Do not build custom ARIA dialog/tab/combobox patterns unless they are tested and necessary.

### Review screens and accessible error summaries

For server-rendered validation, combine `.syn-error-summary` with `.syn-error`, `aria-invalid="true"` and `aria-describedby`, and have the application move focus to the summary after a failed submit. For key/value review views, use a native `dl.syn-description-list` with `dt`/`dd` children. Table sort affordances respond to `th[aria-sort] > button`; the application supplies the sorting logic and updates `aria-sort`. The styles use logical direction where appropriate. See the [design-system pattern guide](mature-system-patterns.md) and [static example](../examples/mature-patterns.html).

## Neutral-first visual styling

The implicit `.syn-root` palette is Studio (light and sans-serif). Explicit `data-syn-theme="grid"` and `data-syn-theme="terminal"` retain technical monospace presentation; other themes remain opt-in. `.syn-panel` and `.syn-stage` are flat by default; add `syn-surface--accent` from the optional recipes CSS for emphasis, or the effects stylesheet for cinematic treatments. `.syn-badge` is a neutral label; use `.syn-status` with readable status text for meaningful state, or `.syn-badge--accent` to emphasize a badge.

Use `.syn-section-heading` between `.syn-heading` and `.syn-display`. Tables retain compact no-wrap defaults for identifiers and numeric values; add `.syn-cell--wrap` to descriptive cells. Selected rows have a logical inline-start accent border in addition to their fill. Keep wide tables in `.syn-table-wrap` and provide an accessible caption.

## Theme tokens

| Token | Purpose |
| --- | --- |
| `--syn-bg`, `--syn-surface`, `--syn-surface-hi` | Background surfaces |
| `--syn-text`, `--syn-muted` | Foreground text |
| `--syn-accent`, `--syn-on-accent`, `--syn-accent-soft` | Accent and contrast |
| `--syn-frame`, `--syn-danger` | Borders and warning states |
| `--syn-font`, `--syn-mono` | System typography |
| `--syn-space-1` ... `--syn-space-5` | Spacing scale |
| `--syn-cut`, `--syn-radius`, `--syn-line`, `--syn-control-height` | Shape and layout |

Application CSS can override tokens:

```css
/* Unlayered CSS overrides the library's layered defaults. */
.my-surface { --syn-accent: #a9f890; }
```

## Optional charts and microvisualizations

Load `syntyr.viz.css` after core for seven-theme chart colors, figure/legend
styling, inline SVG sparklines, bar lists, status trackers and heatmap cells.
Syntyr only styles supplied HTML/SVG; it does not create chart geometry,
fetch data or require a renderer. Read [Syntyr Viz](viz.md) and open the
[static seven-theme gallery](../examples/viz.html).

## Accessibility and performance contracts

- Actual semantic HTML and associated labels; use `button` for actions and `a` for navigation.
- Visible `:focus-visible` outline; do not remove it with theme overrides.
- Contrast target: WCAG 2.2 AA for text; manually verify any customized tokens.
- Honor user preferences: `prefers-reduced-motion`, `forced-colors`; effects opt-in and static.
- Avoid relying on color alone for state; use labels or icons with text alternatives.
- Raw/gzip bundle sizes are reported by `python3 scripts/asset_report.py`, with no hard size ceilings; runtime JS: 0 bytes.
- Browser coverage: current Chromium, Firefox and WebKit. The included automated browser suite runs Chromium when installed and can be extended to other engines.
- Do not automatically treat the demo or contract tests as an accessibility certification: test screen readers, 200%/400% zoom, form errors, contrast, and actual products separately.

## Distribution behavior

The repository now includes an **optional CSS-only `package.json` for package-manager distribution**; there is still no Node runtime requirement, bundling dependency, or mandatory package manager. A standard Python 3 build script creates deterministic concatenated CSS and validates exact committed outputs (see [optional package-manager guide](package-managers.md)):

```sh
python3 scripts/build.py
python3 scripts/build.py --check
python3 -m unittest discover -s tests -v
```

## Licensing and provenance

MIT; this version is original work, not a fork or copy of Pico CSS, Chota or Open Props. If future work ports code from an upstream library, preserve that project's copyright and MIT notices and document the relevant files in `THIRD_PARTY_NOTICES.md`.


## Embedded versus full-page usage

`syn-root` provides a bounded styling context. Add `syn-page` **only for full-page experiences**. This separation prevents an embedded themed widget from unexpectedly forcing a viewport-height section.

```html
<section class="syn-root" data-syn-theme="noir">
  <div class="syn-panel">This can be embedded inside an existing application.</div>
</section>
```

For invalid form controls, associate error text through native labeling and `aria-describedby`, and set `aria-invalid="true"` for server-provided errors. `syn-error` changes text color; do not rely on color alone to communicate invalid state.

```html
<label class="syn-label" for="email">Email</label>
<input class="syn-input" id="email" type="email" aria-invalid="true" aria-describedby="email-error">
<p class="syn-error" id="email-error">Enter a valid email address.</p>
```

## v0.3 compositional patterns (no build step)

The following are ordinary CSS classes in `syntyr.core.css`:

| Class | Purpose |
| --- | --- |
| `.syn-region` | Named `syn-region` inline-size container for independent widget responsiveness |
| `.syn-split` | Stacked by default; two columns at container width >=43rem |
| `.syn-stats` | One/two/three columns at container widths <31rem, >=31rem, >=55rem |
| `.syn-stat`, `.syn-stat-label`, `.syn-stat-value` | Semantic telemetry card presentation |
| `.syn-empty` | Centered dashed-outline empty-state composition |
| `.syn-pricing`, `.syn-price-card` | One column until 43rem, then three equal columns |
| `.syn-price-card[data-syn-featured]` | Opt-in highlighted plan, purely visual, no ARIA claim |
| `.syn-price-value`, `.syn-feature-list` | Pricing typography and list styles |
| `.syn-toolbar` | Wrapping flex toolbar |

Attach `.syn-region` **on an ancestor** of the patterns. A region element isn't its own query container descendant; without a region ancestor the patterns remain readable one-column layouts. Nest separate regions for independently sized widgets. The `syn-region` name prevents unrelated page containers from changing their layouts.

Button state: `.syn-button[aria-pressed="true"]` is a pressed **toggle button**; `[data-syn-state="active"]` is decoration/host state; `[aria-busy="true"]` expresses in-progress updates but does not actually disable interactions. State changes and form handling are application responsibilities.

Additional inherited tokens: `--syn-ease`, `--syn-duration-fast`, `--syn-success`, `--syn-warning`. Extend themes with unlayered `.syn-root[data-syn-theme="custom"] { --syn-accent: ... }` CSS. Test contrast for your own values.

See [theme customization and token overrides](theme-customization.md), [MIT composition recipes](recipes.md) and [Tailwind architectural research](tailwind-research.md).

## Optional SaaS, business and CLI compositions (development branch)

Load `syntyr.core.css` first and `syntyr.recipes.css` second. The core remains separate from optional recipes; measure each bundle instead of enforcing a fixed byte cap.

| Context | Optional classes |
| --- | --- |
| SaaS | `.syn-app-shell`, `.syn-app-rail`, `.syn-app-nav`, `.syn-workspace`, `.syn-app-topbar`, `.syn-kpi-grid`, `.syn-app-card`, `.syn-activity-list` |
| Business website | `.syn-site-hero`, `.syn-site-heading`, `.syn-feature-grid`, `.syn-feature-card`, `.syn-cta-band` |
| Browser terminal | `.syn-terminal`, `.syn-terminal-bar`, `.syn-terminal-body`, `.syn-terminal-line`, `.syn-terminal-prompt` |
| Surface design | `.syn-frame--precision`, `.syn-frame--industrial`, `.syn-frame--soft` |

Native disabled buttons cannot activate; aria-disabled does not block activation by itself. Host application code must suppress actions when ARIA-disabled and should preserve focus when appropriate. Syntyr does not disable click handlers via CSS.

Professional light mode: `data-syn-theme="studio"`. Colors and geometry are intentionally independent. Use `.syn-table-emphasis` for explicit cell highlighting instead of relying on last-column position; `.syn-status--success`, `--warning`, or `--danger` should always accompany readable status text.

Native terminal applications cannot render CSS. Use `terminal/palettes.json` as the portable color reference. See [usage and accessibility guidance](saas-cli-business.md). For bevel, notch, bracket, inset and circuit frame geometry, load the optional geometry stylesheet and follow [the frame guide](geometry-terminal.md). All new visual classes are optional and require no runtime JavaScript.


## Minimalist compositions (experimental)

`syntyr.recipes.css` also includes `.syn-sidebar` (two-column intrinsic
sidebar/content), `.syn-switcher` (all-or-nothing responsive card row),
fluid typography utilities `.syn-fluid-display` / `.syn-fluid-lede`,
and `.syn-reading`. These are not part of `syntyr.core.css`.
Classless checkbox and radio labels align their controls inline when
`syntyr.semantic.css` and `.syn-semantic` are enabled. See
[the recipe guide](recipes.md) and [live example](../examples/minimalist-patterns.html).

## Visual role examples

The optional [design-state example](../examples/design-states.html) exercises active, selected, disabled, and invalid presentation across nested light/dark themes. It contains no application state machine, backend operation, or runtime JavaScript.

## Progressive rendering extensions

System-aware `data-syn-theme="auto"` is built into core CSS. Use optional
`syntyr.print.css` for printable reports and the
[progressive-enhancement guide](progressive-enhancement.md) for fallbacks.
