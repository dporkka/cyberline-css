import { test, expect } from "@playwright/test";

test("Radix action menu supports keyboard navigation and restores focus", async ({ page }) => {
  await page.goto("/");
  const trigger = page.getByRole("button", { name: "Campaign actions" });
  await trigger.focus();
  await page.keyboard.press("ArrowDown");
  await expect(page.getByRole("menu")).toBeVisible();
  const review = page.getByRole("menuitem", { name: "Review campaign" });
  await expect(review).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator(".syn-toast-description")).toHaveText("Review selected; no data changed.");
  await expect(trigger).toBeFocused();
});

test("React Aria combobox filters and selects options via keyboard", async ({ page }) => {
  await page.goto("/");
  const field = page.getByRole("combobox", { name: "Advertising format" });
  await field.fill("Digital");
  await expect(page.getByRole("option", { name: "Digital screen" })).toBeVisible();
  await expect(page.getByRole("option", { name: "Static billboard" })).toHaveCount(0);
  await page.keyboard.press("ArrowDown");
  await page.keyboard.press("Enter");
  await expect(field).toHaveValue("Digital screen");
});

test("Radix toast can be announced, dismissed and remains nonblocking", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Show a notification" }).click();
  await expect(page.locator(".syn-toast-description")).toHaveText("This is not a persisted operation.");
  await page.getByRole("button", { name: "Dismiss Demo notification" }).click();
  await expect(page.locator(".syn-toast-description")).toHaveCount(0);
});

test("opt-in styling applies to portal content inside the themed root", async ({ page }) => {
  await page.goto("/");
  const menu = page.getByRole("button", { name: "Campaign actions" });
  await menu.click();
  const surface = page.locator(".syn-menu-surface");
  await expect(surface).toBeVisible();
  await expect(surface).toHaveCSS("border-top-style", "solid");
  await expect(page.locator("body")).toHaveClass(/syn-root/);
});

test("narrow layouts keep the menu and combobox within the viewport", async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 680 });
  await page.goto("/");
  await page.getByRole("button", { name: "Campaign actions" }).click();
  await expect(page.locator(".syn-menu-surface")).toBeVisible();
  const overflows = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
  expect(overflows).toBe(false);
  await page.keyboard.press("Escape");
  await page.getByRole("combobox", { name: "Advertising format" }).fill("Transit");
  await expect(page.getByRole("option", { name: "Transit advertising" })).toBeVisible();
});

test("forced colors and reduced motion preserve menu keyboard access", async ({ page }) => {
  await page.emulateMedia({ forcedColors: "active", reducedMotion: "reduce" });
  await page.goto("/");
  const trigger = page.getByRole("button", { name: "Campaign actions" });
  await trigger.focus();
  await page.keyboard.press("ArrowDown");
  await expect(page.getByRole("menuitem", { name: "Review campaign" })).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(trigger).toBeFocused();
});
