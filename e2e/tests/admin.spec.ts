import { expect, test } from "@playwright/test";
import { addCategory, confirm, createRoom, joinByLink, phone, score } from "./helpers";

test("expulsar y sucesión de admin al salir", async ({ page, browser }) => {
  const code = await createRoom(page, "Ana");
  const leo = await phone(browser);
  await joinByLink(leo, code, "Leo");
  const sara = await phone(browser);
  await joinByLink(sara, code, "Sara");

  await page.getByRole("button", { name: /Sara/ }).click();
  await page.getByRole("dialog").getByRole("button", { name: "Expulsar" }).click();
  await confirm(page);
  await expect(sara.getByText("Fuera 👋")).toBeVisible();
  await expect(page.getByText("Sara")).toHaveCount(0);

  await expect(leo.getByRole("button", { name: "Añadir 📵" })).toHaveCount(0);
  await page.getByRole("button", { name: "Salir" }).click();
  await confirm(page);
  // Leo era el siguiente en llegar: ahora es admin.
  await expect(leo.getByRole("button", { name: "Añadir 📵" })).toBeVisible();
  await expect(leo.getByLabel("Admin")).toBeVisible();
});

test("voto delegado para un participante sin móvil", async ({ page, browser }) => {
  const code = await createRoom(page, "Ana");
  const leo = await phone(browser);
  await joinByLink(leo, code, "Leo");

  await page.getByRole("button", { name: "Añadir 📵" }).click();
  const dialog = page.getByRole("dialog");
  await dialog.getByLabel("Tu nombre").fill("Abuela");
  await dialog.getByRole("button", { name: "Añadir" }).click();
  await expect(page.getByRole("img", { name: "Sin móvil" })).toBeVisible();

  await addCategory(page, "Gracioso");
  await page.getByRole("button", { name: "Votar" }).click();

  await page.getByRole("radio", { name: /Abuela/ }).click();
  // Votando como la abuela, ella no aparece entre los concursantes.
  await expect(page.getByRole("group", { name: "Gracioso · Abuela" })).toHaveCount(0);
  await score(page, "Gracioso", "Leo").set(10);
  await expect(page.getByText("1/2")).toBeVisible();

  await page.getByRole("radio", { name: /Yo/ }).click();
  await expect(score(page, "Gracioso", "Leo").value).toHaveText("—");
  await expect(page.getByRole("group", { name: "Gracioso · Abuela" })).toBeVisible();
});
