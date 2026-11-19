import { defineConfig, presetWind3 } from 'unocss';

// Bench-only configuration: scan only Uno markup, never Tailwind/Syntyr markup.
export default defineConfig({
  presets: [presetWind3()],
  content: { filesystem: ['./generated/uno/*.html'] },
});
