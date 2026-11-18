/**
 * Optional controls for the external @lottiefiles/dotlottie-wc player.
 * Does not import, download or register a player; the host must do that.
 * No document access, timers, observers or side effects at module import.
 *
 * Usage: connectDotLottie(document.querySelector('dotlottie-wc'),
 *   { poster, playButton, pauseButton, status });
 */
export function connectDotLottie(element, { poster, playButton, pauseButton, status } = {}) {
  if (!element?.addEventListener || !playButton?.addEventListener ||
      !pauseButton?.addEventListener || !poster) {
    throw new TypeError('A dotLottie element, poster, play button and pause button are required');
  }

  const preference = globalThis.matchMedia?.('(prefers-reduced-motion: reduce)');
  let player = null;
  let playing = false;
  let connected = true;
  const announce = (message) => { if (status) status.textContent = message; };
  const controls = () => {
    playButton.disabled = !player || playing;
    pauseButton.disabled = !player || !playing;
  };
  const showPoster = () => {
    poster.hidden = false;
    element.hidden = true;
  };
  const onComplete = () => {
    if (!connected) return;
    playing = false;
    controls();
    announce('Animation complete.');
  };
  const onReady = () => {
    if (!connected || !element.dotLottie) return;
    player?.removeEventListener?.('complete', onComplete);
    player = element.dotLottie;
    playing = false;
    // Never assume a third-party autoplay attribute is absent.
    player.pause();
    player.setFrame?.(0);
    player.addEventListener?.('complete', onComplete);
    showPoster();
    controls();
    announce('Animation ready. Select play to preview.');
  };
  const onError = () => {
    if (playing) player?.pause();
    player?.removeEventListener?.('complete', onComplete);
    player = null;
    playing = false;
    showPoster();
    controls();
    announce('Animation unavailable. Static preview shown.');
  };
  const onPlay = () => {
    if (!player || !connected) return;
    poster.hidden = true;
    element.hidden = false;
    player.play();
    playing = true;
    controls();
    announce('Animation playing.');
  };
  const onPause = () => {
    if (!player || !connected) return;
    player.pause();
    playing = false;
    controls();
    announce('Animation paused.');
  };
  const onPreferenceChange = () => {
    if (!preference?.matches || !connected) return;
    if (playing) player?.pause();
    playing = false;
    showPoster();
    controls();
    announce('Static preview shown for reduced motion.');
  };

  showPoster();
  controls();
  element.addEventListener('load', onReady);
  element.addEventListener('loadError', onError);
  playButton.addEventListener('click', onPlay);
  pauseButton.addEventListener('click', onPause);
  preference?.addEventListener?.('change', onPreferenceChange);
  if (element.dotLottie) onReady();

  return () => {
    if (!connected) return;
    connected = false;
    element.removeEventListener('load', onReady);
    element.removeEventListener('loadError', onError);
    playButton.removeEventListener('click', onPlay);
    pauseButton.removeEventListener('click', onPause);
    preference?.removeEventListener?.('change', onPreferenceChange);
    player?.removeEventListener?.('complete', onComplete);
  };
}
