import { expect, test } from "@playwright/test";
import { addCategory, confirm, createRoom, joinByLink, phone, score } from "./helpers";

test("kick and admin succession on leave", async ({ page, browser }) => {
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
  // Leo joined next, so Leo is now admin.
  await expect(leo.getByRole("button", { name: "Añadir 📵" })).toBeVisible();
  await expect(leo.getByLabel("Admin")).toBeVisible();
});

test("proxy voting for a participant without a phone", async ({ page, browser }) => {
  const code = await createRoom(page, "Ana");
  const leo = await phone(browser);
  await joinByLink(leo, code, "Leo");

  await page.getByRole("button", { name: "Añadir 📵" }).click();
  const dialog = page.getByRole("dialog");
  await dialog.getByLabel("Tu nombre").fill("Grandma");
  await dialog.getByRole("button", { name: "Añadir" }).click();
  await expect(page.getByRole("img", { name: "Sin móvil" })).toBeVisible();

  await addCategory(page, "Gracioso");
  await page.getByRole("button", { name: "Votar" }).click();

  await page.getByRole("radio", { name: /Grandma/ }).click();
  // While voting as Grandma, Grandma is not among the candidates.
  await expect(page.getByRole("group", { name: "Gracioso · Grandma" })).toHaveCount(0);
  await score(page, "Gracioso", "Leo").set(10);
  await expect(page.getByText("1/2")).toBeVisible();

  await page.getByRole("radio", { name: /Yo/ }).click();
  await expect(score(page, "Gracioso", "Leo").value).toHaveText("—");
  await expect(page.getByRole("group", { name: "Gracioso · Grandma" })).toBeVisible();
});
