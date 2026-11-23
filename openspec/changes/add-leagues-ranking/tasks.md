# Tasks

## 1. Base de datos

- [ ] 1.1 Añadir SQLAlchemy 2.0 async (`aiosqlite`, `asyncpg`), `db/engine.py` con selección por `DATABASE_URL` (SQLite por defecto) y modelos ORM de `users`, `leagues`, `league_members`, `contests`, `contest_entries`; verificar con un test que crea y lee una liga en SQLite
- [ ] 1.2 Alembic con `env.py` asíncrono y `render_as_batch=True`, primera migración autogenerada, fixture de tests que aplica migraciones (no `create_all`) y `CMD` de la imagen con `alembic upgrade head && uvicorn …`; verificar que un arranque con BD vacía crea las tablas y que una migración rota hace fallar los tests
- [ ] 1.3 Marcador `@pytest.mark.pg` y job de CI con contenedor de servicio `postgres` que ejecuta esa suite con `DATABASE_URL` efímera; verificar que el job pasa en un PR de prueba

## 2. Cuentas

- [ ] 2.1 `auth/cookies.py` (firmar/leer `cq_session` con itsdangerous, 30 días, `HttpOnly`/`Secure`/`SameSite=Lax`), dependencias `optional_user`/`require_user` y `GET /api/me`; verificar con tests de cookie válida, manipulada y caducada
- [ ] 2.2 Authlib con Google (descubrimiento OIDC, `SessionMiddleware` solo para el `state`), rutas login/callback/logout, upsert de `users` con datos mínimos y redirección con `login=cancelled`; verificar con tests del callback simulando la respuesta de Google (sin red) y de "Datos mínimos"
- [ ] 2.3 Router de login de prueba solo con `AUTH_TEST_LOGIN=1` fuera de producción y validador de `Settings` que impide arrancar en producción con la variable activa; verificar con tests del escenario "Producción"
- [ ] 2.4 `user_id` en la sesión de Socket.IO leído de la cookie en `connect`, y reconexión del socket al entrar/salir en la web; verificar con test de integración con `socketio.AsyncClient` y cookie de prueba
- [ ] 2.5 UI: botón "Entrar", avatar con menú (🏆 Ligas, Salir), aviso de login cancelado; verificar con e2e usando el login de prueba
- [ ] 2.6 `POST /api/me/link-devices` y envío automático de grants tras iniciar sesión; verificar con test del escenario "Jugué como invitado y luego inicio sesión"

## 3. Ligas en la sala en vivo

- [ ] 3.1 `room:create` con `league: {id} | {new_name} | null` (sesión obligatoria si hay liga, I/O de BD antes de aplicar el comando), `contest_id` por ronda y nombre de liga en el snapshot; verificar con tests de "Crear sala con o sin liga" y "Liga visible en la sala"
- [ ] 3.2 `GET /api/leagues/mine` ordenado por `last_played_at` y hoja de creación con la regla 0/1/varias + "Nueva" y "Sin liga"; verificar con e2e de los tres escenarios de "Sugerencia de liga al crear"
- [ ] 3.3 Miembros de la liga en el snapshot proyectado (`locked`, `taken`), selector "¿Quién eres?" con preselección por cuenta o grant, opción "Nuevo" con resolución por `name_key` y candado; verificar con tests y e2e de "Elegir jugador al unirse", "Identidad por nombre" y "Jugadores vinculados a una cuenta"

## 4. Guardado y ranking

- [ ] 4.1 Efecto `SaveContest` y `LeagueService.save_contest` transaccional e idempotente por `contest_id` (upsert de miembros, entries, `last_played_at`, vínculos) sin guardar concursos sin notas; verificar con tests de "Guardar resultados al revelar" (revelar dos veces, nueva ronda) y "Privacidad de las notas"
- [ ] 4.2 Comando interno `save_status`, aviso "⚠️ Sin guardar" para admins y `league:retry_save`; verificar con test que simula fallo de BD
- [ ] 4.3 Evento `league:grant {league_id, access_key, member_id}` a cada participante tras guardar y almacenamiento en el dispositivo; verificar con test de integración de "Membresía de liga"
- [ ] 4.4 `compute_league_ranking` puro (oros, platas, bronces con empates compartidos, jugados, media, mejor nota; excluye solo votantes; orden por medallas o por media); verificar con tests unitarios de "Clasificación de la liga" y "Orden por media"

## 5. API y acceso privado

- [ ] 5.1 Routers `GET /api/leagues/{id}` y `/contests/{contest_id}` con la dependencia `league_access` (miembro o `X-League-Key`, 404 en otro caso) y export de OpenAPI → tipos TS en `make gen`; verificar con tests de "Liga privada" y `make gen-check`
- [ ] 5.2 Gestión del dueño (`require_league_owner`): renombrar liga y jugador, fusionar (rechazo con cuentas distintas) y borrar concurso (dueño o anfitrión); verificar con tests de "Gestión de la liga" y "Borrar un concurso guardado"

## 6. Pantallas de liga

- [ ] 6.1 Lista "🏆 Ligas" (cuenta + grants del dispositivo) y pantalla de liga con pestañas "Medallas"/"Media" e historial; verificar con e2e de "Mis ligas" e "Historial de concursos"
- [ ] 6.2 Botón "🏆 Liga" en resultados con datos ya actualizados (invalidación de caché tras `league:grant`); verificar con e2e de "Ver la liga tras revelar"
- [ ] 6.3 Modo ✏️ del dueño (renombrar, fusionar, borrar con confirmación); verificar con e2e de "Fusionar duplicados"

## 7. Infraestructura y puesta en marcha

- [ ] 7.1 Documentar en README los pasos manuales: proyecto en Neon (endpoint directo o `statement_cache_size=0`), cliente OAuth de Google (orígenes, redirect, usuarios de prueba) y variables de Render; verificar que siguiendo el README se obtiene cada valor
- [ ] 7.2 Configurar variables en Render, desplegar y comprobar migraciones aplicadas, `/healthz` con el nuevo SHA y login real con Google desde Android e iPhone (PWA instalada); registrar el resultado del caso iOS
- [ ] 7.3 Confirmar que CI y una sesión de Claude en la nube pasan `make verify` sin secretos (SQLite + login de prueba); verificar con un PR de prueba

## 8. Integración de extremo a extremo

- [ ] 8.1 E2E de dos concursos seguidos en la misma liga (un invitado que repite eligiéndose de la lista, un empate) y comprobación del medallero y medias resultantes; verificar en verde dentro de `make verify`

## Workflow follow-up

- Jugar una liga real de al menos dos concursos con amigos antes de archivar.
- Comprobar la implementación contra los specs con el workflow `verify` de OpenSpec.
- Archivar con `openspec archive add-leagues-ranking`.
