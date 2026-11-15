# CSS-native motion (experimental)

Syntyr's opt-in `syntyr.motion.css` adds a small set of progressive-enhancement
animations. Load `syntyr.core.css` then `syntyr.motion.css`, or load
`syntyr.all.css` alone. Neither `syntyr.core.css` nor the convenient
`syntyr.css` bundle includes animation presets. No JavaScript or third-party
animation engine is required. All selectors stay inside `.syn-root`.

```html
<link rel="stylesheet" href="dist/syntyr.core.css">
<link rel="stylesheet" href="dist/syntyr.motion.css">
<main class="syn-root" data-syn-theme="studio">
  <h1 data-syn-animate="enter">Operations dashboard</h1>
  <p data-syn-animate="enter" data-syn-from="left">Everything in one place.</p>
  <section data-syn-animate="reveal">Latest campaigns</section>
</main>
```

## One-shot composition

| Attribute | Result |
| --- | --- |
| `data-syn-animate="fade"` | Fade from transparent |
| `data-syn-animate="enter"` | Fade + independent `translate` |
| `data-syn-animate="scale"` | Fade + independent `scale` |
| `data-syn-animate="reveal"` | Geometric `clip-path` reveal |
| `data-syn-from="up"` / `"down"` / `"left"` / `"right"` | Direction for `enter`; reveal origin for `reveal` |

`enter` defaults to `up` (content moves upward from below); `reveal` defaults
to left-to-right. These run once when the element enters the DOM or its
animation style is newly applied. They **do not** trigger on viewport entry,
reorder existing lists automatically, or animate route changes.
After each one-shot animation completes, the element releases its animation
properties so component focus, disabled and layout styles can take precedence. For those use
application logic or the optional integrations below.

Customize without additional CSS classes:

```html
<div data-syn-animate="enter" data-syn-from="right"
     style="--syn-motion-duration: 320ms; --syn-motion-distance: 1.25rem">
  New item
</div>
```

The inherited tokens are `--syn-motion-duration` (220ms),
`--syn-motion-duration-slow` (420ms), `--syn-motion-distance` (.75rem),
`--syn-motion-stagger` (65ms) and `--syn-ease-out` (decelerating curve).
Per-element `--syn-motion-delay` defaults to 0ms; `scale` also accepts
`--syn-motion-scale-from` (default .96). Regular core components retain
`--syn-duration-fast` and `--syn-ease` for state transitions.

### Controlled stagger, without a child-count ceiling

Add `data-syn-stagger` to an immediate parent and set a zero-based
`--syn-motion-index` on animated children:

```html
<ul data-syn-stagger>
  <li data-syn-animate="enter" style="--syn-motion-index: 0">First</li>
  <li data-syn-animate="enter" style="--syn-motion-index: 1">Second</li>
  <li data-syn-animate="enter" style="--syn-motion-index: 2">Third</li>
</ul>
```

The browser computes the delay from the index and spacing token; if CSS
multiplication isn't supported, items still appear without a stagger.
Syntyr does **not** generate child indexes or run a mutation observer.
A server template can provide indexes; React/HTMX/Datastar can apply them
as they render new items.

### Decorative sweep and loading status

`.syn-motion-sweep` adds an optional light beam on hover/focus-within.
Avoid applying it to essential text where decorative overlays would reduce
legibility. Use a native status label with the spinner; the ring alone is
never the only indicator of progress:

```html
<p role="status">
  <span class="syn-loader" aria-hidden="true"></span> Saving changes…
</p>
```

The loader retains a static, visible ring when animation is disabled.
Never put `aria-hidden="true"` on the status label itself.

## Native popovers and dialogs

`class="syn-motion-popover"` on a native `[popover]` and
`class="syn-motion-dialog"` on a native `<dialog>` enable subtle entry/exit
transitions where `@starting-style`, `display` / `overlay` discrete transitions
and the browser's top-layer support allow them:

```html
<button popovertarget="menu">Menu</button>
<div id="menu" popover class="syn-motion-popover">Menu content</div>
```

For dialog controls, use the native `showModal()` / `close()` APIs or supported
HTML invoker commands in your application. Syntyr does not implement the
interaction or change the accessibility tree. Unsupported browsers retain
their native instant opening/closing behavior. Do not fake dialogs with ARIA.

## Accessibility, progressive enhancement and performance

- Every keyframe effect and transition is opt-in. `prefers-reduced-motion:
  no-preference` is the **only** condition that enables motion. When
  `prefers-reduced-motion: reduce`, content is fully visible immediately,
  including elements using `clip-path`. No `display:none` fallback or hidden
  initial state is required.
- `.syn-motion-sweep` is suppressed in forced colors; the loader retains a
  contrasting ring. Avoid repeated flashing, nonessential autoplay motion,
  and relying on animation alone to signal a state change.
- `translate` and `scale` use individual transform properties. Applying the
  `enter` or `scale` animation to an element that already customizes the same
  individual property can conflict; animate a wrapper when needed.
- `clip-path` reveal is more expensive than opacity/translation; use it for
  occasional decorative introductions, not a long table or scrolling list.
- Staggered elements remain accessible in the DOM while fading in. Do not
  apply opacity-changing motion to essential explanatory text or controls;
  even brief fades can temporarily reduce contrast. Avoid long delays. Test in Chromium, Firefox
  and WebKit; new CSS capabilities must degrade cleanly.
- Effects are one-shot. Re-triggering an animation requires an application
  state change, e.g. removing/re-adding the attribute or creating an element.

## Optional imperative animation integrations (not bundled)

For list reorder/insertion/removal, choose [AutoAnimate](https://auto-animate.formkit.com/)
in your application rather than adding a DOM observer to Syntyr.
For interruptible interactions or timelines, use the native
[Web Animations API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Animations_API)
or Motion's optional mini engine. For route transitions, prefer native
[View Transitions](https://developer.mozilla.org/en-US/docs/Web/API/View_Transitions_API)
when supported, with no-animation navigation fallback. These are **not** Syntyr
dependencies; Syntyr supplies colors, timing/easing and component styling.
