# Tasks

## 1. Scaffolding del monorepo

- [x] 1.1 Crear la estructura (`apps/server` como proyecto uv con layout `src/cuadrillapp`, `apps/web`, `packages/protocol`, `e2e`), `pnpm-workspace.yaml`, `.python-version` (3.14), `.node-version` (26), `.gitignore`; verificar con `uv sync` y `pnpm install` sin errores
- [x] 1.2 Configurar en `pyproject.toml` Ruff, mypy strict (plugin Pydantic) y pytest + pytest-asyncio (`asyncio_mode = "auto"`) con un test trivial; configurar Biome, `tsc` y Vitest en la web con un test trivial; verificar que `uv run ruff check`, `uv run mypy`, `uv run pytest` y `pnpm test` pasan
- [x] 1.3 `create_app()` mínimo (FastAPI + `socketio.ASGIApp` + `Settings` con pydantic-settings) con `/healthz` → `{status, version}`; verificar con un test httpx y con `uv run uvicorn cuadrillapp.main:app --factory` + `curl /healthz`
- [x] 1.4 `Makefile` (`setup`, `dev`, `gen`, `gen-check`, `lint`, `typecheck`, `test`, `build`, `e2e`, `verify`) y `CLAUDE.md` inicial con las reglas de design.md §19; verificar que `make verify` termina en verde en un checkout limpio

## 2. Protocolo y constantes

- [x] 2.1 Constantes (30 participantes, 8 categorías, longitudes, alfabeto de código sin ambiguos, lista curada de emojis, sugerencias de categorías); verificar con tests de que el alfabeto excluye 0/O/1/I/L y de que los emojis no se repiten
- [x] 2.2 Modelos Pydantic de todos los comandos, del ack `{ok,data}|{ok,error}`, de `ErrorCode` y del snapshot proyectado (`extra="forbid"`, notas como cuartos 0..40); verificar con tests de payloads válidos e inválidos (nota 41, campo extra, código mal formado)
- [x] 2.3 `python -m cuadrillapp.protocol.export` → `packages/protocol/schema.json` + generación de `generated.ts` con `json-schema-to-typescript` (`make gen`) y `make gen-check`; verificar que modificar un modelo sin regenerar hace fallar `make gen-check`

## 3. Dominio puro

- [x] 3.1 Helpers `scores.py` (cuartos ↔ decimal) y `names.py` (normalización con `unicodedata`: mayúsculas, tildes, espacios) y generación de códigos únicos; verificar con tests ("  Dáni " ≡ "dani", 29 cuartos = 7,25)
- [x] 3.2 Modelos de dominio (dataclasses) y `apply_command` con `deepcopy` + `match` para crear, unirse, título, límite de 30 y nombre único; verificar con tests de los escenarios de `specs/rooms` y del perfil de `specs/participants`
- [x] 3.3 Roles (bloqueo fuera del lobby), participantes manuales, salir y expulsar con descarte de notas salvo en resultados, efecto `NotifyKicked`; verificar con tests de `specs/participants`
- [x] 3.4 Permisos de admin, conceder/quitar, último admin, sucesión por orden de llegada con efectos `StartAdminGrace`/`CancelAdminGrace`; verificar con tests de todos los escenarios de `specs/room-admin`
- [x] 3.5 Categorías (CRUD, orden, solo en lobby), fases y requisitos para empezar, notas (escala, autovoto, edición, cierre), voto delegado, "Listo" y progreso; verificar con tests de `specs/voting`
- [x] 3.6 `compute_results` con `Fraction` (media por categoría, nota final, "Sin votos", empates 1,1,3), revelar (congela), reabrir y nueva ronda; verificar con tests de todos los escenarios de `specs/results`
- [x] 3.7 `project_snapshot(room, viewer_id)` (mis notas; progreso y notas delegadas solo para admins; nunca notas ajenas) y test de que `domain/` no importa `asyncio`, `socketio` ni `fastapi`; verificar con tests del escenario "Notas ajenas ocultas"

## 4. Runtime del servidor

- [x] 4.1 Estáticos de `WEB_DIST_DIR` con fallback SPA para `/r/{code}` (excluyendo `/socket.io`, `/api`, `/healthz`), cabeceras de caché del SW y middleware de cabeceras seguras; verificar con tests httpx
- [x] 4.2 `build_socket_server`, `dispatch` (rate limit → Pydantic → dominio → `store.put` → broadcast proyectado por socket → efectos) y `MemoryRoomStore`; verificar con test de integración con 3 `socketio.AsyncClient` (crear, unirse, todos ven la lista actualizada) y test de que dos comandos concurrentes sobre la misma sala no se pierden
- [x] 4.3 Presencia en `connect`/`disconnect`, `room:rejoin` con token, `Scheduler` real y `FakeScheduler`, gracia de 60 s y sucesión de admin, barrido de salas a los 30 min en el `lifespan`; verificar con tests de integración usando `FakeScheduler.advance()`
- [x] 4.4 Rate limit por socket (token bucket), límite de creación por IP y tope global de salas; verificar con tests de ráfaga y de datos inválidos que no alteran la sala

## 5. Base del frontend

- [x] 5.1 Vite + React 19 + Tailwind v4 con tokens de la paleta "fiesta", fuente Fredoka auto-alojada, `copy.ts`, componentes base (BotónGordo, Tarjeta, Avatar emoji, Toast) y proxy de Vite hacia Uvicorn; verificar con tests de componentes y capturas de Playwright a 375 px
- [x] 5.2 Router (`/`, `/r/:code`), cliente Socket.IO tipado con `@cuadrillapp/protocol`, store del snapshot, reconexión con `rejoin_token`, pantalla "Despertando…" y aviso de conexión perdida; verificar con test del store y prueba manual parando Uvicorn
- [x] 5.3 Mapeo de `ErrorCode` a avisos cortos con emoji ("No existe", "Llena", "Nombre en uso"…); verificar con test unitario de que todos los códigos generados tienen texto

## 6. Pantallas

- [x] 6.1 Inicio: "➕ Crear" y "🚪 Unirse" con campo de código tolerante a minúsculas y espacios; verificar con e2e de unirse con " abc23 "
- [x] 6.2 Perfil: rejilla de emojis + 🎲 aleatorio, nombre, selector de rol, perfil recordado; verificar con e2e de perfil precargado en segunda sala
- [x] 6.3 Lobby: lista con coronas/estado/sin móvil, compartir (código, enlace, QR, Web Share), título editable, panel admin (categorías con sugerencias, añadir manual, expulsar, rol, admin) y botón "Votar" con requisitos; verificar con e2e admin + 2 jugadores
- [x] 6.4 Votación: tarjeta por concursante con deslizador de 0,25 y botones ±, emoji según nota, "—" sin nota, guardado automático, progreso, "Listo", selector "Votar como" para admins; verificar con e2e de nota 7,00 → "+" → 7,25 y voto delegado
- [x] 6.5 Resultados: podio animado sincronizado con confeti (sin animación con movimiento reducido), pestañas por categoría con medias y nº de notas, "Reabrir" y "Otra"; verificar con e2e del flujo completo y comprobación de empates

## 7. Experiencia PWA

- [x] 7.1 Manifest (fullscreen + standalone, portrait, iconos maskable generados del logo) y service worker en modo prompt con aviso "Actualizar" que no recarga dentro de una sala; verificar con e2e que comprueba el manifest, el registro del SW y las cabeceras de caché servidas por FastAPI
- [ ] 7.2 Botón "Instalar" (prompt nativo en Android, mini guía en iOS), botón de pantalla completa si está soportada, Wake Lock con re-adquisición y zonas seguras; verificar instalando en un Android y un iPhone reales (checklist en README)
- [x] 7.3 Accesibilidad: nombres accesibles en botones de icono, contraste de la paleta, `prefers-reduced-motion`; verificar con `@axe-core/playwright` sin violaciones serias en todas las pantallas

## 8. Tests end-to-end de sistema

- [x] 8.1 `webServer` de Playwright que sirve la build con Uvicorn; e2e multi-dispositivo del flujo completo (crear → 2 se unen → categorías → votar → revelar → otra ronda) y de recarga a mitad de votación; verificar que corre dentro de `make verify` en menos de 2 minutos
- [x] 8.2 E2E de sucesión de admin (el admin sale y la corona pasa al siguiente) y de expulsión; verificar en verde en local y en CI

## 9. Empaquetado, CI/CD y despliegue

- [x] 9.1 Dockerfile multi-etapa (build web con Node 26 + runtime `python:3.14-slim` con uv, usuario sin privilegios, 1 worker) y `.dockerignore`; verificar con `docker build`, `docker run` y `curl /healthz` en local
- [ ] 9.2 Workflow `ci.yml` con jobs `verify` (setup-uv + pnpm con cachés, `make setup`, `make verify`, artefacto del informe si falla) y `docker` (build + prueba de humo); verificar con un PR de prueba con un test roto (rojo) y arreglado (verde)
- [ ] 9.3 Repo público en GitHub con escaneo de secretos y protección de push activados, y ruleset de main (PR + checks `verify` y `docker`, sin force-push ni borrado); verificar por API que ambas opciones están activas y que un push directo a main es rechazado
- [ ] 9.4 `render.yaml` (`runtime: docker`, free, `/healthz`, deploy tras checks) y conexión del Blueprint (paso manual del usuario); comprobar si `autoDeployTrigger: checksPass` está disponible y, si no, implementar el fallback con Deploy Hook; verificar que un merge verde despliega y que `/healthz` devuelve el SHA
- [ ] 9.5 Probar la protección del despliegue: un commit que rompe el arranque no sustituye a la versión buena; documentar rollback (revert por PR y rollback en Render) en README; verificar ejecutando ambos procedimientos una vez

## 10. Flujo con Claude desde el móvil

- [ ] 10.1 Completar `CLAUDE.md` (rama, `make verify`, `make gen`, regla de atomicidad, PR corto con capturas si es visual, comprobar `/healthz` tras merge, specs OpenSpec como fuente de verdad) y el script de setup del entorno en la nube (uv + `make setup`); verificar arrancando una sesión de Claude en la nube que ejecuta `make verify` en verde sin pasos manuales
- [ ] 10.2 Prueba de extremo a extremo del sistema: desde el móvil pedir un cambio visual pequeño, revisar el PR, mergear desde el móvil y confirmar el nuevo SHA en `/healthz`; anotar fricciones encontradas en README

## Workflow follow-up

- Revisar con el usuario la app desplegada en una partida real antes de archivar.
- Comprobar la implementación contra los specs con el workflow `verify` de OpenSpec.
- Archivar el change con `openspec archive add-live-voting` para consolidar los specs en `openspec/specs/`.
- Empezar `add-leagues-ranking` una vez archivado este change.
