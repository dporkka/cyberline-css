/**
 * Optional controls for an externally installed @lottiefiles/dotlottie-wc.
 * Syntyr does not register or download the actual player.
 */
export interface DotLottiePlayerInstance {
  play(): void;
  pause(): void;
  setFrame?(frame: number): void;
  addEventListener?(type: string, callback: () => void): void;
  removeEventListener?(type: string, callback: () => void): void;
}
export interface DotLottieElement extends HTMLElement {
  dotLottie?: DotLottiePlayerInstance | null;
}
export interface DotLottieControls {
  poster: HTMLElement;
  playButton: HTMLButtonElement;
  pauseButton: HTMLButtonElement;
  status?: HTMLElement;
}
/** Connect explicit play/pause buttons, preserve a static poster and observe reduced-motion changes. */
export declare function connectDotLottie(
  element: DotLottieElement,
  controls: DotLottieControls,
): () => void;
