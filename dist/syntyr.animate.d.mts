/** Optional, dependency-free animation primitives for browser DOM elements. */
export type SyntyrAnimationPreset = 'fade' | 'enter' | 'scale' | 'slide' | 'press' | 'highlight';
export type SyntyrAnimationDirection = 'up' | 'down' | 'left' | 'right';

export interface SyntyrAnimationOptions {
  /** Milliseconds. Falls back to --syn-motion-duration or 220ms. */
  duration?: number;
  /** Milliseconds before playback. */
  delay?: number;
  easing?: string;
  direction?: SyntyrAnimationDirection;
  /** CSS length, e.g. '1rem'. */
  distance?: string;
  scaleFrom?: string | number;
}

export interface SyntyrStaggerOptions extends SyntyrAnimationOptions {
  /** Milliseconds between elements; fallback --syn-motion-stagger / 65ms. */
  interval?: number;
}

export declare function animate(
  element: Element | null | undefined,
  preset?: SyntyrAnimationPreset,
  options?: SyntyrAnimationOptions,
): Animation | null;

/** Animate an exit; call onComplete to synchronously hide/remove the element.
 * Canceled exits never invoke it. Reduced motion calls it immediately. */
export declare function exit(
  element: Element | null | undefined,
  onComplete: () => void,
  options?: SyntyrAnimationOptions,
): Animation | null;

export declare function stagger(
  elements: Iterable<Element> | null | undefined,
  preset?: SyntyrAnimationPreset,
  options?: SyntyrStaggerOptions,
): Array<Animation | null>;

export interface SyntyrRevealOptions {
  threshold?: number;
  rootMargin?: string;
}
export declare function observeReveals(
  root?: Document | Element | null,
  options?: SyntyrRevealOptions,
): () => void;
