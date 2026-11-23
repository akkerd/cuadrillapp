import { expect, test } from "@playwright/test";
import { addCategory, confirm, createRoom, joinByLink, phone, score } from "./helpers";

test("concurso completo: crear, unirse, votar, revelar y otra ronda", async ({ page, browser }) => {
  const code = await createRoom(page, "Ana");

  // Leo entra por enlace; Sara escribe el código en minúsculas y con espacios.
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
  await expect(page.getByRole("button", { name: "Votar" })).toBeDisabled();

  await addCategory(page, "Gracioso");
  await addCategory(page, "Estilo");
  await expect(leo.getByText("Estilo")).toBeVisible();
  await page.screenshot({ path: "test-results/shots/lobby.png", fullPage: true });

  await page.getByRole("button", { name: "Votar" }).click();
  await expect(leo.getByRole("group", { name: "Gracioso · Sara" })).toBeVisible();
  // Nadie se puntúa a sí mismo.
  await expect(leo.getByRole("group", { name: "Gracioso · Leo" })).toHaveCount(0);

  const leoOnSara = score(leo, "Gracioso", "Sara");
  await leoOnSara.set(7);
  await expect(leoOnSara.value).toHaveText("7,00");
  await leoOnSara.plus.click();
  await expect(leoOnSara.value).toHaveText("7,25");

  await score(sara, "Gracioso", "Leo").set(9);
  await score(page, "Estilo", "Leo").set(8);
  await score(page, "Estilo", "Sara").set(6.5);
  await expect(page.getByText("2/4")).toBeVisible();
  await leo.getByRole("button", { name: "Listo" }).click();
  await expect(page.getByRole("img", { name: "Leo Listo" })).toBeVisible();
  await leo.screenshot({ path: "test-results/shots/voting.png", fullPage: true });

  // Recargar a mitad de votación conserva plaza y notas.
  await leo.reload();
  await expect(score(leo, "Gracioso", "Sara").value).toHaveText("7,25");

  await page.getByRole("button", { name: "Revelar" }).click();
  await confirm(page);
  for (const p of [page, leo, sara]) {
    await expect(p.getByLabel("Podio")).toBeVisible();
  }
  // General: Leo (9 + 8) / 2 = 8,50; Sara (7,25 + 6,5) / 2 = 6,88
  const rows = page.getByTestId("result-score");
  await expect(rows.nth(0)).toHaveText("8,50");
  await expect(rows.nth(1)).toHaveText("6,88");
  await expect(rows.nth(2)).toHaveText("Sin votos");
  await page.getByRole("tab", { name: "Gracioso" }).click();
  await expect(page.getByTestId("result-score").first()).toHaveText("9,00");
  await page.waitForTimeout(2800);
  await page.screenshot({ path: "test-results/shots/results.png", fullPage: true });

  // Las notas ya no se pueden cambiar.
  await expect(leo.getByRole("group", { name: "Gracioso · Sara" })).toHaveCount(0);

  await page.getByRole("button", { name: "Otra" }).click();
  await confirm(page);
  await expect(page.getByRole("button", { name: "Votar" })).toBeEnabled();
  await expect(sara.getByText("Esperando al admin…")).toBeVisible();
});

test("el perfil se recuerda para la siguiente sala", async ({ page }) => {
  await createRoom(page, "Ana");
  await page.getByRole("button", { name: "Salir" }).click();
  await confirm(page);
  await page.waitForURL("/");
  await page.getByRole("button", { name: "Crear" }).click();
  await expect(page.getByLabel("Tu nombre")).toHaveValue("Ana");
});

test("un código inexistente muestra un aviso", async ({ page }) => {
  await page.goto("/r/ZZZZZ");
  await expect(page.getByText("No existe 🤔")).toBeVisible();
  await page.getByRole("button", { name: "Inicio" }).click();
  await expect(page.getByRole("button", { name: "Crear" })).toBeVisible();
});
