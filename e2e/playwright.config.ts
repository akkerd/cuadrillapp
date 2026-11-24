import { fileURLToPath } from "node:url";
import { defineConfig, devices } from "@playwright/test";

export const PORT = 8124;
const webDist = fileURLToPath(new URL("../apps/web/dist", import.meta.url));
const server = fileURLToPath(new URL("../apps/server", import.meta.url));

export default defineConfig({
  testDir: "./tests",
  timeout: 30_000,
  expect: { timeout: 6_000 },
  fullyParallel: true,
  workers: process.env.CI ? 2 : 4,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI
    ? [["github"], ["html", { open: "never" }]]
    : [["list"], ["html", { open: "never" }]],
  use: {
    ...devices["Pixel 7"],
    baseURL: `http://127.0.0.1:${PORT}`,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  webServer: {
    command: `uv run --project ${server} uvicorn cuadrillapp.main:create_app --factory --host 127.0.0.1 --port ${PORT} --workers 1`,
    url: `http://127.0.0.1:${PORT}/healthz`,
    env: {
      ENV: "test",
      WEB_DIST_DIR: webDist,
      RENDER_GIT_COMMIT: "e2e",
      ROOM_CREATES_PER_MINUTE: "1000",
    },
    reuseExistingServer: false,
    timeout: 60_000,
  },
});
