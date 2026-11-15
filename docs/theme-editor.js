/* Optional documentation-only enhancement. Distributed SYNTYR CSS needs no JS. */
(() => {
  "use strict";
  const byId = id => document.getElementById(id);
  const theme = byId("theme");
  const intensity = byId("intensity");
  const density = byId("density");
  const preview = byId("preview");
  const contrastResult = byId("contrast-result");
  const generated = byId("generated-css");
  const generatedTokens = byId("generated-tokens");
  const copyStatus = byId("copy-status");
  const reset = byId("reset-theme");
  const colorTokens = {
    "background": "--syn-bg",
    "surface": "--syn-surface",
    "text-color": "--syn-text",
    "muted": "--syn-muted",
    "frame": "--syn-frame",
    "accent": "--syn-accent",
    "on-accent": "--syn-on-accent"
  };
  const colorControls = Object.fromEntries(
    Object.entries(colorTokens).map(([id, token]) => [token, byId(id)])
  );

  function luminance(hex) {
    const channels = [1, 3, 5].map(index => parseInt(hex.slice(index, index + 2), 16) / 255);
    const linear = channels.map(value => value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4);
    return linear[0] * 0.2126 + linear[1] * 0.7152 + linear[2] * 0.0722;
  }

  function contrastRatio(first, second) {
    const a = luminance(first);
    const b = luminance(second);
    return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
  }

  function pixelValue(raw, fallback) {
    const match = /^([\d.]+)(px|rem)$/.exec(raw.trim());
    if (!match) return fallback;
    const rootSize = parseFloat(getComputedStyle(document.documentElement).fontSize) || 16;
    return Number(match[1]) * (match[2] === "rem" ? rootSize : 1);
  }

  function render() {
    preview.dataset.synIntensity = intensity.value;
    preview.dataset.synDensity = density.value;
    const tokens = {};
    for (const [token, control] of Object.entries(colorControls)) {
      tokens[token] = control.value;
    }
    tokens["--syn-radius"] = `${byId("radius").value}px`;
    tokens["--syn-type-body"] = `${byId("body-size").value}px`;

    for (const [name, value] of Object.entries(tokens)) {
      preview.style.setProperty(name, value);
    }
    // Nested themes inherit an already-computed font-size unless we apply
    // the body type role to the region itself.
    preview.style.fontSize = tokens["--syn-type-body"];
    byId("radius-value").textContent = tokens["--syn-radius"];
    byId("body-size-value").textContent = tokens["--syn-type-body"];

    const buttonRatio = contrastRatio(tokens["--syn-accent"], tokens["--syn-on-accent"]);
    const bodyRatio = contrastRatio(tokens["--syn-text"], tokens["--syn-bg"]);
    const passes = buttonRatio >= 4.5 && bodyRatio >= 4.5;
    contrastResult.dataset.result = passes ? "pass" : "fail";
    contrastResult.textContent = `Primary button text contrast: ${buttonRatio.toFixed(2)}:1; body text contrast: ${bodyRatio.toFixed(2)}:1 — ${passes ? "both meet" : "one or both below"} the 4.5:1 normal-text threshold.`;

    generated.textContent = `/* Set data-syn-intensity="${intensity.value}" and data-syn-density="${density.value}" on the Syntyr region. */
/* Include this unlayered CSS after syntyr.core.css. */
.syn-root[data-syn-theme="${theme.value}"],
.syn-root [data-syn-theme="${theme.value}"] {
${Object.entries(tokens).map(([name, value]) => `  ${name}: ${value};`).join("\n")}
  font-size: var(--syn-type-body);
}`;
    generatedTokens.textContent = JSON.stringify({
      theme: theme.value,
      intensity: intensity.value,
      density: density.value,
      tokens
    }, null, 2);
  }

  function loadThemeDefaults() {
    preview.dataset.synTheme = theme.value;
    for (const token of Object.values(colorTokens)) preview.style.removeProperty(token);
    preview.style.removeProperty("--syn-radius");
    preview.style.removeProperty("--syn-type-body");
    preview.style.removeProperty("font-size");
    const defaults = getComputedStyle(preview);
    for (const [token, control] of Object.entries(colorControls)) {
      control.value = defaults.getPropertyValue(token).trim();
    }
    byId("radius").value = Math.round(pixelValue(defaults.getPropertyValue("--syn-radius"), 4));
    byId("body-size").value = Math.round(pixelValue(defaults.getPropertyValue("--syn-type-base"), 16));
    render();
  }

  async function copyCode(element, label) {
    try {
      if (!navigator.clipboard?.writeText) throw new Error("Clipboard unavailable");
      await navigator.clipboard.writeText(element.textContent);
      copyStatus.textContent = `${label} copied.`;
    } catch (_error) {
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(element);
      selection.removeAllRanges();
      selection.addRange(range);
      copyStatus.textContent = `Clipboard unavailable. ${label} selected; copy it with your keyboard.`;
    }
  }

  theme.addEventListener("change", loadThemeDefaults);
  reset.addEventListener("click", loadThemeDefaults);
  for (const control of [...Object.values(colorControls), byId("radius"), byId("body-size")]) {
    control.addEventListener("input", render);
  }
  intensity.addEventListener("change", render);
  density.addEventListener("change", render);
  byId("copy-css").addEventListener("click", () => copyCode(generated, "CSS"));
  byId("copy-tokens").addEventListener("click", () => copyCode(generatedTokens, "JSON preset"));
  loadThemeDefaults();
})();
