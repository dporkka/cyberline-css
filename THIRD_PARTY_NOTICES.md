# Third-party notices and provenance

## Shipped Syntyr artwork and source

Syntyr's own CSS, code, HTML examples, and 24 optional original SVG icons in
`assets/icons/` are authored for Syntyr under the repository MIT license.
The five patterns in `src/patterns.css` are original implementations.
`blocks/icons.json` is the authoritative SVG source; the exporter generates
both the SVG files and the asset-level index at `metadata/design-assets.json`.

**No third-party icon paths, illustrations, fonts, CSS source, or design
templates are vendored in this release candidate.** The optional symbols CSS
module is vendor-neutral and can style consumer-owned icon artwork.

## External design research only; no redistributed files

| Reference | Upstream license for the referenced project | Upstream |
| --- | --- | --- |
| Lucide | ISC | https://github.com/lucide-icons/lucide |
| Tabler Icons | MIT | https://github.com/tabler/tabler-icons |
| Radix Colors | MIT | https://github.com/radix-ui/colors |
| Open Props | MIT | https://github.com/argyleink/open-props |
| pattern.css | MIT | https://github.com/bansal-io/pattern.css |

These entries **do not imply Syntyr bundles or relicenses upstream assets**.
Licenses and rights for individual third-party fonts, images and trademarks
must be separately verified before copying or redistributing them.
Syntyr's independently implemented visual patterns merely follow general
web-design techniques.

Other research references, including Pico CSS, Chota, Tailwind CSS and Tailwind
Plus, are discussed in Syntyr's research documents. No Tailwind Plus code,
component markup, screenshots, illustrations, icons, templates or other
proprietary material has been copied.
