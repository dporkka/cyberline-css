# Syntyr Desktop — optional webview appearance adapter

Status: experimental source for the **unreleased alpha.5 candidate**. This is not a native widget toolkit or a shipped native binary.

Syntyr Desktop styles HTML applications running in a browser, Tauri, Electron, Wails, or another embedded webview. It is optional, scoped to `.syn-root[data-syn-platform]`, and has no runtime dependencies. The `syntyr.core.css` bytes do not change.

## Install

Load the core **first**, then the desktop CSS adapter:

```html
<link rel="stylesheet" href="/assets/syntyr.core.css">
<link rel="stylesheet" href="/assets/syntyr.desktop.css">
<div class="syn-root" data-syn-theme="studio"
     data-syn-density="compact" data-syn-platform="macos">
  <section class="syn-desktop-shell" aria-label="Workspace">
    <!-- Header, navigation, main, inspector and statusbar slots -->
  </section>
</div>
```

For the unpublished npm source package, use `@syntyr/css/desktop.css` alongside `@syntyr/css/core.css`. Or copy `integrations/desktop/syntyr.desktop.css` beside your self-hosted assets. The [interactive example](../examples/desktop-workspace.html) is self-contained and loads only local files.

## Supported appearances

- `macos` — subtle unified-toolbar, translucent-looking **CSS color-mixed** surfaces, rounded selection.
- `windows` — restrained rounded surfaces and selected navigation indicator, inspired by Windows 11.
- `gnome` — softly rounded header and calm sidebar/inspector, inspired by GNOME/Adwaita.

These are **visual interpretations**, not exact reproductions of Apple, Microsoft or GNOME widgets. KDE may be added after actual demand. An unsupported or omitted platform gets the neutral desktop tokens only when `data-syn-platform` is present.

The `data-syn-platform` attribute is **supplied by the host**. CSS cannot reliably determine the OS from a webview and must not depend on user-agent sniffing. In a Tauri or Electron app, obtain the OS through that host's supported API, normalize it to `macos`, `windows`, or `gnome` based on your product's chosen Linux appearance, then set the attribute. This example's tiny ESM switcher is demo-only, not part of the library.

## Responsibilities and boundaries

| Syntyr CSS handles | Desktop host handles |
| --- | --- |
| Toolbar, sidebar, content, inspector and status layouts | Actual window titlebar, resize, minimize and close |
| Token-based visual treatment and keyboard focus styles | System menus, global shortcuts and IPC |
| Responsive, RTL-aware borders and selected navigation | File dialogs, drag regions, native notifications |
| Reduced-motion and forced-color presentation | Accessibility integration and OS theme detection |

The shell expects descendants with `.syn-desktop-toolbar`, `.syn-desktop-sidebar`, `.syn-desktop-content`, `.syn-desktop-inspector`, and `.syn-desktop-statusbar`. The toolbar can contain `.syn-desktop-toolbar-group`; the sidebar can contain `.syn-desktop-nav`. Use semantic `header`, `aside`, `nav`, `main`, and `footer`, with real links and accessible labels. None of these selectors adds interaction state or a JavaScript requirement.

Platform styling does **not** modify `data-syn-theme`, `data-syn-density`, `data-syn-intensity`, `--syn-control-height`, or global accent palettes. Existing `--syn-*` semantic colors remain authoritative. Use system-native controls where required; do not imitate native window buttons without wiring to supported host APIs.

For a real native SwiftUI, WinUI, GTK or Qt screen, consume Syntyr's design tokens as data and implement the platform's controls natively. This CSS does not render inside native widget trees.

## Validation and adoption

Run `python3 -m unittest discover -s tests -p test_desktop_appearance.py`. Validate at desktop and narrow viewports, 200% zoom, keyboard-only navigation, forced colors, light/dark theme overrides, and Windows/macOS/Linux webviews before promising platform fidelity. The demonstration is a reference, not a tested signed Tauri application. Avoid broadening the API until a real host app exercises it.
