# Performance validation protocol

For the optional reproducible five-framework comparison harness, see
[framework performance benchmark](framework-performance.md). It does not
establish a named-framework ranking until visual parity is independently
validated.

SYNTYR CSS is small and has no required runtime JavaScript, but neither
property proves that its pages render faster than Tailwind, UnoCSS, Pico, or
hand-written CSS. Do not publish cross-framework speed rankings without
running the same test workload and reporting the environment.

## Reproducible CSS payload baseline

At the November 14, 2026 unreleased validation candidate, run:

```sh
python3 scripts/build.py --check
```

The November 14 snapshot reported **4,590 bytes gzip** for
`dist/syntyr.core.css` (20,767 raw bytes) and **7,649 bytes gzip** for
`dist/syntyr.all.css` (38,637 raw bytes). Values can change as the
source evolves. These are Python gzip measurements, **not** HTTP transfer
sizes, Brotli sizes, browser stylesheet parse times, or comparisons to
other frameworks. There are **no arbitrary CSS size release gates**;
inspect deltas and actual page rendering instead.

## Fair comparative benchmark

For Syntyr, Tailwind v4, and plain CSS, create separate pages with identical:

1. Semantic HTML, content, assets, typeface, colors, spacing and visual layout.
2. A representative dashboard (tables, forms, navigation, cards), plus a
   marketing page, at 320 px, 390 px and 1280 px.
3. Interaction semantics and JavaScript budget: no runtime JS unless identical
   application interactions require it in every variant.
4. Network environment, server caching policy, browser version, hardware,
   cold/warm cache settings and performance throttling.

Record the framework and compiler versions, source and build commands, and
exact CSS files transferred. Tailwind's generator is build-time tooling and
must not be counted as browser runtime JavaScript.

Collect at least 10 cold-cache runs per variant; report median and p75,
run-to-run variance, and device/connection details. Measure:

- Compressed CSS transferred (Brotli/gzip), CSS request count and response time.
- Style calculation, layout, paint, and total scripting time from browser traces.
- LCP, CLS and INP where real interactions can be exercised; avoid inferring
  field INP from a purely static synthetic page.
- Interaction responsiveness, zoom/reflow and forced-colors correctness.
- Page screenshots at matching viewport widths to catch visual tradeoffs.

Use Lighthouse/WebPageTest and browser performance traces; obtain independent
field data where sufficient real-user traffic exists. A faster build or a
smaller CSS file alone does not establish faster end-user rendering.

## Publishing gate

Only make a named-framework performance claim with corresponding raw
measurements, reproducible fixtures, dates, versions, and hardware/network
details. If differences are within measurement noise, report **no meaningful
difference**. Evaluate effects (glow, gradients and clip paths) on low-end
devices separately from core UI styling.

The current release candidate has a **verified size baseline only**; no
cross-framework LCP, INP, paint, or style-recalculation ranking has been
established.
