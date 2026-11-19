# Visual intensity and composable cyberpunk frames

SYNTYR separates **palette** (`data-syn-theme`), **decorative intensity**
(`data-syn-intensity`), **density** (`data-syn-density`) and optional geometry
(`.syn-frame` plus one shape). These are independent controls and do not load
JavaScript, fonts, sprites or third-party assets.

## Choose the right intensity

Use `data-syn-intensity` on `.syn-root` or any descendant element. It is
inherited, so a child can opt into a different intensity without switching
palette. Omitting the attribute is equivalent to `standard`.

| Value | Effects | Good for |
| --- | --- | --- |
| `quiet` | Nearly invisible grids/washes; no visible glow/scanline overlay | Data-heavy SaaS, forms, accessibility-sensitive dashboards |
| `standard` | Existing effect strengths and opt-in behavior (default) | Marketing sites, documentation |
| `cinematic` | Stronger washes, luminous shadows and optional scanlines | Demos, editorial hero sections, limited promotional panels |

Intensity changes **only opt-in decorative effects** from
`syntyr.effects.css`. It does not change status colors, border contrast,
focus rings, typography, form affordances or any theme's underlying palette.
For zero decoration, simply do not load effects.

```html
<link rel="stylesheet" href="/css/syntyr.core.css">
<link rel="stylesheet" href="/css/syntyr.effects.css">
<link rel="stylesheet" href="/css/syntyr.geometry.css">

<main class="syn-root" data-syn-theme="grid" data-syn-intensity="quiet">
  <article class="syn-panel syn-glow">
    <h2>Operational view</h2>
    <p>Quiet default for dense data.</p>
  </article>
  <section data-syn-intensity="cinematic">
    <article class="syn-panel syn-glow syn-frame syn-frame--bevel syn-frame--accent">
      <h2>Featured transmission</h2>
      <p>A localized visual accent without changing colors or density.</p>
    </article>
  </section>
</main>
```

For custom presets, override `--syn-grid-alpha`, `--syn-glow-alpha`,
`--syn-wash-alpha`, `--syn-wash-secondary-alpha`,
`--syn-horizon-alpha`, and `--syn-scanline-alpha` on a region.
Values are percentages used in color interpolation, not animation speed.
Cinematic does **not** animate automatically; use optional motion modules
separately and respect `prefers-reduced-motion`.

## Geometry that composes

The optional `syntyr.geometry.css` stylesheet supports five shapes:
`bevel`, `notch`, `bracket`, `inset` and `circuit`.
Use exactly one shape on `.syn-frame`, optionally adding
`.syn-frame--accent` for a stronger outline (2px accent-colored border).
The geometry layer explicitly resets pseudo-element dimensions and clipping
from earlier CSS layers, so `.syn-panel--cut` on the **same host** is safely
superseded by the selected frame geometry rather than corrupting it.

```html
<article class="syn-panel syn-panel--cut syn-frame syn-frame--notch syn-frame--accent">
  <h2>System status</h2>
  <p>The notch frame takes precedence over the simpler panel cut.</p>
</article>
```

`syn-frame--accent` is an *optional* style modifier, not an additional
shape. Set `--syn-frame-cut`, `--syn-frame-stroke`,
`--syn-frame-fill` or `--syn-frame-outline` on the host to customize
one frame. Avoid combining two shape modifiers.

**Remaining composability boundary:** both `syn-frame` geometry and the
older `syn-frame--precision` recipe own `::before`. Applying both
to the same host still supersedes the precision accent; nest separate
elements when both treatments are needed. Likewise, geometry intentionally
uses a transparent host background so gradients painted on the **host**
may spill into its cut corners. Apply complex host backgrounds on an inner
element, or set `--syn-frame-fill` to a solid value.

## Accessibility and performance

- Always keep readable status text; never communicate errors only by glow or color.
- In forced-colors mode, frames fall back to solid system borders and effects
  suppress nonessential backgrounds.
- Prefer `quiet` for long operational pages; reserve `cinematic` for a few
  deliberate accents. Measure paint and scrolling on actual devices.
- The library core does not require any script. The optional docs theme editor
  can preview intensity but is not shipped as an application dependency.
- Test with 200% and 400% zoom, keyboard input, forced colors and all three
  browser engines before relying on a theme in production.

See [live intensity comparison](../examples/intensity-geometry.html),
[advanced geometry](geometry-terminal.md) and
[theme customization](theme-customization.md).
