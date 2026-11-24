import { expect, test } from "@playwright/test";
import { confirm, createRoom, joinByLink, phone } from "./helpers";

test("rooms: create and join by link or by code", async ({ page, browser }) => {
  const code = await createRoom(page, "Ana");

  // Leo joins via the link; Sara types the code in lowercase with spaces.
  const leo = await phone(browser);
  await joinByLink(leo, code, "Leo");
  const sara = await phone(browser);
  await sara.goto("/");
  await sara.getByRole("button", { name: "Unirse" }).click();
  await sara.getByLabel("CÓDIGO").fill(` ${code.toLowerCase()} `);
  await sara.getByRole("button", { name: "Entrar" }).click();
  await sara.getByLabel("Tu nombre").fill("Sara");
  await sara.getByRole("button", { name: "¡Dentro!" }).click();

  await expect(page.getByText("Sara")).toBeVisible();
});

test("the profile is remembered for the next room", async ({ page }) => {
  await createRoom(page, "Ana");
  await page.getByRole("button", { name: "Salir" }).click();
  await confirm(page);
  await page.waitForURL("/");
  await page.getByRole("button", { name: "Crear" }).click();
  await expect(page.getByLabel("Tu nombre")).toHaveValue("Ana");
});

test("an unknown code shows a notice", async ({ page }) => {
  await page.goto("/r/ZZZZZ");
  await expect(page.getByText("No existe 🤔")).toBeVisible();
  await page.getByRole("button", { name: "Inicio" }).click();
  await expect(page.getByRole("button", { name: "Crear" })).toBeVisible();
});
