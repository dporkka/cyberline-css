# Syntyr Blocks & Assets — integration guide

**Status:** Experimental alpha.5 source gallery, not an immutable release or published npm package.

[Browse 24 blocks](blocks.html) | [Component catalog](catalog.html) | [Themes](theme-customization.md) | [Accessibility](accessibility.md)

## Contract

The 24 copy-owned HTML compositions cover marketing, publishing, navigation,
application and technical use cases. Each contains its own Syntyr root, uses accessible native markup and requires
no application JavaScript. The data, testimonials and prices are illustrative, not live.

The gallery script powers optional documentation search, theme switching and copy
buttons. Disable JavaScript and all twenty-four static previews remain visible, with
selectable source under native disclosure elements. No scripts are included in
application CSS, and the core Syntyr build is unchanged.

## Native HTML and framework integration

Load the specific CSS modules shown on each block, from the same pinned version.
For example, blocks using both core and recipes:

~~~html
<link rel="stylesheet" href="/css/syntyr.core.css">
<link rel="stylesheet" href="/css/syntyr.recipes.css">
<!-- Paste a copied HTML block here. -->
~~~

Do not load all.css alongside individual CSS files. Most snippets have their own
root class and default Studio theme. If the application already has a Syntyr root,
you may remove a redundant nested root while retaining the necessary theme scope.

Three supported approaches:

1. **Server HTML / Go templ / Django / PHP / Rust Askama:** Paste snippets into
   templates and bind actual data and routes, with server-side escaping,
   authorization, CSRF protection for writes, and validation.
2. **HTMX / Datastar:** Keep native forms, links and server fallbacks working.
   Add progressive enhancement attributes only in the application; Syntyr
   does not bundle those JavaScript libraries.
3. **React / Astro / Vue / Svelte:** Convert HTML syntax where required, e.g.
   class to className and for to htmlFor in JSX. Bind interactive state and
   event handlers in the host app, not in Syntyr.

Routes like /settings and /checkout/team are example host-app routes. Replace
them before using in production. Static samples do not implement authentication,
filtering, payments, sorting, persistence or actual monitoring.

## 12 original, optional CSS asset recipes

The complete source is [blocks-assets.css](blocks-assets.css). It includes:
fine-grid, dot-field, radar, ambient-glow, glass, blueprint, signal-stripes,
diagonal, beam, corners, horizon and circuit. The gallery displays all twelve.

The CSS is **docs-only** and outside Syntyr's core and all-in-one builds.
You may copy individual modifiers with their necessary base rules into your
application-owned stylesheet. It contains no images, external fonts, canvas,
JavaScript or network imports. Scanning beam animation respects reduced-motion
preferences, and effects disable in forced-colors mode.

Existing Syntyr geometry and effects modules should be the default choice when
they already provide the desired result.

## Six font recipes and 24 original SVG icons

Six system-font typography directions are displayed in the gallery:
Studio sans, Editorial serif, Terminal mono, Technical sans, Reading serif
and Compact system. They do not bundle or download font files. Customize
CSS tokens for UI, display and monospace type, preserving readable fallbacks.

The gallery now provides 24 original, copyable inline SVG examples using
Syntyr's existing generic icon sizing contract. These are not a dependency,
icon font or stand-alone icon runtime. You may also use appropriately licensed
provider packs such as Lucide, Tabler and Heroicons; none are vendored here. Icon-only controls need accessible
names. See [symbols](symbols.md) for supported integration patterns.

## Source, build and maintenance

Editable fragments live in the blocks/snippets directory. Metadata and module
dependencies live in blocks/manifest.json. The gallery is generated, not hand
edited, by the Python standard-library script:

~~~sh
python3 scripts/build_blocks.py
python3 scripts/build_blocks.py --check
python3 -m unittest discover -s tests -p test_blocks_assets.py -v
python3 -m unittest discover -s tests -v

# Optional developer-only browser checks (Playwright plus browser engines):
python tests/blocks_browser.py --browsers chromium firefox webkit --axe-file /tmp/axe.min.js
~~~

Only the rendered gallery and its reviewed documentation assets are publicly
allowlisted by Cloudflare; raw authoring files are not published.

## Accessibility, fidelity and licensing

Test all adapted blocks with keyboard-only navigation, mobile widths, 200% and
400% zoom, forced colors and an actual screen reader. Check contrast with the
real application theme. Do not announce static sample status as live system
state or retain fabricated customer endorsements in production.

All new snippets, original CSS assets and documentation are MIT licensed.
No premium Tailwind, commercial UI kit or third-party icon artwork has been
copied into the public project. The separate private Console Kit is unaffected.

## Experimental shadcn universal-item registry

The source candidate can generate a **copy-owned, framework-independent**
shadcn-compatible universal-item registry from the same 24 MIT blocks and
checked-in CSS distributions. It neither replaces nor duplicates the native
block installer from PR #104. Universal files use explicit project-relative
targets, so no React, Tailwind, or Syntyr runtime JavaScript is required.

```sh
python3 scripts/build.py --check
python3 scripts/build_shadcn_registry.py       # generate registry/registry.json and registry/r/*
python3 scripts/build_shadcn_registry.py --check
# Optional, developer-only shadcn 4.23.0 integration smoke (requires npm):
python3 tests/shadcn_registry_cli_smoke.py --package shadcn@4.23.0
```

Each `registry/r/<block-id>.json` contains the source HTML at
`~/syntyr/blocks/<block-id>.html` and absolute same-origin registry dependencies for
the required stylesheets at `~/syntyr/css/`. Each registry item also installs
the original MIT `LICENSE` at `~/syntyr/LICENSE`. Install in an existing project
only after reviewing the exact files, license and project configuration. For
example, **after publishing the reviewed candidate site**, a shadcn CLI may
consume `https://syntyr-css.pages.dev/registry/r/faq.json`. This is a
candidate endpoint, not a claim that it is currently deployed. The independent
local-mirror smoke verifies that CLI 4.23.0 can install both core-only and
core-plus-recipes blocks without a consumer package.json or runtime dependencies.

The generated index is intended for editor/agent inspection. The generator
never reads private Console Kit assets or executes downloaded code. No dynamic
service, telemetry, npm dependency, or customer license is introduced.
Published alpha.4 assets remain immutable; registry payloads declare their
source-candidate Syntyr version and must not be confused with a tagged release.

## Content collection, publishing, and navigation compositions

Four original blocks borrow the *use cases*, not the Elementor implementation:
content collection, editorial article, website header/footer, and native mega menu.
All four are **MIT copy-owned HTML** and depend only on the existing Syntyr
`core` and optional `recipes` stylesheets. No new Syntyr CSS selector, runtime,
license tier, vendor dependency, or bundled image is added.

- **Content collection:** The GET form, query, and topic select submit to
  `/journal`. The host endpoint must validate inputs and render filtered, paged
  articles. The static cards and pagination demonstrate presentation only.
  Preserve query/category parameters in real pagination URLs; always build
  links from validated, escaped values. Do not imply live JavaScript filtering.
- **Editorial article:** Use the existing `syn-prose` and `syn-sidecar` classes
  for reading content, linked on-page contents, author attribution, and related
  links. Substitute real editorial content and authors; the example author is
  fictional. Place a single page-level `h1` in standalone article templates;
  snippets use `h2` because the gallery already has a page heading.
- **Website header and footer:** Reuse `syn-header`, `syn-nav`, `syn-inline`,
  `syn-stack`, and native navigation landmarks. Replace sample paths and brand.
  Header links wrap as space narrows; no invisible or JS-only hamburger controls.
- **Mega menu:** A native `details` disclosure and ordinary links, **not**
  a custom ARIA `menu` widget. It is shown open in the gallery so its content
  is visible without any script. For an actual site, close it initially if
  appropriate, and keep the trigger as a real `summary`. Test keyboard
  activation, zoom, long translations, and viewport overflow.

Use these as framework-neutral *composition examples*, not WordPress plugins
or theme-builder replacements. Bind dynamic content in the host framework
(PHP, Liquid, Go templates, React, etc.) with proper escaping and authorization.
