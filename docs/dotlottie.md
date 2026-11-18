# Optional dotLottie player integration

Syntyr does **not** ship a renderer, animation asset, WASM runtime or mandatory
JavaScript dependency. This recipe integrates the independently installed
`@lottiefiles/dotlottie-wc` Web Component with a static poster and accessible
user-triggered playback. Use it with `.lottie` or Lottie JSON files that you
own or have permission to redistribute.

## Installation

Install and pin the external renderer separately:

```sh
npm install --save-exact @lottiefiles/dotlottie-wc
```

Bundle it through your application tooling. If you use a strict CSP or want
offline operation, **self-host** the player's matching
`@lottiefiles/dotlottie-web/dist/dotlottie-player.wasm` and call
`setWasmUrl('/assets/dotlottie-player.wasm')` **before the first animation
loads**. A self-hosted JavaScript module does not by itself guarantee that
the player will avoid external network requests. See the upstream
[Web Component README](https://github.com/LottieFiles/dotlottie-web/tree/main/packages/wc)
for WASM and worker requirements; pin and audit both packages together.

## Copy-owned HTML

```html
<section class="syn-root" aria-labelledby="preview-heading">
  <h2 id="preview-heading">Task complete</h2>
  <div class="syn-panel">
    <div class="preview-stage">
      <!-- Static content remains visible with no JavaScript or network. -->
      <p id="success-poster">Success: your changes were saved.</p>
      <!-- The host owns this asset and the external player. Never autoplay. -->
      <div id="success-animation-slot"></div>
    </div>
    <div class="syn-cluster">
      <button class="syn-button" id="preview-play" type="button" disabled>Play preview</button>
      <button class="syn-button" id="preview-pause" type="button" disabled>Pause preview</button>
    </div>
    <p id="preview-status" role="status" aria-live="polite">
      Static success preview available.
    </p>
  </div>
</section>
```

Give the preview stage a fixed or aspect-ratio-constrained size in your own CSS
and style `dotlottie-wc` as a block of that same size. Set
`dotlottie-wc[hidden] { display: none; }` so loading the player cannot cover
the static poster. Use a meaningful static poster for functional information.
For purely decorative animation, avoid duplicated screen-reader descriptions.

## Application module

```js
import { setWasmUrl } from '@lottiefiles/dotlottie-wc';
import { connectDotLottie } from '@syntyr/css/dotlottie';

setWasmUrl('/assets/dotlottie-player.wasm');

// Create and attach the element only after configuring the WASM URL.
// This avoids an upgrade/load race when the player module registers the tag.
const element = document.createElement('dotlottie-wc');
element.hidden = true;
element.src = '/animations/success.lottie';
const disconnect = connectDotLottie(
  element,
  {
    poster: document.querySelector('#success-poster'),
    playButton: document.querySelector('#preview-play'),
    pauseButton: document.querySelector('#preview-pause'),
    status: document.querySelector('#preview-status'),
  },
);

document.querySelector('#success-animation-slot').append(element);

// Call disconnect() before unmounting this region, such as in React cleanup.
```

For a no-bundler setup, self-host the version-pinned player module and Syntyr's
`dist/syntyr.dotlottie.mjs`, then replace the import paths above with those
local paths. The only third-party runtime comes from your independently chosen
player; importing `@syntyr/css` or `syntyr.core.css` never loads it.

The connector starts in static-poster mode. It does not autoplay, even if the
host accidentally supplied an `autoplay` attribute. Load errors preserve the
static poster; Play and Pause are disabled until the player is ready. A change
to `prefers-reduced-motion: reduce` stops active playback and restores the
poster. A user who explicitly selects **Play** can still request playback.
The host remains responsible for treating the animation as decorative or
supplying an equivalent accessible result using semantic text and ARIA.

Do not embed a remote animation asset or an unpinned player CDN into the
Syntyr core distribution. Player code and artwork have **separate licenses**.
