# Getting started with Syntyr CSS

Syntyr is a **scoped CSS design system** for ordinary HTML. You do not install a JavaScript component framework or adopt a build pipeline to use it. This guide starts with the **published, pinned v0.3.0-alpha.4 release**; source-only alpha.5 features are called out separately.

For the shortest possible setup, use explicit `syn-*` classes. For mostly unclassed markup, add the optional semantic stylesheet and `syn-semantic` scope.

## 1. Install the published stylesheet

Download [v0.3.0-alpha.4](https://github.com/dporkka/syntyr-css/releases/tag/v0.3.0-alpha.4), place `dist/syntyr.core.css` into your own project's static directory as `/css/syntyr.core.css`, and load it once:

```html
<link rel="stylesheet" href="/css/syntyr.core.css">
```

For a throwaway prototype, use the [version-pinned public URL](https://syntyr-css.pages.dev/v/0.3.0-alpha.4/syntyr.core.css):

```html
<link rel="stylesheet" href="https://syntyr-css.pages.dev/v/0.3.0-alpha.4/syntyr.core.css">
```

Self-host for production so availability and release rollouts remain under your control. Do not point a page at a hypothetical alpha.5 release path: alpha.5 is currently **unreleased source**, not a tagged or npm-published release.

## 2. Give Syntyr a scope

The `.syn-root` class establishes the token and style scope. Put `data-syn-theme` on that element to pick a theme.

```html
<main class="syn-root syn-page" data-syn-theme="studio">
  <section class="syn-panel" aria-labelledby="overview-title">
    <h1 id="overview-title" class="syn-heading">Overview</h1>
    <p class="syn-muted">Review the active projects.</p>
    <a class="syn-button syn-button--primary" href="/projects">Open projects</a>
  </section>
</main>
```

Use a link for navigation, a button for a local action, and valid `href`, `action`, and `name` attributes for real workflows. Styling an element never adds event handlers or backend behavior.

Published themes: `studio` (neutral SaaS), `grid` (high-contrast control panels), and `noir` (dark editorial). Four additional themes exist only in the unreleased alpha.5 candidate. You can scope nested areas with `data-syn-theme`; see [theme customization](theme-customization.md).

## 3. Choose explicit or semantic styling

**Explicit classes (core alone):** start here when introducing Syntyr into an existing site or using a component library. Add classes only to the elements Syntyr should style.

**Semantic opt-in (two published stylesheets):** load `syntyr.semantic.css` after core and add `syn-semantic` to the Syntyr subtree. This styles native, largely unclassed elements while leaving other parts of your app alone:

```html
<link rel="stylesheet" href="/css/syntyr.core.css">
<link rel="stylesheet" href="/css/syntyr.semantic.css">
<section class="syn-root syn-semantic" data-syn-theme="studio">
  <form method="post" action="/subscribe">
    <label for="email">Email address</label>
    <input type="email" id="email" name="email" autocomplete="email" required>
    <button type="submit">Subscribe</button>
  </form>
</section>
```

A server must handle `/subscribe`. Apply the appropriate CSRF/authentication checks and response validation in that server; the form above is intentionally only a presentation example.

For HTMX and similar frameworks that add transient classes, `data-syn-semantic` can opt an element into semantic styling even while it has other classes. See [framework integrations](framework-integrations.md).

## 4. Add optional modules only as needed

Load optional styles **after core** and do not repeat the same stylesheet:

| Need | Add after core | Release availability |
| --- | --- | --- |
| Class-light native HTML | `syntyr.semantic.css` | Published alpha.4 |
| SaaS shells, pricing, and page compositions | `syntyr.recipes.css` | Published alpha.4 |
| Request-state style bridge | `syntyr.server.css` | **Unreleased alpha.5 source** |
| Visualization presentation | `syntyr.viz.css` | **Unreleased alpha.5 source** |
| Symbols, native recipes, geometry, motion, utilities | Their corresponding `syntyr.*.css` modules | Verify in the [distribution guide](distribution.md) and actual installed version |

`syntyr.recipes.css` supplies visual layouts, not filters, pagination or persistence. `syntyr.viz.css` styles HTML and SVG markup **you supply**; it does not generate charts.

If testing the **unreleased alpha.5 source**, you can use **one** `dist/syntyr.semantic-bundle.css` instead of loading core plus semantic, or choose one complete `dist/presets/{minimal,saas,cinematic}.css` file. Do not load bundles and their constituent CSS together.

For pinned production assets, use the actual published release and load no source-candidate modules until they are released. See [distribution](distribution.md) and [package-manager status](package-managers.md).

## 5. Use it in your framework

Syntyr does not care what emits the HTML. The only framework-specific changes are usually stylesheet inclusion, HTML attribute syntax, and how state or requests are handled.

**React / Next.js:**

```jsx
export function Overview() {
  return (
    <main className="syn-root" data-syn-theme="studio">
      <a className="syn-button syn-button--primary" href="/reports">
        Reports
      </a>
    </main>
  );
}
```

Import or serve a *versioned CSS file* through your app's normal stylesheet pipeline. For Next.js, follow its global CSS import rules; Syntyr itself has no React dependency.

**Server templates (Go, Rust, Rails, Laravel, Phoenix, Django):** include the CSS in the layout and emit ordinary `class` attributes. You do not need a runtime adapter.

**HTMX / Datastar / Turbo / LiveView / Livewire:** keep request behavior in the host library, preserve forms and links as fallbacks where feasible, and use the optional request-state bridge **only if your installed version actually contains it**. Examples: [HTMX source](https://github.com/dporkka/syntyr-css/blob/main/examples/htmx.html) and [Datastar source](https://github.com/dporkka/syntyr-css/blob/main/examples/datastar.html). Their live request demos need a local server; opening the static HTML file alone does not provide an API.

Read the [full integration guide](framework-integrations.md) for CSS ordering, DOM replacement boundaries, and framework-specific behavior.

## 6. Verify your page

- In the browser's Network tab, ensure the CSS file returns a successful response and matches the version you intended.
- Confirm the target subtree has `syn-root`. For plain native HTML, also check `syn-semantic` **and** that semantic CSS loaded after core.
- Inspect one real selector in DevTools and check that another application's global styles are not overriding the Syntyr rule.
- Test at 320 CSS pixels, 200% and 400% zoom; use keyboard-only navigation, reduced motion, and forced-colors modes where supported.
- Test real validation, form submission, loading, and error states in your application. Syntyr does not implement any of these behaviors.
- If an element still looks wrong, use the [troubleshooting checklist](troubleshooting.md), [component contract](components.md), and [accessibility guide](accessibility.md).

**Next:** browse the [component catalog](catalog.html), [recipes](recipes.md), or [theme tokens](theme-customization.md). AI tooling can start from the [agent quickstart](ai-quickstart.md) and the repository [llms.txt](../llms.txt).
