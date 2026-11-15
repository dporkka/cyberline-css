/* Opt-in progressive SVG interactions. Never runs until enhanceViz(root). */
const instances = new WeakMap();

export function enhanceViz(root) {
  if (!root || typeof root.querySelectorAll !== "function") {
    throw new TypeError("enhanceViz(root) needs an Element, Document or DocumentFragment");
  }
  if (instances.has(root)) return instances.get(root);
  const charts = new Map();
  let destroyed = false;

  function mount(chart) {
    const abort = new AbortController();
    const saved = new Map();
    const tip = document.createElement("div");
    tip.className = "syn-chart-tooltip";
    tip.dataset.synVizTip = "";
    tip.setAttribute("role", "tooltip");
    tip.setAttribute("aria-hidden", "true"); // points have their own accessible names
    tip.hidden = true;
    chart.append(tip);
    const line = chart.querySelector("[data-syn-crosshair]");
    const wasHidden = line?.hasAttribute("hidden") ?? true;
    const originalX1 = line?.getAttribute("x1") ?? null;
    const originalX2 = line?.getAttribute("x2") ?? null;
    if (line) line.setAttribute("hidden", "");

    const points = () => [...chart.querySelectorAll("[data-syn-point]")];
    const restore = (point, attrs) => {
      if (attrs.tab === null) point.removeAttribute("tabindex");
      else point.setAttribute("tabindex", attrs.tab);
      if (attrs.name === null) point.removeAttribute("aria-label");
      else point.setAttribute("aria-label", attrs.name);
    };
    const sync = () => {
      const current = points();
      for (const point of current) {
        if (saved.has(point)) continue;
        saved.set(point, {tab: point.getAttribute("tabindex"), name: point.getAttribute("aria-label")});
        if (!point.hasAttribute("aria-label")) {
          point.setAttribute("aria-label", point.dataset.synValue === undefined
            ? (point.dataset.synLabel || "Data point")
            : `${point.dataset.synLabel || "Data point"}: ${point.dataset.synValue}`);
        }
      }
      const active = current.indexOf(document.activeElement);
      const selected = active < 0 ? 0 : active;
      current.forEach((point, i) => point.setAttribute("tabindex", i === selected ? "0" : "-1"));
      for (const [point, attrs] of saved) {
        if (!current.includes(point)) {
          restore(point, attrs);
          saved.delete(point);
        }
      }
    };
    const hide = () => {
      tip.hidden = true;
      if (line) line.setAttribute("hidden", "");
    };
    const show = (point) => {
      if (!point || !chart.contains(point)) return;
      const label = point.dataset.synLabel || point.getAttribute("aria-label") || "Data point";
      tip.textContent = point.dataset.synValue === undefined ? label : `${label}: ${point.dataset.synValue}`;
      tip.hidden = false;
      const box = chart.getBoundingClientRect();
      const anchor = point.getBoundingClientRect();
      const x = anchor.left + anchor.width / 2 - box.left;
      const y = anchor.top + anchor.height / 2 - box.top;
      tip.style.left = `${Math.max(0, Math.min(box.width - tip.offsetWidth, x - tip.offsetWidth / 2))}px`;
      tip.style.top = `${Math.max(0, y - tip.offsetHeight - 10)}px`;
      if (line) {
        const lx = point.getAttribute("data-syn-x") || point.getAttribute("cx");
        if (lx !== null) {
          line.setAttribute("x1", lx);
          line.setAttribute("x2", lx);
          line.removeAttribute("hidden");
        } else line.setAttribute("hidden", "");
      }
    };
    const locate = (target) => {
      const candidate = target?.closest?.("[data-syn-point]");
      return candidate && chart.contains(candidate) ? candidate : null;
    };
    chart.addEventListener("pointerover", (event) => {
      const point = locate(event.target);
      if (point) show(point);
    }, {signal: abort.signal});
    chart.addEventListener("pointerout", (event) => {
      if (locate(event.target) && !locate(event.relatedTarget)) hide();
    }, {signal: abort.signal});
    chart.addEventListener("pointerdown", (event) => {
      locate(event.target)?.focus();
    }, {signal: abort.signal});
    chart.addEventListener("focusin", (event) => {
      const point = locate(event.target);
      if (point) show(point);
    }, {signal: abort.signal});
    chart.addEventListener("focusout", (event) => {
      if (!chart.contains(event.relatedTarget)) hide();
    }, {signal: abort.signal});
    chart.addEventListener("keydown", (event) => {
      const point = locate(event.target);
      if (!point) return;
      if (event.key === "Escape") { hide(); return; }
      if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
      const all = points();
      const index = all.indexOf(point);
      if (index < 0) return;
      event.preventDefault();
      const next = event.key === "Home" ? 0 : event.key === "End" ? all.length - 1
        : (index + (event.key === "ArrowRight" ? 1 : -1) + all.length) % all.length;
      all.forEach((p, i) => p.setAttribute("tabindex", i === next ? "0" : "-1"));
      all[next].focus();
      show(all[next]);
    }, {signal: abort.signal});

    let observer;
    if (chart.hasAttribute("data-syn-viz-resize") && typeof ResizeObserver === "function") {
      observer = new ResizeObserver((entries) => {
        if (destroyed || !chart.isConnected) return;
        for (const entry of entries) {
          chart.dispatchEvent(new CustomEvent("syntyr:viz:resize", {
            detail: {width: entry.contentRect.width, height: entry.contentRect.height},
          }));
        }
      });
      observer.observe(chart);
    }
    sync();
    return {refresh: sync, destroy() {
      abort.abort();
      observer?.disconnect();
      tip.remove();
      if (line) {
        if (wasHidden) line.setAttribute("hidden", "");
        else line.removeAttribute("hidden");
        if (originalX1 === null) line.removeAttribute("x1");
        else line.setAttribute("x1", originalX1);
        if (originalX2 === null) line.removeAttribute("x2");
        else line.setAttribute("x2", originalX2);
      }
      for (const [point, attrs] of saved) restore(point, attrs);
      saved.clear();
    }};
  }

  const api = {
    refresh() {
      if (destroyed) return;
      const all = [
        ...(root.matches?.('[data-syn-viz="points"]') ? [root] : []),
        ...root.querySelectorAll('[data-syn-viz="points"]'),
      ];
      for (const [chart, state] of charts) {
        if (!all.includes(chart)) { state.destroy(); charts.delete(chart); }
      }
      for (const chart of all) {
        if (charts.has(chart)) charts.get(chart).refresh();
        else charts.set(chart, mount(chart));
      }
    },
    destroy() {
      if (destroyed) return;
      destroyed = true;
      for (const state of charts.values()) state.destroy();
      charts.clear();
      instances.delete(root);
    },
  };
  instances.set(root, api);
  api.refresh();
  return api;
}
