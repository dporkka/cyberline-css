# Icons, Unicode, and ASCII art (optional)

Syntyr styles user-supplied icons and text; the `symbols` CSS module has **no** glyphs,
icon font, emoji assets, JavaScript icon runtime, or ASCII-art generator.
A separate, optional set of 24 original MIT SVGs is available as standalone files
under `assets/icons/` (see [the design assets guide](design-assets.md)).
The free MIT module is `dist/syntyr.symbols.css`. It is optional and works
with any of the seven source themes, server-rendered HTML and framework views.

```html
<link rel="stylesheet" href="/css/syntyr.core.css">
<link rel="stylesheet" href="/css/syntyr.symbols.css">
```

Use these two files, **or** `syntyr.all.css`, not both. If you don't use
icons or text art, load core alone. The module is also included in the
unreleased alpha.5 `syntyr.all.css` source bundle.

## 1. SVG icons (no mandatory icon pack)

Syntyr's `.syn-icon` is only a sizing, alignment and inheritance contract.
Put it directly on an inline SVG, or on a wrapper around an SVG. Default size
is `1.25em`; override `--syn-icon-size` for a specific icon or container.
SVG `stroke` and `fill` remain under your control; this supports both
outline packs and filled icons. The following path is an original example.

```html
<button type="button" class="syn-button">
  <svg class="syn-icon" viewBox="0 0 24 24" fill="none"
       stroke="currentColor" stroke-width="1.8" aria-hidden="true"
       focusable="false">
    <path d="M20 7v5h-5M4 17v-5h5M5.8 9a7 7 0 0 1 12.8-1.8L20 12M4 12l1.4 4.8A7 7 0 0 0 18.2 15"/>
  </svg>
  Refresh report
</button>
<button type="button" class="syn-button" aria-label="Search reports">
  <svg class="syn-icon" viewBox="0 0 24 24" fill="none"
       stroke="currentColor" stroke-width="1.8" aria-hidden="true"
       focusable="false">
    <circle cx="10.5" cy="10.5" r="6.5"/>
    <path d="m15.5 15.5 5 5"/>
  </svg>
</button>
```

**Supported icon sources:** your own SVGs, or individually imported or copied
assets from Lucide, Heroicons, Tabler, and similar libraries under their
respective licenses. None is vendored or required. Avoid loading an entire
icon font or a massive SVG sprite for a handful of icons. An SVG that uses
`currentColor` inherits Syntyr's theme colors automatically.

## 2. Unicode as actual text

```html
<span class="syn-symbol syn-symbol--accent" aria-hidden="true">◆</span>
<span>Operational</span>
<span class="syn-symbol syn-symbol--muted" aria-hidden="true">→</span>
<span>Details</span>
```

Useful small marks include `→`, `›`, `◆`, `◇`, `●`, `▸`, `⌘`,
and `⌁`. They are examples, not a mandatory character vocabulary. Unicode
symbols need font coverage; system font fallbacks, emoji variation selectors,
platform-specific glyphs, high-contrast mode and text direction can all change
their presentation. Check the exact characters in your target browsers and fonts.
Do not rely on a symbol's color or shape alone to communicate state.

## 3. ASCII and Unicode box-drawing art

Use real `<pre>` text. `.syn-ascii` preserves spaces, line breaks and
monospace alignment and scrolls horizontally rather than splitting a border.
It pairs with existing `.syn-terminal` recipes, but does not require them.

```html
<p id="sys-health">API online and jobs online.</p>
<pre class="syn-ascii syn-ascii--accent" aria-hidden="true">+-------------------+
|  SYSTEM: ONLINE   |
+-------------------+
|  API  [OK]        |
|  JOBS [OK]        |
+-------------------+</pre>
```

The example above is **ASCII**. Unicode box-drawing characters such as
`┌─┐│└─┘` are an optional visual alternative, not ASCII. Unicode can contain
wide or ambiguous-width characters, so text grids may not align consistently
across fonts and platforms; don't embed emoji in precision-aligned columns.
Use spaces, not tabs, for exact alignment. The CSS never inserts semantic
content with `::before` or `::after`.

## Accessibility and fallback rules

- Decorative SVGs and symbols next to visible labels use
  `aria-hidden="true"`; inline SVGs may also use `focusable="false"`.
  Icon-only interactive controls need a meaningful accessible name
  (`aria-label` or visible visually-hidden text) and keyboard focus.
- Decorative text art may use `aria-hidden="true"`, **but the information
  must also exist as ordinary visible text, table or markup**. If the art
  conveys important information, do not hide it without an equivalent.
  Test with a screen reader, zoom/reflow and forced-colors settings.
- Don't depend on Unicode or pseudoelement `content` for meaningful labels.
  A missing glyph must never remove an action or its status semantics.
- Native CLI programs do **not** load CSS. Use Syntyr's separate
  `terminal/palettes.json` ANSI colors, honor `NO_COLOR`, detect TTY
  support, and offer a plain-text fallback. Don't impose Unicode art on
  terminals that cannot render it.

See the [standalone gallery](../examples/symbols.html), the existing
[terminal and geometry guide](geometry-terminal.md), and the
[CSS distribution notes](distribution.md).
