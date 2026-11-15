# Mature design-system patterns in Syntyr

These opt-in, CSS-only styles adapt lessons from established design systems without copying their source code or adding a JavaScript runtime dependency. See the [static example](../examples/mature-patterns.html).

## Why these patterns?

| System | Verified lesson | Syntyr response |
| --- | --- | --- |
| [Bootstrap](https://getbootstrap.com/docs/5.3/forms/validation/) | Do not rely on inaccessible custom validation tooltips; associate server-side messages with controls | Keep native form validation; style `aria-invalid` controls and a visible, linkable error summary |
| [GOV.UK](https://design-system.service.gov.uk/components/error-summary/) | A page-level summary should link to each invalid field and match its local error message | `.syn-error-summary` is presentation-only; use it alongside `.syn-error` |
| [GOV.UK summary list](https://design-system.service.gov.uk/components/summary-list/) | Key/value reviews benefit from native `dl`, `dt`, `dd` semantics and explicit action labels | `.syn-description-list` adapts to a named container and logical text direction |
| [Carbon](https://www.carbondesignsystem.com/building-blocks/core/components/data-table/accessibility) | Sorting must be keyboard-operable and programmatically exposed | `.syn-table th[aria-sort]` provides styling for a real application-owned `button`, never fake sorting |
| [Tailwind](https://tailwindcss.com/docs/theme/) / [Open Props](https://open-props.style/) | Small reusable tokens and predictable compositions are more valuable than duplicate variants | Reuse existing `--syn-*` variables rather than inventing another token model |

## Server-rendered error handling

1. Keep the submitted field values and preserve the input's `name` and `id`.
2. On validation errors, render a page-level `.syn-error-summary` with a heading (for example `There is a problem`) and a list of anchors pointing to each erroneous input ID.
3. Beside each affected field, render the same actionable message in `.syn-error`, set `aria-invalid="true"`, and reference the error ID with `aria-describedby` along with any hint IDs.
4. After a failed submission, **move focus to the summary** with application/server framework logic. A `tabindex="-1"` makes it programmatically focusable but does **not** focus it on its own. A server-rendered page can provide an explicit navigation/focus strategy as appropriate to its stack.
5. Do not enable custom JavaScript validation tooltips. Browser-native validation is preferable unless the application deliberately implements a tested validation flow. If using `novalidate`, the server must actually validate; CSS cannot validate inputs.

Example (the action and value originate in the host application):

```html
<div class="syn-error-summary" role="alert" tabindex="-1"
     aria-labelledby="error-heading">
  <h2 id="error-heading">There is a problem</h2>
  <ul><li><a href="#email">Enter an email address</a></li></ul>
</div>
<label class="syn-label" for="email">Email</label>
<p class="syn-error" id="email-error">Error: Enter an email address</p>
<input class="syn-input" id="email" name="email" type="email"
       aria-invalid="true" aria-describedby="email-error">
```

Avoid re-announcing the same error multiple times through nested live regions. Test the actual form flow with NVDA/VoiceOver and keyboard users; using `role="alert"` does not guarantee consistent announcements when the entire document loads. The example is server-rendered markup, not an implementation of validation or focus movement.

## Description lists for review screens

Use `dl` for key/value pairs, not a visual-only grid of `div` elements. A row uses a direct `div` child, then `dt` and one or more `dd` children. An optional `dd.syn-description-actions` holds an action with a specific, self-descriptive accessible name such as "Change account name".

The layout defaults to one column. Wrap in an ancestor `.syn-region` to enable a three-column layout at a container width of 38rem or more. The last column can be empty when there is no action; it never changes the DOM reading order. Use native `dir="rtl"` and `lang` as appropriate to the content.

## Sortable tables

The `aria-sort` attribute belongs on **one** active column's `th`, with the value `ascending` or `descending` as appropriate. Use a real `button type="button"` inside the header for keyboard access. On activation the **application** must reorder rows and update `aria-sort` consistently; Syntyr only supplies the affordance and arrow glyph, never sorting behavior.

Leave inactive column headers without `aria-sort` or explicitly use `none` when a button is present. Prefer `scope="col"`, a caption/accessible table name and useful row headers. Place wide tables in a `.syn-table-wrap` region with an accessible name and keyboard focus when overflow makes the region scrollable.

## RTL, forced-colors and reliability

The new compositions use logical border/padding properties. Table base alignment uses `text-align: start` and numeric cells use `text-align: end` rather than hard-coded left/right alignment, so they follow the active writing direction.

Navigation and geometry also honor the nearest `dir` context: `.syn-app-nav` places its active marker at the inline start, breadcrumb separators mirror, `.syn-panel--cut` places its clipped corner at the inline end, and the asymmetric `.syn-frame--notch` and `.syn-frame--circuit` decorations mirror without reversing the text itself. A nested `dir="ltr"` subsection remains LTR even inside an RTL parent. These visual rules use native `:dir(rtl)`, not a new theme or JavaScript.

This is a **targeted RTL improvement**, not a claim that every Syntyr recipe, animation, third-party integration or mixed writing mode has received a complete human localization audit.

Test in Chromium, Firefox and WebKit at desktop/mobile widths, 200% and 400% browser zoom, keyboard-only navigation, real screen readers, and operating-system forced-colors mode before declaring release readiness. The existing `@media (forced-colors: active)` fallback makes error-summary borders visible with system colors, but cannot substitute for human checks.

All styles work with a local copy of `syntyr.core.css`. No JavaScript, framework dependency or new theme tokens are necessary.
