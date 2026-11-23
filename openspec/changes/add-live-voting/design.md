# Design

## Context

Proyecto nuevo (repo vacío). Motivación y alcance en `proposal.md`; comportamiento en `specs/`. Restricciones que dan forma al diseño:

- Uso real: grupos de 3-30 amigos en la misma habitación, cada uno con su móvil, sesiones de 10-60 minutos. Carga mínima.
- Proyecto de prueba sin presupuesto: hosting gratuito.
- Backend en **Python** (decisión del usuario: algo sencillo y escalable "tipo Flask"); frontend en React.
- El código lo modificará sobre todo Claude, a menudo desde sesiones en la nube lanzadas desde el móvil y sin el portátil encendido: todo debe instalarse, probarse y verificarse con un solo comando, sin Docker y sin secretos.
- Este change no persiste nada; `add-leagues-ranking` añadirá base de datos y login. El diseño deja el hueco preparado (mismo origen para cookies, dominio puro, interfaces de almacenamiento) sin implementarlo.

## Goals / Non-Goals

**Goals:**
- Un único artefacto desplegable (imagen Docker) que sirve la PWA, el endpoint de salud y el canal en tiempo real en el mismo origen.
- Reglas de negocio en funciones puras de Python con tests rápidos; red, reloj y temporizadores en una capa fina alrededor.
- Un contrato cliente-servidor con una sola fuente de verdad (Pydantic) y tipos TypeScript generados.
- Un camino de escalado horizontal definido (interfaces intercambiables), aunque hoy se ejecute una sola instancia.
- Pipeline en el que "mergear a main" sea la única forma de desplegar, y solo con checks verdes.

**Non-Goals:**
- Implementar ya el escalado horizontal o la supervivencia de salas a reinicios.
- Renderizado en servidor (SSR) o SEO.
- Optimizar para navegadores de escritorio antiguos (prioridad: Chrome Android y Safari iOS recientes).

## Arquitectura

```
 Móvil (PWA)                                   Render (plan free, 1 instancia, Docker)
┌──────────────────────────┐   HTTPS          ┌────────────────────────────────────────────┐
│ React 19 + Vite          │ ───────────────▶ │ Uvicorn (1 worker) → socketio.ASGIApp      │
│  pantallas ← store       │   GET /, /r/:c   │  ├─ FastAPI                                │
│  (último snapshot)       │   GET /healthz   │  │   ├─ /healthz → {status, version: SHA}  │
│        ▲         │       │                  │  │   └─ estáticos PWA + fallback SPA       │
│ snapshot│     comando     │   WebSocket      │  └─ python-socketio AsyncServer            │
│        │         ▼       │ ◀──────────────▶ │      ├─ dispatch(): Pydantic + rate limit  │
│ socket.io-client          │  (fallback poll) │      ├─ apply_command() ── dominio puro    │
│ Service Worker (shell)   │                  │      ├─ RoomStore (MemoryRoomStore)        │
└──────────────────────────┘                  │      ├─ Scheduler (asyncio)                │
                                              │      └─ project_snapshot() por destinatario│
                                              └────────────────────────────────────────────┘
 GitHub: PR → Actions (make verify + docker build) → main protegida → Render despliega tras checks
```

Estructura del repo:

```
cuadrillapp/
├─ apps/
│  ├─ server/                     proyecto uv (Python 3.14)
│  │  ├─ pyproject.toml           deps + config de Ruff, mypy y pytest
│  │  ├─ uv.lock
│  │  ├─ src/cuadrillapp/
│  │  │  ├─ main.py               create_app(): FastAPI + Socket.IO → ASGI app
│  │  │  ├─ settings.py           Settings (pydantic-settings)
│  │  │  ├─ domain/               PURO: models.py, commands.py, apply.py, results.py,
│  │  │  │                        scores.py, names.py, codes.py, projection.py, errors.py
│  │  │  ├─ protocol/             modelos Pydantic de comandos, acks y snapshot; export.py
│  │  │  ├─ realtime/             server.py (sio), handlers.py, dispatch.py, presence.py,
│  │  │  │                        ratelimit.py, scheduler.py
│  │  │  ├─ store/                base.py (Protocol RoomStore), memory.py
│  │  │  └─ http/                 health.py, static.py, security.py
│  │  └─ tests/                   unit/ (dominio), integration/ (HTTP y sockets)
│  └─ web/                        React PWA (Vite)
├─ packages/protocol/             tipos TS generados (no editar a mano)
├─ e2e/                           Playwright (multi-dispositivo)
├─ openspec/                      specs y changes
├─ Dockerfile, render.yaml, Makefile, CLAUDE.md
├─ pnpm-workspace.yaml            apps/web, packages/protocol, e2e
└─ .github/workflows/ci.yml
```

## Decisions

### 1. FastAPI en lugar de Flask
FastAPI mantiene la sencillez de Flask (una app, rutas con decoradores, poco código), pero es **ASGI y asíncrono de serie**, que es lo que necesita una app de tiempo real: miles de WebSockets abiertos en un solo proceso sin hilos ni monkey-patching. Además trae validación con Pydantic integrada y OpenAPI automática (útil para generar los tipos del frontend en el change 2).
- *Alternativa:* Flask + Flask-SocketIO. Funciona, pero sus modos asíncronos dependen de eventlet (en desuso) o gevent con monkey-patching, que complica usar librerías async (BD, OAuth) y depurar. El modo con hilos escala peor con conexiones largas.
- *Alternativa:* Quart (Flask asíncrono). Misma API que Flask, pero ecosistema y documentación mucho más pequeños.
- *Alternativa:* Django + Channels. Demasiado peso para una app sin modelos de negocio complejos en este change.

### 2. Tiempo real con python-socketio en modo ASGI
`socketio.AsyncServer(async_mode="asgi")` envuelve a FastAPI en una sola app ASGI:

```python
# main.py
def create_app(settings: Settings | None = None) -> ASGIApp:
    settings = settings or Settings()
    api = FastAPI(lifespan=lifespan, docs_url=None if settings.is_production else "/docs")
    api.include_router(health.router)
    install_security_headers(api)
    mount_static(api, settings.web_dist_dir)            # al final: incluye el fallback SPA
    sio = build_socket_server(settings)                  # registra handlers
    return socketio.ASGIApp(sio, other_asgi_app=api, socketio_path="socket.io")
```

El cliente sigue siendo `socket.io-client`: acks, heartbeats, reconexión con backoff y fallback a long-polling en redes móviles que cortan WebSockets, sin reimplementarlos.
- *Alternativa:* WebSockets nativos de FastAPI. Descartado: habría que escribir a mano acks, reconexión, heartbeats y salas, justo lo más delicado en móvil.
- Se ejecuta con `uvicorn cuadrillapp.main:app --factory` y **1 worker**: el estado de las salas vive en el proceso (ver decisión 7 y "Camino de escalado").

### 3. Un único servicio en el mismo origen
FastAPI sirve la build estática de la web (`StaticFiles` para `/assets` y ficheros del SW) y una ruta comodín que devuelve `index.html` para rutas de la SPA (`/r/{code}`); excluye `/socket.io`, `/api` y `/healthz`. Sin CORS, sin dominios cruzados, y cookies first-party listas para el login del change 2. En desarrollo, Vite corre en `:5173` con proxy de `/socket.io`, `/api` y `/healthz` hacia Uvicorn en `:8000`.

### 4. Servidor autoritativo: comandos con ack y snapshots proyectados
- **Cliente → servidor:** un evento por comando (`room:create`, `room:join`, `room:rejoin`, `room:leave`, `participant:update`, `participant:kick`, `admin:set`, `manual:add`, `category:upsert`, `category:delete`, `category:reorder`, `phase:set`, `score:set`, `voter:done`…). Cada handler es una línea que delega en `dispatch`:

```python
# realtime/handlers.py
@sio.on("score:set")
async def score_set(sid: str, data: object) -> AckPayload:
    return await dispatch(sid, ScoreSet, data)

# realtime/dispatch.py
async def dispatch(sid: str, model: type[Command], data: object) -> AckPayload:
    if not limiter.allow(sid):
        return ack_error(ErrorCode.RATE_LIMITED)
    try:
        cmd = model.model_validate(data)
    except ValidationError:
        return ack_error(ErrorCode.INVALID)
    seat = await sio.get_session(sid)                    # {room, participant_id}
    room = store.get(seat["room"])
    if room is None:
        return ack_error(ErrorCode.ROOM_NOT_FOUND)
    result = apply_command(room, seat["participant_id"], cmd, now=clock())
    if isinstance(result, DomainError):
        return ack_error(result.code)
    store.put(result.room)                               # ← sin await entre get y put
    await broadcast(result.room)
    schedule_side_effects(result.effects)                # temporizadores, expulsiones…
    return ack_ok(result.data)
```

- **Atomicidad:** con un solo event loop, no hay `await` entre leer la sala y guardarla, así que dos comandos nunca se intercalan sobre la misma sala. Esta regla se documenta en `CLAUDE.md` y la protege un test.
- **Servidor → cliente:** tras cada mutación, `broadcast` emite `room:state` **a cada socket por separado** con `project_snapshot(room, viewer_id)`: datos públicos + mis notas + (si soy admin) progreso por votante y notas de los participantes manuales. Las notas ajenas nunca salen del servidor (spec de anonimato).
- Con ≤30 participantes × ≤8 categorías el snapshot ocupa pocos KB; no compensa enviar diffs.
- El cliente guarda el último snapshot en un store (Zustand) y la UI es una función de él, con actualización optimista local en la pantalla de puntuación.

### 5. Dominio puro en Python
- `domain/models.py`: `@dataclass(slots=True)` para `Room`, `Participant`, `Category`, `Scores` (dict `(voter_id, candidate_id, category_id) → quarters`), `FrozenResults`. Tipos de valor con `Literal` y `NewType` (no `Enum` de stdlib para que serialicen limpio).
- `domain/apply.py`: `apply_command(room, actor_id, cmd, now) -> Applied | DomainError`. Trabaja sobre `copy.deepcopy(room)` (salas diminutas): si una regla falla a mitad, la copia se descarta y la sala original queda intacta. Despacha con `match cmd:` por tipo de comando.
- `Applied` lleva la nueva sala, los datos de respuesta y **efectos** declarativos (`StartAdminGrace(pid)`, `CancelAdminGrace(pid)`, `NotifyKicked(pid)`) que ejecuta la capa realtime. Así el dominio sigue sin I/O ni temporizadores.
- `domain/results.py`: `compute_results(room) -> Results` con `fractions.Fraction` para medias exactas; rankings y empates se comparan sobre fracciones y solo se redondean a 2 decimales al serializar. Se reutiliza en el change 2.
- Reloj inyectado (`now: float`); nada en `domain/` importa `asyncio`, `socketio` ni `fastapi` (un test de imports lo comprueba).

### 6. Contrato tipado de una sola fuente (Pydantic → TypeScript)
- `protocol/` define con Pydantic v2 todos los comandos (`ScoreSet(room, candidate_id, category_id, quarters: conint(ge=0, le=40) | None)`, …), el formato de ack (`{"ok": true, "data": …} | {"ok": false, "error": ErrorCode}`), los códigos de error y el snapshot proyectado. `model_config = ConfigDict(extra="forbid", frozen=True)`.
- `python -m cuadrillapp.protocol.export` escribe `packages/protocol/schema.json` (JSON Schema de todos los modelos + constantes: límites, alfabeto, emojis, sugerencias de categorías) y `json-schema-to-typescript` genera `packages/protocol/src/generated.ts`. La web solo importa de `@cuadrillapp/protocol`.
- `make gen` regenera; `make gen-check` (parte de `make verify` y de CI) falla si los ficheros generados no coinciden con los modelos → imposible que cliente y servidor se desincronicen sin que CI lo note.
- *Alternativa:* duplicar tipos a mano en TS. Descartado: deriva silenciosa entre lenguajes.

### 7. Estado de salas en memoria detrás de una interfaz
- `store/base.py`: `class RoomStore(Protocol)` con `get`, `put`, `delete`, `code_exists`, `iter_idle(older_than)`. `store/memory.py`: `MemoryRoomStore` con un `dict[str, Room]`.
- Barrido cada 60 s como tarea `asyncio` lanzada en el `lifespan` de FastAPI: elimina salas con 30 min sin conexiones. Límite global de salas activas (p. ej. 300) y de creación por IP (p. ej. 10/min).
- *Consecuencia aceptada:* un reinicio o despliegue cierra todas las salas activas (spec "Reinicio del servidor"); el cliente recibe `ROOM_NOT_FOUND` en `room:rejoin` y muestra "Sala cerrada".

### 8. Identidad de plaza, presencia y temporizadores
- Al unirse, el servidor devuelve `participant_id` y un `rejoin_token = secrets.token_urlsafe(16)` que el cliente guarda en `localStorage` por código de sala. `room:rejoin {code, token}` recupera la plaza; expulsar invalida el token. El servidor guarda `{room, participant_id}` en la sesión de Socket.IO (`sio.save_session`).
- `connect`/`disconnect` de Socket.IO actualizan la presencia (`connected` ↔ `disconnected`). `joined_seq` (contador por sala) define el orden de llegada.
- `realtime/scheduler.py`: `class Scheduler(Protocol)` con `call_later(delay, key, fn)` y `cancel(key)`. Implementación real sobre `asyncio.get_running_loop().call_later`; en tests, `FakeScheduler` con `advance(seconds)` para probar la gracia de 60 s y la sucesión sin esperar.

### 9. Notas como enteros de cuartos
Una nota es un entero 0..40 (cuartos de punto) en todo el backend y en el protocolo. La web convierte para mostrar (`7,25`) con `Intl.NumberFormat('es-ES')`. Elimina errores de coma flotante y simplifica la validación (`conint(ge=0, le=40)`).

### 10. Configuración
`settings.py` con `pydantic-settings`: `ENV` (`development|test|production`), `PORT`, `WEB_DIST_DIR`, `RENDER_GIT_COMMIT` (versión para `/healthz`), límites de rate limit y de salas. Un único objeto `Settings` inyectado en `create_app()`; los tests crean apps con settings propios.

### 11. Herramientas Python
- **uv**: gestiona Python 3.14 (`.python-version`), entorno virtual, dependencias y `uv.lock`. `uv run …` para todo.
- **Ruff** (lint + formato), **mypy --strict** con el plugin de Pydantic, **pytest** + **pytest-asyncio** (`asyncio_mode = "auto"`), **httpx** para tests HTTP.
- Dependencias de runtime mínimas: `fastapi`, `uvicorn[standard]`, `python-socketio`, `pydantic`, `pydantic-settings`.
- Python 3.14 en lugar de 3.15 por madurez de wheels de dependencias; subir de versión es cambiar `.python-version` y la imagen base.

### 12. Frontend
- React 19 + Vite + React Router (rutas `/`, `/r/:code`); pantallas: Inicio, Perfil, Lobby, Votación, Resultados. Dentro de `/r/:code` la pantalla se deriva de la fase del snapshot.
- Tailwind CSS v4 con tokens en CSS variables. Paleta propia "fiesta": fondo degradado violeta (#5B2EE5 → #8F3CF7), amarillo #FFD23F, rosa #FF5FA2, turquesa #22C9B7, naranja #FF8A3D, tinta #1E1338. Tipografía redondeada (Fredoka, auto-alojada). Botones "gorditos" con sombra inferior tipo 3D y tarjetas muy redondeadas. Inspirado en el ambiente de juegos de fiesta, sin copiar assets ni el aspecto de ningún juego concreto.
- Motion para animaciones con muelle (respetando `prefers-reduced-motion`), `canvas-confetti` en el podio, `lucide-react` para iconos, `qrcode` para el QR (generado en cliente).
- Textos en `apps/web/src/copy.ts`. Lista de emojis y sugerencias de categorías vienen de `@cuadrillapp/protocol` (definidas una vez en Python).
- Biome (lint + formato), `tsc --noEmit`, Vitest + Testing Library.

### 13. PWA
`vite-plugin-pwa` (Workbox `generateSW`): precache del shell y fuentes; sin caché de datos. Manifest con `display: "fullscreen"`, `display_override: ["fullscreen", "standalone"]`, `orientation: "portrait"`, iconos maskable 192/512 y `theme_color`. Registro en modo `prompt`: el aviso "Actualizar" solo recarga si el usuario lo pulsa. iOS cae a `standalone` + `viewport-fit=cover` + `env(safe-area-inset-*)`. Wake Lock API mientras hay sala, re-adquirido en `visibilitychange`. Botón de pantalla completa solo si `document.fullscreenEnabled`. FastAPI sirve `sw.js` y `manifest.webmanifest` con `Cache-Control: no-cache` y los assets con hash con caché larga.

### 14. Estrategia de tests
1. **Unit (pytest):** dominio y resultados; cada escenario de los specs de `rooms`, `participants`, `room-admin`, `voting` y `results` tiene su test con nombre del escenario.
2. **Integración (pytest-asyncio):** fixture que arranca `uvicorn.Server` con `create_app(test_settings)` en un puerto libre dentro del event loop del test y conecta varios `socketio.AsyncClient` simulando móviles (unión, proyección anónima, reconexión, rate limit). Temporizadores con `FakeScheduler`. HTTP con `httpx.AsyncClient(transport=ASGITransport(app))`.
3. **Web (Vitest):** store, mapeo de errores y componentes clave.
4. **E2E (Playwright, TS):** `webServer` de Playwright ejecuta la build de producción servida por Uvicorn; varios contextos en emulación móvil (Pixel 7): crear → unirse ×2 → categorías → votar → revelar; recarga a mitad de votación. Solo Chromium en CI; WebKit opcional en local.

### 15. Orquestación con Makefile
Un `Makefile` en la raíz es el punto de entrada único para humanos, CI y Claude:
- `make setup` → `uv sync` + `pnpm install` + `pnpm exec playwright install chromium`
- `make dev` → Uvicorn con `--reload` + Vite dev (en paralelo)
- `make gen` / `make gen-check` → contrato Pydantic → TS
- `make lint` (Ruff + Biome), `make typecheck` (mypy + tsc), `make test` (pytest + Vitest), `make build` (Vite), `make e2e` (Playwright)
- `make verify` → `gen-check lint typecheck test build e2e`, falla al primer error

### 16. Empaquetado: imagen Docker multi-etapa
```dockerfile
FROM node:26-slim AS web            # 1) build de la PWA
RUN npm install -g pnpm@12.21.0   # Node 26 ya no incluye corepack
WORKDIR /repo
COPY pnpm-lock.yaml pnpm-workspace.yaml package.json ./
COPY apps/web apps/web
COPY packages/protocol packages/protocol
RUN pnpm install --frozen-lockfile && pnpm --filter web build

FROM python:3.14-slim AS runtime    # 2) runtime Python
COPY --from=ghcr.io/astral-sh/uv:<versión fijada> /uv /bin/uv
WORKDIR /app
COPY apps/server/pyproject.toml apps/server/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY apps/server/src ./src
RUN uv sync --frozen --no-dev
COPY --from=web /repo/apps/web/dist ./web
ENV WEB_DIST_DIR=/app/web PATH="/app/.venv/bin:$PATH"
USER nobody
CMD ["sh", "-c", "uvicorn cuadrillapp.main:app --factory --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*' --workers 1"]
```
Docker evita depender de que el runtime nativo de Render tenga a la vez Node y Python, y la misma imagen sirve en local, CI o cualquier otro proveedor (Fly.io, Cloud Run).

### 17. CI/CD
- **GitHub Actions** `ci.yml` en `pull_request` y `push` a main:
  - job `verify`: `astral-sh/setup-uv` (con caché), Node desde `.node-version` + pnpm con `pnpm/action-setup` (versión del campo `packageManager`; caché del store y de los navegadores de Playwright), `make setup`, `make verify`; sube el informe de Playwright como artefacto si falla.
  - job `docker`: `docker build` de la imagen y prueba de humo (`docker run` + `curl /healthz`). Detecta un Dockerfile roto antes de mergear (no forma parte de `make verify` porque las sesiones en la nube pueden no tener Docker).
- **Repositorio público** (`akkerd/cuadrillapp`): permite rulesets gratis en el plan Free y activa el escaneo de secretos con protección de push. Nada sensible vive en el repo (specs `delivery-pipeline`).
- **Ruleset de main**: PR obligatorio, checks `verify` y `docker` obligatorios, 0 aprobaciones (proyecto de una persona), sin force-push ni borrado.
- **Render Blueprint** (`render.yaml`): web service `runtime: docker`, `plan: free`, `healthCheckPath: /healthz`, auto-deploy solo cuando los checks del commit pasan (`autoDeployTrigger: checksPass`). Render no cambia el tráfico a la versión nueva hasta que el health check responde → spec "Despliegue sin caída".
  - *Fallback* si esa opción no está disponible en el plan: auto-deploy desactivado + job `deploy` en Actions que, tras `verify` y `docker` en main, llama al Deploy Hook de Render (URL como secreto de GitHub).
- `/healthz` devuelve `{"status": "ok", "version": RENDER_GIT_COMMIT}` → Claude (o el usuario) confirma qué commit está en producción.
- **Rollback:** revert por PR (flujo normal) o "Rollback" a un deploy anterior en el dashboard de Render. Documentado en README.

### 18. Por qué GitHub + Render y no "Claude Artifacts"
Los Artifacts de Claude publican páginas alojadas en claude.ai, lo más rápido para un prototipo de frontend, pero no ejecutan un backend Python propio, no tienen repo/CI y no permiten probar el flujo real "PR → checks → deploy" que se quiere evaluar.
Render frente a alternativas: Fly.io ya no tiene plan gratuito real; Cloud Run exige proyecto con facturación e identidad federada para desplegar desde Actions; Railway es de pago tras la prueba. Render free admite Docker y WebSockets, y los mensajes WebSocket cuentan como tráfico y evitan que el servicio se duerma con una partida en curso.

### 19. Flujo de trabajo con Claude desde el móvil
1. Usuario: app de Claude → Code → repo `cuadrillapp` → "pon el botón de revelar más grande".
2. Sesión en la nube: el script de setup del entorno instala uv si falta y ejecuta `make setup` (sin secretos).
3. Claude crea rama, implementa, ejecuta `make verify`, hace push y abre PR con resumen corto (y capturas de Playwright si el cambio es visual).
4. CI verde → el usuario mergea desde la app de GitHub (o se lo pide a Claude).
5. Render despliega tras checks; Claude comprueba que `/healthz` devuelve el SHA mergeado.
`CLAUDE.md` fija estas reglas: nunca push a main, `make verify` antes de push, specs de OpenSpec como fuente de verdad, textos en `copy.ts`, `make gen` tras tocar `protocol/`, nada de `await` entre leer y guardar una sala. Complementos: Remote Control de la sesión del portátil y la GitHub Action de Claude para `@claude` en issues (opcional, requiere secreto; fuera de este change).

### 20. Seguridad básica
Mismo origen (sin CORS; `cors_allowed_origins` de Socket.IO restringido al propio origen), middleware de cabeceras seguras (CSP `self` + `wss:` propio, `X-Content-Type-Options`, `Referrer-Policy`), validación Pydantic con `extra="forbid"` de todo payload, rate limit por socket (token bucket en memoria) y por IP en creación de salas, tokens con `secrets`, logs (logging estándar en JSON) sin tokens. `/docs` de FastAPI desactivado en producción. No se almacenan datos personales en este change.

### 21. Camino de escalado (no implementado)
Hoy: 1 instancia, 1 worker, estado en memoria. Para escalar horizontalmente solo hay que sustituir piezas detrás de interfaces ya existentes; dominio, handlers y frontend no cambian:
1. `RedisRoomStore` (implementa `RoomStore`), con un lock por sala (Redis `SET NX` con TTL) alrededor de get → apply → put.
2. `socketio.AsyncRedisManager` como `client_manager` para que un broadcast llegue a sockets conectados en otras instancias.
3. Forzar transporte solo WebSocket en el cliente (sin long-polling) para no necesitar sticky sessions, o un balanceador con afinidad.
4. `Scheduler` respaldado por Redis (claves con expiración) en lugar de `call_later` en memoria.
5. Varias instancias o `--workers N` en Uvicorn.

## Risks / Trade-offs

- [Un despliegue cierra las salas activas] → No mergear durante una fiesta; el cliente muestra "Sala cerrada" y vuelve al inicio con un toque. El camino de escalado (Redis) lo resolvería.
- [Arranque en frío de Render free (~1 min tras 15 min sin tráfico)] → Pantalla "Despertando…" con reintentos; el admin abre la app un minuto antes.
- [Builds Docker más lentas y minutos de build limitados en el plan free] → Imagen con caché de capas (dependencias antes que código); despliegues solo desde main.
- [Opción "deploy tras checks" de Render no verificada en el plan free] → Se comprueba en la primera tarea de CD; fallback con Deploy Hook ya diseñado.
- [Dos toolchains (uv + pnpm) en las sesiones en la nube] → `make setup` único y script de setup del entorno; probado en la tarea 10.1.
- [Desincronización del contrato Python ↔ TS] → Tipos generados + `make gen-check` en CI.
- [Un `await` accidental entre leer y guardar una sala rompe la atomicidad] → Regla en `CLAUDE.md`, `dispatch` como único punto de mutación y test de concurrencia.
- [iOS: sin pantalla completa real, sin prompt de instalación] → Standalone + zonas seguras + mini guía de instalación.
- [Desconexiones al bloquear el móvil] → Wake Lock + reconexión con token + gracia de 60 s antes de la sucesión de admin.
- [E2E solo en Chromium en CI] → Prueba manual en iPhone antes de cada uso real; WebKit opcional en local.

## Migration Plan

Proyecto nuevo, sin migración de datos. Puesta en marcha:
1. Hecho: repo público `akkerd/cuadrillapp` creado, con escaneo de secretos y protección de push; commits firmados con el email noreply de GitHub.
2. Usuario: crea cuenta en Render y conecta el Blueprint (`render.yaml`) al repo (una vez, desde el dashboard).
3. Claude configura el ruleset de main y verifica el primer despliegue con `/healthz`.
4. Usuario: instala la app de Claude/GitHub en el repo y configura el entorno de la nube con el script de setup.
Rollback: ver decisión 17.

## Open Questions

- Logo de Cuadrillapp. No afecta a specs ni tareas.
- ¿Dominio propio en lugar de `*.onrender.com`? Se puede añadir más tarde en Render sin cambios de código.
