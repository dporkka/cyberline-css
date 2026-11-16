# Optional native Custom Elements: copy, toast, image compare and rating

**Status:** experimental MIT integration recipes; not part of `syntyr.core.css`, not a component runtime.
The [live source example](../examples/web-components/utilities.html) runs without npm or a framework.

Import the optional local CSS after your pinned Syntyr core, and register only when the page needs behavior:

```html
<link rel="stylesheet" href="syntyr.core.css">
<link rel="stylesheet" href="syntyr-elements.css">
<script type="module">
  import { registerSyntyrElements } from "./syntyr-elements.mjs";
  registerSyntyrElements();
</script>
```

- `<syn-copy-button for="source-id">`: requires a real button (initially disabled), secure-context clipboard access and an element ID. Reports success/failure in a status element and optionally a toast region. It cannot copy inaccessible documents or bypass clipboard permission.
- `<syn-toast-region>`: a modest `announce(message)` interface that writes safe text into an existing native live region. No automatic dismissal, persistence or notification queue.
- `<syn-image-compare>`: two descriptive local images plus a labeled native `input[type=range]`. Without JavaScript, both images remain visible instead of masquerading as a functional comparison slider.
- `<syn-rating-input>`: preserves native `fieldset` radio buttons and form submission; enhancement only updates a text description and emits `syn-rating-change`. Server-side validation is always required.

Use semantic HTML, event listeners owned by the host app, and local assets. No global selectors outside `.syn-root`, remote fonts, dependencies, polyfills, or external assets are introduced. Test on Safari, Firefox, Chromium, mobile screen readers, at 400% zoom and with forced colors before production reuse.

**Verification:** `node --test tests/web_components_utilities.test.mjs` and the existing native Web Components browser fixture. This integration does not change Syntyr core CSS byte output.
