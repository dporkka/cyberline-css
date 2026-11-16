/* Documentation-only progressive enhancement. Gallery previews require no JS. */
(() => {
  "use strict";
  const controls = document.getElementById("blocks-controls");
  const query = document.getElementById("blocks-search");
  const category = document.getElementById("blocks-category");
  const theme = document.getElementById("blocks-theme");
  const results = document.getElementById("blocks-results");
  const empty = document.getElementById("blocks-empty");
  const cards = Array.from(document.querySelectorAll("[data-block-id]"));
  if (!controls || !query || !category || !theme || !results || !empty || !cards.length) return;

  const indexed = cards.map(card => ({
    card,
    words: (card.querySelector("h2")?.textContent || "") + " " + (card.dataset.blockKeywords || ""),
    category: card.dataset.blockCategory,
    preview: card.querySelector(".blocks-preview > .syn-root"),
    code: card.querySelector(".blocks-source code"),
    copy: card.querySelector("[data-block-copy]")
  }));
  for (const item of indexed) item.words = item.words.toLocaleLowerCase();

  function filter() {
    const terms = query.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    const selected = category.value;
    let visible = 0;
    for (const item of indexed) {
      const matches = (selected === "all" || item.category === selected) && terms.every(term => item.words.includes(term));
      item.card.hidden = !matches;
      if (matches) visible += 1;
    }
    empty.hidden = visible !== 0;
    results.textContent = "Showing " + visible + " of " + indexed.length + " blocks.";
  }

  function changeTheme() {
    for (const item of indexed) {
      if (item.preview) item.preview.setAttribute("data-syn-theme", theme.value);
    }
  }

  controls.hidden = false;
  query.addEventListener("input", filter);
  category.addEventListener("change", filter);
  theme.addEventListener("change", changeTheme);
  filter();

  for (const item of indexed) {
    if (!item.copy || !item.code) continue;
    item.copy.hidden = false;
    item.copy.addEventListener("click", async () => {
      const value = item.code.textContent.trim();
      try {
        if (!navigator.clipboard?.writeText) throw new Error("Clipboard unavailable");
        await navigator.clipboard.writeText(value);
        results.textContent = item.card.querySelector("h2").textContent + " HTML copied.";
      } catch {
        const details = item.code.closest("details");
        if (details) details.open = true;
        const selection = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(item.code);
        selection?.removeAllRanges();
        selection?.addRange(range);
        results.textContent = "Source selected. Press Ctrl+C or Cmd+C to copy.";
      }
    });
  }

  // The SVG explorer is a progressive enhancement: previews and native source
  // disclosure remain usable when scripting or clipboard access is unavailable.
  const iconsControls = document.getElementById("icons-controls");
  const iconsSearch = document.getElementById("icons-search");
  const iconsSize = document.getElementById("icons-size");
  const iconsTheme = document.getElementById("icons-theme");
  const iconsResults = document.getElementById("icons-results");
  const iconsGrid = document.getElementById("blocks-icons-grid");
  const iconsSection = document.querySelector(".blocks-icons-section");
  const icons = Array.from(document.querySelectorAll("[data-icon-id]"));
  if (iconsControls && iconsSearch && iconsSize && iconsTheme &&
      iconsResults && iconsGrid && iconsSection && icons.length) {
    const entries = icons.map(card => ({
      card,
      words: (card.dataset.iconKeywords || "").toLocaleLowerCase(),
      source: card.querySelector("details code"),
      copy: card.querySelector("[data-icon-copy]")
    }));
    function filterIcons() {
      const terms = iconsSearch.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
      let visible = 0;
      for (const item of entries) {
        const show = terms.every(term => item.words.includes(term));
        item.card.hidden = !show;
        if (show) visible++;
      }
      iconsResults.textContent = "Showing " + visible + " of " + entries.length + " icons.";
    }
    iconsControls.hidden = false;
    iconsSearch.addEventListener("input", filterIcons);
    iconsSize.addEventListener("change", () => {
      iconsGrid.style.setProperty("--syn-gallery-icon-size", iconsSize.value);
    });
    iconsTheme.addEventListener("change", () => {
      iconsSection.setAttribute("data-syn-theme", iconsTheme.value);
    });
    for (const item of entries) {
      if (!item.copy || !item.source) continue;
      item.copy.hidden = false;
      item.copy.addEventListener("click", async () => {
        const value = item.source.textContent.trim();
        try {
          if (!navigator.clipboard?.writeText) throw new Error("Clipboard unavailable");
          await navigator.clipboard.writeText(value);
          iconsResults.textContent = "SVG copied.";
        } catch {
          const details = item.source.closest("details");
          if (details) details.open = true;
          const range = document.createRange();
          range.selectNodeContents(item.source);
          const selection = window.getSelection();
          selection?.removeAllRanges();
          selection?.addRange(range);
          iconsResults.textContent = "SVG source selected. Press Ctrl+C or Cmd+C to copy.";
        }
      });
    }
    filterIcons();
  }
})();
