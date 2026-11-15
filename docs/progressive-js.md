# Optional progressive JavaScript for Syntyr Viz and Motion

The CSS and HTML are **fully usable without JavaScript**. The two opt-in native
ES modules add only interactions that CSS cannot supply. No package manager,
third-party runtime, global observers, auto-initialization or bundler is required.

| Source / distribution | Responsibility |
| --- | --- |
| `src/js/viz.js` → `dist/syntyr.viz.js` | SVG point tooltips, keyboard arrows/Home/End/Escape, optional crosshair, resize event |
| `src/js/motion.js` → `dist/syntyr.motion.js` | Interruptible Web Animations API entrance, fade and scale effects |

Neither is included inside the CSS files. The maintained Python build copies
ESM source to distribution byte-for-byte; published ZIP and Cloudflare site
include them as individually optional assets. Prefer self-hosting/pinned versions.

## Initialization and cleanup

```html
<link rel="stylesheet" href="/css/syntyr.core.css">
<link rel="stylesheet" href="/css/syntyr.viz.css">
<script type="module">
  import {enhanceViz} from "/js/syntyr.viz.js";
  import {enhanceMotion} from "/js/syntyr.motion.js";

  const root = document.querySelector(".syn-root");
  const viz = enhanceViz(root);
  const motion = enhanceMotion(root);

  // Call after HTMX/Datastar swaps or SPA DOM replacement:
  // viz.refresh();
  // motion.refresh();

  // On route teardown, or before discarding the application root:
  // viz.destroy();
  // motion.destroy();
</script>
```

If only one capability is needed, import only that module. `enhanceViz(root)`
and `enhanceMotion(root)` are individually idempotent: repeated calls on the
same root return the same controller until `destroy()`. Pass the actual
fragment as the root for independently managed fragments, or use
`refresh()` on the existing application root after a swap. No global
`MutationObserver` is installed, and controllers never fetch data.

## SVG point inspection

Provide useful static labels and an inspectable HTML table. Add
`data-syn-viz="points"` to a `syn-chart` container and `data-syn-point`
to the SVG shape of each inspectable sample. Include readable
`data-syn-label` and `data-syn-value` on each point. The enhancement
creates a **visual-only** tooltip; each point retains an accessible
`aria-label` and becomes reachable by keyboard.

```html
<figure class="syn-chart" data-syn-viz="points" data-syn-viz-resize>
  <figcaption class="syn-chart-title">Revenue, Jan–Feb</figcaption>
  <svg viewBox="0 0 120 80" role="group" aria-label="Revenue trend">
    <polyline class="syn-viz-sparkline-path" points="20,60 100,20"/>
    <line data-syn-crosshair hidden aria-hidden="true" y1="0" y2="80"></line>
    <circle data-syn-point data-syn-label="Jan" data-syn-value="$20k"
            aria-label="January: 20 thousand dollars" cx="20" cy="60" r="5"/>
    <circle data-syn-point data-syn-label="Feb" data-syn-value="$42k"
            aria-label="February: 42 thousand dollars" cx="100" cy="20" r="5"/>
  </svg>
  <table class="syn-table">
    <caption>Revenue source data</caption>
    <tbody><tr><th scope="row">Jan</th><td>$20,000</td></tr>
           <tr><th scope="row">Feb</th><td>$42,000</td></tr></tbody>
  </table>
</figure>
```

Arrow keys cycle through the points; Home/End select the first/last; Escape
dismisses the tooltip. Pointer hovering and pressing also activate the nearest
targeted point. The crosshair is optional and uses the SVG point's `cx`
attribute (or `data-syn-x`) in the same SVG coordinate system. Supply the
crosshair's y-coordinates in HTML.

If the chart includes `data-syn-viz-resize`, its controller emits
`syntyr:viz:resize` on that chart with
`event.detail = {width, height}` from `ResizeObserver`. This event is
for application-owned renderers; Syntyr **does not generate new chart geometry**
or change existing data on resize. For a scalable `viewBox` SVG, no observer
or JS layout adjustment is needed.

Every text value is inserted with `textContent`; never interpret untrusted
labels as HTML. All listeners, observer instances, injected tooltip nodes,
and script-added point attributes are removed with `destroy()`.

## Interruptible motion

`data-syn-motion-js="enter"`, `"fade"` or `"scale"` opts in.
The element remains visible before JavaScript initializes and if it fails.
The controller animates matched elements **once** per initialization.
When an application inserts a new fragment, call `motion.refresh()`. To replay
an existing element, call `motion.play(element, "fade")` explicitly.

Motion uses the native Web Animations API. Calling `play` again cancels the
prior active animation on the element. `destroy()` cancels remaining animations.
When the operating system preference changes to `prefers-reduced-motion:
reduce`, active animations are canceled. If reduced motion is already enabled,
no animations start.

No scroll observers, timeline engine, physics simulation, automatic rerenders
or list reordering are included. CSS-native animation remains appropriate for
simple hover effects and one-shot keyframes.

## Production checklist

1. Start with meaningful HTML, an SVG title or accessible label, and a real
   table/list of values. Disable JS to verify functionality.
2. Use stable `data-syn-*` hooks under a `.syn-root`. Never apply this to an
   unrelated page area.
3. Test touch and keyboard focus, screen reader labels, 200%/400% zoom,
   forced-colors, reduced motion and client-side route replacement.
4. When using HTMX, call `refresh()` after swaps and `destroy()` when
   removing the application root.
5. Observe interactions and frame cost in your actual app; the scripts are
   optional and no hard byte-size gate is imposed.

[Try the static + enhanced demonstration](../examples/progressive-js.html).
