# Advanced frames and terminal presentation

These are original, MIT-licensed SYNTYR CSS components. They do not replicate entertainment franchise assets or require JavaScript.

## Installation

Load only the modules you need. Advanced geometry is separate so ordinary pages do not load its CSS:

```html
<link rel="stylesheet" href="/css/syntyr.core.css">
<link rel="stylesheet" href="/css/syntyr.geometry.css">
<!-- Only for the optional application/terminal layouts: -->
<link rel="stylesheet" href="/css/syntyr.recipes.css">
```

The all-in-one stylesheet includes geometry and recipes already. Do not load it alongside the individual modules.

## Seven independent frame profiles

Use `.syn-frame` with exactly **one** shape modifier. These can decorate an article, section, or any normal element. The surrounding content stays semantic:

```html
<section class="syn-root" data-syn-theme="grid">
  <article class="syn-panel syn-frame syn-frame--bevel" style="--syn-frame-cut: 1.5rem">
    <h2>Monitoring</h2>
    <p>All systems operational.</p>
    <a href="/status">See status</a>
  </article>
</section>
```

| Class | Purpose |
| --- | --- |
| `.syn-frame--bevel` | Diagonal cut on all four corners |
| `.syn-frame--notch` | Asymmetric top-right and bottom-left cuts |
| `.syn-frame--step` | Square stepped cuts on top-right and bottom-left |
| `.syn-frame--facet` | Diagonal cuts on top-left and bottom-right |
| `.syn-frame--bracket` | Four HUD-style L-shaped corner markers |
| `.syn-frame--inset` | Nested technical border |
| `.syn-frame--circuit` | Subtle corner trace bars |

These style variables are inherited and can be overridden on a specific panel:

- `--syn-frame-cut`: default `1rem`; fallback size for all cuts (backwards-compatible)
- `--syn-frame-cut-tl`, `--syn-frame-cut-tr`, `--syn-frame-cut-br`, `--syn-frame-cut-bl`: optional **Per-corner** overrides; use explicit CSS lengths
- `--syn-frame-stroke`: default `1px`; border thickness for clipped shapes
- `--syn-frame-fill`: default `var(--syn-surface)`; interior background
- `--syn-frame-outline`: default `var(--syn-frame-strong)`; solid border fallback
- `--syn-frame-border-paint`: optional color or CSS gradient for the complete border
- `--syn-frame-inlay-paint`: optional CSS gradient layered over the inner fill; use a translucent wash

The clipped shapes use individually corrected inner polygons to keep diagonal borders closer to their specified perpendicular stroke width. Square steps use the same step size for both polygons. These are **painted frames**, not clipped interactive hit regions; the native element remains a rectangle for layout and focus. Avoid cut sizes larger than the element can accommodate, or strokes as large as the cuts.

### Asymmetric geometry and gradient border example

```html
<link rel="stylesheet" href="/css/syntyr.core.css">
<link rel="stylesheet" href="/css/syntyr.geometry.css">
<section class="syn-root" data-syn-theme="grid">
  <article class="syn-panel syn-frame syn-frame--facet" style="
    --syn-frame-cut-tl: 1.5rem; --syn-frame-cut-br: .75rem;
    --syn-frame-stroke: 2px;
    --syn-frame-border-paint: linear-gradient(120deg, var(--syn-accent), var(--syn-frame-strong));
    --syn-frame-inlay-paint: linear-gradient(145deg, rgb(118 231 247 / 7%), transparent 65%);
  ">
    <h2>Signal analysis</h2>
    <p>Decorative geometry never replaces semantic content.</p>
  </article>
</section>
```

For the interactive **geometry editor**, open [Syntyr's component playground](playground.html#geometry-title). The playground JavaScript is documentation-only; consumers load only CSS. Existing bevel/notch markup retains its original appearance unless new controls are set, apart from the improved diagonal stroke geometry.

**Composition:** Advanced frame profiles own both pseudo-elements of the host node. They now reset the prior layer's corner dimensions and clip-path, so `.syn-panel--cut` can be used on the same element: the selected frame shape **supersedes** its simpler corner decoration. Add `.syn-frame--accent` for a stronger outline without adding any pseudo-elements. Do not combine multiple shape variants. The older `.syn-frame--precision` also owns `::before`; nest those two treatments if both accents must remain visible. The clipped border geometry does not depend on matching the parent background, but background gradients on the host can bleed into cut corners; prefer solid `--syn-frame-fill` or an inner element.

In forced-colors mode, decorative pseudo-elements disappear and a visible native border and Canvas background take over. Frames should not be the only way you communicate operational state.

## Browser terminal

Load `syntyr.recipes.css` for the existing `.syn-terminal` base and the additional presentation classes:

| Class | Role |
| --- | --- |
| `.syn-terminal-bar`, `.syn-terminal-title`, `.syn-terminal-dots` | Window chrome; mark visual-only dots `aria-hidden="true"` |
| `.syn-terminal-body`, `.syn-terminal-line`, `.syn-terminal-output` | Readable lines, wrapped output |
| `.syn-terminal-command`, `.syn-terminal-path`, `.syn-terminal-prompt` | CLI command anatomy |
| `.syn-terminal-success`, `.syn-terminal-warning`, `.syn-terminal-error` | Colored output (with textual status) |
| `.syn-terminal-meta`, `.syn-terminal-muted` | Secondary readouts |
| `.syn-terminal-cursor` | Static decorative caret; hide from accessibility APIs |

The terminal is **not** a shell emulator. It performs no input capture or commands. Applications implement real interaction separately; native CLI applications use `terminal/palettes.json` rather than browser CSS.

## Table and button behavior

The existing `.syn-table-emphasis` class highlights whichever cell you choose: there is no implicit highlight on the last column. Use `.syn-cell--numeric` on monetary or numeric cells for right-aligned tabular numbers.

The native HTML `disabled` attribute blocks button activation. The ARIA `aria-disabled="true"` attribute only communicates a disabled state; it **does not block activation**. Application/server code must enforce disabled behavior. CSS alone cannot guarantee it. For a disabled action that must remain discoverable to keyboard users, preserve focus and handle input appropriately.

## Validation

```sh
python3 scripts/build.py
python3 scripts/build.py --check
python3 -m unittest discover -s tests -v
python3 tests/browser_matrix.py --browsers chromium firefox webkit
```

See [the frame + terminal example](../examples/geometry-terminal.html). Browser checks are developer-only; the distributed CSS still has zero runtime JS or dependencies.
