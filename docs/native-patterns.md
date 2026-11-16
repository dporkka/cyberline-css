# Native platform patterns and component imports

This prerelease Syntyr example uses original CSS, not upstream Blades source.
The standard native recipes retain semantic HTML and need **no runtime JavaScript**; the separate clipboard/toast companion described below is explicitly opt-in.
For a live static preview, see [the native recipe example (live alpha.5 source preview)](https://syntyr-css.pages.dev/examples/native-recipes.html).

## Native interaction recipes

The standard library includes the following **five native interaction
compositions**, using existing core classes plus normal HTML. They do **not**
require a new JavaScript runtime, Syntyr component subclass, or optional
`syntyr.native-recipes.css` import. Use `syntyr.core.css` for the classed
controls; load `syntyr.semantic.css` and opt in with `.syn-semantic` if
you want unclassed `meter` and `output` styling.

- **Exclusive accordion:** use `<details class="syn-details" name="faq">`
  and a real `<summary>` for each item. Reuse the `name` only *within*
  an intended disclosure group; only one item opens at once in current
  browsers. Do not invent `role="tab"`, `aria-expanded`, or keyboard handlers.
- **GET search:** use `<search>`, `<form method="get" action="/inventory">`,
  an associated label, and `<input class="syn-input" type="search" name="q">`.
  Native form navigation works with scripts disabled. Your server must filter
  results, preserve the query, escape untrusted input, and return a useful
  response; Syntyr does not implement a search endpoint.
- **Confirmation dialog:** use a `commandfor` + `command="show-modal"`
  button, `<dialog class="syn-dialog" aria-labelledby="...">`, and a
  `<form method="dialog">` with Cancel/Confirm choices. `method="dialog"`
  **only closes the dialog**; it does not submit a destructive action or
  authorize a mutation. A real save/delete must use a secure application
  endpoint or separately tested application logic. Provide a reachable
  non-dialog fallback for older browsers without invoker commands.
- **Datalist suggestions:** connect a labeled text input's `list` to a
  native `<datalist id="...">`. Users can enter text not in the suggestions.
  For restricted values use native `<select>` with optional `<optgroup>`;
  do not claim `datalist` is an accessible custom combobox.
- **Meter and output:** use `<meter min max low high optimum value>` for a
  bounded measurement and `<output>` for a computed or server-provided
  result. Provide readable labels and numeric text. Values do not update
  automatically: the server or application must calculate and synchronize
  them when inputs change.

[Open the script-free native interaction demo](https://syntyr-css.pages.dev/examples/native-interactions.html)
or [copy each recipe from the component catalog](https://syntyr-css.pages.dev/docs/catalog.html).
The page is intentionally static: search reloads with a query string,
dialog confirmation has no side effects, and output is a snapshot. In a
production application, implement real search and mutations in the host.

These patterns compose existing `syn-form`, `syn-input`, `syn-details`,
`syn-dialog`, `syn-inline`, and native HTML; adding a separate
`.syn-accordion`, `.syn-search`, or `.syn-confirm` class would duplicate
styles, selectors, documentation, and long-term compatibility obligations.
Native picker popup details and suggestion menus vary among browsers.
Test keyboard interaction, forced colors, zoom/reflow, and real product
copy in the target browsers. **Application-owned behavior** includes
search filtering, validation on the server, destructive action
authorization, and live calculations; none are provided by CSS.

## Individually importable CSS

Use the following **source-tree alpha.5 candidate** entrypoints after this PR
is merged and released; they are not available in the published alpha.4 package:

~~~css
@import "@syntyr/css/components/tokens.css";
@import "@syntyr/css/components/base.css";
@import "@syntyr/css/components/buttons.css";
@import "@syntyr/css/components/forms.css";
@import "@syntyr/css/components/form-composition.css";
@import "@syntyr/css/components/overlays.css";
@import "@syntyr/css/native-recipes.css";
~~~

Every component CSS file is directly generated from its original source, using
the same order and cascade layers as core. Tokens, then base, then components,
then optional recipes is the supported loading order. Form-composition requires
forms. Do **not** load core and component entrypoints together, or styles will be
duplicated. Runtime CSS dependencies, imports and JavaScript are not included in
these distributables. In plain HTML, link the equivalent checked-in files under
the dist directory. Use version-pinned self-hosted assets in production.

If no selective loading is needed, use core plus the optional recipe sheet:

~~~html
<link rel="stylesheet" href="/css/syntyr.core.css">
<link rel="stylesheet" href="/css/syntyr.native-recipes.css">
~~~

## Native anchored popovers and modal commands

~~~html
<button type="button" class="syn-button" popovertarget="actions">Actions</button>
<div id="actions" popover class="syn-popover syn-popover--anchored">
  <a href="/settings">Settings</a>
</div>
<button type="button" class="syn-button" commandfor="report" command="show-modal">Report</button>
<dialog id="report" class="syn-dialog" aria-labelledby="report-title">
  <h2 id="report-title">Report</h2>
  <form method="dialog"><button type="submit">Close</button></form>
</dialog>
~~~

Native popover invokers provide an implicit CSS anchor in supporting browsers.
The anchored variant uses position-area plus block/inline flip candidates; in
other browsers it falls back to Syntyr's existing fixed corner positioning.
For vital actions, links remain real links. Modal invoker commands are not
universally available in older browsers, so provide a navigable fallback for
critical content or use a small explicit progressive enhancement in the host.
Transitions do **not** ship in core. To opt into native popover/dialog
motion, load the additional `syntyr.motion.css` file, then add
`.syn-popover--transition` to a `.syn-popover` or
`.syn-dialog--transition` to a `.syn-dialog`. Both class and file are
required. The motion module honors reduced-motion preferences; without
either opt-in, dialogs and popovers use their native static behavior.
The native recipe gallery pairs its dialog command with a `<details>`
disclosure exposing equivalent critical information on older engines.
Native browsers own focus management, Escape and dialog inertness; the stylesheet
does not implement a custom ARIA menu.

## Native direction-aware presentation

The core popover's fixed-corner fallback and optional cut-corner panels use
CSS **logical** inset properties. They follow the document's text direction
(LTR or **RTL**) without a new theme or variant. Anchored popovers use the
browser's native block/inline positioning and flip candidates when available.
Optional activity timelines also place their markers on inline-start. Native
`dir="rtl"` controls direction; components keep semantic document order.

## Floating labels

~~~html
<div class="syn-field syn-field--floating">
  <input id="name" name="name" class="syn-input" placeholder=" " required>
  <label for="name" class="syn-floating-label">Full name</label>
</div>
~~~

Both floating and stacked labels remain real pointer targets; clicking a label
focuses its associated native control without JavaScript.

Keep a persistent programmatic label with for/id. The one-space placeholder
is a deliberate :placeholder-shown state hook, **not** the accessible label.

The field becomes a **stacked, wrapping label above the input** when its own
container is narrow (21rem or less). This protects visible field identification
when users enlarge text, including long translated labels. At wider sizes the
floating presentation remains. In RTL documents (`dir="rtl"`), the floating
label shrinks toward the right-hand inline-start edge rather than drifting
left. The label is always a real `<label for>`; the CSS never substitutes
placeholders for an accessible name. Test real browser zoom and translations
in consuming applications.

Use only for text-like controls that implement placeholder-shown. Avoid for
date, color, select, checkbox, radio and unsupported types. Validate contrast
and long translated labels in the actual application.

## Semantic timelines and captioned code

~~~html
<ol class="syn-timeline" role="list">
  <li><time datetime="2026-11-15">15 November</time>Published</li>
</ol>

<figure class="syn-code-figure">
  <figcaption id="example-caption">example.go</figcaption>
  <pre tabindex="0" aria-labelledby="example-caption"><code>package main</code></pre>
</figure>
~~~

An ordered list communicates sequence; date/time labels are optional.
The figure gives code an authentic, accessible caption, and the focusable pre
supports keyboard scrolling of wide code samples.

## Server-rendering and framework use

- **Go templates and templ:** Emit the same native HTML; escape dynamic label,
  body and code text with the renderer and ensure stable unique id/for pairs.
- **Rust Askama:** Render this markup in a regular Askama template. Escape
  dynamic content; let forms submit to real routes.
- **Astro:** Import selected CSS files through its CSS pipeline, render standard
  HTML, and use Astro islands only for behaviors that require application state.
- **HTMX:** Keep popovertarget and commandfor on native controls; for actions
  that mutate data, use real forms/links and HTMX only as progressive enhancement.

### Go html/template

~~~html
<form class="syn-root" data-syn-theme="studio" action="/profile" method="post">
  <div class="syn-field syn-field--floating">
    <input class="syn-input" id="profile-email" name="email"
           type="email" value="{{ .Email }}" placeholder=" " required>
    <label class="syn-floating-label" for="profile-email">Email address</label>
  </div>
  <button class="syn-button" type="submit">Save</button>
</form>
~~~

The standard Go html/template engine escapes the Email value by context.

### Rust Askama

~~~html
<form class="syn-root" data-syn-theme="studio" action="/profile" method="post">
  <div class="syn-field syn-field--floating">
    <input class="syn-input" id="profile-email" name="email"
           type="email" value="{{ email }}" placeholder=" " required>
    <label class="syn-floating-label" for="profile-email">Email address</label>
  </div>
  <button class="syn-button" type="submit">Save</button>
</form>
~~~

Use Askama's HTML autoescaping, unique IDs when rendering multiple forms, and
normal server-side validation.

### Astro

~~~astro
---
import "@syntyr/css/components/tokens.css";
import "@syntyr/css/components/base.css";
import "@syntyr/css/components/buttons.css";
import "@syntyr/css/components/forms.css";
import "@syntyr/css/native-recipes.css";
---
<form class="syn-root" data-syn-theme="studio" action="/profile" method="post">
  <div class="syn-root syn-field syn-field--floating">
    <input class="syn-input" id="astro-email" name="email"
           type="email" placeholder=" " required />
    <label class="syn-floating-label" for="astro-email">Email address</label>
  </div>
  <button class="syn-button" type="submit">Save</button>
</form>
~~~

In a real Astro page place the syn-root scope around the entire page region,
as in this form. Package imports
are source candidate features until a corresponding npm release is published.

### HTMX (optional enhancement)

~~~html
<form class="syn-root" data-syn-theme="studio" action="/profile" method="post"
      hx-post="/profile" hx-target="#profile-result" hx-swap="outerHTML">
  <label for="profile-email">Email address</label>
  <input class="syn-input" id="profile-email" name="email" type="email" required>
  <button class="syn-button" type="submit">Save</button>
</form>
<p id="profile-result" role="status" aria-live="polite"></p>
~~~

The action/method pair remains functional without HTMX. Host applications must
provide their own HTMX script and server response semantics.

This guide intentionally avoids wrappers and framework-specific JavaScript.
Refer to [framework integrations](framework-integrations.md) and the
[progressive enhancement guide (online)](https://syntyr-css.pages.dev/docs/progressive-enhancement.md) for host behavior
and fallbacks.

## Common website and application controls (source candidate)

[Open the common UI example](https://syntyr-css.pages.dev/examples/common-ux.html). This is a small, free,
MIT-licensed addition to the existing native recipes, not a replacement for the
standard core. Load `syntyr.core.css` and `syntyr.native-recipes.css`; no
framework, icon runtime, bundler, or JavaScript is needed for the first four.

| Need | Browser-native composition | Important limitation |
| --- | --- | --- |
| Action dropdown | `button[popovertarget]` + `[popover]` with `.syn-action-menu` and ordinary links/buttons | Native Tab navigation; do not add `role="menu"` unless implementing all menu keyboard semantics |
| Slide-over inspector | `dialog.syn-dialog.syn-drawer` with `command="show-modal"` | Browser focus trapping/Escape; authorization and persistence remain application-owned |
| Gallery / lightbox | `.syn-gallery` with `figure` and `dialog.syn-gallery-dialog` | Each image's button targets a real modal; keep thumbnails or an ordinary link as fallback |
| Date range | Two labeled native `input[type=date]` fields inside `.syn-date-range` | Validate start <= end, timezones, and inclusive/exclusive policy **on the server** |
| Copy and toast | Optional `syntyr.feedback.mjs` + `.syn-toast-region` | Requires a secure-context Clipboard API and a user click; failures are announced rather than silently ignored |

The native gallery uses original Syntyr screenshot assets already authorized
for public previews. Image alt text describes their content, figure captions
label the previews, and modal close controls use `form method="dialog"`.
The side drawer likewise has a real heading, labeled dialog and close button.
Older browsers may lack declarative `commandfor` invokers; provide critical
information as ordinary links or integrate an explicitly tested compatibility
enhancement. These patterns do not ship a homemade modal manager.

### Optional copy and toast enhancement

The CSS-only core and native recipes remain entirely script-free. To enable
one specific subtree's copy controls, load `dist/syntyr.feedback.mjs` as an
explicit ES module, using an external initializer if the host CSP disallows
inline JavaScript (as Syntyr's own site does):

~~~html
<section class="syn-root" id="my-feedback" data-syn-feedback-scope>
  <pre id="my-snippet">Accessible HTML first.</pre>
  <button type="button" data-syn-copy-target="my-snippet" disabled>Copy</button>
  <output class="syn-toast-region" data-syn-feedback-status
          role="status" aria-live="polite" aria-atomic="true" hidden></output>
</section>
~~~

~~~js
import { enhanceFeedback } from "/assets/syntyr.feedback.mjs";
const dispose = enhanceFeedback(document.getElementById("my-feedback"));
// Call dispose() before removing/replacing this host subtree.
~~~

The copy target is an **ID within the same feedback scope**, not a CSS
selector. The enhancer uses the Clipboard API and copies the target's
`value` or `textContent`; it does not parse HTML or execute copied content.
It sets the disabled control to enabled only after initialization, is
idempotent for the same root, and uses `textContent` for feedback (never
`innerHTML`). Its `announceFeedback(status, message, { duration })`
export also supports application-owned status messages; `duration: 0`
keeps the message visible. The default auto-dismiss is 4.5 seconds. For
important validation errors and irreversible operations, use persistent inline
errors or dialogs rather than a disappearing toast. The enhancer adds no
backend operations, user analytics, styling globals or remote dependencies.
