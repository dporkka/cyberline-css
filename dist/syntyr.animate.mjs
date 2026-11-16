/**
 * Optional Syntyr animation companion. Native Web Animations API only.
 * No imports, startup DOM side effects, hidden states, or implicit observers.
 *
 * Import only where application-driven motion is needed. CSS-first consumers
 * can continue using syntyr.motion.css without loading any JavaScript.
 */

const PRESETS = new Set(['fade', 'enter', 'scale', 'slide', 'press', 'highlight']);
const DIRECTIONS = new Set(['up', 'down', 'left', 'right']);
const NOOP = () => {};
// Tracks one-shot reveals without retaining detached DOM nodes.
const revealedElements = new WeakSet();
const activeByElement = new WeakMap();
// A new invocation invalidates any queued completion callback from an older
// exit, even when its finished promise was already fulfilled before cancel().
const invocationByElement = new WeakMap();
const activeAnimations = new Set();
// Only exits have a host state transition to complete on reduced-motion
// activation; ordinary effects are canceled without touching DOM state.
const reducedExitCompletion = new WeakMap();
let motionPreference = null;

function stopPreferenceWatch() {
  if (activeAnimations.size !== 0 || !motionPreference) return;
  motionPreference.removeEventListener?.('change', onPreferenceChange);
  motionPreference = null;
}

function onPreferenceChange(event) {
  if (!event.matches) return;
  for (const animation of [...activeAnimations]) {
    const completeExit = reducedExitCompletion.get(animation);
    if (completeExit) completeExit();
    else animation.cancel();
  }
}

function track(element, animation, preference) {
  activeByElement.set(element, animation);
  activeAnimations.add(animation);
  if (!motionPreference && typeof preference?.addEventListener === 'function') {
    motionPreference = preference;
    motionPreference.addEventListener('change', onPreferenceChange);
    // A preference may change between the initial check and listener setup.
    if (motionPreference.matches) animation.cancel();
  }
  const forget = () => {
    activeAnimations.delete(animation);
    if (activeByElement.get(element) === animation) activeByElement.delete(element);
    stopPreferenceWatch();
  };
  Promise.resolve(animation.finished).then(forget, forget);
}


function styleOf(element) {
  return globalThis.getComputedStyle?.(element);
}

function token(style, name, fallback) {
  return style?.getPropertyValue(name)?.trim() || fallback;
}

function milliseconds(value, fallback) {
  if (typeof value === 'number') return Number.isFinite(value) && value >= 0 ? value : fallback;
  if (typeof value !== 'string') return fallback;
  const match = /^([0-9]*\.?[0-9]+)\s*(ms|s)$/.exec(value.trim());
  return match ? Number(match[1]) * (match[2] === 's' ? 1000 : 1) : fallback;
}

function keyframes(preset, options, style) {
  if (preset === 'fade') return [{ opacity: 0 }, { opacity: 1 }];
  if (preset === 'press') {
    const pressed = String(options.scaleFrom ?? token(style, '--syn-motion-press-scale', '0.97'));
    return [{ scale: '1' }, { scale: pressed }, { scale: '1' }];
  }
  if (preset === 'highlight') {
    const from = style?.backgroundColor || 'transparent';
    const highlight = token(style, '--syn-accent-soft', 'rgb(128 128 128 / 14%)');
    return [{ backgroundColor: from }, { backgroundColor: highlight }, { backgroundColor: from }];
  }
  if (preset === 'scale') {
    const from = options.scaleFrom ?? token(style, '--syn-motion-scale-from', '0.96');
    return [{ opacity: 0, scale: String(from) }, { opacity: 1, scale: '1' }];
  }

  const direction = options.direction ?? 'up';
  if (!DIRECTIONS.has(direction)) throw new TypeError('Invalid direction: ' + direction);
  const distance = options.distance ?? token(style, '--syn-motion-distance', '.75rem');
  const offset = String(distance);
  // CSS math works with both functional lengths (calc/var) and signed values.
  // Prefixing '-' to 'calc(...)' produces invalid keyframes.
  const negative = 'calc(-1 * ' + offset + ')';
  const origin = {
    up: '0 ' + offset,
    down: '0 ' + negative,
    left: negative + ' 0',
    right: offset + ' 0',
  }[direction];
  return preset === 'slide'
    ? [{ translate: origin }, { translate: '0 0' }]
    : [{ opacity: 0, translate: origin }, { opacity: 1, translate: '0 0' }];
}

function begin(element, options, frames, fill = 'none') {
  if (!element || typeof element.animate !== 'function') return null;
  const preference = globalThis.matchMedia?.('(prefers-reduced-motion: reduce)');
  if (preference?.matches) return null;

  const style = styleOf(element);
  const duration = milliseconds(options.duration,
    milliseconds(token(style, '--syn-motion-duration', '220ms'), 220));
  const delay = milliseconds(options.delay, 0);
  const easing = options.easing ?? token(style, '--syn-ease-out', 'cubic-bezier(.22, 1, .36, 1)');
  const keyframeValues = frames(style);
  // Invalidate any queued exit completion *before* cancelling the prior
  // effect. Promise fulfillment cannot be undone by a late cancel().
  const invocation = Symbol('syntyr-animation');
  invocationByElement.set(element, invocation);
  // The rejected finished promise is observed by track(), so cancellation
  // remains leak-free even for an interrupted animation.
  activeByElement.get(element)?.cancel();
  const animation = element.animate(keyframeValues, {
    duration, easing, delay, iterations: 1, fill,
  });
  track(element, animation, preference);
  return animation;
}

/**
 * Animate an already-rendered element. A later call replaces an earlier
 * animation on that same element, without affecting other elements.
 * Returns a native Animation or null when reduced motion / WAAPI is unavailable.
 * @param {Element} element
 * @param {'fade'|'enter'|'scale'|'slide'|'press'|'highlight'} [preset='enter']
 * @param {{duration?: number, delay?: number, easing?: string,
 *  direction?: 'up'|'down'|'left'|'right', distance?: string, scaleFrom?: string}} [options]
 */
export function animate(element, preset = 'enter', options = {}) {
  if (!PRESETS.has(preset)) throw new TypeError('Unknown Syntyr animation: ' + preset);
  return begin(element, options, style => keyframes(preset, options, style));
}

/**
 * Exit is coordinated with the host's synchronous hide/remove action.
 * The animation holds its end state until onComplete updates the DOM, then
 * releases styles. A replacement animation cancels the exit without removal.
 * Reduced motion or missing WAAPI invokes onComplete immediately.
 */
export function exit(element, onComplete, options = {}) {
  if (typeof onComplete !== 'function') throw new TypeError('exit requires an onComplete callback');
  const animation = begin(element, options, style => {
    const [start] = keyframes('enter', options, style);
    return [
      { opacity: 1, translate: '0 0' },
      { opacity: 0, translate: start.translate },
    ];
  }, 'forwards');
  if (!animation) { onComplete(); return null; }
  const invocation = invocationByElement.get(element);
  let completed = false;
  const complete = () => {
    // A later animation may replace this one after it finished but before
    // its queued callback runs. Replacement must never remove the element.
    if (completed || invocationByElement.get(element) !== invocation) return;
    completed = true;
    reducedExitCompletion.delete(animation);
    try { onComplete(); }
    finally {
      // Release this specific forwards-filled exit even when the host callback
      // immediately starts another effect on the same element.
      animation.cancel();
    }
  };
  // A preference change must commit the host state immediately rather than
  // strand a canceled exit. Ordinary cancellation and replacements do not.
  reducedExitCompletion.set(animation, complete);
  animation.finished.then(complete, () => reducedExitCompletion.delete(animation));
  return animation;
}

/**
 * Coordinate independent animations through WAAPI delays, with no timers.
 * @param {Iterable<Element>} elements
 * @param {'fade'|'enter'|'scale'} [preset='enter']
 * @param {object} [options] Supports animate() options plus interval (ms).
 * @returns {Array<Animation|null>}
 */
export function stagger(elements, preset = 'enter', options = {}) {
  const targets = Array.from(elements ?? []);
  const style = targets.length ? styleOf(targets[0]) : null;
  const interval = milliseconds(options.interval,
    milliseconds(token(style, '--syn-motion-stagger', '65ms'), 65));
  const initialDelay = milliseconds(options.delay, 0);
  return targets.map((element, index) =>
    animate(element, preset, { ...options, delay: initialDelay + interval * index }));
}

/**
 * Progressive one-time viewport animations. Elements remain visible until their
 * intersection actually triggers; unsupported APIs do not hide content.
 * Call explicitly after rendering an HTML fragment. No MutationObserver.
 *
 * <div class="syn-root"><p data-syn-reveal="enter">New feature</p></div>
 *
 * @param {Document|Element} [root=document] Query scope.
 * @param {{threshold?: number, rootMargin?: string}} [options] Observer settings.
 * @returns {() => void} Disconnects the observer.
 */
export function observeReveals(root = globalThis.document, options = {}) {
  if (!root?.querySelectorAll || !globalThis.IntersectionObserver ||
      globalThis.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches) return NOOP;

  const targets = Array.from(root.querySelectorAll('.syn-root [data-syn-reveal]'))
    .filter(element => !revealedElements.has(element));
  if (!targets.length) return NOOP;

  const observer = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      observer.unobserve(entry.target);
      // Two observers can queue callbacks for the same target. Mark before
      // animating so rescans and queued entries cannot replay a reveal.
      if (revealedElements.has(entry.target)) continue;
      revealedElements.add(entry.target);
      const preset = entry.target.dataset?.synReveal || 'enter';
      animate(entry.target, PRESETS.has(preset) ? preset : 'enter');
    }
  }, {
    threshold: options.threshold ?? 0.1,
    ...(options.rootMargin === undefined ? {} : { rootMargin: options.rootMargin }),
  });

  for (const element of targets) observer.observe(element);
  return () => observer.disconnect();
}
