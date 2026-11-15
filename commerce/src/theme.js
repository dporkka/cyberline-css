const HEX = /^#[0-9a-fA-F]{6}$/;

function rgb(hex) {
  return [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255);
}

function luminance(hex) {
  const [r, g, b] = rgb(hex).map((channel) =>
    channel <= 0.04045 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4);
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function contrast(a, b) {
  const high = Math.max(luminance(a), luminance(b));
  const low = Math.min(luminance(a), luminance(b));
  return Number(((high + 0.05) / (low + 0.05)).toFixed(2));
}

function foreground(background) {
  return contrast(background, '#000000') >= contrast(background, '#ffffff')
    ? '#000000' : '#ffffff';
}

export function generateTheme({ accent = '#79e3ed', surface = '#111827' } = {}) {
  if (typeof accent !== 'string' || !HEX.test(accent)) {
    throw new Error('accent must be a six-digit #RRGGBB value');
  }
  if (typeof surface !== 'string' || !HEX.test(surface)) {
    throw new Error('surface must be a six-digit #RRGGBB value');
  }
  const normalizedAccent = accent.toLowerCase();
  const normalizedSurface = surface.toLowerCase();
  const accentText = foreground(normalizedAccent);
  const surfaceText = foreground(normalizedSurface);
  return {
    schema_version: 1,
    kind: 'syntyr-generated-theme-tokens',
    output_license: 'MIT',
    tokens: {
      '--syn-accent': normalizedAccent,
      '--syn-accent-ink': accentText,
      '--syn-surface': normalizedSurface,
      '--syn-surface-ink': surfaceText,
    },
    accessibility: {
      accent_text_contrast: contrast(normalizedAccent, accentText),
      surface_text_contrast: contrast(normalizedSurface, surfaceText),
    },
    note: 'Generated token suggestions, not a substitute for full WCAG testing.',
  };
}
