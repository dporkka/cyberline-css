import { animate, stagger, observeReveals } from '../dist/syntyr.animate.mjs';

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

// The explicit call is the entire initialization contract; no hidden state,
// global listener, or observer exists for ordinary Syntyr pages.
observeReveals(document);
