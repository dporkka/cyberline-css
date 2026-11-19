# Optional Radix Primitives visual adapter

Syntyr core remains plain CSS with zero runtime JavaScript and zero React dependencies. Radix is a **separate application choice**. Its components own the accessible name, **ARIA** attributes, focus management, keyboard controls and state updates. Syntyr only adds styling.

## Install and opt in

In a React project using Radix Primitives, add a link **after** the core CSS:

```html
<link rel="stylesheet" href="/css/syntyr.core.css">
<link rel="stylesheet" href="/css/radix/states.css">
```

Copy [the adapter](../integrations/radix/states.css) into your project, or reference its repository source. Do not load it when you do not use Radix. It is **not** included in `syntyr.all.css`, either.

Wrap the relevant app area in `.syn-root`. Apply `.syn-radix` on that root, on a container inside it, **or directly on a stateful Syntyr control** to opt in only that control. If Radix portals content to the document body, set that portal's `container` inside the styled root, or style the portal explicitly. Do not assume portal content inherits Syntyr tokens when it is mounted outside the root.

## Example: controlled behavior, CSS presentation

```jsx
import * as Accordion from "@radix-ui/react-accordion";
import * as Toggle from "@radix-ui/react-toggle";

export function Controls() {
  return (
    <section className="syn-root syn-radix" data-syn-theme="studio">
      <Toggle.Root className="syn-button" aria-label="Pin dashboard">
        Pin dashboard
      </Toggle.Root>
      <Accordion.Root type="single" collapsible>
        <Accordion.Item value="filters">
          <Accordion.Header>
            <Accordion.Trigger className="syn-button syn-accordion-trigger">
              Advanced filters
            </Accordion.Trigger>
          </Accordion.Header>
          <Accordion.Content className="syn-accordion-content">
            <p>Additional filters belong here.</p>
          </Accordion.Content>
        </Accordion.Item>
      </Accordion.Root>
    </section>
  );
}
```

Radix supplies `data-state="on"`, `data-state="open"`, `data-state="closed"`, and `data-disabled` where applicable. The adapter consumes only those documented state hooks on **explicit Syntyr component classes**. It does not create a generic `data-state` styling API, and it does not replace Radix behavior.

## Accessibility and compatibility boundaries

- Test with keyboard only (Enter, Space, Arrow keys where appropriate, Escape) and screen readers; CSS passing a contract test is **not** an accessibility certification.
- Use a native button or Radix trigger for actions. Visual `[data-disabled]` states do not prevent click handlers from running; Radix/application logic must enforce disabled behavior.
- Preserve the focus-visible indication from Syntyr core and verify contrasts for all themes and custom token overrides.
- Avoid CSS-only emulations of focus traps, listbox navigation, complex comboboxes or dialogs.
- The adapter does not guarantee complete styling for every Radix primitive. Extend it with component-specific classes only when real use cases justify maintenance.

Related: [copy-owned component recipes](component-recipes.md), [framework integrations](framework-integrations.md).
