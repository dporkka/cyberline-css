# Copy-owned form recipes

These are **MIT-licensed, plain-HTML examples**. Copy and modify them without installing a Syntyr CLI, template registry, React, or a JavaScript runtime. Syntyr provides presentation; your browser and application provide behavior.

Load `dist/syntyr.core.css` and apply `.syn-root` on a stable ancestor. Input groups and fields are included in core. The examples below also work in Go/templ, Askama, Django templates, Astro, React, and HTMX.

## 1. Labeled field with assistance and server-side validation

```html
<div class="syn-root" data-syn-theme="studio">
  <div class="syn-field">
    <label class="syn-label" for="email">Work email</label>
    <input class="syn-input" id="email" name="email" type="email"
           autocomplete="email" aria-invalid="true"
           aria-describedby="email-help email-error" required>
    <p class="syn-help" id="email-help">Use your company email address.</p>
    <p class="syn-error" id="email-error">Enter a valid work email.</p>
  </div>
</div>
```

Only render `aria-invalid="true"` and the error message when the form is actually invalid. Do not use CSS as a substitute for server-side validation. The field class groups presentation; the native `label for` association supplies the accessible name.

## 2. Search field with a connected button

```html
<search class="syn-root" data-syn-theme="studio" aria-label="Search accounts">
  <form method="get" action="/accounts">
    <div class="syn-field">
      <label class="syn-label" for="account-query">Account name</label>
      <div class="syn-input-group">
        <input class="syn-input" id="account-query" name="q"
               type="search" placeholder="Search accounts">
        <button class="syn-button syn-button--primary" type="submit">Search</button>
      </div>
    </div>
  </form>
</search>
```

This is **progressive enhancement**: the GET form submits with **No JavaScript**. An HTMX application may add `hx-get` and `hx-target` while preserving `action`, `method`, and a server-rendered fallback. The application must implement the endpoint and return actual search results.

At narrow available widths (12rem or less relative to the current text size), a connected input and submit button stack instead of squeezing the input into a tall, narrow strip. The `.syn-input-group` itself determines the breakpoint through a CSS container query; no viewport breakpoint, JavaScript, or additional component class is needed. Input groups containing only currency/unit addons keep their existing inline layout. Test long button labels, translations and browser zoom in consuming applications.

## 3. Input addon (currency and unit)

```html
<div class="syn-root" data-syn-theme="studio">
  <div class="syn-field">
    <label class="syn-label" for="monthly-budget">Monthly budget (USD)</label>
    <div class="syn-input-group">
      <span class="syn-input-addon" aria-hidden="true">$</span>
      <input class="syn-input" id="monthly-budget" name="budget"
             type="text" inputmode="decimal">
      <span class="syn-input-addon" aria-hidden="true">USD</span>
    </div>
  </div>
</div>
```

The unit is included in the label, not only in the decorative addon; assistive technologies must not depend on a symbol alone. Keep addons concise; overly long addons can compress their associated input. For monetary amounts, text plus `inputmode="decimal"` avoids native number spinners and floating-point assumptions; the server must parse localized decimal input and validate exact precision. Use `type="number"` for quantities where native numeric stepping is appropriate.

## 4. Container-responsive horizontal form

```html
<form class="syn-root syn-region syn-form" action="/settings" method="post"
      data-syn-theme="corporate">
  <div class="syn-field-row">
    <label class="syn-label" for="org-name">Organization</label>
    <div class="syn-field-body">
      <input class="syn-input" id="org-name" name="organization"
             aria-describedby="org-help" required>
      <p class="syn-help" id="org-help">Visible to members of your team.</p>
    </div>
  </div>
  <button class="syn-button syn-button--primary" type="submit">Save</button>
</form>
```

The `syn-region` container determines whether rows become horizontal at 42rem. Without that ancestor they remain safely stacked. This is intentionally not a full grid/breakpoint framework. The help text is associated with its input via `aria-describedby`. A production POST endpoint must handle authorization, validation and CSRF.

## 5. Server-rendered error recovery

The optional `syntyr.recipes.css` adds `.syn-error-summary` styling; the
following HTML remains readable and operable without that stylesheet or any
JavaScript. Render this response **only after a failed submission**, with the
submitted value preserved and error messages associated with the field.

```html
<section class="syn-root" data-syn-theme="studio" aria-labelledby="account-title">
  <h2 id="account-title">Account settings</h2>
  <div class="syn-error-summary" id="form-errors" tabindex="-1"
       role="region" aria-labelledby="form-errors-title">
    <h3 id="form-errors-title">There is a problem</h3>
    <ul><li><a href="#account-email">Enter a valid email address</a></li></ul>
  </div>
  <form class="syn-form" method="post" action="/account">
    <div class="syn-field">
      <label class="syn-label" for="account-email">Email address</label>
      <input class="syn-input" id="account-email" name="email" type="email"
             autocomplete="email" value="not-an-email" required
             aria-invalid="true"
             aria-describedby="account-email-hint account-email-error">
      <p class="syn-help" id="account-email-hint">Use the address for account notices.</p>
      <p class="syn-error" id="account-email-error">Enter a valid email address.</p>
    </div>
    <button class="syn-button syn-button--primary" type="submit">Save</button>
  </form>
</section>
```

The server owns validation, authorization, CSRF protection and re-rendering.
On a successful response, omit the error summary, error paragraph and
`aria-invalid`. On enhanced/partial-page submissions, the application must
announce errors and move focus to the summary or first invalid field; CSS cannot
do this. On a full-page response, keep the summary before the form in document
order and link directly to each invalid input. Keep working `action`/`method`
attributes even when HTMX, Datastar or another client adds progressive
enhancement. Native constraint validation still runs; `aria-invalid` alone
does not prevent submission or execute server-side validation.

## 6. Native readonly text fields

Use the real `readonly` attribute, not `aria-readonly` or `disabled`, when
text must remain selectable and submit with the form:

```html
<div class="syn-root syn-field">
  <label class="syn-label" for="reference-id">Reference ID</label>
  <input class="syn-input" id="reference-id" name="reference_id"
         value="WS-1042" readonly>
</div>
```

Classed inputs and opt-in `syn-semantic` fields display readonly text with a
recessed surface and dashed border. Do not place `readonly` on native
`select`, checkbox, radio, or file inputs: those controls do not support it.
Keep the browser's autofill appearance and autocomplete functionality available;
do not conceal autofilled values with pseudo-elements or forced-color overrides.

## Optional companion styles

- [Radix Primitives state styling](radix-integration.md) provides an opt-in adapter for React applications while keeping Radix responsible for keyboard behavior.
- shadcn/ui components can adopt Syntyr tokens in application-owned CSS. Modern color variables can use values such as `--background: var(--syn-bg)` and `--foreground: var(--syn-text)`, **only when** the shadcn component expects complete CSS color values. Older `hsl(var(--background))` consumers require an HSL-channel bridge instead; do not apply the mappings blindly.
- `syntyr.semantic.css` remains a separate opt-in style for unclassed native HTML. Do not apply it indiscriminately around other component libraries.

See [the static form showcase](../examples/form-composition.html) and the [main component contract](components.md).


## Optional CSS-only conversation layout

The `syntyr.recipes.css` bundle includes a small, **presentational-only**
conversation composition: `.syn-conversation`, `.syn-message`,
`.syn-message--incoming`, `.syn-message--outgoing`, `.syn-message-meta`,
`.syn-composer`, and `.syn-composer-actions`. It reuses existing colors,
density, typography, `.syn-textarea`, and `.syn-button` without shipping
a chat runtime, stream parser, message history, or new dependencies.

```html
<link rel="stylesheet" href="/css/syntyr.core.css">
<link rel="stylesheet" href="/css/syntyr.recipes.css">
<main class="syn-root" data-syn-theme="minimal" data-syn-intensity="quiet">
  <section class="syn-conversation" aria-label="Conversation">
    <article class="syn-message syn-message--outgoing" aria-label="User message">
      <p>Summarize our release plan.</p>
    </article>
    <article class="syn-message syn-message--incoming" aria-label="Response">
      <p>Start with the smallest verified release candidate.</p>
    </article>
    <form class="syn-composer" action="/messages" method="post">
      <!-- Your server must provide CSRF protection and authenticated POST handling. -->
      <label class="syn-label" for="reply">Message</label>
      <textarea class="syn-textarea" id="reply" name="message" required></textarea>
      <div class="syn-composer-actions">
        <span class="syn-caption">Messages are handled by your application.</span>
        <button class="syn-button syn-button--primary" type="submit">Send</button>
      </div>
    </form>
  </section>
</main>
```

A production application supplies authenticated persistence, input validation,
request rate limits, message announcements and focus management for updates,
and a server action or optional progressive enhancement for streaming.
Avoid using `aria-live` on an entire long message history. See the
[offline static demo](../examples/chat-interface.html); its Send button
is deliberately disabled because it has no server backend.
