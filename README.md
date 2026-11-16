# SYNTYR CSS

**Framework-neutral, CSS-first styling for HTML applications and websites.** Syntyr supplies scoped components, design tokens, themes, and optional layout recipes—**without a JavaScript runtime, required build tool, or remote assets**.

[Live site](https://syntyr-css.pages.dev/) · [Component catalog](https://syntyr-css.pages.dev/docs/catalog.html) · [Examples](https://syntyr-css.pages.dev/docs/) · [Guides](https://syntyr-css.pages.dev/docs/guides.html) · [Source and releases](https://github.com/dporkka/syntyr-css/releases)

Use it with server-rendered HTML, HTMX, Datastar, Rails, Laravel, Go templates, Phoenix, React, Vue, Svelte, Astro, or other systems that render HTML. Syntyr is **not** an authentication library, data grid engine, chart renderer, or JavaScript component framework.

## Release status: read before installing

| Version | Availability | What you can rely on |
| --- | --- | --- |
| **v0.3.0-alpha.4** | [Published, immutable release](https://github.com/dporkka/syntyr-css/releases/tag/v0.3.0-alpha.4) | Core CSS with **Grid, Noir, and Studio** themes; published modules and examples |
| **v0.3.0-alpha.5** | **Unreleased source candidate on `main`** | Seven palettes, one-file presets, `syntyr.semantic-bundle.css`, utilities, and additional experimental modules |

The checked-in documentation and `dist/` describe the **alpha.5 source candidate** unless explicitly labeled as alpha.4. Do not mistake a file on `main` for a published release, use an alpha.5 CDN URL that does not exist, or assume `@syntyr/css` has been published to npm. Alpha APIs may change; see [API stability](docs/api-stability.md).

## Quick start: published alpha.4

1. Copy `syntyr.core.css` from the [published release](https://github.com/dporkka/syntyr-css/releases/tag/v0.3.0-alpha.4) to your site's static assets. Self-host a pinned copy for production.
2. Load the stylesheet once and add `syn-root` to the element whose descendants Syntyr will style.
3. Use native HTML and opt-in `syn-*` classes:

```html
<link rel="stylesheet" href="/css/syntyr.core.css">

<main class="syn-root syn-page" data-syn-theme="studio">
  <section class="syn-panel" aria-labelledby="welcome-title">
    <h1 id="welcome-title" class="syn-heading">Project overview</h1>
    <p class="syn-muted">Your workspace is ready.</p>
    <a class="syn-button syn-button--primary" href="/projects">View projects</a>
  </section>
</main>
```

For a quick prototype, the published CSS is also available at [the versioned URL](https://syntyr-css.pages.dev/v/0.3.0-alpha.4/syntyr.core.css). Pin and self-host before relying on it for production. The `href` in the example must point to a file you actually copied; Syntyr does not inject styles automatically.

**Prefer ordinary semantic HTML?** Load the published `syntyr.semantic.css` **after** `syntyr.core.css`, then opt in with `class="syn-root syn-semantic"`:

```html
<link rel="stylesheet" href="/css/syntyr.core.css">
<link rel="stylesheet" href="/css/syntyr.semantic.css">
<main class="syn-root syn-semantic" data-syn-theme="studio">
  <article>
    <h1>Account settings</h1>
    <form action="/settings" method="post">
      <label for="display-name">Display name</label>
      <input id="display-name" name="display_name" required>
      <button type="submit">Save changes</button>
    </form>
  </article>
</main>
```

The form needs a real endpoint and appropriate security controls; CSS does not handle submission. See the [step-by-step getting-started guide](docs/getting-started.md) and [troubleshooting](docs/troubleshooting.md).

## Choosing a stylesheet

| Need | Load | Notes |
| --- | --- | --- |
| Components and three published themes | `dist/syntyr.core.css` | Default starting point; explicit classes |
| Class-light semantic HTML | Core, then `dist/syntyr.semantic.css` | Scoped to `syn-semantic` |
| Application or marketing layouts | Core, then `dist/syntyr.recipes.css` | Layout only, not behavior |
| Request-state presentation (**alpha.5 source only**) | Core, then `dist/syntyr.server.css` | Host framework owns requests; not in published alpha.4 |
| Charts / data visualization appearance (**alpha.5 source only**) | Core, then `dist/syntyr.viz.css` | Styles supplied data; not in published alpha.4 |
| One-file class-light starter (alpha.5 **source only**) | `dist/syntyr.semantic-bundle.css` | Replaces core + semantic; do not duplicate |
| One-file preset (alpha.5 **source only**) | `dist/presets/minimal.css`, `saas.css`, or `cinematic.css` | Choose **one** complete preset |
| Other optional modules | `dist/syntyr.utilities.css`, `syntyr.symbols.css`, effects, motion, geometry, print, native recipes, data grid | Source candidate availability varies |

**Do not combine** a preset or `syntyr.all.css` with modules already included inside it. See [distribution](docs/distribution.md), [optional selective builds](docs/selective-builds.md), and the [versioned CSS contract](metadata/css-contract.v1.json). Syntyr's `--syn-*` custom properties, `syn-*` classes, and `data-syn-*` attributes are the styling API; use [theme customization](docs/theme-customization.md) instead of editing generated CSS.

## See it in use

- [Studio operations console](examples/operations-console.html), [SaaS workflow](examples/saas-workflows.html), and [Vertigo resource lifecycle](examples/vertigo-resource-workflow.html): representative HTML dashboards and forms with **illustrative data**, not working backends.
- [Component catalog](docs/catalog.html), [common UI](examples/common-ui.html), [native HTML elements](examples/native-elements.html), [enterprise data tables](examples/data-tables.html), and [form composition](https://syntyr-css.pages.dev/examples/form-composition.html).
- [Theme comparison](examples/themes.html), [three flagship layouts](docs/visual-composition.md), [original free HTML blocks](docs/blocks-guide.md), and [interactive playground](https://syntyr-css.pages.dev/docs/playground.html) ([source](docs/playground.html)).
- [Visualizations](docs/viz.md) via `syntyr.viz.css`; [symbols](docs/symbols.md) via `syntyr.symbols.css`; [intensity and geometry](docs/visual-intensity.md). Optional visuals do not add application logic.
- [Browser-native API demonstration](examples/native-apis.html), [headless interactions](docs/headless-interactions.md), and [performance-first demo](examples/performance-first.html).
- [Runnable Unpoly](https://github.com/dporkka/syntyr-css/blob/main/examples/unpoly.html) and [Turbo](https://github.com/dporkka/syntyr-css/blob/main/examples/turbo.html) integration fixtures: [local server](https://github.com/dporkka/syntyr-css/blob/main/examples/hypertext_server.py) and [cross-browser test suite](https://github.com/dporkka/syntyr-css/blob/main/tests/hypertext_browser.py) (development-only; not static Cloudflare demos).

All shipped repository source is MIT-licensed. Static examples can illustrate loading, search controls, buttons, and filters **without** implementing those behaviors.

## Documentation map

| Goal | Guide |
| --- | --- |
| Install, pick a version, or solve unstyled markup | [Getting started](docs/getting-started.md) · [Troubleshooting](docs/troubleshooting.md) · [Distribution](docs/distribution.md) |
| Find classes and modules | [Components](docs/components.md) · [Recipes](docs/recipes.md) · [Native patterns](docs/native-patterns.md) · [API stability](docs/api-stability.md) |
| Integrate with your stack | [Framework integrations](docs/framework-integrations.md) · [Lit / Web Components](docs/lit-integration.md) · [Tailwind and shadcn](docs/ecosystem-integrations.md) |
| Themes and access needs | [Theme tokens](docs/theme-customization.md) · [Theme editor](docs/theme-editor.html) · [Accessibility](docs/accessibility.md) · [Progressive enhancement](docs/progressive-enhancement.md) |
| Optimize or ship | [Progressive loading](docs/progressive-loading.md) · [Performance](docs/performance-validation.md) · [Cloudflare hosting](docs/cloudflare-hosting.md) |
| Use AI or editor tooling | [AI quickstart](docs/ai-quickstart.md) · [llms.txt](llms.txt) · [Editor integration](docs/editor-integration.md) · [Canonical DESIGN.md contract](DESIGN.md) |
| Contribute / report problems | [Contributing](CONTRIBUTING.md) · [Security policy](SECURITY.md) · [Architecture](ARCHITECTURE.md) |

Human-readable HTML guides: [documentation index](https://syntyr-css.pages.dev/docs/reference.html). Agent-friendly Markdown and the generated [llms-full.txt](llms-full.txt) use the same authored guides. The optional [package-manager workflow](docs/package-managers.md) currently applies to a **locally tested unpublished alpha.5 candidate**.

## Develop and contribute

Consumers do **not** need Python, npm, Playwright, or build tooling. Maintainers use Python 3 and the following checks:

```sh
python3 scripts/build.py --check
python3 scripts/export_api_metadata.py --check
python3 scripts/build_agent_docs.py --check
python3 scripts/build_doc_pages.py --check   # requires maintainer-only markdown-it-py
python3 -m unittest discover -s tests -v
python3 scripts/build_cloudflare_site.py --check
```

Before running the docs check, install `requirements-docs.txt` in a **maintainer-only** environment. When editing public Markdown, regenerate its committed HTML with `python3 scripts/build_doc_pages.py` and regenerate `llms-full.txt` with `python3 scripts/build_agent_docs.py`. Review the explicit Cloudflare publication allowlist before exposing new docs. Follow [CONTRIBUTING.md](CONTRIBUTING.md) for release and browser validation requirements.

## Boundaries, support, and licensing

Syntyr relies on browser-native controls and progressive enhancement; it does not polyfill unsupported browser features. Interactive data grids, comboboxes, sorting, persistence, authentication, and chart calculations remain application responsibilities. Validate real screens at high zoom, with keyboard navigation, assistive technology, reduced motion, and forced-colors modes; **alpha releases are not a production-v1 compatibility or accessibility guarantee**.

This repository, including its current themes, documentation, demos, and code, is licensed under [MIT](LICENSE). Possible separate premium kits are **proposals, not products currently for sale**; the current open-source functionality remains MIT. See [the project roadmap and change history](CHANGELOG.md) for progress.
