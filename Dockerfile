# syntax=docker/dockerfile:1
# Imagen única: build de la PWA con Node y runtime Python (FastAPI + Socket.IO).

FROM node:26-slim AS web
# Node 26 ya no incluye corepack: instalamos la versión de `packageManager`.
RUN npm install -g pnpm@12.21.0
WORKDIR /repo
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml tsconfig.base.json ./
COPY apps/web/package.json apps/web/
COPY packages/protocol/package.json packages/protocol/
COPY e2e/package.json e2e/
RUN pnpm install --frozen-lockfile --filter web...
COPY apps/web apps/web
COPY packages/protocol packages/protocol
RUN pnpm --filter web build

FROM python:3.14-slim AS runtime
COPY --from=ghcr.io/astral-sh/uv:0.13.9 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY apps/server/pyproject.toml apps/server/uv.lock apps/server/.python-version ./
RUN uv sync --frozen --no-dev --no-install-project
COPY apps/server/src ./src
RUN uv sync --frozen --no-dev
COPY --from=web /repo/apps/web/dist ./web

ENV PATH="/app/.venv/bin:$PATH" \
    WEB_DIST_DIR=/app/web \
    ENV=production \
    PORT=8000
USER nobody
EXPOSE 8000
# Un solo worker: el estado de las salas vive en memoria (ver design.md, "Camino de escalado").
CMD ["sh", "-c", "exec uvicorn cuadrillapp.main:create_app --factory --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips='*' --workers 1"]
