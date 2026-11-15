/* Docs-only progressive enhancement; Syntyr CSS ships with zero runtime JavaScript. */
(() => {
  "use strict";
  const examples = {
    metrics: `<section class="syn-region">
  <h2 class="syn-heading">System telemetry</h2>
  <div class="syn-stats">
    <article class="syn-stat"><span class="syn-stat-label">USERS</span><p class="syn-stat-value">2,840</p></article>
    <article class="syn-stat"><span class="syn-stat-label">UPTIME</span><p class="syn-stat-value">99.9%</p></article>
    <article class="syn-stat"><span class="syn-stat-label">ALERTS</span><p class="syn-stat-value">02</p></article>
  </div>
</section>`,
    actions: `<section class="syn-panel" style="--syn-panel-radius: .75rem; --syn-panel-padding: 1.5rem">
  <h2 class="syn-heading">Deployment ready</h2>
  <p class="syn-muted">Scoped tokens customize this panel without a new component class.</p>
  <div class="syn-inline syn-u-wrap">
    <button class="syn-button syn-button--primary">Deploy</button>
    <button class="syn-button syn-button--outline">Preview</button>
    <button class="syn-button syn-button--ghost">Cancel</button>
  </div>
</section>`,
    form: `<form class="syn-panel syn-form" action="#" method="get">
  <h2 class="syn-heading">Create workspace</h2>
  <label class="syn-label" for="workspace-name">WORKSPACE NAME</label>
  <input id="workspace-name" class="syn-input syn-u-w-full" name="workspace" required placeholder="Example Studio">
  <label class="syn-check"><input type="checkbox" required> I accept the terms</label>
  <button class="syn-button syn-button--primary" type="submit">Create</button>
  <p class="syn-muted">Preview only; forms cannot submit in this frame.</p>
</form>`,
    cards: `<section class="syn-grid">
  <article class="syn-panel" style="--syn-panel-padding: 1.5rem; --syn-panel-radius: .65rem">
    <span class="syn-badge">ANALYTICS</span>
    <h2 class="syn-heading">Discover patterns</h2>
    <p class="syn-muted">Readable content and restrained color.</p>
    <a class="syn-button syn-button--primary" href="#details">Explore</a>
  </article>
  <article class="syn-panel" style="--syn-panel-padding: 1.5rem; --syn-panel-radius: .65rem">
    <span class="syn-badge">WORKFLOWS</span>
    <h2 class="syn-heading">Move faster</h2>
    <p class="syn-muted">Reusable visual language in ordinary HTML.</p>
    <a class="syn-button" href="#details">Learn more</a>
  </article>
</section>`
  };
  const example = document.getElementById("playground-example");
  const theme = document.getElementById("playground-theme");
  const size = document.getElementById("playground-size");
  const density = document.getElementById("playground-density");
  const state = document.getElementById("playground-state");
  const markup = document.getElementById("playground-markup");
  const preview = document.getElementById("playground-preview");
  const status = document.getElementById("playground-status");
  const renderButton = document.getElementById("playground-render");
  const copyButton = document.getElementById("playground-copy");
  const copySetupButton = document.getElementById("playground-copy-setup");
  const supportedThemes = new Set(["studio", "grid", "noir", "industrial", "terminal", "corporate", "minimal", "auto"]);
  const supportedDensities = new Set(["comfortable", "compact", "spacious"]);
  const supportedWidths = new Set(["fit", "375", "768", "1280"]);
  let framePending = false;

  function selectedTheme() {
    return supportedThemes.has(theme.value) ? theme.value : "studio";
  }

  function selectedDensity() {
    return supportedDensities.has(density.value) ? density.value : "comfortable";
  }

  function updateViewport() {
    const requested = supportedWidths.has(size.value) ? size.value : "fit";
    preview.style.width = requested === "fit" ? "100%" : `${requested}px`;
  }

  function previewControlState() {
    // The sandbox has no scripts or form submission. This change is confined to
    // the rendered frame, so the source editor and exported HTML stay untouched.
    const doc = preview.contentDocument;
    if (!doc) return;
    const current = state.value;
    if (current === "default") return;
    const target = current === "invalid"
      ? doc.querySelector("input:not([type=hidden]), select, textarea")
      : doc.querySelector("button:not([disabled]), input:not([type=hidden]):not([disabled]), select:not([disabled]), textarea:not([disabled])");
    if (!target) {
      status.textContent = `Preview updated; no suitable ${current === "invalid" ? "form field" : "native control"} in this example.`;
      return;
    }
    if (current === "invalid") target.setAttribute("aria-invalid", "true");
    if (current === "disabled") target.disabled = true;
    status.textContent = `Preview updated with a ${current} control. Source HTML unchanged.`;
  }
  preview.addEventListener("load", previewControlState);

  function render() {
    // No script or form permissions, even if an editor pastes arbitrary markup.
    // allow-same-origin permits Syntyr's *local* stylesheet to load; it does
    // not permit script execution without allow-scripts.
    updateViewport();
    const shell = `<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self' 'unsafe-inline'; img-src data:; base-uri 'none'; form-action 'none'">
<link rel="stylesheet" href="../dist/syntyr.all.css">
<style>html,body{min-height:100%;} body.syn-root{margin:0;padding:1.5rem;} *,*::before,*::after{box-sizing:border-box;}</style>
</head><body class="syn-root syn-page" data-syn-theme="${selectedTheme()}" data-syn-density="${selectedDensity()}">${markup.value}</body></html>`;
    preview.srcdoc = shell;
    status.textContent = `Preview updated: ${theme.options[theme.selectedIndex].text} theme, ${selectedDensity()} density.`;
  }

  function scheduleRender() {
    if (framePending) return;
    framePending = true;
    requestAnimationFrame(() => { framePending = false; render(); });
  }

  function loadExample() {
    markup.value = examples[example.value] || examples.metrics;
    scheduleRender();
  }

  example.addEventListener("change", loadExample);
  theme.addEventListener("change", scheduleRender);
  density.addEventListener("change", scheduleRender);
  state.addEventListener("change", scheduleRender);
  size.addEventListener("change", updateViewport);
  markup.addEventListener("input", scheduleRender);
  renderButton.addEventListener("click", render);
  async function copySource(source, successMessage) {
    try {
      if (!navigator.clipboard?.writeText) throw new Error("Clipboard unavailable");
      await navigator.clipboard.writeText(source);
      status.textContent = successMessage;
    } catch (_error) {
      markup.focus();
      markup.select();
      status.textContent = "Clipboard unavailable. Editable HTML selected; copy it with your keyboard.";
    }
  }

  copyButton.addEventListener("click", () => copySource(markup.value, "HTML copied."));
  copySetupButton.addEventListener("click", () => {
    const source = `<!-- Put syntyr.all.css at the path referenced below. -->
<link rel="stylesheet" href="syntyr.all.css">
<section class="syn-root" data-syn-theme="${selectedTheme()}" data-syn-density="${selectedDensity()}">
${markup.value}
</section>`;
    copySource(source, "CSS setup and HTML copied.");
  });
  loadExample();
})();

/* Geometry mixer is docs-only; application styles remain zero-JavaScript. */
(() => {
  "use strict";
  const byId = id => document.getElementById(id);
  const shape = byId("geometry-shape");
  const stroke = byId("geometry-stroke");
  const paint = byId("geometry-border-paint");
  const inlay = byId("geometry-inlay");
  const theme = byId("playground-theme");
  const frame = byId("geometry-preview");
  const stage = byId("geometry-preview-theme");
  const output = byId("geometry-code");
  const status = byId("geometry-status");
  const cornerIds = ["tl", "tr", "br", "bl"];
  const corners = cornerIds.map(corner => byId(`geometry-cut-${corner}`));
  const allowedShapes = new Set(["bevel", "notch", "step", "facet"]);
  const borderPaints = {
    outline: null,
    accent: "var(--syn-accent)",
    gradient: "linear-gradient(120deg, var(--syn-accent), var(--syn-frame-strong))"
  };
  const wash = "linear-gradient(145deg, color-mix(in srgb, var(--syn-accent) 9%, transparent), transparent 70%)";

  function updateGeometry() {
    const profile = allowedShapes.has(shape.value) ? shape.value : "bevel";
    const width = Math.max(1, Math.min(6, Number(stroke.value) || 1));
    frame.className = `syn-panel syn-frame syn-frame--${profile}`;
    stage.dataset.synTheme = theme.value;
    const declarations = [];
    corners.forEach((control, index) => {
      const corner = cornerIds[index];
      const pixels = Math.max(0, Math.min(48, Number(control.value) || 0));
      const value = `${pixels}px`;
      byId(`geometry-cut-${corner}-value`).textContent = value;
      frame.style.setProperty(`--syn-frame-cut-${corner}`, value);
      declarations.push(`--syn-frame-cut-${corner}: ${value};`);
    });
    byId("geometry-stroke-value").textContent = `${width}px`;
    frame.style.setProperty("--syn-frame-stroke", `${width}px`);
    declarations.push(`--syn-frame-stroke: ${width}px;`);
    const selectedPaint = Object.hasOwn(borderPaints, paint.value) ? borderPaints[paint.value] : null;
    if (selectedPaint) {
      frame.style.setProperty("--syn-frame-border-paint", selectedPaint);
      declarations.push(`--syn-frame-border-paint: ${selectedPaint};`);
    } else {
      frame.style.removeProperty("--syn-frame-border-paint");
    }
    if (inlay.checked) {
      frame.style.setProperty("--syn-frame-inlay-paint", wash);
      declarations.push(`--syn-frame-inlay-paint: ${wash};`);
    } else {
      frame.style.removeProperty("--syn-frame-inlay-paint");
    }
    output.value = `<!-- Load syntyr.core.css and syntyr.geometry.css -->\n<section class="syn-root" data-syn-theme="${stage.dataset.synTheme}">\n  <article class="syn-panel syn-frame syn-frame--${profile}"\n    style="${declarations.join(" ")}">\n    <h2>Signal interface</h2>\n    <p>Semantic content with optional framing.</p>\n  </article>\n</section>`;
    status.textContent = "Geometry preview updated.";
  }

  for (const control of [shape, stroke, paint, inlay, theme, ...corners]) {
    control.addEventListener("input", updateGeometry);
    control.addEventListener("change", updateGeometry);
  }
  byId("geometry-copy").addEventListener("click", async () => {
    try {
      if (!navigator.clipboard?.writeText) throw new Error("Clipboard unavailable");
      await navigator.clipboard.writeText(output.value);
      status.textContent = "HTML copied.";
    } catch (_error) {
      output.focus();
      output.select();
      status.textContent = "HTML selected. Copy with your keyboard.";
    }
  });
  updateGeometry();
})();
