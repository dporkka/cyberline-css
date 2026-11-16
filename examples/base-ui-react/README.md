# Syntyr + real Base UI

Opt-in React integration fixture. Syntyr's own stylesheet is CSS-only;
the separate example requires React, Base UI, Vite and developer-only Playwright.

```sh
npm ci
npm run build
npm test
```

Five browser tests exercise a scoped portal menu, modal dialog focus
restoration, real Select/Switch/Tabs state changes, RTL menu keyboard control,
and direction-dependent switch-thumb styling. The portal container is mounted
inside the same `.syn-root` subtree to preserve the selected theme.

This is a test fixture, **not** a claim of complete screen-reader/axe audit
or coverage of every Base UI component. No JavaScript is added to Syntyr core.
