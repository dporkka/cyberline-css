import { LitElement, css, html } from "lit";

// Shadow DOM: global .syn-* selectors cannot cross this boundary.
// Inherited public --syn-* tokens DO cross it, so styles consume tokens.
export class DemoShadowSignal extends LitElement {
  static properties = {
    label: { type: String },
    active: { type: Boolean, reflect: true },
  };

  constructor() {
    super();
    this.label = "Relay gateway";
    this.active = false;
  }

  static styles = css`
    :host {
      display: block;
      color: var(--syn-text, CanvasText);
      font-family: var(--syn-font, system-ui);
    }
    [part="panel"] {
      padding: var(--syn-panel-padding, 1.25rem);
      background: var(--syn-surface, Canvas);
      border: 1px solid var(--syn-frame, CanvasText);
      border-radius: var(--syn-panel-radius, 0.25rem);
    }
    h3 { margin: 0 0 .75rem; font-size: 1.125rem; }
    [part="indicator"] {
      display: inline-block;
      margin-block-end: 1rem;
      font-weight: 650;
      color: var(--syn-warning, currentColor);
    }
    :host([active]) [part="indicator"] { color: var(--syn-accent, currentColor); }
    button {
      min-height: 2.75rem;
      padding: .5rem 1rem;
      border: 1px solid var(--syn-frame, currentColor);
      border-radius: var(--syn-radius, .25rem);
      background: var(--syn-accent, ButtonFace);
      color: var(--syn-on-accent, ButtonText);
      font: inherit;
      cursor: pointer;
    }
    button:focus-visible {
      outline: 2px solid var(--syn-focus-ring, currentColor);
      outline-offset: 3px;
    }
    @media (prefers-reduced-motion: reduce) {
      button { transition: none; }
    }
    @media (forced-colors: active) {
      [part="panel"] { border-color: CanvasText; }
      button { background: ButtonFace; color: ButtonText; }
      [part="indicator"] { color: CanvasText; }
    }
  `;

  _toggle() {
    this.active = !this.active;
    this.dispatchEvent(new CustomEvent("syn-demo-signal-change", {
      detail: { active: this.active },
      bubbles: true,
      composed: true,
    }));
  }

  render() {
    return html`
      <section part="panel" role="group" aria-label=${this.label}>
        <h3>${this.label}</h3>
        <p part="indicator" role="status">${this.active ? "Active" : "Standby"}</p>
        <div>
          <button part="toggle" type="button" aria-pressed=${String(this.active)}
                  @click=${this._toggle}>Toggle signal</button>
        </div>
      </section>
    `;
  }
}

customElements.define("syn-demo-shadow-signal", DemoShadowSignal);
