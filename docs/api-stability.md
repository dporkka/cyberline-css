# SYNTYR CSS public API and prerelease stability

**Status: experimental `0.3.0-alpha.5` candidate; no v1 stability promise.**
This document names the intended public contracts so that changes can be
reviewed consistently before `1.0.0`. It is not a new compatibility guarantee.

## Public surface and intended v1 boundaries

| Surface | Current policy | Intent for v1 |
| --- | --- | --- |
| `syntyr.core.css`, `.syn-root`, stable component classes | Public prerelease API | Stable selectors and behavior |
| Documented `--syn-*` design-token names | Public prerelease API | Stable names, not fixed default values |
| `data-syn-theme` and documented `data-syn-*` state hooks | Public prerelease API | Stable names and meanings |
| `syntyr.semantic.css` and `.syn-semantic` | Opt-in prerelease API | Stable scoped semantics after audit |
| `syntyr.recipes.css`, `syntyr.geometry.css` | Experimental, opt-in | Evaluate for individual stabilization |
| `syntyr.effects.css`, `syntyr.utilities.css`, `syntyr.motion.css` | Experimental, opt-in | Evaluate for individual stabilization |
| `syntyr.css`, `syntyr.all.css` | Public convenience bundles | Maintain documented contents/meaning at v1 |
| `terminal/palettes.json` | Optional example/palette asset | Separate compatibility decision from CSS |
| `integrations/`, `examples/`, documentation editor | Non-core adapters/showcases | No automatic CSS-core stability promise |

The `syn-*` selector namespace, `--syn-*` properties and `data-syn-*` attributes
remain the only Syntyr-specific styling namespace. ARIA states such as
`aria-pressed`, `aria-busy`, `aria-invalid` and native HTML state remain governed
by web-platform semantics, not a separate Syntyr state machine.

Core classes do **not** require an application build pipeline. The opt-in
semantic mode only styles elements under `.syn-semantic` within `.syn-root`.
Themes set design tokens; component selectors should not fork per theme. The
finite utilities are explicit overrides in their own final `syn.utilities`
cascade layer. Do not load a convenience bundle and its component modules
simultaneously.

## Compatibility and version policy

- Before v1: breaking prerelease changes are possible; document them in the
  changelog. Do not maintain obsolete aliases solely for alpha compatibility.
- After v1: breaking changes to stabilized selector names, attribute meanings,
  documented file entrypoints and core component behavior require a major
  version. Additions can use minor releases; corrections use patch releases
  when semantically compatible.
- Values and appearance are not identical across patch versions. Accessibility
  fixes may adjust color, spacing, focus or contrast without renaming tokens.
- Custom, undocumented selectors and implementation variables are not a
  supported extension API. Use documented tokens and composition instead.
- Versioned `/v/<version>/` CDN assets remain byte-for-byte immutable; prefer
  self-hosting or pinning a version for production deployments.

## Pre-1.0 release checklist

1. Confirm which individual classes and tokens merit permanent compatibility.
2. Finish keyboard, screen-reader, browser zoom and contrast review; automated
   scans do not establish WCAG conformance.
3. Validate the supported browser/version matrix on realistic applications,
   including nested themes, CSS utilities and semantic opt-in behavior.
4. Publish versioned docs, a reproducible CSS distribution and a complete
   migration note if prerelease contracts change.

See [`ARCHITECTURE.md`](../ARCHITECTURE.md) for feature-admission criteria,
layer ownership and dependency boundaries. Optional package integrations may
provide additional contracts but must never introduce a mandatory core
runtime dependency.
