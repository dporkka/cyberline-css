# Syntyr Blocks & Assets — integration guide

**Status:** Experimental alpha.5 source gallery, not an immutable release or published npm package.

[Browse 20 blocks](blocks.html) | [Component catalog](catalog.html) | [Themes](theme-customization.md) | [Accessibility](accessibility.md)

## Contract

The 20 copy-owned HTML compositions cover marketing, application and technical use
cases. Each contains its own Syntyr root, uses accessible native markup and requires
no application JavaScript. The data, testimonials and prices are illustrative, not live.

The gallery script powers optional documentation search, theme switching and copy
buttons. Disable JavaScript and all twenty static previews remain visible, with
selectable source under native disclosure elements. No scripts are included in
application CSS, and the core Syntyr build is unchanged.

## Optional block installer (Python standard library only)

The copy button remains the simplest path for individual blocks. For developers
and coding agents that prefer local, repeatable source handoff, the repository
includes a development-time CLI. It reads the same 20-block public manifest
used by this gallery; it is **not** a runtime or deployment dependency.

~~~sh
# From a pinned Syntyr source checkout (alpha.5 is not yet released)
python3 scripts/blocks_cli.py list
python3 scripts/blocks_cli.py list --category Applications --json

# Review the exact files before any changes, then install to an app folder
python3 scripts/blocks_cli.py install metric-overview team-directory --output ./my-app --dry-run
python3 scripts/blocks_cli.py install metric-overview team-directory --output ./my-app
~~~

This creates `my-app/syntyr/blocks/*.html`, only the required prebuilt
`syntyr/css/syntyr.<module>.css` files, an integration README, a
`LICENSE-MIT` copy and `installed.json` with the pinned source version
and SHA-256 checksums for every copied file. No data is sent to a server.

A [runnable Go standard-library consumer](https://github.com/dporkka/syntyr-css/tree/main/examples/blocks-go)
shows one copied block adapted into a server-rendered `html/template` page,
with a real HTTP handler and HTML escaping tests. Go is optional; no Go
toolchain is required to use the core CSS or the block installer.

This is intentionally a **one-shot, non-destructive copy operation**: it
refuses to overwrite an existing file, even on a repeat invocation.
To select additional blocks, use a new output folder or copy them manually;
there is no automated in-place upgrade yet. The CLI does not install premium
assets or grant a commercial license. Adapt the CSS URLs to your hosting root,
and integrate server behavior in your app as described below.

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
