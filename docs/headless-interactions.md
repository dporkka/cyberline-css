# Optional accessible menus, comboboxes and notifications

Syntyr is a CSS presentation layer with **no runtime JavaScript**. Interactive
menu and combobox ARIA patterns require keyboard, focus, filtering and
selection logic; CSS cannot implement those.

The [opt-in headless adapter](../integrations/headless/interactions.css)
provides token-driven styling for explicit menu, combobox and toast classes.
It does NOT ship in the Syntyr core CSS, all.css or presets.

- Menus: `.syn-menu-surface`, `.syn-menu-item`, `.syn-menu-separator`.
  [Radix DropdownMenu](https://www.radix-ui.com/primitives/docs/components/dropdown-menu)
  owns ARIA roles, arrow navigation, typeahead, dismissal and focus.
- Comboboxes: `.syn-combobox`, `.syn-combobox-field`,
  `.syn-combobox-popover`, `.syn-combobox-listbox`,
  `.syn-combobox-option`. [React Aria ComboBox](https://react-aria.adobe.com/ComboBox)
  owns the filtered options, selection and accessible active focus.
- Toasts: `.syn-toast-region`, `.syn-toast`, `.syn-toast-title`,
  `.syn-toast-description`. [Radix Toast](https://www.radix-ui.com/primitives/docs/components/toast)
  owns notification timing, focus, hover pauses, dismissals and live regions.

No styles target generic ARIA roles or library internals. The adapter only
matches Syntyr-named classes and documented state hooks such as
`[data-highlighted]`, `[data-focused]`, `[aria-selected="true"]`, and
`[data-disabled]`. Application semantics remain authoritative.

## Run the isolated React example

[Source](https://github.com/dporkka/syntyr-css/tree/main/examples/headless-react) provides actual React, Radix and React
Aria controls, not inert HTML copies. Its npm dependencies are optional
**application dependencies**. They are not dependencies of Syntyr itself.

~~~sh
cd examples/headless-react
npm ci
npm run build
npx playwright install chromium  # optional browser-test setup
npm test                      # six Chromium keyboard/state smoke tests
npm run dev
~~~

The example imports both CSS files directly from the repository.
In your own application, include the core stylesheet before the optional
integration stylesheet:

~~~html
<link rel="stylesheet" href="/css/syntyr.core.css">
<link rel="stylesheet" href="/css/headless/interactions.css">
~~~

Or import `@syntyr/css/core.css` followed by
`@syntyr/css/headless.css` if the installed release includes this new export.
The example is *not* hosted as an executable React app in Syntyr's
static documentation site. The existing source branch may be newer than
the published release; always check your installed version.

**Portal scoping:** Radix and React Aria often portal menu/listbox/toast
content to `document.body`. The example uses `body.syn-root` so its portal
content inherits theme tokens and CSS rules. In other apps mount portals
within a stable styled `.syn-root`. Without this, unscoped portal content
will look unstyled. Keep root scope stable across updates.

## Native alternatives that need no headless dependencies

For a short list of links/actions, use HTML `popover` with regular
`<a>` and `<button>` controls. This is a *popover*, not an ARIA
application menu: Tab/Shift+Tab are expected rather than Arrow-key
menu interactions. For small suggestion lists, native `input[list]` and
`datalist` may be sufficient, though their presentation and accessibility
differ by browser and are not completely themeable.

A true ARIA menu needs Arrow navigation, typeahead, Escape, disabled state
and focus restoration. A rich combobox needs correct ARIA relations,
keyboard navigation and IME composition support. Do not recreate these
with hand-written CSS-only role attributes.

## Toast boundaries and accessibility

Toasts are for temporary, noncritical notifications. A confirmation or
irreversible decision must not auto-dismiss: use inline feedback or a dialog.
Do not indiscriminately apply `role="alert"` to every toast. The
host implementation owns announcements, queue limits, timing and
dismissal. The example deliberately labels its actions as demos rather
than claiming any backend persistence.

Test focus and announcements in real browsers and with a screen reader,
plus reduced-motion, forced-colors, high zoom and narrow viewports.
Syntyr's CSS contract tests are **not** accessibility certification.

See [Radix state adapter](radix-integration.md),
[framework integrations](framework-integrations.md) and
[native browser API guidance](native-browser-apis.md).
