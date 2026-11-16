/* Optional MIT Custom Elements. Importing this file does not register elements.
   Plain HTML and Syntyr's core CSS remain independently usable. */
export function normalizePercent(value) {
  const n = Number(value);
  return Number.isFinite(n) ? Math.min(100, Math.max(0, n)) : 50;
}

export function ratingDescription(value, total = 5) {
  const n = Number(value);
  if (!Number.isFinite(n) || n <= 0) return "Not rated";
  return `${Math.min(total, n)} of ${total} stars`;
}

export function registerSyntyrElements(registry = globalThis.customElements) {
  if (!registry) return;
  const Base = globalThis.HTMLElement || class {};

  class CopyButton extends Base {
    connectedCallback() {
      this.button = this.querySelector("button");
      const targetId = this.getAttribute("for");
      const target = targetId && this.ownerDocument?.getElementById(targetId);
      const clipboard = globalThis.navigator?.clipboard;
      if (!this.button || !target || !clipboard?.writeText) return;
      this.button.disabled = false;
      this.handleCopy = async () => {
        const status = this.querySelector("[data-syn-copy-status]");
        let message;
        try {
          await clipboard.writeText(target.textContent || "");
          message = "Copied to clipboard";
        } catch {
          message = "Copy unavailable. Select the text and copy manually.";
        }
        if (status) status.textContent = message;
        this.ownerDocument?.querySelector("syn-toast-region")?.announce(message);
        this.dispatchEvent(new CustomEvent("syn-copy-result", {
          bubbles: true, composed: true, detail: { success: message === "Copied to clipboard" },
        }));
      };
      this.button.addEventListener("click", this.handleCopy);
    }
    disconnectedCallback() {
      if (this.button && this.handleCopy) this.button.removeEventListener("click", this.handleCopy);
      this.handleCopy = null;
    }
  }

  class ToastRegion extends Base {
    announce(message) {
      const output = this.querySelector('[data-syn-toast-message]') || this;
      output.textContent = String(message);
    }
  }

  class ImageCompare extends Base {
    connectedCallback() {
      const range = this.querySelector('input[type="range"]');
      const images = this.querySelectorAll("[data-syn-compare-before], [data-syn-compare-after]");
      if (!range || images.length !== 2) return;
      this.range = range;
      this.handleChange = () => {
        const percent = normalizePercent(range.value);
        this.style.setProperty("--syn-compare-percent", `${percent}%`);
        range.setAttribute("aria-valuetext", `${percent}% before image visible`);
      };
      range.addEventListener("input", this.handleChange);
      this.handleChange();
      this.setAttribute("data-syn-enhanced", "");
    }
    disconnectedCallback() {
      if (this.range && this.handleChange) this.range.removeEventListener("input", this.handleChange);
    }
  }

  class RatingInput extends Base {
    connectedCallback() {
      this.handleRating = event => {
        if (!event.target?.matches?.('input[type="radio"]') || !event.target.checked) return;
        const current = Number(event.target.value);
        const count = this.querySelectorAll('input[type="radio"]').length;
        const output = this.querySelector("output");
        if (output) output.textContent = ratingDescription(current, count);
        this.dispatchEvent(new CustomEvent("syn-rating-change", {
          bubbles: true, composed: true, detail: { value: current },
        }));
      };
      this.addEventListener("change", this.handleRating);
      const selected = this.querySelector('input[type="radio"]:checked');
      const output = this.querySelector("output");
      if (output) output.textContent = ratingDescription(selected?.value ?? 0, this.querySelectorAll('input[type="radio"]').length);
    }
    disconnectedCallback() {
      if (this.handleRating) this.removeEventListener("change", this.handleRating);
    }
  }

  for (const [name, definition] of [
    ["syn-copy-button", CopyButton],
    ["syn-toast-region", ToastRegion],
    ["syn-image-compare", ImageCompare],
    ["syn-rating-input", RatingInput],
  ]) {
    if (!registry.get(name)) registry.define(name, definition);
  }
}
