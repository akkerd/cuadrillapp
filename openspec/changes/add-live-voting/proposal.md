# Proposal

## Why

Queremos una app móvil, rápida y divertida para montar concursos entre amigos (disfraces, cocina, outfits…) en los que todos puntúan desde su móvil, sin instalar nada de una tienda y sin cuentas. A la vez, el proyecto sirve para probar un sistema de desarrollo en el que se piden cambios desde el móvil a Claude y este los implementa, prueba y despliega de forma segura.

## What Changes

- Nueva PWA instalable a pantalla completa con un tono visual colorido y desenfadado (estilo juego de fiesta), botones con icono + palabra corta.
- Salas en tiempo real identificadas por un código corto, con enlace y QR para unirse.
- Perfil por sala: emoji gracioso + nombre de usuario; rol de **concursante** (recibe puntuaciones) o **solo votante**.
- Administración de sala: el creador es admin; los admins pueden añadir participantes manuales (sin móvil), sacar gente, votar en nombre de los participantes manuales, cambiar roles y dar o quitar permisos de admin. Si no queda ningún admin, pasa al siguiente participante por orden de llegada.
- Categorías definidas por los admins (emoji + nombre corto).
- Votación: cada votante puntúa a cada concursante (menos a sí mismo) en cada categoría con una nota de 0 a 10 en pasos de 0,25.
- Resultados revelados por un admin: ranking por categoría y ranking general con podio animado.
- Pipeline de entrega: CI en GitHub Actions, despliegue automático en Render solo tras checks verdes, health check con versión y flujo documentado para que Claude haga cambios desde sesiones en la nube (móvil) vía PR.

## Capabilities

### New Capabilities

- `rooms`: creación de salas, código, enlace/QR, unión, reconexión, título, ciclo de vida y límites.
- `participants`: perfil (emoji + nombre), roles concursante/votante, participantes manuales, salir y ser expulsado.
- `room-admin`: permisos de admin, conceder y quitar admin, sucesión automática.
- `voting`: categorías, fases del concurso, puntuación 0-10 en pasos de 0,25, voto delegado, progreso y anonimato.
- `results`: cálculo de medias, rankings por categoría y general, empates, revelado y nuevas rondas.
- `app-shell`: experiencia PWA (instalación, pantalla completa, pantalla siempre encendida, actualización), idioma y tono de la UI.
- `delivery-pipeline`: checks de CI, protección de main, despliegue automático y verificable, rollback y flujo de cambios con Claude.

### Modified Capabilities

Ninguna (proyecto nuevo).

## Impact

- Repositorio nuevo `cuadrillapp` (monorepo): `apps/server` (Python 3.14 + FastAPI + Socket.IO), `apps/web` (React), `packages/protocol` (tipos TypeScript generados desde el backend), `e2e`.
- Dependencias externas: GitHub (repo, Actions), Render (plan gratuito, un servicio web).
- Sin base de datos ni datos personales en este change: todo el estado de las salas vive en memoria del servidor.
- Pasos manuales del usuario: `gh auth login`, crear cuenta en Render y conectar el Blueprint, instalar la app de Claude/GitHub en el repo.

## Out of Scope

- Ligas, cuentas de Google, persistencia y ranking global (change `add-leagues-ranking`).
- Chat, sonidos, temas personalizables y multi-idioma.
- Escalado horizontal: se ejecuta un único proceso; el camino para escalar queda definido en `design.md` pero no se implementa.
- Juego offline: la app requiere conexión durante la partida.
