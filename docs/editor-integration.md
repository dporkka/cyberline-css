# Syntyr editor autocomplete and metadata

Syntyr's editor integration is **optional**. Applications still consume ordinary
prebuilt CSS, HTML, and custom properties without Node, JavaScript, or a build step.

## VS Code and compatible editors

For an opt-in local extension package that bundles these files without an extension runtime, see [ecosystem interoperability](ecosystem-integrations.md). The extension is not yet published to the VS Code Marketplace; the manual workspace integration below remains supported.

Copy these four generated files from the Syntyr release or repository into
your project, e.g. `./vendor/syntyr/metadata/`:

- `syntyr.html-custom-data.json` — HTML attribute values, including themes
- `syntyr.css-custom-data.json` — documented `--syn-*` custom properties
- `syntyr.code-snippets` — a curated set of class completion snippets
- `syntyr-api.json` — complete machine-readable index of classes, tokens and themes

Add the following to your **workspace** `.vscode/settings.json` (not required
for Syntyr consumers using other editors):

```json
{
  "html.customData": ["./vendor/syntyr/metadata/syntyr.html-custom-data.json"],
  "css.customData": ["./vendor/syntyr/metadata/syntyr.css-custom-data.json"]
}
```

Optionally copy `syntyr.code-snippets` to `.vscode/syntyr.code-snippets`.
This provides snippets for common `syn-*` classes in HTML and JSX/TSX. The
custom HTML data includes all classes as possible `class` attribute values,
but the extent of **class-name completion** varies by editor and extension;
do not assume it works identically in every language mode. CSS custom
property autocomplete also depends on the editor's CSS language support.

The JSON files are standard, inspectable data; other editors and integrations
can consume `syntyr-api.json` directly.

## Regenerate after CSS changes

From the Syntyr source repository:

```sh
python3 scripts/export_api_metadata.py
python3 scripts/export_api_metadata.py --check
```

The Python standard-library exporter scans `src/**/*.css`, strips comments,
deduplicates discovered classes and declared custom properties, adds
documented component override variables, and writes stable JSON and snippets.
`--check` fails if the checked-in outputs differ from source. Descriptions
are curated for core APIs and source-file-derived for others.

This is an editor convenience layer, **not** a Tailwind-style CSS compiler.
A class being present in the metadata does not mean its optional stylesheet
is already loaded. Check each item's `module` in the generated catalog and
load the corresponding Syntyr CSS distribution.

## Optional CSS dependency and version diagnostics

Syntyr can also diagnose duplicate stylesheet links, overlapping distribution
bundles (for example, `syntyr.core.css` loaded with
`syntyr.semantic-bundle.css`), and conflicting explicit release pins:

```sh
python3 scripts/syntyr_check.py --doctor --semantic index.html
python3 scripts/syntyr_check.py --doctor --format json index.html
```

The `--doctor` flag builds on the existing validator; it does not install or
change CSS. It reads the generated `distribution_sources` from
`metadata/syntyr-contract.json`, which comes from the canonical CSS build
registry. Keep the checker, metadata, and stylesheet release versions together.
Older contracts without this field are rejected instead of silently missing
overlaps.

An overlapping bundle, including a duplicated stylesheet, produces a
**warning** (exit code 0 if no errors). Two different explicit
`/v/<version>/` release pins produce an **error** (exit code 1), since
mixing different Syntyr releases is unsafe. Generated diagnostics include
filename, source position, severity, code and explanation. Normal validation
without `--doctor` is unchanged.

**Scope:** This is a static HTML check of Syntyr `<link rel="stylesheet">`
references. It does not infer versions for unpinned local assets, parse CSS
`@import` graphs, or inspect imports inside JS/TS build pipelines. When
using bundlers, validate the final loaded stylesheets and run browser tests.
Unknown host-application CSS is ignored. Duplicate warnings are advisory;
releases still need actual cross-browser and accessibility verification.

## Optional static HTML diagnostics

The generated `metadata/syntyr-contract.json` is Syntyr's machine-readable
development contract. It combines the **full source-discovered** class and token
inventory with the existing **curated** semantic component recipes, supported
theme/state values, and CSS distribution filenames. The contract is generated
by `python3 scripts/export_api_metadata.py` and checked by `--check`. Do
not edit it directly. The existing `metadata/components.json` remains a
curated subset and is not a complete list of classes.

The unreleased alpha.5 release ZIP candidate now includes both `scripts/syntyr_check.py` and its matching `metadata/syntyr-contract.json`, so the extracted archive can run the optional checker without a source checkout. The published alpha.4 ZIP does not include these tools.

To validate static HTML during development (Python 3.10+, standard library only):

```sh
python3 scripts/syntyr_check.py index.html examples/saas.html
python3 scripts/syntyr_check.py --format json index.html
# Opt-in, conservative native HTML checks (warnings do not fail the CLI):
python3 scripts/syntyr_check.py --semantic --format json examples/semantic-starter.html
python3 scripts/syntyr_check.py --stylesheets syntyr.core.css,syntyr.recipes.css partial.html
# Pipe generated markup into the same deterministic checker without a temporary file:
printf '<button class="syn-buttn">Save</button>' | python3 scripts/syntyr_check.py --format json -
# For fragments, supply the CSS modules actually installed in the consumer app:
cat fragment.html | python3 scripts/syntyr_check.py --format json --stylesheets syntyr.core.css -
```

### Agent-ready composition recipes

The same generated `metadata/syntyr-contract.json` includes an optional
`recipes` array curated in `metadata/components.json`. Each recipe declares:

- A stable `id`, purpose, example page and required CSS distributions.
- A native HTML `root` element and named `slots` with `tag`, `classes`,
  `optional` and `repeatable` fields.
- `variants` restricted to real, CSS-supported `data-syn-*` attribute values.
- `host_behavior` explaining what CSS **cannot** perform (server requests,
  selection, pagination, validation, focus or authorization).

Available recipes cover a CRM filter form, semantic resource table, app shell,
and validated form. Use a `.syn-root` ancestor for every composition, and load
all listed stylesheets in the documented order (core before optional recipes).
The contract's `slots` describe roles, **not a strict DOM nesting validator**;
authors must still use accessible native HTML in context. The host application
supplies state and behavior. No JavaScript component engine is required.

Source truth is the existing curated `metadata/components.json`, not another
hand-maintained metadata registry. After editing a recipe, run
`python3 scripts/export_api_metadata.py` to regenerate the contract;
`python3 scripts/export_api_metadata.py --check` detects drift. The exporter
rejects stale class names, missing CSS modules, unsupported variant values,
invalid example paths and duplicate slot names before publication.

The checker reports source positions, unknown literal `syn-*` classes, invalid
literal `data-syn-*` values, and missing optional CSS modules **when a Syntyr
stylesheet is linked or explicitly specified**. For full HTML documents with
an explicit `<html>` element, it also reports `unscoped-class` when a known
Syntyr component class is outside every `.syn-root` ancestor. Since CSS
selectors are scoped, those classes would otherwise silently render without
Syntyr styles. Plain HTML fragments are exempt because the embedding app may
supply the root; dynamic ancestor classes and inert `<template>` contents are
also exempt because their rendered scope is unknown.

With `--semantic`, a second standard-library pass checks literal HTML for
duplicate static IDs, missing form labels, unmatched `label for` and
`aria-labelledby`/`aria-describedby` ID references (the latter two only in
complete documents). It advises when an ordinary table row uses
`aria-selected` instead of `data-syn-state`, or when a headed data table
lacks a caption or other accessible name. Errors produce exit code 1; advisory
warnings are included in text/JSON output but do not fail the command unless
`--fail-on warning` is explicitly supplied for strict CI.
The mode is **off by default** to preserve existing integrations.

This is not an HTML conformance parser, a WCAG audit, or a template renderer.
It deliberately skips inert template content and avoids guessing what dynamic
attributes resolve to. Validate rendered server/framework templates and actual
screen-reader behavior separately. Static fragments may reference IDs supplied
by their embedding document, so cross-document references are checked only
when a full `<html>` document is supplied.

The checker recognizes local and version-pinned stylesheet paths (including
query parameters). Without a known Syntyr stylesheet, module-presence checks
are skipped, but root-scope checks still run for complete documents. Explicit
`--stylesheets` overrides stylesheet-link discovery.

Exit code 0 means no errors (including warnings-only), 1 means one or more
errors, and 2 means invalid arguments or unreadable files. Explicit
`--fail-on warning` makes warnings exit 1 as well. JSON diagnostics contain `file`, `line`,
`column`, `severity`, `code` and `message` fields. Input `-` reads HTML
from standard input and identifies findings with `file: "<stdin>"`; JSON stays
a top-level diagnostics array for backward compatibility. Agent-friendly
optional fields include `suggestions` (up to three real source-contract class
names with available stylesheet distributions), `class_name` and
`required_root` (unscoped component classes), `attribute` and
`allowed_values` (invalid theme or state), and `required_stylesheets` and
`loaded_stylesheets` (missing CSS modules). Suggestions are hints, **not**
automatic edits; confirm the target class exists in the **installed** release.

**Boundaries:** This is a static HTML checker, not a full HTML accessibility
auditor, runtime type checker, or an HTML/CSS build requirement. Dynamic
template class expressions are conservatively skipped. Component `elements`
describe composite examples rather than allowed tags for every constituent
class; the validator deliberately does not enforce those as strict rules.
JSX/TSX, HEEx, Blade, and Nulang template adapters would need separate
language-aware parsing. Semantic accessibility and actual loaded CSS still
need browser and keyboard checks. No script or generated manifest is shipped
to the browser by this integration.
