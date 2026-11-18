# Syntyr Blocks & Assets — integration guide

**Status:** Experimental alpha.5 source gallery, not an immutable release or published npm package.

[Browse 47 blocks](blocks.html) | [Component catalog](catalog.html) | [Themes](theme-customization.md) | [Accessibility](accessibility.md)

## Contract

The 47 copy-owned HTML compositions cover marketing, editorial, services, portfolio, commerce, navigation, application and technical use
cases. Each contains its own Syntyr root, uses accessible native markup and requires
no application JavaScript. The data, testimonials and prices are illustrative, not live.

Gallery preview controls are wrapped in disabled fieldsets to prevent
accidental submissions to illustrative authentication, contact and newsletter
routes even when JavaScript is disabled. Unlike an inert form, disabled controls
retain a readable form structure and labels for assistive technology. A scoped
submit handler is a progressive fallback. The copyable HTML source and block
registry retain the original form actions and methods; host applications must
implement them securely.

The gallery script powers optional documentation search, theme switching and copy
buttons. Disable JavaScript and all forty static previews remain visible, with
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

## Optional scroll, parallax, and hover effects

Any copied block can opt into decorative animation by loading
[syntyr.motion.css](animation.md#website-block-effects-css-only) alongside its
existing CSS. Add `data-syn-scroll="rise"` or `data-syn-scroll="fade"` directly
to a heading or card in its original HTML; do not clone the block to create
an animation variant. A decorative background can use `data-syn-parallax`
with a separate media layer, and image tiles can use `data-syn-hover="zoom"`.

These are CSS-first progressive enhancements: unsupported browser versions
and users requesting reduced motion retain visible, static content. See the
[block effects guide and examples](animation.md#website-block-effects-css-only)
and the [live animation gallery](../examples/animation.html).

Use the existing static gradient wash with the optional motion module to
add a gentle animated background without inventing a new block variant.
`data-syn-gradient="drift"` works on `syn-gradient-wash` with a
`data-syn-gradient-content` foreground wrapper. Short editorial headings
may opt into `data-syn-text="underline"` or
`data-syn-text="glint"`. Motion and high-contrast fallbacks are explained
in the [animation guide](animation.md#animated-gradient-wash-composable-css).

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
shadcn-compatible universal-item registry from the same 40 MIT blocks and
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

## WordPress-inspired website section collection (alpha.5 candidate)

Twenty additional MIT site sections cover headers, footers, editorial publishing,
service-business pages, project portfolios, comparisons, integration directories,
newsletter/contact forms, and product collection showcases. All are standalone
copy-owned HTML files in blocks/snippets and use the same manifest and generated
gallery as the original twenty. Filter the gallery by Navigation, Editorial,
Services, Portfolio or Commerce.

These are HTML design references, not native Gutenberg editor blocks, a
WordPress plugin, a WooCommerce checkout, or live site integrations. For theme
integration, follow the WordPress guide, prefer the isolated alpha.5
syntyr.embed.css candidate inside existing themes, and verify on an
actual published page. Routes such as /services, /journal, and
/products are placeholders, not routes supplied by Syntyr.

Form snippets intentionally have native POST actions but no backend. Before
publishing, implement server validation, authorization where applicable,
CSRF/anti-spam protection, privacy policy and opt-in confirmation. Do not
claim a form is operational merely because it renders and submits.

The new section families add no new CSS API, premium source, runtime scripts,
bundled imagery, third-party assets, remote fonts or framework dependencies.
Free MIT blocks and commercial website-kit compositions stay separate.

## Additional native application and editorial patterns (alpha.5 candidate)

Seven independently copy-owned blocks complement the website sections without
adding another header/footer, article grid or comparison variant:
`auth-sign-in`, `auth-recovery`, `docs-layout`, `error-recovery`, `empty-state`,
`content-collection` and `mega-navigation`. All are built from the existing
Syntyr CSS primitives and ordinary HTML; only the content collection and mega
navigation need the separately optional recipes stylesheet.

The authentication forms are **design references**, not login or password-reset
services. Implement session management, CSRF protection, request throttling,
non-enumerating responses, token expiry and authorization in your host
application before enabling their routes. The content collection uses a native
GET form and navigation links; the host server owns real filtering, pagination
and query safety. The mega-navigation uses native `details` disclosure, not a
JavaScript menu runtime. Replace fictional sample URLs before publishing.

The block IDs are intentionally distinct from existing site-header, site-footer,
article-detail and comparison patterns. The canonical manifest supplies the
standalone snippets, gallery cards and shadcn-compatible registry payloads; a
regression test checks each public registry item against its source snippet.

## Four complete free website starter pages

The following alpha.5 reference pages are generated from the same reviewed
MIT block snippets, rather than duplicating their markup in a second template
system:

- [Business homepage](../examples/site-starter-business.html)
- [Editorial index](../examples/site-starter-journal.html)
- [Article detail](../examples/site-starter-article.html)
- [Service business](../examples/site-starter-services.html)

Run python3 scripts/build_site_starters.py to regenerate, or add --check
to verify reproducibility. The generator uses only the Python standard
library and adds no runtime dependency. These demonstrators are intentionally
noindexed, contain fictional information and have placeholder host URLs.
