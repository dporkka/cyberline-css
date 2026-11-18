// Demo-only interaction: production desktop hosts should set data-syn-platform.
const selector = document.querySelector("#desktop-platform");
const root = document.querySelector(".syn-root[data-syn-platform]");
const allowed = new Set(["macos", "windows", "gnome"]);

if (selector && root) {
  selector.addEventListener("change", () => {
    if (allowed.has(selector.value)) {
      root.dataset.synPlatform = selector.value;
    }
  });
}
