import test, { afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { connectDotLottie } from '../src/dotlottie.mjs';

const originalMatchMedia = globalThis.matchMedia;
afterEach(() => {
  if (originalMatchMedia === undefined) delete globalThis.matchMedia;
  else globalThis.matchMedia = originalMatchMedia;
});

function emitter() {
  const events = new Map();
  return {
    addEventListener(name, fn) {
      if (!events.has(name)) events.set(name, new Set());
      events.get(name).add(fn);
    },
    removeEventListener(name, fn) { events.get(name)?.delete(fn); },
    dispatch(name) { for (const fn of events.get(name) ?? []) fn(); },
  };
}

function fixture(reduced = false) {
  const media = { matches: reduced, ...emitter() };
  globalThis.matchMedia = () => media;
  const player = { hidden: true, dotLottie: null, ...emitter() };
  const poster = { hidden: false };
  const playButton = { disabled: true, ...emitter() };
  const pauseButton = { disabled: true, ...emitter() };
  const status = { textContent: 'Preview available' };
  const calls = [];
  const core = {
    ...emitter(),
    play() { calls.push('play'); },
    pause() { calls.push('pause'); },
    setFrame(frame) { calls.push(['frame', frame]); },
  };
  const options = { poster, playButton, pauseButton, status };
  return { media, player, poster, playButton, pauseButton, status, core, options, calls };
}

test('no playback, external import, or DOM mutation before player load', () => {
  const f = fixture();
  const disconnect = connectDotLottie(f.player, f.options);
  assert.deepEqual(f.calls, []);
  assert.equal(f.poster.hidden, false);
  assert.equal(f.player.hidden, true);
  assert.equal(f.playButton.disabled, true);
  assert.equal(f.pauseButton.disabled, true);
  disconnect();
});

test('load exposes explicit play/pause, never autoplays, and keeps a poster until play', () => {
  const f = fixture();
  const disconnect = connectDotLottie(f.player, f.options);
  f.player.dotLottie = f.core;
  f.player.dispatch('load');
  assert.equal(f.calls.includes('play'), false);
  assert.equal(f.poster.hidden, false);
  assert.equal(f.playButton.disabled, false);
  f.playButton.dispatch('click');
  assert.equal(f.player.hidden, false);
  assert.equal(f.poster.hidden, true);
  assert.equal(f.calls.at(-1), 'play');
  assert.equal(f.pauseButton.disabled, false);
  f.pauseButton.dispatch('click');
  assert.equal(f.calls.at(-1), 'pause');
  assert.equal(f.pauseButton.disabled, true);
  assert.match(f.status.textContent, /paused/i);
  disconnect();
});

test('reduced motion defaults to a static fallback but allows explicit user playback', () => {
  const f = fixture(true);
  const disconnect = connectDotLottie(f.player, f.options);
  f.player.dotLottie = f.core;
  f.player.dispatch('load');
  assert.equal(f.poster.hidden, false);
  assert.equal(f.player.hidden, true);
  assert.equal(f.calls.includes('play'), false);
  f.playButton.dispatch('click');
  assert.equal(f.calls.at(-1), 'play');
  assert.equal(f.poster.hidden, true);
  f.media.matches = true;
  f.media.dispatch('change');
  assert.equal(f.poster.hidden, false);
  assert.equal(f.player.hidden, true);
  disconnect();
});

test('switching into reduced-motion while playing pauses and restores a static poster', () => {
  const f = fixture();
  const disconnect = connectDotLottie(f.player, f.options);
  f.player.dotLottie = f.core;
  f.player.dispatch('load');
  f.playButton.dispatch('click');
  f.media.matches = true;
  f.media.dispatch('change');
  assert.equal(f.calls.at(-1), 'pause');
  assert.equal(f.poster.hidden, false);
  assert.equal(f.player.hidden, true);
  assert.equal(f.pauseButton.disabled, true);
  disconnect();
});

test('load failures keep fallback and disable controls', () => {
  const f = fixture();
  const disconnect = connectDotLottie(f.player, f.options);
  f.player.dispatch('loadError');
  assert.equal(f.poster.hidden, false);
  assert.equal(f.player.hidden, true);
  assert.equal(f.playButton.disabled, true);
  assert.match(f.status.textContent, /unavailable/i);
  disconnect();
});

test('complete resets playback state and disconnect removes listeners', () => {
  const f = fixture();
  const disconnect = connectDotLottie(f.player, f.options);
  f.player.dotLottie = f.core;
  f.player.dispatch('load');
  f.playButton.dispatch('click');
  f.core.dispatch('complete');
  assert.equal(f.pauseButton.disabled, true);
  disconnect();
  const length = f.calls.length;
  f.playButton.dispatch('click');
  f.player.dispatch('load');
  f.media.dispatch('change');
  assert.equal(f.calls.length, length);
});


test('a late load error stops active playback and restores the static result', () => {
  const f = fixture();
  const disconnect = connectDotLottie(f.player, f.options);
  f.player.dotLottie = f.core;
  f.player.dispatch('load');
  f.playButton.dispatch('click');
  f.player.dispatch('loadError');
  assert.equal(f.calls.at(-1), 'pause');
  assert.equal(f.poster.hidden, false);
  assert.equal(f.player.hidden, true);
  assert.equal(f.playButton.disabled, true);
  disconnect();
});

test('published Syntyr optional subpath imports without installing the renderer', async () => {
  const api = await import('@syntyr/css/dotlottie');
  assert.deepEqual(Object.keys(api), ['connectDotLottie']);
});
