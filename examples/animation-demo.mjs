import { animate, exit, stagger, observeReveals } from '../dist/syntyr.animate.mjs';

const cards = Array.from(document.querySelectorAll('#motion-cards .syn-panel'));
const status = document.querySelector('#animation-status');

document.querySelector('#animate-one')?.addEventListener('click', () => {
  const result = animate(cards[0], 'enter', { direction: 'up' });
  status.textContent = result ? 'Animated the first card.' : 'Animation skipped by browser preference or support.';
});

document.querySelector('#animate-all')?.addEventListener('click', () => {
  const results = stagger(cards, 'scale', { interval: 90 });
  status.textContent = results.some(Boolean) ? 'Animated all three cards.' : 'Animation skipped by browser preference or support.';
});

for (const [selector, preset] of [
  ['#animate-press', 'press'],
  ['#animate-highlight', 'highlight'],
  ['#animate-slide', 'slide'],
]) {
  document.querySelector(selector)?.addEventListener('click', () => {
    const result = animate(cards[0], preset);
    status.textContent = result ? `Played ${preset} feedback.` : 'Motion skipped by browser preference.';
  });
}

document.querySelector('#animate-exit')?.addEventListener('click', () => {
  const note = document.querySelector('#exit-note');
  if (!note || note.hidden) return;
  exit(note, () => { note.hidden = true; status.textContent = 'Dismissed note.'; });
});

// Enable controls only once this module and its action handlers have loaded.
for (const id of ['animate-one', 'animate-all', 'animate-press',
                  'animate-highlight', 'animate-slide', 'animate-exit']) {
  const button = document.getElementById(id);
  if (button) button.disabled = false;
}

// The explicit call is the entire initialization contract; no hidden state,
// persistent listener, or observer exists for ordinary Syntyr pages.
observeReveals(document);
