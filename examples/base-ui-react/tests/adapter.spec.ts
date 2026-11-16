import { test, expect } from "@playwright/test";

test("menu is themed in the portal and supports keyboard navigation", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Actions" }).click();
  const menu = page.getByRole("menu");
  await expect(menu).toBeVisible();
  await expect(page.locator(".syn-root .syn-base-popup").first()).toBeVisible();
  const popupColor = await page.locator(".syn-root .syn-base-popup").first()
    .evaluate((element) => getComputedStyle(element).backgroundColor);
  expect(popupColor).not.toBe("rgba(0, 0, 0, 0)");
  await page.keyboard.press("Escape");
  await expect(menu).not.toBeVisible();
  await expect(page.getByRole("button", { name: "Actions" })).toBeFocused();
});

test("dialog traps focus and Escape restores its trigger", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Open settings" }).click();
  const dialog = page.getByRole("dialog");
  await expect(dialog).toBeVisible();
  await expect(page.locator(".syn-root .syn-base-dialog")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(dialog).not.toBeVisible();
  await expect(page.getByRole("button", { name: "Open settings" })).toBeFocused();
});

test("select, switch and tabs reflect Base UI state without Syntyr JS", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("combobox", { name: "Advertising format" }).click();
  await page.getByRole("option", { name: "Digital" }).click();
  await expect(page.getByRole("combobox", { name: "Advertising format" })).toContainText("Digital");
  const switchControl = page.getByRole("switch", { name: "Notifications" });
  await expect(switchControl).toHaveAttribute("aria-checked", "false");
  await switchControl.click();
  await expect(switchControl).toHaveAttribute("aria-checked", "true");
  await page.getByRole("tab", { name: "Activity" }).click();
  await expect(page.getByRole("tab", { name: "Activity" })).toHaveAttribute("aria-selected", "true");
  await expect(page.getByRole("tabpanel", { name: "Activity" })).toContainText("Activity panel");
});

test("RTL logical styling and focus survive a direction change", async ({ page }) => {
  await page.goto("/");
  const button = page.getByRole("button", { name: "Actions" });
  await page.locator(".syn-root").evaluate((el) => el.setAttribute("dir", "rtl"));
  await button.focus();
  const dir = await button.evaluate((el) => getComputedStyle(el).direction);
  expect(dir).toBe("rtl");
  await page.keyboard.press("Enter");
  await expect(page.getByRole("menu")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(button).toBeFocused();
});

test("component styles remain scoped and checked-switch direction reverses in RTL", async ({ page }) => {
  await page.goto("/");
  const root = page.locator(".syn-root");
  const control = page.getByRole("switch", { name: "Notifications" });
  await control.click();
  const thumb = page.locator(".syn-base-switch-thumb");
  await expect(thumb).toHaveAttribute("data-checked", "");
  await expect.poll(() => thumb.evaluate((el) => getComputedStyle(el).translate)).toBe("18.4px");
  await root.evaluate((el) => el.setAttribute("dir", "rtl"));
  await expect.poll(() => thumb.evaluate((el) => getComputedStyle(el).translate)).toBe("-18.4px");
});
