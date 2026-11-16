# Optional Syntyr animation library

`syntyr.animate.mjs` is an **opt-in, dependency-free ES module** for
application-triggered motion. It delegates timing and compositing to the native
**Web Animations API** and viewport detection to **IntersectionObserver**.
There are no imports, startup side effects, persistent listeners, background
timers, framework adapters, CSS resets, or mandatory changes to core Syntyr.
While native animations are running, one temporary media-query listener
cancels them if the user switches to reduced motion.

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
import { animate, exit, stagger, observeReveals } from '/js/syntyr.animate.mjs';

document.querySelector('#show')?.addEventListener('click', () => {
  const card = document.querySelector('#card');
  animate(card, 'enter', { direction: 'up', duration: 280 });
});

stagger(document.querySelectorAll('.syn-root .card'), 'fade', {
  interval: 75, delay: 0,
});

// This does nothing until invoked, and only animates opted-in descendants.
const disconnect = observeReveals(document, { threshold: 0.1, rootMargin: '0px' });
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
| `exit(element, onComplete, options?)` | Animate a dismissal; call a synchronous host hide/remove callback after exit | Native `Animation` or `null` |
| `stagger(iterable, preset = 'enter', options?)` | Animate each element with an incremental WAAPI delay | Array of animations or `null` entries |
| `observeReveals(root = document, options?)` | Observe `.syn-root [data-syn-reveal]` once per element | `disconnect()` cleanup function |

Presets are `fade` (opacity), `enter` (opacity and individual `translate`),
`scale` (opacity and individual `scale`), `slide` (individual translate only),
`press` (short scale-down-and-back interaction), and `highlight` (temporary
background-color change). No preset autoplays or repeats indefinitely. The
highlight effect repaints and should not be applied to large regions.
`enter` and `slide` support `direction: 'up' | 'down' |
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
without modifying the DOM. Animations on **the same element replace** earlier
Syntyr animations. Callers can still `animation?.cancel()` for interruption
or inspect `animation?.finished`; cancellation rejects that native promise,
so handle rejection when awaiting it. Per-element tracking and the transient
motion-preference listener are cleaned up on settle. Ordinary entrance and
feedback effects use `fill: 'none'` and release styles at completion.

For dismissal, `exit(element, () => element.remove())` holds opacity at zero
until the **synchronous** callback runs, then releases the effect. When reduced
motion is requested or WAAPI is missing, the callback runs immediately.
A replacement animation cancels the dismissal without invoking the callback.
Do not use asynchronous removal callbacks: complete the DOM change
synchronously before the exit's final keyframe is released.

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
const disconnect = observeReveals(document, { threshold: 0.15, rootMargin: '0px 0px 20px 0px' });
```

No `IntersectionObserver` is created automatically; call `observeReveals`
after rendering the relevant HTML fragment. It observes only descendants of
`.syn-root` with a `data-syn-reveal` attribute, runs each animation once,
and does **not** add `opacity: 0` to page content before JavaScript starts.
A region can be re-scanned after HTMX/Datastar/React renders new nodes.
The root argument limits the query, and optional `threshold` and `rootMargin`
are forwarded to the native IntersectionObserver. The return function disconnects it.
There is no `MutationObserver` or automatic event interception.

## Accessibility and performance

- `prefers-reduced-motion: reduce` takes precedence over all presets and
  custom durations. Reduced-motion users always get visible, immediate content;
  if that preference changes while observing, animation is checked again;
  existing ordinary Syntyr animations are canceled when it changes to reduce,
  while any pending exit commits its synchronous hide/remove callback so it
  cannot leave content stranded in an intermediate state.
- Content is never hidden while waiting for JavaScript, scroll observation,
  or native feature detection. Effects do not replace semantic HTML, focus
  management, ARIA announcements, or actual state-change notifications.
- Most keyframes use composited `opacity`, `translate`, and `scale` rather than
  layout dimensions. `highlight` intentionally repaints a small surface. Avoid animating essential text and high-density data,
  where fading can temporarily reduce readability. An element with custom
  individual transform properties may need a wrapper for composition.
- Ordinary effects use one-shot `fill: 'none'` and `iterations: 1` to avoid
  persistent overrides. `exit` temporarily holds its end state until the
  host synchronously removes or hides the node.
- For layout changes, prefer native View Transitions where available. For
  interactive scrubbing and complex timelines, use a specialized animation
  engine *outside* Syntyr instead of expanding this low-level module.

## CSS-only disclosures and native overlays

Load `dist/syntyr.motion.css` alongside core, then opt in with
`<details class="syn-disclosure--transition">` within `.syn-root`.
The module animates native `::details-content` sizing only when
`interpolate-size` and the pseudo-element are supported. Otherwise
`<details>` opens and closes normally; no script or custom ARIA state is
needed. The same stylesheet already provides the opt-in
`syn-popover--transition` and `syn-dialog--transition` classes. These
transitions read `--syn-motion-duration` and `--syn-ease-out` from the
core tokens, matching the JS defaults. Avoid overriding these tokens with
nonpositive or unreasonably long values in interactive contexts.

## Verification

```sh
node --test tests/animate.test.mjs
python3 scripts/build.py --check
python3 -m unittest discover -s tests -v
```

Node is for the optional JavaScript behavior tests, **not** for building
Syntyr or using the CSS library. The production JS is copied byte-for-byte
by Syntyr's existing Python build, allowing deterministic release checks.
