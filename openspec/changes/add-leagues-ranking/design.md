# Design

## Context

Parte del sistema construido en `add-live-voting` (ver su `design.md`): una app ASGI (FastAPI + python-socketio) en una imagen Docker en Render, salas en memoria detrás de `RoomStore`, dominio puro, `dispatch` como único punto de mutación, snapshots proyectados por destinatario, `compute_results` con fracciones exactas y contrato Pydantic → TypeScript generado. Motivación en `proposal.md`, comportamiento en `specs/`.

Restricciones nuevas:
- Hace falta persistencia duradera y gratuita: Render Postgres free caduca a los 30 días y se borra.
- CI y las sesiones de Claude en la nube no deben necesitar secretos; las sesiones en la nube, tampoco Docker.
- El login debe funcionar en la PWA instalada (iOS incluido).

## Goals / Non-Goals

**Goals:**
- Persistir solo lo necesario para ligas y ranking; la partida en vivo sigue en memoria.
- Que todo el flujo (login incluido) sea testeable end-to-end sin Google ni base de datos externa.
- Mantener el juego sin cuenta exactamente igual que antes.

**Non-Goals:**
- Persistir el estado de las salas en vivo.
- Roles finos en ligas más allá de "dueño" y "miembro".
- Panel de administración global.

## Arquitectura (añadidos)

```
 PWA ──HTTPS──▶ ASGI app ─┬─ FastAPI
                          │   ├─ /api/auth/*      Authlib (OIDC Google) → cookie firmada `cq_session`
                          │   ├─ /api/me*         usuario actual, vincular dispositivos
                          │   └─ /api/leagues*    routers con dependencias de acceso
                          ├─ python-socketio      connect(): lee `cq_session` → user_id en la sesión del socket
                          │    └─ al revelar: asyncio task → LeagueService.save_contest() (transacción)
                          └─ SQLAlchemy 2.0 async ──▶ prod: Neon Postgres (asyncpg)
                                                     dev/tests: SQLite (aiosqlite)
                                                     CI: + Postgres de servicio (suite marcada `pg`)
```

Módulos nuevos en `apps/server/src/cuadrillapp/`:

```
db/         engine.py (create_async_engine según DATABASE_URL), models.py (ORM), session.py
migrations/ Alembic (env async, render_as_batch para SQLite)
auth/       google.py (Authlib), cookies.py (firmar/leer cq_session), routes.py, test_login.py, deps.py
leagues/    service.py (save_contest, vínculos), ranking.py (PURO), access.py (deps), routes.py
```

## Decisions

### 1. SQLAlchemy 2.0 async con Postgres (prod) y SQLite (dev/tests)
- **Producción:** Neon free (Postgres gestionado y persistente, scale-to-zero). URL `postgresql+asyncpg://…?ssl=require`.
- **Desarrollo, tests y sesiones de Claude:** SQLite con `aiosqlite` (fichero o `:memory:`). Cero instalación, sin Docker ni secretos.
- **CI:** además de la suite normal sobre SQLite, un paso ejecuta los tests marcados `@pytest.mark.pg` contra un contenedor de servicio `postgres` de GitHub Actions para detectar diferencias de dialecto.
- Para que la portabilidad sea real: tipos genéricos de SQLAlchemy (`String` para ids UUID, `JSON`, `DateTime(timezone=True)`, `Float`), nada de SQL específico de Postgres, y los cálculos del ranking en Python (decisión 8), no en SQL.
- *Alternativas:* PGlite (solo existe para JS); `py-pglite` (necesita Node en tiempo de test); `pytest-postgresql` (necesita binarios de Postgres en la sesión en la nube); Render Postgres (caduca); Supabase free (se pausa tras una semana sin uso); SQLite en producción (Render free no tiene disco persistente).

### 2. Migraciones con Alembic al arrancar
`alembic revision --autogenerate` genera migraciones versionadas en el repo (`env.py` asíncrono, `render_as_batch=True` para que también apliquen en SQLite). El `CMD` de la imagen pasa a `alembic upgrade head && uvicorn …`: si una migración falla, el proceso no arranca, el health check falla y Render mantiene la versión anterior. Regla en `CLAUDE.md`: migraciones solo aditivas (expandir/contraer) para que la versión anterior funcione con el esquema nuevo durante el despliegue. Los tests crean el esquema aplicando las mismas migraciones (no `create_all`), así que una migración rota rompe CI.

### 3. Login con Google: Authlib + cookie de sesión firmada
- **OIDC con Authlib** (`authlib.integrations.starlette_client.OAuth`, registro `google` con `server_metadata_url` de descubrimiento y scopes `openid email profile`). Rutas:
  - `GET /api/auth/google/login` → redirección completa (no popup) a Google con `state` y `nonce`.
  - `GET /api/auth/google/callback` → `authorize_access_token()` valida el ID token; upsert de `users` por `google_sub`; emite la cookie; redirige a `/`. Si el usuario canceló, redirige a `/?login=cancelled` (spec "Login cancelado").
  - `POST /api/auth/logout` borra la cookie. `GET /api/me` devuelve el usuario o 401.
- `SessionMiddleware` de Starlette se usa **solo** para el `state` temporal del flujo OAuth.
- **Sesión de usuario:** cookie propia `cq_session` = `itsdangerous.URLSafeTimedSerializer(SESSION_SECRET).dumps({"uid": …})`, `HttpOnly`, `Secure`, `SameSite=Lax`, 30 días (spec "Sesión persistente"). Sin tabla de sesiones: no hace falta revocar sesiones individuales en un proyecto entre amigos; rotar `SESSION_SECRET` cierra todas.
- Dependencias FastAPI: `optional_user` y `require_user` leen y verifican la cookie con `auth/cookies.py`.
- **Socket.IO:** en el handler `connect(sid, environ, auth)` se lee la cabecera `Cookie` del `environ` con el mismo helper y se guarda `user_id` (o `None`) en `sio.save_session`. Al iniciar o cerrar sesión, el cliente reconecta el socket.
- **Login de prueba:** router `test_login` (`POST /api/auth/test-login {name}`) incluido solo si `settings.env != "production"` y `settings.auth_test_login`. Un validador de `Settings` lanza un error si `ENV=production` y `AUTH_TEST_LOGIN` está activo → la app no arranca (spec "Producción"). Lo usan pytest, Playwright y las sesiones de Claude.
- *Alternativas:* `fastapi-users` (más pesado, sesiones/JWT y tablas que no necesitamos); Google Identity Services con ID token en el cliente (popup, peor en PWA iOS); sesiones en base de datos (revocación individual no necesaria).
- *Riesgo PWA iOS:* la redirección OAuth dentro de una PWA instalada puede abrirse en una vista de Safari aislada. Mitigación: probarlo en dispositivo real en la primera tarea de auth; si falla, en modo standalone "Entrar" indica iniciar sesión primero desde Safari y se documenta.

### 4. Modelo de datos (ORM)

```
users            id, google_sub UNIQUE, name, email, avatar_url, created_at
leagues          id, name, emoji, owner_user_id → users, access_key UNIQUE, created_at, last_played_at
league_members   id, league_id → leagues, display_name, name_key, emoji, user_id → users NULL, created_at
                 UNIQUE(league_id, name_key), UNIQUE(league_id, user_id)
contests         id (generado al abrir cada ronda), league_id, title, host_user_id → users,
                 categories JSON [{emoji, name}], revealed_at, created_at
contest_entries  contest_id → contests, member_id → league_members, role ('candidate'|'voter'),
                 final_score FLOAT NULL, position INT NULL, scores_count INT,
                 category_scores JSON [{avg, count, position}]
                 PK(contest_id, member_id)
```
- `name_key` = el mismo `names.normalize()` del dominio de salas (spec "Identidad por nombre").
- Los solo votantes y quienes no recibieron notas tienen fila con `final_score NULL`: cuentan como miembros (acceso) sin entrar en la clasificación.
- `position` se copia de `compute_results` (calculada con fracciones exactas); `final_score` se guarda como float solo para mostrar y ordenar por media.

### 5. Ligas en la sala en vivo
- `room:create` acepta `league: {id} | {new_name} | null` y exige `user_id` en la sesión del socket si no es `null`. **Regla de atomicidad:** las consultas a BD se hacen antes de leer la sala (resolver o crear la liga, cargar sus miembros) y después se aplica el comando de dominio de forma síncrona, como en el resto de `dispatch`.
- La sala guarda `league: {id, name}`, los miembros cargados y el `contest_id` de la ronda actual (uno nuevo en cada "Otra").
- El snapshot de una sala de liga incluye `league.members` (id, nombre, emoji, `locked` si está vinculado a otra cuenta distinta de la del destinatario, `taken` si otro participante de la sala ya lo usa), proyectado por destinatario.
- `Participant.member_id` es opcional: si el participante eligió uno, se usa; si no, al guardar se resuelve por `name_key` o se crea. El candado se valida al unirse y al cambiar de perfil (spec "Jugadores vinculados a una cuenta").
- Sugerencia de liga: `GET /api/leagues/mine` devuelve las ligas del usuario (dueño o vinculado) ordenadas por `last_played_at`; el cliente aplica la regla 0/1/varias de la spec.

### 6. Guardado al revelar
Tras `phase:set results` en una sala de liga, el dominio emite el efecto `SaveContest(contest_id, results, participants)`. La capa realtime lanza una tarea `asyncio` que ejecuta `LeagueService.save_contest()` en una transacción (`async with session.begin()`): upsert de miembros, borrado e inserción de `contest_entries` de ese `contest_id` (idempotente ante re-revelados), `last_played_at` y vínculos `user_id`. Al terminar, aplica por `dispatch` un comando interno `save_status(ok|failed)` y vuelve a emitir el snapshot; si falló, los admins ven "⚠️ Sin guardar" y `league:retry_save`. El servicio recibe solo la salida de `compute_results`: las notas individuales nunca llegan a la capa de persistencia (spec "Privacidad de las notas").

### 7. Acceso privado
- Usuarios con sesión: miembro si es dueño o tiene un `league_members.user_id` en la liga.
- Dispositivos sin sesión: tras guardar, el servidor emite a cada participante `league:grant {league_id, access_key, member_id}`, que el cliente guarda en `localStorage`. `access_key = secrets.token_urlsafe(16)`, única por liga.
- Dependencia `league_access(league_id, user=Depends(optional_user), x_league_key: str | None = Header(None))`: concede si es miembro o si la clave coincide (`secrets.compare_digest`); en otro caso `HTTPException(404)` (spec "Acceso ajeno"). `require_league_owner` para la gestión.
- Al iniciar sesión, el cliente envía sus grants a `POST /api/me/link-devices` y el servidor vincula los `member_id` sin `user_id` (spec "Vincular participaciones del dispositivo").

### 8. Ranking calculado en Python
`leagues/ranking.py`: función pura `compute_league_ranking(entries) -> list[RankingRow]` (oros, platas y bronces por `position` 1/2/3 con empates compartidos, jugados como concursante, media de `final_score`, mejor nota; orden por medallas o por media). La consulta solo carga las `contest_entries` de la liga (pocas filas). Ventajas: mismo resultado en SQLite y Postgres, y tests unitarios directos de cada escenario de `specs/league-ranking`.

### 9. API REST y tipos del frontend
Routers FastAPI con modelos Pydantic de entrada/salida: `GET /api/leagues/mine`, `GET /api/leagues/{id}` (ranking + historial), `GET /api/leagues/{id}/contests/{contest_id}`, `PATCH /api/leagues/{id}`, `PATCH /api/leagues/{id}/members/{member_id}`, `POST /api/leagues/{id}/members/merge`, `DELETE /api/leagues/{id}/contests/{contest_id}`, `POST /api/me/link-devices`. `make gen` exporta también `openapi.json` y genera los tipos REST con `openapi-typescript` en `packages/protocol`; `make gen-check` cubre ambos contratos.

### 10. Frontend
- Inicio: botón "Entrar" (G) / avatar con menú (🏆 Ligas, Salir). "🏆 Ligas" lista ligas de la cuenta + grants del dispositivo.
- Crear: hoja inferior con la regla de la spec (nueva / preseleccionada / lista) + "Nueva" y "Sin liga".
- Perfil en sala de liga: carrusel "¿Quién eres?" de chips emoji+nombre (candado/ocupado deshabilitados) + "Nuevo".
- Resultados: botón "🏆 Liga". Pantalla de liga: medallero con pestañas "Medallas" / "Media", historial y modo ✏️ del dueño.
- Datos REST con TanStack Query (caché e invalidación tras `league:grant`).

### 11. Configuración y secretos
Variables en Render: `DATABASE_URL` (Neon), `SESSION_SECRET`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `PUBLIC_URL`. Ninguna en GitHub ni en el repo. CI y sesiones de Claude: SQLite + `AUTH_TEST_LOGIN=1` (el job de Postgres en CI usa credenciales efímeras del contenedor de servicio, no secretos). Cliente OAuth de Google tipo "Web" con redirect `https://<app>.onrender.com/api/auth/google/callback` y `http://localhost:5173/api/auth/google/callback`; pantalla de consentimiento en modo "Testing" con los amigos como usuarios de prueba, o publicada (scopes básicos sin verificación).

## Risks / Trade-offs

- [Diferencias SQLite ↔ Postgres] → Tipos genéricos, cálculos en Python, migraciones aplicadas en ambos y suite `pg` en CI contra Postgres real.
- [asyncpg con el pooler de Neon (PgBouncer en modo transacción) falla con sentencias preparadas] → Usar el endpoint directo (no pooled) de Neon o `connect_args={"statement_cache_size": 0}`; cubierto en la tarea de puesta en marcha.
- [OAuth dentro de la PWA en iOS] → Prueba en dispositivo real; fallback documentado en la decisión 3.
- [Identidad por nombre ambigua (dos "Dani" distintos)] → Selector "¿Quién eres?", candado para jugadores vinculados y fusión/renombrado por el dueño.
- [Grants en `localStorage` se pierden al borrar datos] → Iniciar sesión conserva las ligas; el dueño siempre conserva el acceso.
- [`access_key` filtrada da acceso de lectura] → Solo lectura y sin emails; aceptable entre amigos. Mejora futura: regenerar la clave.
- [Un `await` de BD intercalado en `dispatch` rompe la atomicidad de la sala] → I/O antes de leer la sala o en tareas aparte que vuelven por `dispatch`; test de concurrencia.
- [Migración rota en despliegue] → El proceso no arranca y Render conserva la versión anterior; migraciones solo aditivas.

## Migration Plan

1. Implementar con SQLite y login de prueba (todo testeable sin cuentas externas).
2. Usuario: crear proyecto en Neon y cliente OAuth en Google Cloud Console (pasos guiados en README); Claude añade las variables en Render (o el usuario, si no hay acceso).
3. Merge → la imagen aplica migraciones al arrancar → verificar `/healthz` y un login real desde el móvil.
4. Rollback: revertir el PR. Las tablas nuevas no afectan a la versión anterior; no hace falta deshacer la migración.

## Open Questions

- Nombre por defecto de una liga nueva ("Liga de <nombre>" con emoji aleatorio) y si la liga tiene emoji editable: detalle de UI que no cambia specs ni tareas.
