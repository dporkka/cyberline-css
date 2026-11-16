import { test, expect } from "@playwright/test";

test.describe("optional free animation companion", () => {
  test.use({ reducedMotion: "no-preference" });

  test("plays finite feedback and coordinates synchronous dismissal", async ({ page }) => {
    await page.goto("/examples/animation.html");
    await expect(page.locator("#animate-press")).toBeVisible();
    await page.locator("#animate-press").click();
    await expect(page.locator("#animation-status")).toContainText("press");
    await page.locator("#animate-exit").click();
    await expect(page.locator("#exit-note")).toBeHidden();
    await expect(page.locator("#animation-status")).toContainText("Dismissed note");
    await page.locator("#animate-highlight").click();
    await expect(page.locator("#animation-status")).toContainText("highlight");
    await page.locator("#animate-slide").click();
    await expect(page.locator("#animation-status")).toContainText("slide");
  });

  test("a live reduced-motion preference cancels in-flight WAAPI animations", async ({ page }) => {
    await page.goto("/examples/animation.html");
    const began = await page.evaluate(async () => {
      const { animate } = await import("/dist/syntyr.animate.mjs");
      const panel = document.querySelector("#motion-cards .syn-panel");
      return Boolean(animate(panel, "enter", { duration: 10000 }));
    });
    expect(began).toBe(true);
    await expect.poll(() => page.locator("#motion-cards .syn-panel").first().evaluate(e => e.getAnimations().length)).toBeGreaterThan(0);
    await page.emulateMedia({ reducedMotion: "reduce" });
    await expect.poll(() => page.locator("#motion-cards .syn-panel").first().evaluate(e => e.getAnimations().length)).toBe(0);
  });

  test("turning on reduced motion completes an in-flight native exit", async ({ page }) => {
    await page.goto("/examples/animation.html");
    const started = await page.evaluate(async () => {
      const { exit } = await import("/dist/syntyr.animate.mjs");
      const target = document.querySelector("#exit-note");
      return Boolean(exit(target, () => { target.hidden = true; }, {duration: 10000}));
    });
    expect(started).toBe(true);
    await page.emulateMedia({ reducedMotion: "reduce" });
    await expect(page.locator("#exit-note")).toBeHidden();
  });

  test("native disclosure works with CSS motion and degrades without JS", async ({ page }) => {
    await page.goto("/examples/animation.html");
    const disclosure = page.locator("#motion-disclosure");
    await disclosure.locator("summary").click();
    await expect(disclosure).toHaveAttribute("open", "");
    await expect(disclosure.locator("p")).toBeVisible();
  });
});

test.describe("scriptless motion fallback", () => {
  test.use({ javaScriptEnabled: false });

  test("keeps all default content and disclosure operable", async ({ page }) => {
    await page.goto("/examples/animation.html");
    await expect(page.locator("#motion-cards .syn-panel")).toHaveCount(3);
    await expect(page.locator("#exit-note")).toBeVisible();
    for (const id of ["animate-one", "animate-all", "animate-press", "animate-highlight", "animate-slide", "animate-exit"]) {
      await expect(page.locator("#" + id)).toBeDisabled();
    }
    await page.locator("#motion-disclosure summary").click();
    await expect(page.locator("#motion-disclosure")).toHaveAttribute("open", "");
  });
});
