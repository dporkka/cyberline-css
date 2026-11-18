import test, { afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { animate, stagger, observeReveals, withViewTransition } from '../src/animate.mjs';

const previous = {
  matchMedia: globalThis.matchMedia,
  getComputedStyle: globalThis.getComputedStyle,
  IntersectionObserver: globalThis.IntersectionObserver,
};
afterEach(() => {
  for (const [key, value] of Object.entries(previous)) {
    if (value === undefined) delete globalThis[key];
    else globalThis[key] = value;
  }
});

function target(tokens = {}) {
  const calls = [];
  const element = {
    animate(frames, options) {
      calls.push({ frames, options });
      return { finished: Promise.resolve(), cancel() {} };
    },
    dataset: {},
  };
  globalThis.getComputedStyle = () => ({
    getPropertyValue: (key) => tokens[key] ?? '',
  });
  globalThis.matchMedia = () => ({ matches: false });
  return { element, calls };
}

test('animation is always opt-in and safe with no DOM globals at import', () => {
  const { element, calls } = target();
  assert.equal(animate(element, 'fade').finished instanceof Promise, true);
  assert.equal(calls.length, 1);
});

test('reduced-motion and missing native animate leave content untouched', () => {
  const { element, calls } = target();
  globalThis.matchMedia = () => ({ matches: true });
  assert.equal(animate(element, 'enter'), null);
  assert.equal(calls.length, 0);
  globalThis.matchMedia = () => ({ matches: false });
  assert.equal(animate({ }, 'fade'), null);
});

test('fade is one-shot and releases its properties after completion', () => {
  const { element, calls } = target({ '--syn-motion-duration': '0.3s', '--syn-ease-out': 'ease-in-out' });
  animate(element, 'fade', { delay: 40 });
  assert.deepEqual(calls[0].frames, [{ opacity: 0 }, { opacity: 1 }]);
  assert.deepEqual(calls[0].options, {
    duration: 300, easing: 'ease-in-out', delay: 40, iterations: 1, fill: 'none',
  });
});

test('enter directions use independent translate and overrideable distance', () => {
  const { element, calls } = target({ '--syn-motion-distance': '2rem' });
  animate(element, 'enter', { direction: 'left' });
  assert.deepEqual(calls[0].frames, [
    { opacity: 0, translate: 'calc(-1 * 2rem) 0' },
    { opacity: 1, translate: '0 0' },
  ]);
  animate(element, 'enter', { direction: 'down', distance: '16px' });
  assert.equal(calls[1].frames[0].translate, '0 calc(-1 * 16px)');
});

test('scale is a finite compositor-friendly entrance', () => {
  const { element, calls } = target();
  animate(element, 'scale', { duration: 180 });
  assert.deepEqual(calls[0].frames, [
    { opacity: 0, scale: '0.96' }, { opacity: 1, scale: '1' },
  ]);
  assert.equal(calls[0].options.duration, 180);
  assert.equal(calls[0].options.iterations, 1);
});

test('unknown presets and directions fail explicitly', () => {
  const { element } = target();
  assert.throws(() => animate(element, 'wiggle'), /Unknown Syntyr animation/);
  assert.throws(() => animate(element, 'enter', { direction: 'diagonal' }), /Invalid direction/);
});

test('stagger applies a finite native delay without timers or mutation observers', () => {
  const { element: first, calls: a } = target({ '--syn-motion-stagger': '65ms' });
  const { element: second, calls: b } = target({ '--syn-motion-stagger': '65ms' });
  const result = stagger([first, second], 'fade', { delay: 20 });
  assert.equal(result.length, 2);
  assert.equal(a[0].options.delay, 20);
  assert.equal(b[0].options.delay, 85);
});

test('observeReveals observes only opted-in scoped elements once, and can disconnect', () => {
  const { element: first, calls: a } = target();
  const { element: second, calls: b } = target();
  first.dataset.synReveal = 'enter';
  second.dataset.synReveal = 'scale';
  const events = [];
  let observer;
  globalThis.IntersectionObserver = class {
    constructor(callback, options) { this.callback = callback; this.options = options; observer = this; }
    observe(e) { events.push(['observe', e]); }
    unobserve(e) { events.push(['unobserve', e]); }
    disconnect() { events.push(['disconnect']); }
  };
  const root = {
    querySelectorAll(selector) {
      assert.equal(selector, '.syn-root [data-syn-reveal]');
      return [first, second];
    },
  };
  const stop = observeReveals(root);
  assert.equal(typeof stop, 'function');
  assert.equal(observer.options.threshold, 0.1);
  observer.callback([{ target: first, isIntersecting: false }]);
  assert.equal(a.length, 0);
  observer.callback([{ target: first, isIntersecting: true }, { target: second, isIntersecting: true }]);
  assert.equal(a.length, 1);
  assert.equal(b.length, 1);
  assert.equal(events.filter(([event]) => event === 'unobserve').length, 2);
  stop();
  assert.equal(events.at(-1)[0], 'disconnect');
});

test('observer fallback avoids hiding content when JS features or motion are unavailable', () => {
  const { element, calls } = target();
  const root = { querySelectorAll: () => [element] };
  delete globalThis.IntersectionObserver;
  assert.equal(typeof observeReveals(root), 'function');
  globalThis.matchMedia = () => ({ matches: true });
  assert.equal(typeof observeReveals(root), 'function');
  assert.equal(calls.length, 0);
});

test('package subpath exposes only the optional native animation module', async () => {
  const api = await import('@syntyr/css/animate');
  assert.deepEqual(Object.keys(api).sort(), ['animate', 'observeReveals', 'stagger', 'withViewTransition']);
});


test('functional and negative distances are correctly negated by CSS calc', () => {
  const { element, calls } = target({ '--syn-motion-distance': 'calc(1rem + 2px)' });
  animate(element, 'enter', { direction: 'left' });
  assert.equal(calls[0].frames[0].translate, 'calc(-1 * calc(1rem + 2px)) 0');
  animate(element, 'enter', { direction: 'down', distance: '-16px' });
  assert.equal(calls[1].frames[0].translate, '0 calc(-1 * -16px)');
  animate(element, 'enter', { direction: 'right', distance: 'calc(1rem + 2px)' });
  assert.equal(calls[2].frames[0].translate, 'calc(1rem + 2px) 0');
});

test('rescan only observes and animates new elements, even with queued duplicate entries', () => {
  const { element: first, calls: one } = target();
  const { element: second, calls: two } = target();
  first.dataset.synReveal = 'enter';
  second.dataset.synReveal = 'fade';
  let nodes = [first];
  const observers = [];
  globalThis.IntersectionObserver = class {
    constructor(callback) {
      this.callback = callback;
      this.targets = [];
      observers.push(this);
    }
    observe(element) { this.targets.push(element); }
    unobserve() {}
    disconnect() {}
  };
  const root = { querySelectorAll: () => nodes };
  const firstStop = observeReveals(root);
  observers[0].callback([{ target: first, isIntersecting: true }]);
  assert.equal(one.length, 1);
  nodes = [first, second];
  const secondStop = observeReveals(root);
  assert.deepEqual(observers[1].targets, [second]);
  observers[1].callback([
    { target: first, isIntersecting: true },
    { target: second, isIntersecting: true },
  ]);
  assert.equal(one.length, 1);
  assert.equal(two.length, 1);
  firstStop();
  secondStop();
});

test('two observers racing for the same element still animate it once', () => {
  const { element, calls } = target();
  element.dataset.synReveal = 'fade';
  const observers = [];
  globalThis.IntersectionObserver = class {
    constructor(callback) { this.callback = callback; observers.push(this); }
    observe() {}
    unobserve() {}
    disconnect() {}
  };
  const root = { querySelectorAll: () => [element] };
  const stopOne = observeReveals(root);
  const stopTwo = observeReveals(root);
  const entry = { target: element, isIntersecting: true };
  observers[0].callback([entry]);
  observers[1].callback([entry]);
  assert.equal(calls.length, 1);
  stopOne();
  stopTwo();
});


test('withViewTransition performs updates synchronously without API or under reduced motion', () => {
  globalThis.matchMedia = () => ({ matches: false });
  let count = 0;
  assert.equal(withViewTransition(() => count++, {}), null);
  assert.equal(count, 1);
  globalThis.matchMedia = () => ({ matches: true });
  assert.equal(withViewTransition(() => count++, {
    startViewTransition() { throw Error('reduced motion must not animate'); },
  }), null);
  assert.equal(count, 2);
});

test('withViewTransition uses native API when present and preserves its result', () => {
  globalThis.matchMedia = () => ({ matches: false });
  const transition = { finished: Promise.resolve() };
  let count = 0;
  const root = {
    startViewTransition(update) {
      update();
      return transition;
    },
  };
  assert.equal(withViewTransition(() => count++, root), transition);
  assert.equal(count, 1);
  assert.throws(() => withViewTransition(null, root), /update callback/);
});
