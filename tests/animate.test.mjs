import test, { afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { animate, stagger, observeReveals, exit } from '../src/animate.mjs';

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
  assert.deepEqual(Object.keys(api).sort(), ['animate', 'exit', 'observeReveals', 'stagger']);
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

function controlledTarget() {
  const animations = [];
  const element = {
    dataset: {},
    animate(frames, options) {
      let resolve, reject;
      const finished = new Promise((res, rej) => { resolve = res; reject = rej; });
      const animation = {
        frames, options, finished, cancelled: false,
        finish() { resolve(); },
        cancel() { this.cancelled = true; reject(new Error('cancelled')); },
      };
      animations.push(animation);
      return animation;
    },
  };
  globalThis.getComputedStyle = () => ({
    backgroundColor: 'rgb(255, 255, 255)',
    getPropertyValue: (key) => ({
      '--syn-motion-press-scale': '0.95',
      '--syn-accent-soft': 'rgb(220, 235, 255)',
    }[key] ?? ''),
  });
  return { element, animations };
}

test('a later animation on the same element replaces the previous one', async () => {
  const {element, animations} = controlledTarget();
  globalThis.matchMedia = () => ({matches: false});
  animate(element, 'fade');
  animate(element, 'scale');
  assert.equal(animations[0].cancelled, true);
  assert.equal(animations[1].cancelled, false);
  animations[1].finish();
  await Promise.allSettled(animations.map(a => a.finished));
});

test('live reduced-motion change cancels existing animations and detaches its listener', async () => {
  const listeners = new Set();
  const preference = {
    matches: false,
    addEventListener(name, fn) { assert.equal(name, 'change'); listeners.add(fn); },
    removeEventListener(name, fn) { assert.equal(name, 'change'); listeners.delete(fn); },
  };
  globalThis.matchMedia = () => preference;
  const first = controlledTarget(), second = controlledTarget();
  animate(first.element, 'enter');
  animate(second.element, 'fade');
  assert.equal(listeners.size, 1);
  preference.matches = true;
  for (const fn of [...listeners]) fn({matches: true});
  assert.equal(first.animations[0].cancelled, true);
  assert.equal(second.animations[0].cancelled, true);
  await Promise.allSettled([first.animations[0].finished, second.animations[0].finished]);
  assert.equal(listeners.size, 0);
});

test('exit retains end style until synchronous removal callback, without replay on cancellation', async () => {
  const {element, animations} = controlledTarget();
  globalThis.matchMedia = () => ({matches: false});
  const events = [];
  const animation = exit(element, () => {
    events.push('removed');
    assert.equal(animation.options.fill, 'forwards');
    assert.equal(animation.cancelled, false);
  }, {direction: 'left'});
  assert.equal(animation.frames[0].opacity, 1);
  assert.equal(animation.frames[1].opacity, 0);
  assert.equal(animation.frames[1].translate, 'calc(-1 * .75rem) 0');
  animation.finish();
  await animation.finished;
  await Promise.resolve();
  assert.deepEqual(events, ['removed']);
  assert.equal(animation.cancelled, true);
});

test('exit commits immediately without motion and never fires after replacement', async () => {
  const {element, animations} = controlledTarget();
  const callbacks = [];
  globalThis.matchMedia = () => ({matches: true});
  assert.equal(exit(element, () => callbacks.push('reduced')), null);
  assert.deepEqual(callbacks, ['reduced']);
  globalThis.matchMedia = () => ({matches: false});
  const outgoing = exit(element, () => callbacks.push('cancelled'));
  animate(element, 'fade');
  assert.equal(outgoing.cancelled, true);
  animations.at(-1).finish();
  await Promise.allSettled(animations.map(a => a.finished));
  await Promise.resolve();
  assert.deepEqual(callbacks, ['reduced']);
});

test('slide, press and highlight provide finite opt-in feedback keyframes', async () => {
  const {element, animations} = controlledTarget();
  globalThis.matchMedia = () => ({matches: false});
  animate(element, 'slide', {direction:'right'});
  assert.equal(animations[0].frames[0].translate, '.75rem 0');
  assert.equal(animations[0].frames[0].opacity, undefined);
  animate(element, 'press');
  assert.deepEqual(animations[1].frames.map(frame => frame.scale), ['1', '0.95', '1']);
  animate(element, 'highlight');
  assert.equal(animations[2].frames[0].backgroundColor, 'rgb(255, 255, 255)');
  assert.equal(animations[2].frames[1].backgroundColor, 'rgb(220, 235, 255)');
  assert.equal(animations[2].frames[2].backgroundColor, 'rgb(255, 255, 255)');
  animations[2].finish();
  await Promise.allSettled(animations.map(a => a.finished));
});

test('viewport reveal supports optional threshold and rootMargin', () => {
  const {element} = target();
  let args;
  globalThis.IntersectionObserver = class {
    constructor(callback, options) { args = options; }
    observe() {}
    unobserve() {}
    disconnect() {}
  };
  observeReveals({querySelectorAll: () => [element]}, {threshold: .3, rootMargin: '0px 0px 15px 0px'});
  assert.deepEqual(args, {threshold: .3, rootMargin: '0px 0px 15px 0px'});
});

test('finished exit never removes content after a new animation replaces it before callbacks run', async () => {
  const {element, animations} = controlledTarget();
  globalThis.matchMedia = () => ({matches: false});
  const removed = [];
  const outgoing = exit(element, () => removed.push('removed'));
  outgoing.finish(); // Queues a success callback which native cancel cannot undo.
  const replacement = animate(element, 'fade');
  replacement.finish();
  await Promise.allSettled(animations.map(animation => animation.finished));
  await Promise.resolve();
  assert.equal(outgoing.cancelled, true);
  assert.deepEqual(removed, [], 'a stale queued exit must not remove its replacement target');
});

test('switching to reduced motion completes an in-flight exit immediately without replay', async () => {
  const listeners = new Set();
  const preference = {
    matches: false,
    addEventListener(name, fn) { listeners.add(fn); },
    removeEventListener(name, fn) { listeners.delete(fn); },
  };
  globalThis.matchMedia = () => preference;
  const {element, animations} = controlledTarget();
  let removed = 0;
  exit(element, () => { removed += 1; });
  assert.equal(removed, 0);
  preference.matches = true;
  for (const listener of [...listeners]) listener({matches: true});
  await Promise.allSettled(animations.map(animation => animation.finished));
  await Promise.resolve();
  assert.equal(removed, 1, 'reduced motion must not strand a pending dismissal');
  assert.equal(animations[0].cancelled, true);
  assert.equal(listeners.size, 0);
});

test('reduced-motion cancellation does not run a replaced exit callback', async () => {
  const listeners = new Set();
  const preference = {
    matches: false,
    addEventListener(_, fn) { listeners.add(fn); },
    removeEventListener(_, fn) { listeners.delete(fn); },
  };
  globalThis.matchMedia = () => preference;
  const {element, animations} = controlledTarget();
  let removed = 0;
  exit(element, () => { removed += 1; });
  animate(element, 'fade');
  preference.matches = true;
  for (const fn of [...listeners]) fn({matches: true});
  await Promise.allSettled(animations.map(animation => animation.finished));
  await Promise.resolve();
  assert.equal(removed, 0);
  assert.equal(animations.every(a => a.cancelled), true);
});

test('completed exit releases its filled effect when callback starts a new animation', async () => {
  const {element, animations} = controlledTarget();
  globalThis.matchMedia = () => ({matches: false});
  const outgoing = exit(element, () => {
    animate(element, 'press');
  });
  outgoing.finish();
  await outgoing.finished;
  await Promise.resolve();
  assert.equal(animations.length, 2);
  assert.equal(outgoing.cancelled, true, 'old forwards-filled opacity must be released');
  assert.equal(animations[1].cancelled, false, 'cleanup must not cancel the new animation');
  animations[1].finish();
  await animations[1].finished;
});
