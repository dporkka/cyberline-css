# SaaS, business websites, and native CLI applications

Syntyr is a **framework-neutral styling library**. Its three themes are orthogonal to page structure:

| Theme | Default use | Palette |
| --- | --- | --- |
| `grid` | technical interfaces, operations tooling | dark/cyan |
| `noir` | cinematic product sites, experimental campaigns | dark/amber |
| `studio` | SaaS dashboards, professional websites and documentation | light/blue |

Use Grid/Noir selectively—most enterprise interfaces benefit more from Studio's low-noise hierarchy than extensive neon decoration. **All themes remain MIT licensed.**

## Start with a modern business or SaaS UI

```html
<link rel="stylesheet" href="/css/syntyr.core.css">
<link rel="stylesheet" href="/css/syntyr.recipes.css">
<section class="syn-root syn-region" data-syn-theme="studio">
  <div class="syn-kpi-grid">
    <article class="syn-app-card syn-frame--soft">
      <span class="syn-stat-label">ACTIVE PROJECTS</span>
      <p class="syn-stat-value">24</p>
    </article>
  </div>
</section>
```

The optional recipes module provides app shells, responsive navigation, KPI cards, activity lists, editorial heroes, marketing feature grids, call-to-action bands and browser-rendered terminals. Use `syntyr.core.css` alone when you do not need full-page patterns. `syntyr.all.css` includes all optional modules, but the modular files are generally preferable for small websites.

- [Responsive SaaS application](../examples/saas.html)
- [Professional business website](../examples/business.html)
- [Complete four-page business-site starter](../examples/business-starter/index.html) — homepage, services, illustrative case study and safely disabled contact-form pattern; [copy/edit guide](../examples/business-starter/README.md) is repository-only.
- [Browser terminal/documentation](../examples/terminal.html)
- [Original Grid dashboard](../examples/console.html)
- [Original Noir marketing page](../examples/landing.html)

All examples contain fictional data and no backend. You must supply application actions, authentication and server state. Native `details`, `dialog` and `popover` can reduce JavaScript, but compatibility of newer HTML invoker commands requires testing on the browsers you support.

## Real terminal applications (Go, Rust, Python, etc.)

A native shell application cannot load CSS. Syntyr instead provides [`terminal/palettes.json`](../terminal/palettes.json) with three matching terminal palettes:

- `background`, `foreground`, `accent`, and `cursor`: design guidance for terminal emulator themes.
- `ansi`: 16 hex RGB colors, ordered by ANSI indices 0–15 (standard black/red/green/yellow/blue/magenta/cyan/white followed by bright variants).
- CLI output: use foreground ANSI SGR sequences if supported, but **never assume your application can control the user's terminal background**.

```bash
python3 examples/ansi_cli.py --theme studio
python3 examples/ansi_cli.py --theme grid --no-color
python3 examples/ansi_cli.py --theme noir | cat  # plain text, not ANSI
```

The demonstration uses Python's standard library only. It checks `sys.stdout.isatty()`, `NO_COLOR`, `CLICOLOR=0`, and `TERM=dumb` before printing true-color SGR escape sequences. A production CLI should additionally detect terminal color depth, handle Windows environments and let users override the theme. Prefer standard 8/16-color output or plain text when true-color support is unknown. Do not put ANSI control sequences in logs, data files, JSON or machine-readable output.

**Do not mistake CSS browser-terminal panels for actual executable shells.** The `.syn-terminal` class is presentation only.

## Accessibility and performance

Themes should preserve readable body text and visible keyboard focus. Distinguish status with explicit words, not color alone. Check contrast in every pair used in a customized theme, including disabled and error states. The default `studio` palette is designed around WCAG AA text contrast; a real site still requires manual contrast, screen-reader, forced-colors and zoom testing.

- `src/recipes.css` ships only when requested and does not add runtime JavaScript.
- CSS decorative surfaces are static by default. Avoid continuous glowing, flashing, animated scanlines and heavy blur.
- Avoid forcing a full viewport-height widget inside an app: use `.syn-page` on page-level roots only.
- Use container queries for embedded cards, but provide a simple stacked layout without support.
- For native CLIs, prefer readable default terminal styles over trying to repaint a user's terminal emulator.

## Commercial boundaries

The core, all three themes, reusable recipes, terminal palettes, documentation and these example pages are MIT licensed. Future paid offerings should be **separately authored end-to-end page templates** (complete dashboards, vertical SaaS apps or professionally composed marketing pages), not gated primitive classes or paid accessibility fixes.
