# Syntyr visual page builder (experimental)

The [visual builder](page-builder.html) is a local-first, optional editing tool in the public Syntyr documentation. It assembles a small set of existing Syntyr CSS/HTML patterns; it is **not** an application framework, CMS, universal importer, SaaS hosting product, or complete GrapesJS integration.

## What works

- Add hero, feature-card, split-text, testimonial, FAQ, CTA, site header and footer sections from the palette.
- Search and insert **gallery components** from the generated `metadata/component-gallery.v1.json` contract (16 curated examples in the current source candidate). Edit their visible text, placeholders and safe links; examples carry the CSS modules needed and can be repeated without duplicate input IDs.
- The gallery is loaded from the same origin as the builder. If the JSON is missing, the original eight semantic page sections remain available; no external API or build service is required.
- Select sections in the outline or preview, edit their text and links, reorder with buttons or drag-and-drop, and remove sections. Keyboard focus remains in the outline during reordering; native FAQ disclosures open in the preview.
- Switch among themes available to the unreleased source candidate and preview true 1200px desktop, 760px tablet, and 390px mobile iframe viewports. Narrow canvases scroll rather than silently scaling the device viewport.
- Undo and redo editing changes (limited in-memory history).
- Export an HTML file and matching Syntyr CSS as separate files and host them alongside each other.
- Download a JSON project and reopen that JSON to restore editability.

The builder runs entirely in your browser. It does not upload projects or require a server account. Save the JSON file before closing the page: unsaved edits are not persisted.

## Framework-independent output

Gallery-backed blocks use a `gallery:<catalog-example-id>` type with only typed,
string-valued editable properties. The trusted native HTML fragment comes from
the generated, publicly published manifest, **never from imported project JSON**.
Imported projects referencing missing gallery definitions or incompatible
editable-field schemas fail validation rather than executing arbitrary markup.
A changed definition with the same field names can still import, potentially
placing saved strings in different locations. Preserve an exported HTML copy
for long-term rendering when the optional source catalog changes. The manifest is an **unreleased alpha.5 source candidate**; these
examples are not promised in the published alpha.4 release.

The document schema is syntyr.page.v1, with schema, title, theme, and an ordered array of id, type, and props blocks. The canonical validation and renderer are in page-builder-model.mjs, a dependency-free ESM module with no browser globals.

The exported index.html uses ordinary HTML sections, anchors, buttons-styled links, native FAQ disclosures, and existing syn-* classes. The local syntyr.all.css stylesheet must be hosted next to it; the page does not contain React, a builder script, or Syntyr editor dependencies. You can instead load CSS modules required by your chosen components using the [distribution guide](distribution.md).

An HTML export does **not** preserve editor metadata sufficiently for arbitrary HTML import; the JSON project is the editable source of truth. Proprietary embeds, CMS integrations, React/Vue/Svelte code generation, hosting, and collaboration are not yet implemented.

## Security boundaries

Imported project data is strictly validated: only recognized string block types and string fields, unique safe IDs, a known theme, up to 50 blocks, bounded property lengths, and a 16 MiB UTF-8 JSON import cap compatible with the maximum valid exported project size. Repeating gallery snippets scopes internal HTML IDs and their `for`,
`list`, `commandfor`, and ARIA references to each block instance.
The gallery manifest is restricted to checked-in, validated markup; links
are normalized to local anchors/paths or HTTPS. Every user-controlled text value is HTML escaped, and unsupported href protocols (including javascript: and data:) are rendered as #. The preview is inside a sandboxed iframe without script or form-submission permissions. The exported result is still **static HTML**, not a backend application.

This experimental tool is deliberately separate from the MIT CSS core. It uses only small first-party documentation scripts; adopting a heavyweight editor engine such as GrapesJS should be justified through comparative testing, not as a mandatory dependency.

## Maintainer verification

Run from repository root:

    node --test tests/page_builder_model.test.mjs tests/page_builder_gallery.test.mjs
    python3 -m unittest tests.test_cloudflare_site -v
    python3 scripts/build_cloudflare_site.py --check

For the optional browser smoke test:

    python3 tests/page_builder_browser.py

The browser smoke test requires Playwright and a local browser installation. Validate keyboard access, small screens, malicious imported JSON, and download/export before treating this as a stable product.
