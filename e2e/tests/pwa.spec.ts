import AxeBuilder from "@axe-core/playwright";
import { expect, type Page, test } from "@playwright/test";
import { addCategory, createRoom, joinByLink, phone } from "./helpers";

test("manifest instalable a pantalla completa", async ({ request }) => {
  const manifest = await (await request.get("/manifest.webmanifest")).json();
  expect(manifest.display).toBe("fullscreen");
  expect(manifest.display_override).toContain("standalone");
  expect(manifest.icons.map((i: { sizes: string }) => i.sizes)).toEqual(
    expect.arrayContaining(["192x192", "512x512"]),
  );
});

test("service worker registrado y cabeceras de caché correctas", async ({ page, request }) => {
  await page.goto("/");
  const scope = await page.evaluate(async () => (await navigator.serviceWorker.ready).scope);
  expect(scope).toContain("127.0.0.1");
  const sw = await request.get("/sw.js");
  expect(sw.headers()["cache-control"]).toBe("no-cache");
  const health = await (await request.get("/healthz")).json();
  expect(health).toEqual({ status: "ok", version: "e2e" });
});

async function expectAccessible(page: Page) {
  const results = await new AxeBuilder({ page }).analyze();
  const serious = results.violations.filter((v) =>
    ["serious", "critical"].includes(v.impact ?? ""),
  );
  expect(serious.map((v) => `${v.id}: ${v.nodes.map((n) => n.target).join(", ")}`)).toEqual([]);
}

test("pantallas sin problemas serios de accesibilidad", async ({ page, browser }) => {
  await page.goto("/");
  await expectAccessible(page);
  const code = await createRoom(page, "Ana");
  const leo = await phone(browser);
  await joinByLink(leo, code, "Leo");
  await addCategory(page, "Gracioso");
  await expectAccessible(page);
  await page.getByRole("button", { name: "Votar" }).click();
  await expect(page.getByRole("group", { name: "Gracioso · Leo" })).toBeVisible();
  await expectAccessible(page);
});
