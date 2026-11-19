# Syntyr Viz: optional, renderer-neutral charts

`syntyr.viz.css` is an **optional CSS-only presentation module**. It styles
charts and small, server-renderable data visualizations in all seven Syntyr
themes. It does not compute chart geometry, ingest data, perform interactions,
supply a JavaScript runtime, or require a frontend framework.

```html
<link rel="stylesheet" href="/css/syntyr.core.css">
<link rel="stylesheet" href="/css/syntyr.viz.css">
```

Alternatively load `syntyr.all.css` by itself. Do **not** load the all-in-one
bundle together with component modules: it already includes Viz. Core, the
convenience `syntyr.css` bundle, and the optional recipes stylesheet do not
contain Viz.

## Chart token API

All visualization colors are CSS variables. Their defaults recompute on
`.syn-root` and nested `[data-syn-theme]` containers.

| Token | Purpose |
| --- | --- |
| `--syn-chart-1` through `--syn-chart-4` | Data series colors, derived from theme accent, secondary accent, success, warning |
| `--syn-chart-grid` | Grid and chart cell border color |
| `--syn-chart-axis` | Axis labels and marks |
| `--syn-chart-tooltip-bg` | Noninteractive tooltip/popup surface |

Override the tokens on a specific themed chart or a nested dashboard area.
Always check contrast and series distinguishability after palette changes.
Color is not an adequate standalone representation of categories or status.
Use text, patterns, line types, legends and accessible values.

```html
<section class="syn-root" data-syn-theme="studio">
  <figure class="syn-chart" style="--syn-chart-1: #2458c6;">
    <figcaption class="syn-chart-title">Weekly signups</figcaption>
    <!-- Supply SVG, a server-side renderer, or a client chart here. -->
  </figure>
</section>
```

## Four microvisualizations

### 1. SVG sparkline

`syn-viz-sparkline` styles a precomputed inline SVG. Syntyr does not calculate
points. For a time series, the HTML generator computes the polyline/area and
includes an accessible name. Use SVG `<title>` or `aria-label` and make the
numerical values inspectable in a nearby table or list.

```html
<figure class="syn-chart">
  <figcaption class="syn-chart-title">Revenue, Jan–Jun</figcaption>
  <svg class="syn-viz-sparkline" viewBox="0 0 240 60" role="img"
       aria-label="Revenue increased from 20 to 54 thousand dollars">
    <polyline class="syn-viz-sparkline-path"
              points="2,54 49,44 96,46 143,24 190,20 238,5"/>
  </svg>
  <table class="syn-table">
    <caption>Revenue by month, thousands of dollars</caption>
    <thead><tr><th scope="col">Month</th><th scope="col">Revenue</th></tr></thead>
    <tbody><tr><th scope="row">Jan</th><td>20</td></tr>
           <tr><th scope="row">Jun</th><td>54</td></tr></tbody>
  </table>
</figure>
```

### 2. Ranked bar list

Use real text for values; the bar widths are visual duplicates of the
values. `--syn-viz-value` is a number on a 0–100 scale, not a percentage
string. The CSS clamps it into that interval. **Validate and escape values
at the rendering boundary.** This is presentation only, not a semantic
`progress` or `meter` control.

```html
<ol class="syn-viz-bars" aria-label="Revenue mix">
  <li class="syn-viz-bar">
    <div class="syn-viz-bar-label">
      <span>Direct</span><data value="72">72%</data>
    </div>
    <div class="syn-viz-bar-track" aria-hidden="true">
      <span class="syn-viz-bar-fill" style="--syn-viz-value: 72"></span>
    </div>
  </li>
</ol>
```

### 3. Status tracker

This represents a series of discrete periods, not a live network monitor.
Each segment needs **real semantic text** even when a screen reader reads
its visual color differently.

```html
<ol class="syn-viz-tracker" aria-label="Past three days">
  <li data-syn-state="healthy"><span class="syn-viz-sr-only">Mon: Healthy</span></li>
  <li data-syn-state="degraded"><span class="syn-viz-sr-only">Tue: Degraded</span></li>
  <li data-syn-state="down"><span class="syn-viz-sr-only">Wed: Down</span></li>
</ol>
<p>Healthy, degraded and down states appear in chronological order.</p>
```

Supported state values are `healthy`, `degraded`, `down`, and `unknown`.
Do not depend on color alone to convey a critical state.

### 4. Activity heatmap

The heatmap is a compact grid. Set `--syn-viz-columns` to the number of
columns; each cell uses one of five levels, `0` through `4`.
The default is twelve columns. For small screens, the grid scrolls rather
than reducing each cell below its minimum width.

```html
<div class="syn-viz-heatmap" style="--syn-viz-columns: 3;"
     role="group" aria-label="Three days of activity">
  <span class="syn-viz-cell" data-syn-level="0">
    <span class="syn-viz-sr-only">Mon: no activity</span>
  </span>
  <span class="syn-viz-cell" data-syn-level="2">
    <span class="syn-viz-sr-only">Tue: medium activity</span>
  </span>
  <span class="syn-viz-cell" data-syn-level="4">
    <span class="syn-viz-sr-only">Wed: very high activity</span>
  </span>
</div>
```

## Generic chart styling and integrations

`syn-chart`, `syn-chart-title`, `syn-chart-grid`, `syn-chart-axis`,
`syn-chart-legend`, `syn-chart-legend-item`, `syn-chart-key` and
`syn-chart-tooltip` are **styling hooks only**. They never calculate axes,
create a legend, open a tooltip, or attach event handlers.

- **SVG/server-side:** generate SVG paths and visible, textual value tables
  with Go, Rust, HTMX, Python or any HTML renderer. All functionality remains
  available with no JavaScript.
- **Recharts:** set `className="syn-chart"` on your container and pass
  `var(--syn-chart-1)` etc. into the renderer's stroke/fill props. Use
  native Recharts tooltips/accessibility rather than expecting CSS to
  provide interactions.
- **ECharts:** ECharts needs resolved color strings in its JavaScript
  options, not literal CSS `var()` strings (Canvas cannot interpret them).
  Resolve scoped computed custom properties **inside an optional application
  adapter** and update them if the theme changes. Syntyr does not ship that
  adapter or make it a dependency.

## Accessibility and performance

Keep a visible title, visible value labels where possible, and a navigable
HTML table, list, or accessible summary for the underlying values. Verify
screen reader announcements, high-contrast/forced-colors mode, keyboard
navigation, and 200–400% zoom. Decorative SVG should be `aria-hidden` only
when equivalent numerical information exists elsewhere; meaningful SVG must
have a readable accessible name. Labels and patterns must distinguish status
independently of hue. The CSS includes forced-colors distinctions; test them
on the target browser rather than assuming automatic compliance.

All CSS is scoped under `.syn-root` and deliberately has no network assets,
fonts, animations, script tags or client-side data transforms. Syntyr Viz does
not impose arbitrary CSS size budgets. Use the library's existing deterministic
build and performance tests and measure real browser behavior.

Try the [seven-theme static Viz gallery](../examples/viz.html).
