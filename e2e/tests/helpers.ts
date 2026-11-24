import { type Browser, devices, expect, type Page } from "@playwright/test";

export const BASE = "http://127.0.0.1:8124";

/** A new phone (an isolated context with its own localStorage). */
export async function phone(browser: Browser): Promise<Page> {
  const context = await browser.newContext({ ...devices["Pixel 7"], baseURL: BASE });
  return context.newPage();
}

export async function createRoom(page: Page, name = "Ana"): Promise<string> {
  await page.goto("/");
  await page.getByRole("button", { name: "Crear" }).click();
  await page.getByLabel("Tu nombre").fill(name);
  await page.getByRole("button", { name: "Crear" }).click();
  await page.waitForURL(/\/r\/[A-Z0-9]{5}$/);
  const code = page.url().split("/r/")[1] ?? "";
  await expect(page.getByRole("heading", { name: /Jugadores/ })).toBeVisible();
  return code;
}

export async function joinByLink(
  page: Page,
  code: string,
  name: string,
  role: "Concursa" | "Solo vota" = "Concursa",
): Promise<void> {
  await page.goto(`/r/${code}`);
  await page.getByLabel("Tu nombre").fill(name);
  await page.getByRole("radio", { name: role }).click();
  await page.getByRole("button", { name: "¡Dentro!" }).click();
  await expect(page.getByText(`${name} · Tú`)).toBeVisible();
}

export async function confirm(page: Page): Promise<void> {
  await page.getByRole("dialog").getByRole("button", { name: "Sí" }).click();
}
