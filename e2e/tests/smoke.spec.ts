import { expect, test } from "@playwright/test";

test("the service responds and serves the home page", async ({ page, request }) => {
  const health = await (await request.get("/healthz")).json();
  expect(health).toEqual({ status: "ok", version: "e2e" });
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Cuadrillapp" })).toBeVisible();
});
