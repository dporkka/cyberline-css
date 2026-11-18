/**
 * Optional Syntyr animation companion. Native Web Animations API only.
 * No imports, DOM side effects, hidden initial states, or implicit observers.
 *
 * Import only where application-driven motion is needed. CSS-first consumers
 * can continue using syntyr.motion.css without loading any JavaScript.
 */

const PRESETS = new Set(['fade', 'enter', 'scale']);
const DIRECTIONS = new Set(['up', 'down', 'left', 'right']);
const NOOP = () => {};
// Tracks one-shot reveals without retaining detached DOM nodes.
const revealedElements = new WeakSet();

function reducedMotion() {
  return globalThis.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches === true;
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
  return [{ opacity: 0, translate: origin }, { opacity: 1, translate: '0 0' }];
}

/**
 * Animate a single already-rendered element. Returns an Animation (or null when
 * reduced motion / native support is unavailable). Never mutates inline styles.
 * @param {Element} element
 * @param {'fade'|'enter'|'scale'} [preset='enter']
 * @param {{duration?: number, delay?: number, easing?: string,
 *  direction?: 'up'|'down'|'left'|'right', distance?: string, scaleFrom?: string}} [options]
 */
export function animate(element, preset = 'enter', options = {}) {
  if (!PRESETS.has(preset)) throw new TypeError('Unknown Syntyr animation: ' + preset);
  if (!element || typeof element.animate !== 'function' || reducedMotion()) return null;

  const style = styleOf(element);
  const duration = milliseconds(options.duration,
    milliseconds(token(style, '--syn-motion-duration', '220ms'), 220));
  const delay = milliseconds(options.delay, 0);
  const easing = options.easing ?? token(style, '--syn-ease-out', 'cubic-bezier(.22, 1, .36, 1)');

  // fill:none prevents completed animations from capturing focus, disabled,
  // transform, or opacity styles after their one-shot effect has finished.
  return element.animate(keyframes(preset, options, style), {
    duration, easing, delay, iterations: 1, fill: 'none',
  });
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
 * @returns {() => void} Disconnects the observer.
 */
export function observeReveals(root = globalThis.document) {
  if (!root?.querySelectorAll || !globalThis.IntersectionObserver || reducedMotion()) return NOOP;

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
  }, { threshold: 0.1 });

  for (const element of targets) observer.observe(element);
  return () => observer.disconnect();
}

/**
 * Animate a DOM update with the native View Transitions API when available.
 * Without support (or under reduced motion), update is performed immediately.
 * The caller owns its DOM update; Syntyr never instruments or observes it.
 * @param {() => void | Promise<void>} update
 * @param {Document} [root=document]
 * @returns {ViewTransition|null}
 */
export function withViewTransition(update, root = globalThis.document) {
  if (typeof update !== 'function') throw new TypeError('Expected an update callback');
  if (reducedMotion() || typeof root?.startViewTransition !== 'function') {
    update();
    return null;
  }
  return root.startViewTransition(update);
}
