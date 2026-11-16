# Optional Base UI / Syntyr integration

**Status:** Experimental alpha.5 source candidate. Syntyr is still plain CSS with
**no runtime** JavaScript dependencies; Base UI is an optional React application
dependency, not part of Syntyr's CSS package.

Use [Base UI](https://base-ui.com/react/handbook/styling) for headless accessible
interactions and Syntyr for presentation. Base UI owns keyboard navigation,
focus management and restoration, ARIA semantics, positioning, selection,
dismissal, transitions and form behavior. Syntyr does not replace those APIs.

## Install and load

In a React application, install `@base-ui/react` separately. Load Syntyr core
first, then the optional CSS adapter (the package export is an unpublished
candidate until a release is approved):

```tsx
import "@syntyr/css/core.css";
import "@syntyr/css/base-ui.css";
```

Or copy `dist/syntyr.core.css` and `integrations/base-ui/states.css` into
your static assets and load both as ordinary stylesheets in that order. Syntyr
can also be consumed with native HTML, Go templates, HTMX, Ruby, Rust or PHP;
these do not need Base UI for native controls. Use Base UI only where rich
accessible interaction is warranted in React.

## Styling contracts

Assign **explicit** Syntyr part classes to the matching Base UI components,
for example:

| Component family | Parts | State hooks |
| --- | --- | --- |
| Menu, Select, Combobox, Popover, Tooltip | `syn-base-trigger`, `syn-base-popup`, `syn-base-item`, `syn-base-separator` | `data-popup-open`, `data-highlighted`, `data-selected`, `data-disabled`, `data-focus-visible` |
| Dialog | `syn-base-dialog-viewport`, `syn-base-backdrop`, `syn-base-popup syn-base-dialog`, `syn-base-dialog-title`, `syn-base-dialog-description` | `data-open`, `data-starting-style`, `data-ending-style` |
| Switch, Checkbox | `syn-base-switch`, `syn-base-switch-thumb`, `syn-base-checkbox`, `syn-base-checkbox-indicator` | `data-checked`, `data-indeterminate`, `data-disabled` |
| Tabs | `syn-base-tabs-list`, `syn-base-tab`, `syn-base-tabs-panel` | `data-selected`, `data-focus-visible`, `data-disabled` |
| Field | `syn-base-field`, `syn-base-field-error` | `data-invalid` |

Consult the exact Base UI component version for its emitted part attributes;
not every state exists on every part. No selectors target Base UI implementation
details, generic ARIA roles, unclassed elements, or global `:root`.

## Portal and theme scope

Base UI's `Portal` defaults to rendering into `document.body`. Content
outside the `.syn-root` scope does not receive Syntyr CSS or inherit its
palette. Put a stable portal container **inside** the theme root and pass it
to `Portal container`. This is particularly important with nested themes.
Do not rely on theme variables being magically inherited through a portal.

```tsx
import { useRef } from "react";
import { Dialog } from "@base-ui/react/dialog";

export function Example() {
  const portalRef = useRef<HTMLDivElement>(null);
  return (
    <section className="syn-root" data-syn-theme="studio">
      <Dialog.Root>
        <Dialog.Trigger className="syn-base-trigger">Open settings</Dialog.Trigger>
        <Dialog.Portal container={portalRef} className="syn-base-dialog-viewport">
          <Dialog.Backdrop className="syn-base-backdrop" />
          <Dialog.Popup className="syn-base-popup syn-base-dialog">
            <Dialog.Title className="syn-base-dialog-title">Settings</Dialog.Title>
            <Dialog.Description className="syn-base-dialog-description">
              Review this setting.
            </Dialog.Description>
            <Dialog.Close className="syn-base-trigger">Close</Dialog.Close>
          </Dialog.Popup>
        </Dialog.Portal>
      </Dialog.Root>
      <div ref={portalRef} />
    </section>
  );
}
```

The `Portal` element may be placed at a different DOM location after
hydration. Verify that actual portaled DOM nodes descend from the intended
`.syn-root`, including after a route change. Avoid attaching `syn-root` to
the entire body unless the application explicitly wants global Syntyr styling.

## RTL and state behavior

The adapter uses logical CSS properties such as `padding-inline`,
`border-inline-start`, `inset`, and `block-size`. Switch-thumb travel
changes direction via `:dir(rtl)`. Set `dir="rtl"` at the application or
nested component boundary; Base UI itself determines keyboard and placement
semantics. CSS alone cannot implement those behaviors.

The adapter honors reduced motion and forced-colors modes. Error and disabled
states must be set by the application or Base UI; invalid visual styling is
not a substitute for an accessible error message or server validation.
Transitions never control visibility or focus; the headless primitive does.

## Runnable integration smoke

[The optional React fixture](https://github.com/dporkka/syntyr-css/tree/main/examples/base-ui-react) pins Base UI 1.9.0
and runs real menu, dialog, select, switch and tabs browser tests. From that
example directory run `npm ci`, `npm run build` and `npm test`. The test
project does not change the Syntyr CSS distribution.

## Validation and limitations

Run `python3 -m unittest discover -s tests -p 'test_base_ui_integration.py' -v`,
then the repository's full suite. Verify real Base UI dialogs, menus and selects
with keyboard-only operation, screen readers, real portal roots, 200%/400%
zoom and multiple themes. Syntyr's static selectors alone cannot certify
Base UI accessibility. No JavaScript or React is included in Syntyr's core,
standalone presets or CSS release bundle.
