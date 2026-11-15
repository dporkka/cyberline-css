# Syntyr architecture and maintenance policy

Syntyr is a framework-neutral CSS library, not a JavaScript component framework.
Its primary product is stable HTML/CSS conventions, not a build service. The
smallest working application must need only a local stylesheet and HTML.

## Non-negotiable invariants

1. **Zero CSS runtime dependencies:** no required JavaScript, package manager,
   network fonts, icons, CDN, server, or compiler for consumers.
2. **One styling contract:** public selectors use `syn-*`, custom properties
   `--syn-*`, and state/theme attributes `data-syn-*` (with semantic ARIA and
   native HTML states where appropriate). Avoid competing ways to express the
   same styling concern.
3. **Scoped by default:** Syntyr styles must not affect HTML outside
   `.syn-root`. Semantic element styling requires explicit `.syn-semantic`.
4. **Composable themes:** a theme changes tokens, not component implementations.
   Theme-specific component forks and cascade-specificity escalation are
   architectural defects to fix, not patterns to repeat.
5. **Native behavior first:** buttons, forms, `details`, `dialog` and `popover`
   retain their HTML semantics. Complex interactive widgets belong to the
   application or separately maintained packages, not the CSS core.
6. **One-way dependencies:** core CSS cannot import from `examples/`, `docs/`,
   `integrations/`, or a consumer framework. Optional adapters may depend on
   the public core but must never become core dependencies.
7. **Predictable releases:** generated CSS comes only from `src/`, is checked
   into `dist/`, and must exactly match the deterministic Python stdlib build.
   Published versioned CDN assets are immutable; consumers should pin a
   version or self-host it.

## Dependency direction

```text
src/tokens.css + src/base.css + src/components/*.css
                       |
              syntyr.core.css
                       |
            optional CSS modules
   semantic | recipes | geometry | symbols | effects | motion | utilities | print
                       |
       examples, integrations, templates, docs
                       |
          applications and websites
```

This is a consumption graph, not a requirement to load every module.
`syntyr.css` is the core-plus-effects convenience bundle;
`syntyr.all.css` includes all opt-in modules. Do not load bundles alongside
files they already contain. `scripts/build.py:distributions()` is the one
canonical distribution registry; the ZIP packager and Cloudflare site builder
consume it instead of maintaining separate CSS entrypoint inventories.

## Cascade policy

Layers have an explicit normal-declaration priority, earliest to latest:

```css
@layer syn.tokens, syn.base, syn.components, syn.semantic,
       syn.recipes, syn.geometry, syn.symbols, syn.effects, syn.motion, syn.utilities;
```

Component styles belong in `syn.components`. Optional finite utilities belong
in `syn.utilities` so explicitly applied utility classes can win over ordinary
component declarations without new specificity tricks, regardless of the
order in which component and utility modules appear. Optional print styling uses
a final `syn.print` layer (loaded after core and utilities) to override ordinary
component and utility presentation on paper. Author-defined unlayered
normal CSS takes priority over layered normal CSS; `!important` follows the
CSS cascade's reversed layer priority. Do not use `!important` for ordinary
component or utility styling. Accessibility-related reduced-motion overrides
are an existing documented exception.

See [the public API stability policy](docs/api-stability.md) for the specific
prerelease compatibility boundaries and v1 acceptance checklist.

## API stability and feature admission

Before 1.0, refine the public surface rather than carrying compatibility
aliases for experimental selectors. For 1.0+, version stable component classes,
core design-token **names**, state attributes and documented entrypoints under
semantic versioning. Token values and visuals may change for bug fixes and
accessibility; a stable name is not an immutable RGB value. Mark experimental
recipes, effects and integrations explicitly instead of silently promising
long-term compatibility.

Accept a new module, component or theme only when it:

- solves a reusable need that cannot be composed cleanly from existing HTML,
  tokens, classes and CSS features;
- works across the supported themes, zoom and responsive layouts without
  theme-specific copies;
- keeps the zero-runtime-dependency contract and passes regression checks;
- can be documented with a short example and a clear opt-in boundary;
- has a credible owner for its continuing maintenance cost.

Prefer removing duplicate rules and simplifying variants before adding new
features. Do not add a CSS compiler, framework runtime, NPM dependency,
custom widget system or site generator without measured demand.

## Maintainer checks and release gates

```sh
python3 scripts/build.py --check
python3 -m unittest discover -s tests -v
python3 scripts/package_release.py
```

Keep the full Playwright browser matrix, reflow, automated accessibility and
manual keyboard/assistive-technology checks as separate release-quality gates
(see `docs/accessibility.md` and `docs/accessibility-alpha5-review.md`). A
passing unit suite is not proof of WCAG conformance or cross-browser support.
Avoid accumulating near-identical version-labelled tests: retain valuable
regressions, but consolidate them into enduring behavior/contract tests when
refactoring those areas.

Report raw and gzip bytes for every build, without arbitrary CSS size
budgets or release failures based on byte ceilings. Browser behavior,
accessibility, and modular loading govern performance decisions. Runtime
JavaScript remains unnecessary; nonessential effects and recipes are opt-in.

Before any 1.0 release, settle the supported browser matrix, close the open
manual accessibility findings, and document precisely which selectors and
modules carry the stability promise.
