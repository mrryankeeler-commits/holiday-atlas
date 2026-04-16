import { expect, test } from "@playwright/test";

test.describe("critical explorer flows", () => {
  test("welcome/explorer navigation, selection sync, hash navigation, and tab switching", async ({ page }) => {
    await page.goto("/");

    await expect(page.getByRole("heading", { name: "Plan your next trip with confidence." })).toBeVisible();
    await page.getByRole("button", { name: "Explore map" }).click();
    await expect(page).toHaveURL(/#explorer$/);

    const locButtons = page.locator("#loc-list .loc-btn");
    await expect(locButtons.first()).toBeVisible();
    await locButtons.nth(1).click();

    await expect(locButtons.nth(1)).toHaveClass(/active/);
    await expect(page.locator("#main .hero .loc-name")).toHaveText(await locButtons.nth(1).locator(".loc-city").textContent());

    await page.goto("/#welcome");
    await expect(page).toHaveURL(/#welcome$/);
    await expect(page.getByRole("heading", { name: "Plan your next trip with confidence." })).toBeVisible();

    await page.goto("/#explorer");
    await expect(page.locator("#main .tab-nav")).toBeVisible();

    await page.getByRole("button", { name: "Costs & flights" }).click();
    await expect(page.locator("#tab-body")).toContainText("Accommodation");

    await page.getByRole("button", { name: "Practical info" }).click();
    await expect(page.locator("#tab-body")).toContainText("Flights from");
  });
});
