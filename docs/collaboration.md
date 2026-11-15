# Collaboration and human/AI agent UI

Syntyr's optional, **MIT-licensed** collaboration module offers original CSS-only layouts for threaded discussions, agent activity, attached artifacts, and contextual review. The information hierarchy is informed by [Chatudo (CircleChat)](https://github.com/dporkka/chatudo), but this module does not copy Chatudo's React application, Tailwind rules, runtime, icons, or branding.

[View the static three-theme collaboration example](../examples/collaboration.html). It demonstrates **Minimal**, **Grid**, and **Noir** with the same selectors and synthetic data. No network connection, web font, JavaScript, authentication, message delivery, or persistent state is provided.

## Installation

Load the existing core stylesheet and the separate optional collaboration module:

~~~html
<link rel="stylesheet" href="/css/syntyr.core.css">
<link rel="stylesheet" href="/css/syntyr.collaboration.css">
~~~

Or load the full, larger `syntyr.all.css` distribution (do not load the collaboration file twice). `syntyr.core.css` remains unchanged. The new module is alpha-candidate source until included in an actual tagged release; do not claim it is available in older published archives.

## CSS API

| Selector | Purpose |
| --- | --- |
| `.syn-conversation`, `.syn-conversation__header`, `.syn-conversation__stream` | Surface, heading, scrollable stream |
| `.syn-message`, `.syn-message--continued`, `.syn-message__avatar`, `.syn-message__content`, `.syn-message__meta`, `.syn-message__body`, `.syn-message__actions` | Readable message groups and accessible action presentation |
| `.syn-identity`, `.syn-identity--agent`, `.syn-identity__role` | Name and explicit AI/human role metadata |
| `.syn-presence[data-syn-presence]` | Online, busy, error or neutral statuses; caller supplies visible status text |
| `.syn-attachment`, `.syn-attachment__icon`, `.syn-attachment__details` | Attachment / artifact cards; no file handler |
| `.syn-composer`, `.syn-composer__toolbar` | Bordered textarea and action layout; no rich-text engine |
| `.syn-collab-layout`, `.syn-thread-panel` | Responsive main stream and adjacent thread/details area |
| `.syn-agent-run`, `.syn-agent-run__steps` | Read-only step/result presentation |

The opt-in `--syn-collab-avatar` and `--syn-collab-thread-width` custom properties control avatar size and thread width. All colors, borders, shadows, and typography read existing `--syn-*` tokens; nested themes, density, and visual intensity remain orthogonal.

## Server-rendered pattern

~~~html
<section class="syn-root" data-syn-theme="minimal">
  <div class="syn-collab-layout">
    <section class="syn-conversation" aria-label="Project updates">
      <header class="syn-conversation__header"><h2>Project updates</h2></header>
      <ol class="syn-conversation__stream" role="list" aria-label="Message history">
        <li class="syn-message">
          <span class="syn-message__avatar" aria-hidden="true">QA</span>
          <div class="syn-message__content">
            <div class="syn-message__meta">
              <span class="syn-identity syn-identity--agent">
                QA Agent <span class="syn-identity__role">AI agent</span>
              </span>
              <time datetime="2026-11-15T11:07:00">11:07</time>
            </div>
            <div class="syn-message__body"><p>Review finished.</p></div>
            <span class="syn-presence" data-syn-presence="online">Completed</span>
          </div>
        </li>
      </ol>
    </section>
    <aside class="syn-thread-panel" aria-label="Related evidence">
      <h2>Evidence</h2>
      <p>Link to application-owned review details here.</p>
    </aside>
  </div>
</section>
~~~

A native `<form>` may wrap `.syn-composer`, and a labeled `<textarea>` is recommended. The example intentionally disables its send control because no backend exists. Never make a decorative "Send" button appear operational.

## Responsibilities and accessibility

The **application** provides authentic messages, timestamps, access controls, file links and sanitization, real-time presence, delivery, optimistic state, pagination, keyboard behavior, and any threaded discussion. CSS does not execute actions, infer member roles, or validate permissions.

- Use a real list for message history and distinguish each author in text. For continued messages, keep an author identifier in the DOM; the avatar is decorative and can be hidden visually.
- Do not rely on color or a dot for agent state: pair every status indicator with visible wording. Do not use `role="status"` or `aria-live` indiscriminately on each message in a busy stream. Announce only meaningful new events using the application's live-region strategy.
- Action links/buttons stay visible on hover, keyboard and touch; never require pointer hover for access. Nonfunctional or dangerous actions must be disabled, not simulated.
- Use real anchors for downloadable artifacts; apply application-specific URL validation, content security, upload scanning and permission checks.
- At narrow widths the side rail stacks under the thread. For drawer-like mobile threads, implement correct focus handling and dismissal in the application rather than hiding content with CSS.
- Validate at 320px, 200%/400% zoom, keyboard-only input, forced-colors, reduced motion and actual screen readers. No animation is required for online/working indicators.

## Scope and commercial separation

These *primitives* remain free under MIT. Complete premium conversation, human-review inbox, or agent-operations screen templates may be distributed separately as original, source-editable Pro layouts, but the paid kit must not relicense the MIT CSS. Existing Syntyr approval, timeline, inspector, pipeline and activity components should be reused rather than duplicated.
