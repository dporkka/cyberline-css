# Syntyr Blocks & Assets — integration guide

**Status:** Experimental alpha.5 source gallery, not an immutable release or published npm package.

[Browse 23 blocks](blocks.html) | [Component catalog](catalog.html) | [Themes](theme-customization.md) | [Accessibility](accessibility.md)

## Contract

The 23 copy-owned HTML compositions cover marketing, application, technical and AI interface use
cases. Each contains its own Syntyr root, uses accessible native markup and requires
no application JavaScript. The data, testimonials and prices are illustrative, not live.

The gallery script powers optional documentation search, theme switching and copy
buttons. Disable JavaScript and all 23 static previews remain visible, with
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

## AI interface patterns (unreleased source candidate only)

Three CSS-only compositions are available in the **AI interfaces** gallery category:

- **AI conversation:** explicitly attributed ordered messages. Keep author names in text;
  do not rely on bubbles or color for role meaning.
- **Agent tool execution:** ordered steps and a native `<details>` disclosure for a
  text-rendered result. Populate results from trusted or safely escaped data;
  do not paste executable or untrusted HTML into the DOM.
- **Human approval gate:** visual pending state with disabled preview buttons.
  Enable controls **only** when your host app supplies authenticated, authorized,
  CSRF-protected, audited approval/rejection handlers and a clear action scope.

These examples are **alpha.5 unreleased source-only**, not available in the
published alpha.4 CSS. Load candidate `syntyr.core.css` and
`syntyr.recipes.css` together from the **same build**. Styling does not execute
models or tools, stream messages, establish permission, or implement decisions.
For streamed chat, manage announcement frequency and focus in the host application;
never mark an entire updating transcript as an assertive live region.

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
shadcn-compatible universal-item registry from the same 20 MIT blocks and
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
