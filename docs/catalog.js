/* Optional documentation-only enhancement. Syntyr CSS requires no JavaScript. */
(() => {
  'use strict';
  const search = document.getElementById('catalog-search');
  const category = document.getElementById('catalog-category');
  const controls = document.getElementById('catalog-controls');
  const results = document.getElementById('catalog-results');
  const feedback = document.getElementById("catalog-feedback");
  const empty = document.getElementById('catalog-empty');
  const cards = [...document.querySelectorAll('.catalog-card')];
  if (!search || !category || !controls || !results || !feedback || !empty || !cards.length) return;

  const searchable = cards.map((card) => ({
    card,
    terms: `${card.querySelector('h2')?.textContent || ''} ${card.dataset.catalogKeywords || ''} ${card.querySelector('.syn-muted')?.textContent || ''}`.toLocaleLowerCase(),
  }));

  function updateResults() {
    const terms = search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    let count = 0;
    for (const {card, terms: text} of searchable) {
      const match = (category.value === 'all' || card.dataset.catalogCategory === category.value)
        && terms.every((term) => text.includes(term));
      card.hidden = !match;
      if (match) count += 1;
    }
    empty.hidden = count !== 0;
    results.textContent = `Showing ${count} of ${cards.length} examples.`;
  }

  const theme = document.getElementById('catalog-theme');
  const previewSize = document.getElementById('catalog-preview-size');
  const grid = document.getElementById('catalog-items');
  const root = document.querySelector('.syn-root');
  if (theme && root) {
    theme.addEventListener("change", () => {
      root.dataset.synTheme = theme.value;
    });
  }
  if (previewSize && grid) {
    previewSize.addEventListener("change", () => {
      grid.setAttribute('data-catalog-preview', previewSize.value);
    });
  }
  controls.hidden = false;
  search.addEventListener("input", updateResults);
  category.addEventListener("change", updateResults);
  updateResults();

  for (const card of cards) {
    const button = card.querySelector('[data-catalog-copy]');
    const code = card.querySelector('.catalog-source code');
    if (!button || !code) continue;
    const edit = document.createElement("a");
    edit.className = "syn-button catalog-edit";
    edit.href = `playground.html#component=${encodeURIComponent(card.getAttribute("aria-labelledby") || "")}`;
    edit.textContent = "Edit in playground";
    button.insertAdjacentElement("afterend", edit);
    button.hidden = false;
    button.addEventListener('click', async () => {
      const value = code.textContent.trim();
      try {
        if (!navigator.clipboard?.writeText) throw new Error('Clipboard API unavailable');
        await navigator.clipboard.writeText(value);
        feedback.textContent = `${card.querySelector('h2').textContent} HTML copied.`;
      } catch {
        code.closest('details').open = true;
        const selection = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(code);
        selection?.removeAllRanges();
        selection?.addRange(range);
        feedback.textContent = 'HTML selected. Use your keyboard to copy it.';
      }
    });
  }
})();
