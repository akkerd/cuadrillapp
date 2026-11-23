// Renderiza los iconos PNG de la PWA desde los SVG con Chromium (pnpm --filter e2e icons).
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { chromium } from "@playwright/test";

const publicDir = new URL("../../apps/web/public/", import.meta.url);
const jobs = [
  ["icon.svg", "icon-192.png", 192],
  ["icon.svg", "icon-512.png", 512],
  ["icon-maskable.svg", "icon-maskable-512.png", 512],
  ["icon-maskable.svg", "apple-touch-icon.png", 180],
];

const browser = await chromium.launch();
for (const [source, output, size] of jobs) {
  const page = await browser.newPage({ viewport: { width: size, height: size } });
  const svg = await readFile(new URL(source, publicDir));
  const src = `data:image/svg+xml;base64,${svg.toString("base64")}`;
  await page.setContent(
    `<style>html,body{margin:0;background:transparent}</style><img src="${src}" width="${size}" height="${size}">`,
  );
  await page.screenshot({ path: fileURLToPath(new URL(output, publicDir)), omitBackground: true });
  await page.close();
  console.log(`${output} (${size}px)`);
}
await browser.close();
