# Syntyr + Svelte 5 (Vite)

From this directory, run:

    npm install
    npm run dev
    npm run build

The CSS comes from the local checkout's unpublished @syntyr/css package using
file:../... Import it once in the entry point. In SvelteKit, import
@syntyr/css/core.css in src/routes/+layout.svelte (or the app's global CSS);
keep .syn-root on the intended app subtree. Do not duplicate CSS imports.

Syntyr does not require Svelte and supplies no JS/actions/stores. Native Svelte
runes manage state, submission, disabled state, and ARIA.

This example changes a **local list only**. The 250-ms simulated delay is
illustrative, not a real network request; replace it with your application API
and error handling. Use a reviewed release artifact or pinned published package
for production when available.
