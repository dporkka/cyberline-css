# Optional Syntyr animation library

`syntyr.animate.mjs` is an **opt-in, dependency-free ES module** for
application-triggered motion. It delegates timing and compositing to the native
**Web Animations API** and viewport detection to **IntersectionObserver**.
There are no imports, startup side effects, global listeners, background timers,
framework adapters, CSS resets, or changes to core Syntyr.

Use the CSS-only `syntyr.motion.css` for static declarative effects. Load this
JavaScript module only when you actually need to trigger animations in code or
observe viewport entry; either add-on can be used without the other.

## Install and invoke

Copy `dist/syntyr.animate.mjs` and, if desired, `dist/syntyr.core.css` to
your own static directory. The module needs no bundler and runs in evergreen
browsers that support ES modules.

```html
<link rel="stylesheet" href="/css/syntyr.core.css">
<main class="syn-root">
  <button id="show" type="button">Animate card</button>
  <article id="card">Card content stays visible without JavaScript.</article>
</main>
<script type="module" src="/js/animation-demo.mjs"></script>
```

```js
// /js/animation-demo.mjs
import { animate, stagger, observeReveals } from '/js/syntyr.animate.mjs';

document.querySelector('#show')?.addEventListener('click', () => {
  const card = document.querySelector('#card');
  animate(card, 'enter', { direction: 'up', duration: 280 });
});

stagger(document.querySelectorAll('.syn-root .card'), 'fade', {
  interval: 75, delay: 0,
});

// This does nothing until invoked, and only animates opted-in descendants.
const disconnect = observeReveals(document);
// Call disconnect() when unmounting the page/region.
```

When the experimental `@syntyr/css` npm package is published, the module
also has a dedicated typed subpath:

```js
import { animate } from '@syntyr/css/animate';
```

That subpath exposes only the optional animation code and matching TypeScript
declarations. The default package import remains the CSS entrypoint.

## Minimal API

| Export | Purpose | Result |
| --- | --- | --- |
| `animate(element, preset = 'enter', options?)` | Animate one element on demand | Native `Animation` or `null` |
| `stagger(iterable, preset = 'enter', options?)` | Animate each element with an incremental WAAPI delay | Array of animations or `null` entries |
| `observeReveals(root = document)` | Observe `.syn-root [data-syn-reveal]` once per element | `disconnect()` cleanup function |

Presets are `fade` (opacity), `enter` (opacity plus individual `translate`),
and `scale` (opacity plus individual `scale`). There is no infinite or
autoplay animation preset. `enter` supports `direction: 'up' | 'down' |
'left' | 'right'` and `distance: '.75rem'`. Use `scaleFrom` to override the
initial scale.

All presets accept `duration` and `delay` in milliseconds and `easing`
as a CSS timing function. `stagger` additionally accepts `interval` in
milliseconds. The module reads existing CSS custom properties when options
are omitted: `--syn-motion-duration` (220ms default),
`--syn-motion-stagger` (65ms), `--syn-motion-distance` (.75rem),
`--syn-motion-scale-from` (.96), and `--syn-ease-out`
(`cubic-bezier(.22, 1, .36, 1)`). These defaults also work without a Syntyr
stylesheet, and per-element CSS tokens can override them.

Unknown presets and invalid directions throw `TypeError`; missing target,
missing Web Animations API, or a reduced-motion preference return `null`
without modifying the DOM. Prefer `animation?.cancel()` for interruption and
`animation?.finished` when coordinating an actual transition (cancellation
rejects its promise). Animation properties are released at the end rather
than persisting a hidden or transformed element.

## Viewport reveals

```html
<section class="syn-root">
  <h2>Visible with CSS alone</h2>
  <p data-syn-reveal="enter">Animate on first viewport entry.</p>
  <p data-syn-reveal="fade">Fade when first seen.</p>
</section>
```

```js
import { observeReveals } from '/js/syntyr.animate.mjs';
const disconnect = observeReveals(document);
```

No `IntersectionObserver` is created automatically; call `observeReveals`
after rendering the relevant HTML fragment. It observes only descendants of
`.syn-root` with a `data-syn-reveal` attribute, runs each animation once,
and does **not** add `opacity: 0` to page content before JavaScript starts.
A region can be re-scanned after HTMX/Datastar/React renders new nodes.
The root argument limits the query, and the return function disconnects it.
There is no `MutationObserver` or automatic event interception.

## Accessibility and performance

- `prefers-reduced-motion: reduce` takes precedence over all presets and
  custom durations. Reduced-motion users always get visible, immediate content;
  if that preference changes while observing, animation is checked again.
- Content is never hidden while waiting for JavaScript, scroll observation,
  or native feature detection. Effects do not replace semantic HTML, focus
  management, ARIA announcements, or actual state-change notifications.
- Keyframes use composited `opacity`, `translate`, and `scale` rather than
  layout dimensions. Avoid animating essential text and high-density data,
  where fading can temporarily reduce readability. An element with custom
  individual transform properties may need a wrapper for composition.
- The module uses one-shot `fill: 'none'` and `iterations: 1`, so focus and
  disabled states cannot remain overridden by a completed animation.
- For layout changes, prefer native View Transitions where available. For
  interactive scrubbing and complex timelines, use a specialized animation
  engine *outside* Syntyr instead of expanding this low-level module.

## Verification

```sh
node --test tests/animate.test.mjs
python3 scripts/build.py --check
python3 -m unittest discover -s tests -v
```

Node is for the optional JavaScript behavior tests, **not** for building
Syntyr or using the CSS library. The production JS is copied byte-for-byte
by Syntyr's existing Python build, allowing deterministic release checks.


## Website block effects (CSS only)

Load the optional `syntyr.motion.css` stylesheet **alongside core**. These
effects can be applied to existing Syntyr Blocks, sections, React-rendered
markup, and CMS templates. No JavaScript, hydration, observer setup, or new
framework is required. This section describes the **unreleased alpha.5
candidate**, not the published alpha.4 assets.

```html
<link rel="stylesheet" href="/css/syntyr.core.css">
<link rel="stylesheet" href="/css/syntyr.motion.css">

<section class="syn-root syn-region" aria-labelledby="features-heading">
  <h2 id="features-heading" data-syn-scroll="rise">Built for clarity</h2>
  <div class="syn-grid">
    <article class="syn-panel" data-syn-scroll="fade">Feature one</article>
    <article class="syn-panel" data-syn-scroll="slide-left">Feature two</article>
    <article class="syn-panel" data-syn-scroll="zoom">Feature three</article>
    <article class="syn-panel" data-syn-scroll="slide-right">Feature four</article>
  </div>
</section>
```

`data-syn-scroll` accepts `fade`, `rise`, `slide-left`,
`slide-right`, or `zoom`. Add it to a short block or an individual
heading/card. Native CSS view timelines link animation progress to scroll
position, with short blocks completing when they have fully entered the viewport,
without JavaScript scroll handlers. Override
`--syn-block-reveal-distance` (default `1.5rem`) or
`--syn-block-reveal-scale` (default `.94`) per element.
Avoid scroll-linked opacity on long-form text or content essential to
understanding the page.

### Image parallax blocks

Apply `data-syn-parallax` to a section with a natural or explicit height.
Include one decorative media layer as a **direct child** marked
`data-syn-parallax-layer`, plus a foreground `data-syn-parallax-content`.

```html
<section class="syn-root syn-region" data-syn-parallax
         style="min-block-size: 26rem; --syn-parallax-travel: 2rem"
         aria-labelledby="parallax-title">
  <img data-syn-parallax-layer src="/images/landscape.webp"
       alt="" width="1600" height="900" loading="lazy">
  <div class="syn-site-hero" data-syn-parallax-content>
    <h2 id="parallax-title">A more engaging hero</h2>
    <p>Important content stays in normal document flow.</p>
    <a class="syn-button syn-button--primary" href="/start">Explore</a>
  </div>
</section>
```

Media is oversized and clipped inside its section. The parent defines a
native view timeline, and the media moves over its visible scroll range.
Use `--syn-parallax-travel` (default `2.5rem` each way) to keep movement
subtle. Make sure foreground text stays readable against the image; add
an overlay if needed. The layer should never contain essential content
or controls. When motion is reduced or view timelines are unsupported,
the image is **static** and all foreground content remains visible.
Avoid `background-attachment: fixed` and JavaScript scroll handlers.

### Media hover zoom and existing hover lift

```html
<a class="syn-root syn-panel" style="display: block" href="/portfolio/project" data-syn-hover="zoom">
  <img src="/images/project.webp" alt="Project preview"
       width="640" height="420" data-syn-hover-media>
  <span>Explore the project</span>
</a>
```

Use `data-syn-hover="zoom"` on an image block and
`data-syn-hover-media` on its image. Hover or keyboard focus-within
scales only the media by `--syn-hover-zoom` (default `1.06`) on
fine-pointer devices. For cards, reuse the existing
`syn-surface--lift` from `syntyr.recipes.css` instead of another
hover-lift class. You can use CSS-only scroll effects and static
Syntyr effects together, but check contrast and visual distraction.

**Fallback and accessibility:** Unsupported browsers simply show the
static blocks; no baseline CSS hides content. All new scroll, parallax,
and hover motion is disabled by `prefers-reduced-motion: reduce`.
The module never intercepts input, alters semantics, starts a timer, or
ships an animation dependency. Existing `data-syn-reveal` belongs to
the separate optional JavaScript `observeReveals()` API; it does not
control CSS-only `data-syn-scroll`.


### Animated gradient wash (composable CSS)

Use the existing static `syn-gradient-wash` from `syntyr.effects.css`.
The optional `syntyr.motion.css` adds a decorative, slowly drifting
gradient layer when `data-syn-gradient="drift"` is present. The background
remains static if motion is reduced or unsupported, and all content remains
visible. The animated layer never accepts pointer events.

```html
<link rel="stylesheet" href="/css/syntyr.core.css">
<link rel="stylesheet" href="/css/syntyr.effects.css">
<link rel="stylesheet" href="/css/syntyr.motion.css">

<section class="syn-root syn-gradient-wash" data-syn-gradient="drift"
         style="--syn-gradient-drift-duration: 16s"
         aria-labelledby="gradient-title">
  <div data-syn-gradient-content class="syn-site-hero">
    <h2 id="gradient-title">An atmospheric landing page</h2>
    <p>The content stays stationary and remains readable.</p>
  </div>
</section>
```

Keep the `data-syn-gradient-content` wrapper as a direct child for the
foreground stacking order. The animation moves only a decorative pseudo-element
with a composited `translate`, rather than repainting the entire gradient
on every frame. Use modest sections and inspect contrast against actual
photography or themes. Do not mix `data-syn-gradient` and `data-syn-parallax`
on the same element; instead nest separate wrappers.

### Text accents (no splitting or JavaScript)

```html
<section class="syn-root" aria-labelledby="text-effects-title">
  <h2 id="text-effects-title" data-syn-text="underline">
    A headline with an animated underline
  </h2>
  <p>Supporting information stays completely static.</p>
  <p class="syn-heading" data-syn-text="glint">
    A restrained shifting headline accent
  </p>
</section>
```

`data-syn-text="underline"` uses a native CSS view timeline to
transition underline color as a short heading enters. Without view timelines,
the accent underline is **static** and visible. It preserves natural line
wrapping, selectable text, and the document's accessible name.

`data-syn-text="glint"` animates a text-clipped theme gradient, when
`background-clip: text` is supported; set
`--syn-text-glint-duration` (default `9s`). Reduced motion or increased
contrast leaves the original solid text color. Forced-colors mode also
restores a solid system text color. Do not apply shifting text gradients to
essential text, body paragraphs, form labels, or critical navigation.
Check the foreground contrast in all custom themes: an animated accent
is decorative and is not guaranteed to preserve every arbitrary token
combination's contrast.

The two effects are independent of the optional JavaScript animation
companion and do not add timers, DOM cloning, inaccessible character
splitting, or component variants. They are **alpha.5 source-candidate APIs**
until included in a published Syntyr version.
