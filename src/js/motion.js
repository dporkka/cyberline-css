/* Opt-in Web Animations orchestration. No MutationObserver, timers or auto-start. */
const instances = new WeakMap();
const presets = {
  fade: [{opacity: 0}, {opacity: 1}],
  scale: [{opacity: 0, transform: "scale(.96)"}, {opacity: 1, transform: "scale(1)"}],
  enter: [{opacity: 0, transform: "translateY(.75rem)"}, {opacity: 1, transform: "translateY(0)"}],
};

export function enhanceMotion(root) {
  if (!root || typeof root.querySelectorAll !== "function") {
    throw new TypeError("enhanceMotion(root) needs an Element, Document or DocumentFragment");
  }
  if (instances.has(root)) return instances.get(root);
  let destroyed = false;
  const active = new Map();
  const seen = new WeakSet();
  const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
  const cancelAll = () => {
    for (const animation of active.values()) animation.cancel();
    active.clear();
  };

  const api = {
    play(element, effect = element?.dataset?.synMotionJs || "enter") {
      if (destroyed || !element || !(root === element || root.contains(element))) return null;
      const previous = active.get(element);
      if (previous) {
        previous.cancel();
        active.delete(element);
      }
      if (preference.matches || typeof element.animate !== "function" || !presets[effect]) return null;
      const animation = element.animate(presets[effect], {
        duration: 240,
        easing: "cubic-bezier(.16, 1, .3, 1)",
        fill: "none",
      });
      active.set(element, animation);
      const finish = () => {
        if (active.get(element) === animation) active.delete(element);
      };
      animation.addEventListener("finish", finish, {once: true});
      animation.addEventListener("cancel", finish, {once: true});
      return animation;
    },
    refresh() {
      if (destroyed) return;
      const elements = [
        ...(root.matches?.("[data-syn-motion-js]") ? [root] : []),
        ...root.querySelectorAll("[data-syn-motion-js]"),
      ];
      for (const element of elements) {
        if (seen.has(element)) continue;
        seen.add(element);
        api.play(element);
      }
    },
    destroy() {
      if (destroyed) return;
      destroyed = true;
      cancelAll();
      preference.removeEventListener("change", onChange);
      instances.delete(root);
    },
  };
  function onChange(event) {
    if (event.matches) cancelAll();
  }
  preference.addEventListener("change", onChange);
  instances.set(root, api);
  api.refresh();
  return api;
}
