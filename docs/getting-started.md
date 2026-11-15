# Getting started with Syntyr CSS

Build a useful page with **one stylesheet and semantic HTML**. Syntyr ships
plain CSS: no Node.js, JavaScript runtime, provider, build plugin, or package
manager is required in your application.

> **Release boundary (November 2026):** The latest published release is
> [v0.3.0-alpha.4](https://github.com/dporkka/syntyr-css/releases/tag/v0.3.0-alpha.4).
> The repository's 0.3.0-alpha.5 source is an **unreleased candidate**.
> The CSS examples below work with published alpha.4; the optional static
> HTML checker described later is packaged only in the proposed alpha.5 ZIP.

## 1. Copy the released CSS

Download the **published alpha.4 ZIP**, extract it, and copy
`dist/syntyr.core.css` into your site's public CSS directory, for example
`public/css/syntyr.core.css`. The file is ready to use as-is.

For a quick preview, you can use the
[immutable version-pinned CDN asset](https://syntyr-css.pages.dev/v/0.3.0-alpha.4/syntyr.core.css).
For production, self-hosting the pinned asset avoids an extra network origin.

## 2. Paste a complete working page

Save this as `index.html` in a site that serves the copied stylesheet at
`/css/syntyr.core.css`:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>My first Syntyr page</title>
  <link rel="stylesheet" href="/css/syntyr.core.css">
</head>
<body class="syn-root syn-page" data-syn-theme="studio">
  <main class="syn-shell" id="main">
    <article class="syn-panel">
      <h1 class="syn-heading">Project overview</h1>
      <p class="syn-text">A page built with HTML and one CSS file.</p>
      <a class="syn-button syn-button--primary" href="/projects">
        View projects
      </a>
    </article>
  </main>
</body>
</html>
```

Serve the directory with your existing application server. If you open this
HTML directly as `file://`, replace the `/css/` URL with the actual
relative path to the stylesheet. Replace the example `/projects` link with
a real route in your application.

Use `syn-root` around the part of the page you want Syntyr to style.
Without that scope, component classes will not receive their Syntyr styles.
Change `data-syn-theme` to `grid` or `noir` to use either of the
other published alpha.4 themes.

## 3. Choose the *minimum* CSS you need

- **Default:** `syntyr.core.css` — tokens and explicit component classes.
- **Optional semantic HTML:** load `syntyr.semantic.css` **after** core;
  add `syn-semantic` to the scoped root to style ordinary HTML elements.
- **Optional SaaS layouts:** load `syntyr.recipes.css` after core when using
  documented recipes.
- **Optional decorative effects:** use `syntyr.effects.css` only if needed.

Do not combine `syntyr.all.css` with individual modules, or
`syntyr.css` with core and effects. These bundles overlap.

Read the [component reference](components.md), [recipe reference](recipes.md),
and [framework integrations](framework-integrations.md) for HTML variants
and host-application responsibilities. Syntyr styles controls; your app
provides form handling, data access, authorization, and navigation.

## 4. Validate markup (optional, alpha.5 ZIP candidate)

After the alpha.5 archive is released, its extracted root will include
`scripts/syntyr_check.py` and `metadata/syntyr-contract.json`.
The checker requires **Python 3.10+ on the developer machine only**;
it ships no JavaScript or build-time requirement to consumers.

From the **extracted matching-version archive**, check your HTML file:

```sh
python3 scripts/syntyr_check.py /path/to/your/index.html
python3 scripts/syntyr_check.py --format json /path/to/your/index.html
```

It reports misspelled `syn-*` classes, invalid literal state values,
unscoped classes in complete documents, and missing optional CSS files when
it can identify the installed stylesheets. For HTML fragments with no links,
pass the actual modules using `--stylesheets syntyr.core.css`.
Dynamic template expressions are skipped, not executed.

**Do not run the candidate checker against published alpha.4 CSS** and assume
its alpha.5 class inventory is accurate for alpha.4. Use matching-version
metadata; this is a static HTML check, not an accessibility or runtime audit.
See the [editor and validator guide](editor-integration.md).

## 5. Optional package-manager projects

`@syntyr/css` is prepared in the alpha.5 source, but it is **not yet published to npm**.
Do not assume `npm install @syntyr/css` works today. If your application
already uses a bundler, the source candidate supports a locally packed
tarball; follow the [package-manager guide](package-managers.md).
Applications that don't use a build tool can remain on copied CSS indefinitely.

## Check before production

Test real routes and submission behavior, keyboard focus, zoom/reflow,
forced colors, and browser compatibility in your own application. Alpha
releases are experimental and do not carry a v1 compatibility or accessibility
conformance guarantee. [Release guidance](distribution.md) and
[accessibility checklist](accessibility.md) explain the current boundaries.
