# Design assets: original SVG icons and CSS-only patterns

**Status:** Experimental alpha.5 source candidate; not yet published as a stable release.
Syntyr stays MIT licensed, framework-neutral and without consumer JavaScript,
network assets or a mandatory icon library. This guide describes files checked
into this repository, not a separately published npm package.

[View the five-pattern and icon gallery](../examples/design-assets.html) |
[Browse the existing 12 decorative recipes and 24 SVG examples](blocks.html) |
[View the asset provenance manifest](../metadata/design-assets.json)

## Installation without a package manager

Use the Syntyr core stylesheet and the optional background-pattern module.
Only load the modules you actually use. The full all-in-one distribution already
includes patterns, so do not load them a second time.

~~~html
<link rel="stylesheet" href="/dist/syntyr.core.css">
<link rel="stylesheet" href="/dist/syntyr.patterns.css">
<section class="syn-root" data-syn-theme="studio" data-syn-intensity="quiet">
  <div class="syn-panel syn-pattern syn-pattern--dots">
    <h2>Upcoming renewals</h2>
    <p>Illustrative dashboard content.</p>
  </div>
</section>
~~~

Patterns are intentionally background-only; they do not set layout, text
color, component semantics, animation or network image requests. Supported
classes: `syn-pattern--dots`, `syn-pattern--blueprint`,
`syn-pattern--diagonal`, `syn-pattern--hatch` and
`syn-pattern--scanlines`. Pair each with `syn-pattern` for a shared
configuration contract. These are **original Syntyr CSS recipes** that use
theme tokens; they are not copies of pattern.css or Open Props.

Tune `--syn-pattern-step` (default 1.5rem) for spacing and
`--syn-pattern-strength` (default 12%) for opacity. Existing
`data-syn-intensity="quiet|standard|cinematic"` regions provide
3%, 12% and 20% defaults respectively, and recompute inside nested regions.
Set a strength override in **application-owned unlayered CSS** if desired.
Use one background pattern per element: combining multiple pattern classes
does not promise stacked layers. Text and important status remain real HTML.

Decorative backgrounds disable automatically under
`prefers-contrast: more` and forced colors. The five new patterns are static
and do not animate, so they also meet `prefers-reduced-motion` without
JavaScript. For existing animated effects, see the separate
[visual-intensity guidance](visual-intensity.md).

## One design language, three existing theme presets

Rather than add three near-duplicate themes and color systems, use Syntyr's
existing palettes and separate visual intensity controls:

- **Enterprise**: `data-syn-theme="studio"` with `data-syn-intensity="quiet"`.
  Use regular panels, readable type, and restrained accents in SaaS dashboards.
- **Neon**: `data-syn-theme="grid"` with `data-syn-intensity="cinematic"`.
  Reserve strong cyan effects for hero panels, not dense content.
- **Noir**: `data-syn-theme="noir"` with `data-syn-intensity="standard"`.
  Warm accents and quiet atmospheric patterns work well for editorial layouts.

These are recommended **compositions**, not new `data-syn-theme` values.
Changing the theme updates CSS variables, including patterns, without
changing the markup or requiring scripting.

## Original SVG icons, without vendor runtime

Syntyr's existing gallery contains **24 original** single-color SVG examples.
Run `python3 scripts/export_icons.py` to reproduce their individual
`assets/icons/*.svg` files and `metadata/design-assets.json` manifest;
`--check` verifies bytes in CI. The exported SVG files are MIT licensed and
decorative by default. They are not copied from Lucide, Tabler or Radix.

~~~html
<!-- Decorative beside a readable label; the image needs no text alternative. -->
<button class="syn-button" type="button">
  <img src="/assets/icons/search.svg" width="20" height="20" alt="">
  Search
</button>
~~~

External `img` SVGs cannot be recolored reliably with the parent's
`currentColor`. For theme-colored icons, copy the inline SVG from the
[icons gallery](blocks.html) and use `class="syn-icon"`. When an icon
conveys unique information, use a real accessible label/description;
icon-only buttons need a meaningful `aria-label`. The browser supplies
no focus or keyboard behavior for a bare SVG icon.

**External packs remain optional.** Lucide (ISC), Tabler Icons (MIT),
Radix Icons (MIT), and Heroicons (MIT) can supply more icons, but their
files and licenses must be managed by the consuming application. Do not mix
stroke weights, proportions or optical sizes arbitrarily.

## Attribution and redistribution policy

The included 24 SVGs and five CSS patterns are original MIT Syntyr
implementations. The machine-readable asset list is
[metadata/design-assets.json](../metadata/design-assets.json), and
[THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) documents provenance.
**No third-party implementation source or illustration files are bundled.**
Open Props (MIT), Radix Colors (MIT), and pattern.css (MIT) are design
research references only. A repository license does not automatically license
included artwork, fonts, brand marks or trademark use.

To add a third-party asset in a future release, verify the license for its
exact source file and release, preserve required copyright and license texts
and source URLs, and update the asset manifest. Avoid bundling third-party
illustrations merely because their website permits free usage; restrictions
on redistribution may still apply.

## Maintainer validation

~~~sh
python3 scripts/export_icons.py --check
python3 scripts/build.py --check
python3 -m unittest discover -s tests -p test_design_assets_distribution.py -v
python3 -m unittest discover -s tests -v
~~~

All emitted CSS and SVG are standalone browser assets. The Python exporter
is a maintainer convenience, not a consumer runtime dependency.
