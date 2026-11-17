import assert from "node:assert/strict";
import test from "node:test";
import { inspectText, predictWithPretext } from "../integrations/pretext/audit.mjs";

const css = {
  fontSize: "16px", fontFamily: '"Inter", sans-serif', fontStyle: "normal",
  fontWeight: "400", lineHeight: "24px", letterSpacing: "normal",
  whiteSpace: "normal", wordBreak: "normal", overflowWrap: "break-word",
  paddingLeft: "8px", paddingRight: "8px", borderLeftWidth: "1px",
  borderRightWidth: "1px", textWrapStyle: "auto", fontVariationSettings: "normal",
  fontFeatureSettings: "normal"
};
function element(overrides = {}, styles = {}) {
  const rects = [{top: 2}, {top: 26}];
  return {
    textContent: "Syntyr a readable label", childElementCount: 0,
    scrollWidth: 200, clientWidth: 200, scrollHeight: 48, clientHeight: 48,
    getBoundingClientRect: () => ({width: 218, height: 48}),
    ownerDocument: {
      defaultView: {getComputedStyle: () => ({...css, ...styles})},
      createRange: () => ({selectNodeContents() {}, getClientRects: () => rects})
    },
    ...overrides
  };
}
test("reports distinct visual text lines and horizontal overflow", () => {
  const result = inspectText(element({scrollWidth: 243}));
  assert.equal(result.actualLines, 2);
  assert.equal(result.overflowInline, true);
  assert.equal(result.overflowBlock, false);
});
test("pretext predictor consumes content width rather than border-box width", () => {
  let prepared, layoutArgs;
  const pretext = {
    prepare: (...args) => { prepared = args; return "handle"; },
    layout: (...args) => { layoutArgs = args; return {lineCount: 2, height: 48}; }
  };
  const result = predictWithPretext(element(), pretext);
  assert.equal(result.status, "measured");
  assert.deepEqual(layoutArgs, ["handle", 200, 24]);
  assert.equal(prepared[0], "Syntyr a readable label");
  assert.equal(prepared[2].wordBreak, "normal");
});
test("skips unsupported balanced wrapping rather than declaring false mismatch", () => {
  const result = predictWithPretext(element({}, {textWrapStyle: "balance"}), {
    prepare: () => { throw new Error("must not run"); }, layout: () => {}
  });
  assert.equal(result.status, "skipped");
});
test("skips rich inline content, where layout has different assumptions", () => {
  const result = predictWithPretext(element({childElementCount: 1}), {
    prepare: () => { throw new Error("must not run"); }, layout: () => {}
  });
  assert.equal(result.status, "skipped");
});
