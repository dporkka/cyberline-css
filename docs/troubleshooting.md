# Troubleshooting Syntyr CSS

Use this checklist when a page is unstyled, a component looks wrong, or styles behave differently across frameworks. Diagnose **stylesheet version, loaded modules, scope, and actual HTML** before changing CSS specificity.

## My page is completely unstyled

1. Check DevTools → Network: did your stylesheet load with an HTTP success response, not HTML from a 404 fallback?
2. Open the stylesheet and confirm it is Syntyr CSS from the version you intend to use.
3. Ensure the intended ancestor has `class="syn-root"`. Syntyr intentionally does not globally style your document.
4. Inspect the element's computed styles. If `syn-*` rules do not appear, either the stylesheet is missing or the class is not supported by the loaded version.
5. Check your framework's stylesheet registration: for example, its global CSS entry point or public assets directory.

**Do not** add `!important` globally or remove `syn-root` scoping to hide a missing stylesheet problem.

## Semantic HTML is not styled

`syntyr.core.css` does **not** automatically restyle every unclassed `button`, `table`, or `article`. You must load `syntyr.semantic.css` **after** core and opt into `class="syn-root syn-semantic"`. Alternatively, test the one-file `syntyr.semantic-bundle.css` in the **unreleased alpha.5 source candidate**; do not also load core or semantic with that bundle.

Semantic rules intentionally target unclassed elements, with `data-syn-semantic` available for specific elements whose classes are inserted by libraries such as HTMX. Check the [semantic guide](components.md) and [framework integration guide](framework-integrations.md).

## A class from an example has no effect

Confirm **both** the selector and its stylesheet. Some classes live only in `syntyr.recipes.css`, `syntyr.viz.css`, `syntyr.data-grid.css`, or other optional modules. A `syn-*` class name does not trigger automatic CSS loading.

Use the [component reference](components.md), [recipes reference](recipes.md), and the [curated component metadata](../metadata/components.json). The metadata is intentionally non-exhaustive; the installed CSS is authoritative.

Also check the release: the **published v0.3.0-alpha.4** has three themes and a narrower module set. The **v0.3.0-alpha.5** `main` tree is an **unreleased candidate**, not a published download. Do not mix stylesheets from both versions.

## Colors, typography, or themes are inconsistent

- Set `data-syn-theme="studio"`, `grid`, or `noir` on `.syn-root` (or a nested themed subtree) when using the published alpha.4 CSS.
- Theme-aware CSS variables such as `--syn-bg`, `--syn-text`, and `--syn-accent` inherit through the scoped element tree. Override them inside the relevant Syntyr scope.
- Check stylesheet order and other global CSS that may override Syntyr declarations. Avoid copying theme variable values from a different release.
- Do not assume alpha.5-only themes (`industrial`, `terminal`, `corporate`, `minimal`) exist in the published alpha.4 release.

See [theme customization](theme-customization.md) and [API stability](api-stability.md).

## Layout breaks after a partial HTML update

Server-driven frameworks can replace containers or add transient state classes. Ensure the replacement includes necessary `syn-*` classes, or keep `.syn-root` on a stable ancestor. If semantic styling stops applying when classes appear, try `data-syn-semantic` on the affected element.

If using HTMX, Datastar, Turbo, LiveView, or Livewire, request wiring, event lifecycles, and morphing belong to that framework, not Syntyr. The [integration guide](framework-integrations.md) documents the opt-in server-state styles and limitations.

## Buttons, overlays, filters, and charts do nothing

Syntyr supplies **presentation**, not application logic. A styled button needs a real event/action handler. Filtering and pagination need data logic. A chart needs markup or a renderer; `syntyr.viz.css` only styles HTML/SVG provided by the app.

Native `details`, popover, dialog and invoker commands depend on browser support. For essential workflows, implement a working fallback or progressive enhancement. Do not mistake a static demo's sample controls for working backend features.

See [native browser APIs](native-browser-apis.md), [progressive enhancement](progressive-enhancement.md), and [accessibility guidance](accessibility.md).

## Duplicate rules, unexpectedly large CSS, or conflicting styles

Choose one strategy:

- `syntyr.core.css` plus the individual optional modules you use.
- `syntyr.semantic-bundle.css` **alone** for one-file semantic styling in alpha.5 source.
- One `dist/presets/*.css` **alone** for a complete alpha.5 source preset.
- `syntyr.all.css` **alone** when intentionally opting into all included modules.

Do not combine a bundle or preset with files that it already contains. Prefer the smallest *maintainable* choice rather than introducing automated purging; Syntyr supports explicit [selective builds](https://github.com/dporkka/syntyr-css/blob/main/docs/selective-builds.md) for source users.

## Still stuck?

Create a minimal reproduction containing the exact CSS filename/version, stylesheet order, root classes, a short HTML sample, browser and OS, and expected versus observed behavior. Check [existing issues](https://github.com/dporkka/syntyr-css/issues) before filing a public bug. For security vulnerabilities, follow the [private reporting policy](https://github.com/dporkka/syntyr-css/blob/main/SECURITY.md) instead.
