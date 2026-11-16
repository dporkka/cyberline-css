# Syntyr + Vue 3 (Vite)

From this directory, run:

    npm install
    npm run dev
    npm run build

This example resolves the **local checkout's** unpublished @syntyr/css package
via file:../.. and imports @syntyr/css/core.css once from the Vue entry point.
For production, use a reviewed release artifact or a published, pinned package
once one is available. No Syntyr provider or JavaScript runtime is installed.

The form is a local demo, **not a persisted API**. A 250-ms delay illustrates
host-owned pending/disabled state; replace it with your actual request and error
handling. The theme root stays outside the form and repeated list elements.

For Nuxt, install/load Syntyr CSS in nuxt.config.ts via the css array (or a
global CSS file), and use the same Vue markup and native ARIA bindings.
Do not load it again from every component. Nuxt and its SSR/hydration belong to
the host application, not Syntyr.
