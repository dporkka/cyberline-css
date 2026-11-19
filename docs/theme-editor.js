/* Optional documentation-only enhancement. Distributed SYNTYR CSS needs no JS. */
(() => {
  const theme = document.getElementById('theme');
  const accent = document.getElementById('accent');
  const intensity = document.getElementById('intensity');
  const onAccent = document.getElementById('on-accent');
  const preview = document.getElementById('preview');
  const contrastResult = document.getElementById('contrast-result');
  const generated = document.getElementById('generated-css');
  const reset = document.getElementById('reset-theme');

  function luminance(hex) {
    const channels = [1, 3, 5].map((index) => parseInt(hex.slice(index, index + 2), 16) / 255);
    const linear = channels.map((value) => value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4);
    return linear[0] * 0.2126 + linear[1] * 0.7152 + linear[2] * 0.0722;
  }

  function contrastRatio(first, second) {
    const a = luminance(first);
    const b = luminance(second);
    return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
  }

  function render() {
    preview.dataset.synIntensity = intensity.value;
    preview.style.setProperty('--syn-accent', accent.value);
    preview.style.setProperty('--syn-on-accent', onAccent.value);
    const ratio = contrastRatio(accent.value, onAccent.value);
    const passes = ratio >= 4.5;
    contrastResult.dataset.result = passes ? 'pass' : 'fail';
    contrastResult.textContent = `Primary button text contrast: ${ratio.toFixed(2)}:1 — ${passes ? 'meets' : 'below'} the WCAG AA normal-text 4.5:1 threshold.`;
    generated.textContent = `/* Set data-syn-intensity="${intensity.value}" on your Syntyr root or nested region. */\n.syn-root[data-syn-theme="${theme.value}"],\n.syn-root [data-syn-theme="${theme.value}"] {\n  --syn-accent: ${accent.value};\n  --syn-on-accent: ${onAccent.value};\n}`;
  }

  function loadThemeDefaults() {
    preview.dataset.synTheme = theme.value;
    preview.style.removeProperty('--syn-accent');
    preview.style.removeProperty('--syn-on-accent');
    const defaults = getComputedStyle(preview);
    accent.value = defaults.getPropertyValue('--syn-accent').trim();
    onAccent.value = defaults.getPropertyValue('--syn-on-accent').trim();
    render();
  }

  theme.addEventListener('change', loadThemeDefaults);
  intensity.addEventListener('change', render);
  accent.addEventListener('input', render);
  onAccent.addEventListener('input', render);
  reset.addEventListener('click', loadThemeDefaults);
  loadThemeDefaults();
})();
