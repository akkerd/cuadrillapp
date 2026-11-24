import { expect, test } from "@playwright/test";
import { confirm, createRoom, joinByLink, phone } from "./helpers";

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
