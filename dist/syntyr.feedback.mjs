/* Optional feedback enhancement: no dependencies, global handlers, or auto-init. */
const cleanups = new WeakMap();
const dismissTimers = new WeakMap();

export function announceFeedback(status, message, { duration = 4500 } = {}) {
  if (!status?.hasAttribute?.("data-syn-feedback-status")) return false;
  const oldTimer = dismissTimers.get(status);
  if (oldTimer !== undefined) clearTimeout(oldTimer);
  status.textContent = String(message);
  status.hidden = false;
  dismissTimers.delete(status);
  if (duration > 0) {
    const timer = setTimeout(() => {
      status.hidden = true;
      status.textContent = "";
      dismissTimers.delete(status);
    }, duration);
    dismissTimers.set(status, timer);
  }
  return true;
}

export function enhanceFeedback(root = document) {
  if (!root?.addEventListener || !root?.contains) {
    throw new TypeError("enhanceFeedback expects a document or element");
  }
  if (cleanups.has(root)) return cleanups.get(root);

  const copyButtons = Array.from(root.querySelectorAll("button[data-syn-copy-target]"));
  // Disabled in server-rendered markup until this optional module is installed.
  for (const button of copyButtons) {
    if (button.closest("[data-syn-feedback-scope]")) button.disabled = false;
  }
  const onClick = async (event) => {
    const button = event.target?.closest?.("button[data-syn-copy-target]");
    if (!button || !root.contains(button) || button.disabled) return;
    const scope = button.closest("[data-syn-feedback-scope]");
    if (!scope || !root.contains(scope)) return;
    const status = scope.querySelector("[data-syn-feedback-status]");
    if (!status) return;
    const targetId = button.getAttribute("data-syn-copy-target");
    // Exact ID equality; never interpolate user data into a CSS selector.
    const target = Array.from(scope.querySelectorAll("[id]")).find((node) => node.id === targetId);
    if (!target || !targetId) {
      announceFeedback(status, "Copy source unavailable.");
      return;
    }
    const text = "value" in target ? target.value : target.textContent;
    try {
      if (!navigator.clipboard?.writeText) throw new Error("Clipboard API unavailable");
      await navigator.clipboard.writeText(String(text ?? ""));
      announceFeedback(status, "Copied to clipboard.");
    } catch {
      announceFeedback(status, "Copy unavailable. Select and copy the text manually.");
    }
  };
  root.addEventListener("click", onClick);
  const cleanup = () => {
    root.removeEventListener("click", onClick);
    for (const button of copyButtons) button.disabled = true;
    cleanups.delete(root);
  };
  cleanups.set(root, cleanup);
  return cleanup;
}
