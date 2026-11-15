# Syntyr CSS distribution

**First time here?** Follow the [getting-started guide](getting-started.md) for one version-pinned stylesheet and a complete working page.

Syntyr CSS is MIT-licensed. No NPM install, JavaScript runtime, fonts,
icons, Sass compiler or CSS framework is required to use the distributed CSS.

## Recommended: self-host a versioned stylesheet

1. Download the asset from the [GitHub release](https://github.com/dporkka/syntyr-css/releases/tag/v0.3.0-alpha.4), or copy the matching file from the tag.
2. Put `syntyr.core.css` in your application's static CSS directory.
3. Load it normally:

```html
<link rel="stylesheet" href="/css/syntyr.core.css">
<section class="syn-root" data-syn-theme="grid">
  <button class="syn-button syn-button--primary">Initialize</button>
</section>
```

The stylesheet's path is *your* path; mount or copy the file there.
The above works with Go templates, plain HTML, Astro, HTMX, React and other
renderers. See [the framework integration guide](framework-integrations.md) for
HTMX request-state classes, optional semantic markers, and server-side fragments. Add `syn-page` to the root only if you want full-page min-height.

## Offline SaaS preview in the next release ZIP (unreleased alpha.5)

The alpha.5 source candidate now packages `examples/saas.html` together with
`dist/syntyr.core.css` and `dist/syntyr.recipes.css`. After building or
extracting the **alpha.5** ZIP, open `examples/saas.html` directly in your
browser. Its relative stylesheets resolve within the extracted archive, so it
requires **no internet connection, local server, npm, build step or runtime
JavaScript**. You can edit the HTML and CSS locally to test integration.

This is a static **illustrative SaaS dashboard**: fictional metrics, no real
account data, authentication, filtering, API calls, or backend actions. To use
it in an application, replace sample values with server-rendered data and wire
navigation and mutations to your own server. The already published **alpha.4**
release does *not* contain this packaged example; the next alpha.5 release
has not been published yet.

## One-file semantic starter (unreleased alpha.5 source)

For a Pico-like HTML workflow, `dist/syntyr.semantic-bundle.css` combines core and semantic CSS into a single file. Copy it to your static assets, then opt in on the region you want styled:

```html
<link rel="stylesheet" href="/css/syntyr.semantic-bundle.css">
<body class="syn-root syn-page syn-semantic" data-syn-theme="studio">
  <main class="syn-shell">
    <article><h1>Dashboard</h1><button type="button">Open</button></article>
  </main>
</body>
```

Only the controls and elements inside `.syn-root.syn-semantic` are styled semantically. This is **not** Pico's globally classless behavior: the root scope is deliberate. No script or build tool is required. [See the runnable starter](../examples/semantic-starter.html) and the [Pico migration guide](from-pico.md). **This file is not in the published alpha.4 release** and its `/dist/` URL is not an immutable release asset; pin a released version once alpha.5 is actually published. Do not load `core.css` or `semantic.css` alongside this bundle.

## Optional npm/package-manager distribution

A CSS-only `@syntyr/css` manifest is available in the alpha.5 repository candidate, but **it has not been published to npm**. See [package-manager installation and local tarball testing](package-managers.md) for supported imports and an explicit no-publication boundary. No package manager is required for the documented self-hosted stylesheet path.

## Optional themes and semantic HTML

Grid, Noir and Studio ship in the **same** core stylesheet; set
`data-syn-theme="grid"` or `data-syn-theme="noir"` or `data-syn-theme="studio"` on the scoped root.
You can nest differently themed elements.

The unreleased alpha.5 candidate adds Industrial, Terminal, Corporate and Minimal using the same scoped `data-syn-theme` contract. The published alpha.4 release includes Grid, Noir and Studio only.

Load `syntyr.semantic.css` after core **only** if you want automatic semantic
element styles within `.syn-semantic`. For static glows and decorative grid
effects, load `syntyr.effects.css` after core. SaaS, business and terminal layouts
are opt-in via `syntyr.recipes.css`. Optional frame geometry is in `syntyr.geometry.css`.
The alpha.5 working tree additionally provides `syntyr.utilities.css` for finite
layout helpers and `syntyr.print.css` for print-friendly reports. System-aware
Grid/Studio `data-syn-theme="auto"` is already included in core CSS, with
no additional stylesheet or runtime JavaScript. See the
[progressive-enhancement guide](progressive-enhancement.md) for examples.
The optional `syntyr.symbols.css` adds BYO-SVG icon sizing, literal Unicode styling and ASCII/box-drawing alignment without shipping fonts or icons; see [symbols and accessibility](symbols.md).

`syntyr.semantic-bundle.css` bundles core and semantic styles with scoped opt-in.
`syntyr.css` bundles core and effects. `syntyr.all.css` bundles all modules
while still requiring `.syn-semantic` to opt into semantic element styles.
Avoid loading these bundles alongside their component files: that duplicates CSS. Optional utilities live in the final `syn.utilities` cascade layer, allowing explicitly applied utility classes to override ordinary component declarations; see [the architecture policy](../ARCHITECTURE.md).

## Optional explicit selective build

Applications needing fewer core components can assemble a custom CSS file with
the Python standard-library-only `scripts/build_selective.py`. It does not scan
templates or purge individual selectors, and does not alter published assets.
See [selective builds and their limits](selective-builds.md).

## Pinned CDN for prototyping

```html
<link rel="stylesheet"
      href="https://syntyr-css.pages.dev/v/0.3.0-alpha.4/syntyr.core.css">
```

The first-party Cloudflare CDN serves frozen, checksum-verified CSS releases
from a global edge network. Unversioned `/dist/` URLs can change with builds;
pin `/v/<version>/` instead. The documentation's optional theme editor
has JavaScript, but the library CSS and consumer sites do not require it.
For production applications, copying the versioned CSS to your own origin
usually avoids an additional hostname connection.

## Release artifacts and guarantees

The published alpha.4 release contains seven SYNTYR CSS distributions. The
unreleased alpha.5 source candidate includes modular SYNTYR distributions,
including the optional utilities, print and symbols stylesheets, plus
the terminal ANSI palette JSON, this guide, MIT license, and README. No retired compatibility aliases are shipped. The ZIP is created deterministically using only
Python's standard library:

```sh
python3 scripts/build.py --check
python3 -m unittest discover -s tests -v
python3 scripts/package_release.py
```

Both visual themes and all essential components are MIT-licensed. Commercial
premium templates, if introduced, will be independently authored and sold
separately. This v0.3 alpha is **not** a v1 production compatibility guarantee;
cross-browser and full accessibility audits are still release gates.

The `syn-` selectors, `--syn-` custom properties and `data-syn-` attributes are the only supported source API.
