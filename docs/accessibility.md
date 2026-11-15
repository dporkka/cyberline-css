# Syntyr CSS accessibility validation

**Status:** experimental alpha; not a WCAG certification or professional audit.

## Latest candidate validation (November 15, 2026)

The unmerged candidate combining `main` at `cfab482` with PR #55 at
`6fdf594` passed **180 real Chromium/Firefox/WebKit viewport checks** and
**240 enlarged-text reflow cases** in the Playwright 1.64.1 Linux container.
The optional suites also passed 30 interaction tests, 2 simulated forced-colors checks, the theme editor across three widths, and a component playground check at two widths in all three engines.
A new 20-page axe-core scan found **zero confirmed automated rule violations**
while leaving **83 inconclusive `color-contrast` element targets across 10
page/rule groups** for manual review. None of those 83 are certified passes.
The GitHub head has successful Cloudflare and CodeRabbit checks but **no
confirmed Woodpecker status**. The published alpha.4 release is unchanged.

See [the dated, exact-revision candidate evidence and remaining release
gates](accessibility-alpha5-review.md). Native 200%/400% browser zoom, real
screen-reader testing and OS-level high contrast are still open.

## Historical post-merge results (November 14, 2026)

On `main` commit `b19c331` (after PRs #14 and #22), the Python suite
passed **155 tests**. The 16-page, three-viewport gallery matrix and 64
reflow cases per engine passed in Chromium **156.0.8078.4**, Firefox
**157.0**, and WebKit **27.2** using the pinned Playwright 1.64.1
Linux developer container. Twenty-three Chromium interaction
tests and the documentation theme-editor checks also passed.

axe-core 4.10.3 reported **zero confirmed automated violations** but
**345 inconclusive color-contrast element entries on 13 of 16 pages**.
These remain open for manual review. Live Cloudflare assets sampled against
the reproducible 63-file allowlisted build matched byte-for-byte; private
repository paths returned 404. Cloudflare's exact-head build passed, but
an independent Woodpecker pipeline execution has not been verified.

See [the historical per-page counts and updated candidate evidence](accessibility-alpha5-review.md).
This is not WCAG certification or verification of real zoom, screen-reader
behavior, or native OS high-contrast mode.

## What is and is not covered

- Source contracts: native HTML, semantic labels, opt-in scoping, predictable
  focus-visible outline, reduced-motion support, and forced-color hooks.
- Real browser matrix: Chromium, Firefox, and WebKit on desktop/mobile viewport widths,
  testing navigation, table semantics, native popover, disclosure, and overflow.
- Automated accessibility: axe-core WCAG 2.0/2.1/2.2 A/AA tagged checks on the
  20 public showcase and example pages. The tool may return
  **incomplete/manual-review** findings even with zero confirmed violations.
- Still needed: screen reader testing (NVDA + Firefox or Chrome, VoiceOver +
  Safari), actual browser zoom at 200% and 400%, touch target examination,
  interactive error states, font reflow and low-vision inspection.

## Reproduce the tests without installing production dependencies

Run the standard library contracts and optional Playwright checks:

```sh
python3 scripts/build.py --check
python3 -m unittest discover -s tests -v

# Dev-only installation; choose your package/environment manager.
python3 tests/browser_test.py
python3 tests/browser_matrix.py --browsers chromium firefox webkit
python3 tests/reflow_test.py --browsers chromium firefox webkit
python3 tests/minimalist_browser.py --browsers chromium firefox webkit
```

For a pinned axe-core 4.10.3 audit, provide the checker at test time. No
JavaScript file is shipped to application consumers:

```sh
curl -fsSL https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.3/axe.min.js -o /tmp/axe.min.js
python3 tests/axe_audit.py --axe-file /tmp/axe.min.js \
  --report /tmp/syntyr-axe-targets.json \
  --summary /tmp/syntyr-axe-summary.json
```

For reproducible WebKit on an isolated testing host with Podman or Docker, clone
the repository to a directory that the container can read and run:

```sh
podman run --rm --shm-size=1g -v "$PWD":/work:ro,Z -w /work \
  mcr.microsoft.com/playwright/python:v1.65.2-noble \
  bash -lc 'python3 -m pip install -q playwright==1.65.2 && \
    python3 tests/browser_matrix.py --browsers chromium firefox webkit && \
    python3 tests/reflow_test.py --browsers chromium firefox webkit'
```

The image supplies browser binaries and native dependencies, not the Python
Playwright package. This test-only container may download packages and should
be run against trusted code. The `:Z` mount flag is Podman/SELinux-specific;
adjust for Docker hosts. Keep the Python and browser versions aligned.

The remote URL is part of a **developer-only test**, not a browser runtime
dependency. Pin the checker release, review its MIT license, and verify its
provenance if incorporating it into build infrastructure.

## Earlier automated baseline (November 14, 2026, unreleased alpha.5)

Against post-merge `main` commit `6109b79`, an isolated Playwright v1.65.2
Linux container passed **126** page/viewport cases (14 pages × 3 widths × 3
engines) and **168** enlarged-text reflow cases (14 pages × 4 width/font
configurations × 3 engines). Browser-reported versions: Chromium
159.0.8154.6, Firefox 159.0 and WebKit 27.2. These versions describe a
specific passing test environment; they are not a promise of broader browser
support. Chromium additionally passed 17 interactive browser checks, two
simulated forced-colors checks and three documentation theme-editor viewport
checks in the developer environment.

The axe-core 4.10.3 WCAG-tagged scan found **0 confirmed automated violations**
across 14 pages, alongside **11 incomplete rule results encompassing 325
individual nodes**. Gradients, pseudo-elements and obscured backgrounds cause
most incomplete results; a missing automated verdict is **not** a passing
contrast measurement. Generate a selector-level local review list with:

```sh
python3 tests/axe_audit.py --axe-file /tmp/axe.min.js \
  --report /tmp/syntyr-axe-manual-review.json
```

A subsequent post-merge investigation of `4a623d0` confirmed that live
Cloudflare Pages serves identical CSS and selected documentation assets. A
supplemental Chromium pixel-sampling pass at 1280, 390 and 320 px found no
below-threshold contrast among **944 sampled element/viewport observations**
(19,689 background-pixel samples). The lowest was 4.65:1; a textarea's
placeholder was evaluated separately at 10.14:1. Sampling does **not**
resolve axe's 325 inconclusive color-contrast targets into certified passes.
See the detail and remaining exceptions in the review document.

See [`accessibility-alpha5-review.md`](accessibility-alpha5-review.md) for
per-page counts and the remaining manual release gates. In particular, the
browser harness modifies root font size; this is not equivalent to genuine
200%/400% browser zoom; simulated forced colors do not represent all native OS contrast modes;
and neither an axe scan nor automated keyboard actions constitute screen-reader
validation. Native HTML dialog invoker command support also varies by browser.

## Manual checklist

1. Tab from the top of every page; test visible focus, no keyboard traps and
   skip-link behavior. Open and dismiss popovers/dialogs with keyboard.
2. At 200% and 400% zoom, inspect all content at narrow widths; no clipped
   actions, invisible labels or lost table information.
3. Test one screen reader per major browser engine for headings, landmarks,
   table captions, form labels and live status; document the actual device,
   browser version and assistive technology.
4. Force-colors/high-contrast: check panel separation, focus and form controls.
5. Disable animations in system settings and ensure nothing depends on motion.
6. Validate both the default Grid/Noir palettes and any project-specific
   token overrides for text contrast and non-text essential indicators.


## Optional system palette and intrinsic layout checks

The [minimalist patterns example](../examples/minimalist-patterns.html)
uses a CSS-only `auto` palette (Studio for light, Grid for dark),
classless form controls and intrinsic layouts. Its optional browser test
checks both OS color-scheme emulations, an explicit nested Noir region,
native checkbox/radio label layout, keyboard focus and mobile wrapping.

These automated checks do **not** replace manual audits at actual 200% and
400% browser zoom, assistive-technology operation, or customized palette
contrast validation. Record browser engine and OS when testing these paths.

## Experimental native-HTML semantic coverage (unreleased branch)

The optional `syntyr.semantic.css` now also presents native `search`, `figure`, `figcaption`,
`mark`, `kbd`, `output`, `meter` and scrollable `pre` regions. These styles apply
only inside an opted-in `.syn-semantic` subtree and do not implement
application behavior.

The development-only `tests/native_semantic_browser.py` checks Chromium,
Firefox and WebKit at 320px and 900px: the `mark` foreground/background pair
has at least 4.5:1 computed contrast in seven named palettes and automatic
light/dark mode; forced-colors emulation keeps it distinguishable; the native
GET form works without JavaScript; removing `.syn-root` removes the styling.
At 320px it checks horizontal document overflow with 200% and 400% *root
font-size enlargement*, including a scrollable code block.

These tests are **not** actual browser 200%/400% zoom, manual OS high-contrast
inspection, NVDA/VoiceOver validation, or a WCAG conformance audit. The
pre-existing inconclusive axe contrast cases and manual release gates remain
open. Use the separate [native example](../examples/native-elements.html)
for representative manual checks after publishing.

## Post-merge native-element review follow-up (November 15, 2026)

The native HTML example received four confirmed actionable review findings after
PR #38 merged. The follow-up fixes make its horizontally scrollable `pre`
region keyboard-focusable with an accessible name/region role, allow long `kbd`
chords to wrap, preserve readable foreground color for `mark > code`, and
strengthen the browser regression to verify actual internal scrolling and
keyboard focus instead of merely checking `scrollWidth >= clientWidth`.

Reproducible checks on the follow-up worktree:

- New unit contracts: 11 native-element tests pass; the full stdlib suite
  passed 189 tests before final documentation/rebase.
- Developer-only Playwright smoke: Chromium, Firefox, WebKit each passed
  across seven themes, light/dark auto, 320px/900px widths, forced-colors
  emulation, 200%/400% root-font enlargement and keyboard access to the
  scrollable SQL example.
- Shared browser matrix: all three engines passed 18 pages at three viewports.
- Shared reflow matrix: all three engines completed 72 checks each (216 total).
- Pinned axe-core 4.10.3 audit: **0 confirmed automated violations**, with
  **10 incomplete rule checks** across the 18 included pages. The new
  `examples/native-elements.html` page reported 0 violations and 0
  incomplete checks. Other pages' inconclusive findings remain manual-review
  items; these results are not blanket color-contrast certification.

### Outstanding human validation (not yet performed)

1. With **VoiceOver + Safari** and **NVDA + Firefox/Chrome** (Orca + Firefox
   can be supplementary on Linux), navigate to
   [the native HTML example](../examples/native-elements.html); verify the
   "SQL query example" region is named, focusable with Tab, and responds to
   horizontal scroll keys, without trapping focus.
2. In a real browser, set **200% and 400% browser zoom**, not only the root
   font-size test harness. At a 320 CSS-pixel effective viewport, verify
   readable captions, long keyboard shortcuts, full access to the code
   example, visible focus and no clipped form action.
3. With an actual OS high-contrast/forced-colors mode, distinguish highlights,
   focus rings, and selected controls. Also examine all axe inconclusive
   contrast targets from the main release accessibility report.
4. Record device, assistive technology version, browser version, observed
   behavior, any defects, and reviewer sign-off before claiming WCAG
   conformance or closing the manual release gate.

These are QA instructions, not evidence that human assistive-technology or
browser-UI zoom testing has happened.

## Searchable component catalog coverage (November 15, 2026)

The documentation-only component catalog has been added to the normal browser,
reflow, and axe-core matrices rather than relying only on static contracts.
It contains ten rendered component examples. With JavaScript disabled, the
examples and native HTML source disclosures remain available. Enhanced search,
empty state, live result count and clipboard/keyboard fallback were checked
in both Chromium and Firefox.

Exact-branch developer-only verification:

- Chromium and Firefox: **19 pages × 3 viewports** each, including the catalog
  interactions, passed.
- Chromium and Firefox: **76 enlarged-root-font reflow cases per engine**
  passed. This is **not** genuine browser-UI zoom.
- Local axe-core: **zero confirmed automated violations** across the 19
  audited pages, with **10 incomplete rule checks** requiring manual review.
  The catalog contributed one incomplete color-contrast rule with two nodes
  in the featured pricing demo: axe cannot infer its gradient background.
- For the catalog Studio palette, a source-token-based conservative calculation
  gives approximately **13.79:1** for dark #15233a text against the strongest
  9% blue-accent overlay on white. This is theoretical CSS compositing, not
  sampled pixels or a conformance certification.
- WebKit was **not** validated on this exact branch: the Gertrude test host
  lacks libevent-2.1.so.7.

The remaining release gates are genuine browser 200%/400% zoom, screen readers,
native high-contrast inspection, and manual resolution of incomplete axe
targets. Do not present these findings as WCAG conformance certification.
