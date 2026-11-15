# Syntyr theme customization — copy, override, ship

Syntyr themes are **CSS custom properties**, not JavaScript configuration.
The MIT core already includes Grid and Noir palettes, responsive primitives,
accessible focus styling and semantic element options.

## 1. Choose a theme

Without a `data-syn-theme` attribute, `.syn-root` now uses Studio. Select Grid or Noir explicitly for technical/cinematic styles. This change is only in the unreleased alpha.5 candidate; version-pinned alpha.4 assets remain unchanged.

Load the published `syntyr.core.css` in your application and use regular HTML:

```html
<link rel="stylesheet" href="/css/syntyr.core.css">
<section class="syn-root" data-syn-theme="grid">
  <article class="syn-panel syn-panel--cut">
    <h2 class="syn-heading">Sector status</h2>
    <button class="syn-button syn-button--primary">Open</button>
  </article>
  <aside data-syn-theme="noir" class="syn-panel">
    Nested Noir preview
  </aside>
</section>
```

Use `data-syn-theme="noir"` for warm amber. Native HTML features
such as `details`, `dialog` and `popover` don't need framework JavaScript.

## 2. Override tokens using application CSS

Syntyr declares its defaults in named cascade layers. App CSS without a
layer takes precedence over layered author rules regardless of selector specificity.
Load application overrides **after** the Syntyr stylesheet to reduce surprises:

```css
/* app.css: original tokens, not copied from existing entertainment IP. */
.syn-root[data-syn-theme="grid"] {
  --syn-accent: #80dfef;
  --syn-on-accent: #07121a;
  --syn-accent-soft: rgb(128 223 239 / 10%);
  --syn-frame: #34576c;
}

/* Override one nested region without affecting the rest of the site. */
.my-warning-panel {
  --syn-surface: #1b232d;
  --syn-warning: #ffe2aa;
}
```

Important: `--syn-accent` is the most visible token, but `--syn-on-accent`
is the contrasting **foreground on primary buttons**. Change both when
necessary. Verify 4.5:1 contrast for body text and 3:1 for essential non-text
graphics; don't assume arbitrary overrides remain accessible.

Primary-button hover backgrounds default to the unchanged accent. On hover,
the border switches to the contrasting foreground for a visible affordance.
To customize the hover fill, set `--syn-primary-hover-bg` on the desired
theme/root and test its contrast with `--syn-on-accent` in both rest and hover
states. Syntyr does not automatically invent a contrast-safe hover color.

Use `.syn-panel--raised` for opt-in elevation. The `.syn-title`/`.syn-display`
and `.syn-section-heading` roles use native `text-wrap: balance` when
supported; unsupported browsers fall back to ordinary line wrapping.
Syntyr leaves platform font smoothing untouched.

Useful tokens:

| Token | Description |
| --- | --- |
| `--syn-bg` | Main background |
| `--syn-surface`, `--syn-surface-hi` | Cards and controls |
| `--syn-text`, `--syn-muted` | Main and secondary text |
| `--syn-accent`, `--syn-on-accent`, `--syn-accent-soft` | Brand accent, its foreground, soft fill |
| `--syn-frame`, `--syn-danger`, `--syn-success`, `--syn-warning` | Borders and status |
| `--syn-font`, `--syn-mono`, `--syn-font-ui`, `--syn-font-display` | Body, technical, control, and display typography |
| `--syn-type-xs`, `--syn-type-sm`, `--syn-type-base` | Typography sizes |
| `--syn-surface-recessed`, `--syn-surface-raised`, `--syn-border-subtle` | Derived surfaces and quiet separators |
| `--syn-text-subtle`, `--syn-border-default`, `--syn-border-hover`, `--syn-border-focus`, `--syn-focus-ring` | Semantic text, borders, and focus |
| `--syn-surface-interactive`, `--syn-surface-hover`, `--syn-surface-pressed` | Theme-aware interactive control states |
| `--syn-primary-hover-bg` | Primary-button hover background; defaults to the accent so foreground contrast does not regress |
| `--syn-shadow-sm`, `--syn-shadow-raised`, `--syn-shadow-overlay` | Semantic elevation (small surfaces, raised panels, floating overlays) |
| `--syn-type-display`, `--syn-type-section`, `--syn-type-heading`, `--syn-type-body`, `--syn-leading-body`, `--syn-tracking-display` | Composable typography roles |
| `--syn-row-padding-block`, `--syn-card-padding`, `--syn-control-padding-block` | Density-aware spacing |
| `--syn-space-1` … `--syn-space-5` | Spacing |
| `--syn-cut`, `--syn-radius`, `--syn-control-height` | Geometry |
| `--syn-duration-fast`, `--syn-duration-standard`, `--syn-ease`, `--syn-ease-enter` | Optional transitions |
| `--syn-panel-padding`, `--syn-panel-radius`, `--syn-panel-border-width` | Local panel customization |
| `--syn-button-padding-inline`, `--syn-button-border-width` | Local button customization |

## Design-system editor: customize and export

The [browser theme editor](theme-editor.html) now previews the actual seven
Syntyr palettes while you customize semantic background, surface, foreground,
secondary text, border and accent tokens. Set body text size, corner radius,
component density and visual intensity independently.

- **Copy CSS** to generate an unlayered override targeting both root and nested
  `data-syn-theme` regions. Load it after `syntyr.core.css`, and copy the
  selected `data-syn-density` and `data-syn-intensity` attributes onto the
  appropriate HTML region.
- **Copy JSON** creates a Syntyr-specific preset with theme, density, intensity
  and CSS token values. It is **not** a DTCG or Figma interchange format.
- The editor checks normal body text against page background and primary button
  text against its fill at **4.5:1**. This does not verify secondary text,
  every semantic status, hover/focus, non-text contrast or WCAG conformance.
- All controls and copy interactions live exclusively in documentation JS.
  Applications using Syntyr remain CSS-only.

The [component playground](playground.html) also supports fixed 375/768/1280px
preview widths (with horizontal scrolling when the editor panel is narrower),
density presets, and *preview-only* disabled/invalid native control states.
The **Copy setup + HTML** action emits HTML and a stylesheet link with your
chosen theme and density, but never serializes simulated control states.
Adjust the stylesheet path to match your deployment.

## 3. Independent visual intensity

Use `data-syn-intensity="quiet"` on a dense dashboard, the default `standard` for a balanced presentation, or `cinematic` on a limited hero region. Intensity controls only opt-in decoration in `syntyr.effects.css`; it does not alter palette, density, typography or control contrast. Nested regions can override an inherited value. See the [visual-intensity guide](visual-intensity.md) and [live comparison](../examples/intensity-geometry.html).

## 4. CSS component mode versus native semantic mode

Scoped component classes: `.syn-panel`, `.syn-button`, `.syn-table`.
They work with only `syntyr.core.css`.

For classless HTML resembling Pico CSS, load **both** files and opt in:

```html
<link rel="stylesheet" href="/css/syntyr.core.css">
<link rel="stylesheet" href="/css/syntyr.semantic.css">
<div class="syn-root syn-semantic" data-syn-theme="noir">
  <article>
    <h2>Operator access</h2>
    <label for="operator">Operator ID</label>
    <input id="operator" name="operator" required>
    <button>Continue</button>
  </article>
</div>
```

Unclassed controls outside `.syn-semantic` are not restyled.
If you need glows or static grid effects, add `syntyr.effects.css`
as a third optional file. Don't load `syntyr.all.css` **and** its
individual component files at the same time.

## 5. Responsive applications and accessibility

Use `.syn-region` as the parent for container-responsive patterns such as
`.syn-stats`, `.syn-split`, `.syn-pricing`; width comes from the container,
not the whole viewport. Use `.syn-page` only for a full-page experience.

Syntyr also honors `prefers-contrast: more` by strengthening tokenized borders
and suppressing nonessential decorative effects, including inside nested
themes and explicit cinematic-intensity regions. This is a preference-aware
visual enhancement, not a substitute for actual high-contrast/forced-colors,
zoom, and screen-reader testing.

Syntyr honors `prefers-reduced-motion: reduce`. Theme overrides
must not remove focus outlines, fake disabled states, or communicate state
only through color. Test keyboard navigation, 200%/400% browser zoom,
high-contrast/forced-colors, and relevant screen readers in the target app.

**No runtime JavaScript is required for styling.** Search, authentication,
live data, and server-side form handling are intentionally application
responsibilities; optional advanced widgets are outside the CSS core.

## Seven theme palettes (unreleased alpha.5 candidate)

The published alpha.4 tag offers Grid, Noir and Studio. This candidate adds Industrial, Terminal, Corporate and Minimal. Use the same HTML and change only the theme attribute:

- `data-syn-theme="grid"`
- `data-syn-theme="noir"`
- `data-syn-theme="studio"`
- `data-syn-theme="industrial"`
- `data-syn-theme="terminal"`
- `data-syn-theme="corporate"`
- `data-syn-theme="minimal"`

To use finite opt-in layout utilities, load `syntyr.utilities.css` after `syntyr.core.css` (or use the all bundle). Utilities include `.syn-u-flex`, `.syn-u-grid`, `.syn-u-between`, spacing helpers and a visually hidden helper. No compiler or runtime JavaScript is required.


## System palette, no JavaScript (experimental)

`data-syn-theme="auto"` on `.syn-root` or a nested themed region
uses Studio colors for light system preference and Grid colors for dark
system preference. It relies on native `color-scheme: light dark` and
CSS `light-dark()`, supported by current Chromium, Firefox and WebKit.
Older engines that lack `light-dark()` retain the inherited/default
palette. No preference is stored or read by Syntyr.

```html
<body class="syn-root syn-page" data-syn-theme="auto">
  <section data-syn-theme="noir">This remains Noir regardless of OS theme.</section>
</body>
```

Explicit palettes are unchanged. For sensitive applications, test nested
themes, native form controls, and contrast in both OS preference modes.
## Typography, density, and quiet surfaces

Control and navigation text uses `--syn-font-ui`. Display headings use
`--syn-font-display`, while code and CLI regions retain `--syn-mono`.
Grid and Terminal choose monospace UI explicitly; Studio is the implicit default; light themes and Noir use
system sans-serif controls. Replace the font variables if a product has its
own typeface, without introducing required external fonts.

The `--syn-surface-recessed`, `--syn-surface-raised`, and
`--syn-border-subtle` tokens derive from the active theme palette and
recompute in nested themed regions. Strong borders remain available for
focus and essential controls. Avoid treating subtle separators as a substitute
for accessible non-text contrast where boundaries are required.

To opt into compact operational layouts:

```html
<section class="syn-root" data-syn-theme="minimal" data-syn-density="compact">
  <table class="syn-table"><!-- ... semantic rows ... --></table>
</section>
```

Compact density reduces padding and control heights, **not font sizes**.
Use the default density for content-heavy business pages or touch-first forms.
For an optional editorial hero, combine `syn-site-heading--editorial` from
`syntyr.recipes.css` with `syn-gradient-wash` from `syntyr.effects.css`.
Both use local fonts and static CSS without runtime dependencies.


## Semantic roles, states, and content rhythm

Use `.syn-display` (also available as `.syn-title`), `.syn-section-heading` for section titles, `.syn-heading` for card headings,
`.syn-body`, `.syn-text-support`, and the opt-in `.syn-prose` content
container. Typography roles inherit theme fonts and allow applications to
override type scale without rewriting individual component selectors.

Semantic aliases are derived separately in each nested `data-syn-theme`
scope, so a Grid panel inside a Studio page retains Grid's own contrast and
control appearance. To override theme colors, prefer changing the primitive
palette (`--syn-accent`, `--syn-frame`, `--syn-surface`, etc.). Override a
semantic role only when the change is intentional and contrast has been checked.

Native `disabled`, `aria-invalid`, `aria-pressed`, `aria-busy`,
`:focus-visible`, and `:active` styles are presentation only. `aria-busy`
does not stop clicks or run a task. Use actual `disabled` for disabled form
controls; `aria-disabled` requires the application to suppress activation.
For errors, pair `aria-invalid="true"` with an associated error message
(`aria-describedby`); never rely on border color alone.

See [the live design-state example](../examples/design-states.html) for
semantic typography, nested themes, compact layout and form states.
