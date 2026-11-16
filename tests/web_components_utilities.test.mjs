import test from "node:test";
import assert from "node:assert/strict";
import { normalizePercent, ratingDescription, registerSyntyrElements }
  from "../integrations/web-components/syntyr-elements.mjs";

test("comparison position clamps finite values and defaults invalid input", () => {
  assert.equal(normalizePercent("-10"), 0);
  assert.equal(normalizePercent("120"), 100);
  assert.equal(normalizePercent("42"), 42);
  assert.equal(normalizePercent("garbage"), 50);
  assert.equal(normalizePercent(Infinity), 50);
});

test("rating announcements are meaningful for accessible native radio choices", () => {
  assert.equal(ratingDescription(3, 5), "3 of 5 stars");
  assert.equal(ratingDescription(0, 5), "Not rated");
});

test("optional native elements register once without global runtime dependencies", () => {
  const classes = new Map();
  const registry = { get: id => classes.get(id), define: (id, cls) => classes.set(id, cls) };
  registerSyntyrElements(registry);
  registerSyntyrElements(registry);
  assert.deepEqual([...classes.keys()], [
    "syn-copy-button", "syn-toast-region", "syn-image-compare", "syn-rating-input",
  ]);
});
