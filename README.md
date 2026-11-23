# Cuadrillapp 🦄🌮🐸

Concursos entre amigos desde el móvil: creas una sala, los demás entran con un código (o QR), cada uno
elige emoji y nombre, y todos puntúan a todos de 0 a 10 (en pasos de 0,25) en las categorías que
decida el admin. Al final, podio con confeti.

- **PWA** instalable a pantalla completa, sin cuentas.
- **Tiempo real** con Socket.IO; reconexión automática si el móvil se bloquea.
- **Backend** Python 3.14 + FastAPI + python-socketio. **Frontend** React 19 + Vite + Tailwind.
- Specs y diseño en [`openspec/`](openspec/) (OpenSpec).

## Desarrollo

Requisitos: [uv](https://docs.astral.sh/uv/), Node 26 y pnpm 12.

```bash
make setup    # dependencias + Chromium para e2e
make dev      # http://localhost:5173 (backend en :8000)
make verify   # lo mismo que CI
```

`make` sin argumentos lista todos los comandos. Las reglas de trabajo para agentes están en
[`CLAUDE.md`](CLAUDE.md).

## Arquitectura

```
Móvil (PWA React) ⇄ Socket.IO ⇄ Uvicorn (1 worker) ─ FastAPI (/healthz, estáticos)
                                                   └ python-socketio → dominio puro → salas en memoria
```

- El servidor es la autoridad: el cliente envía comandos con ack y recibe snapshots de la sala
  proyectados para él (nadie recibe las notas de otros).
- El contrato vive en modelos Pydantic; `make gen` genera los tipos TypeScript de
  `packages/protocol` y CI comprueba que están al día.
- Una sola imagen Docker sirve todo desde el mismo origen.

Detalles y decisiones: [`openspec/changes/add-live-voting/design.md`](openspec/changes/add-live-voting/design.md).

## Despliegue (Render, plan gratuito)

1. En Render: **New → Blueprint** y elige este repo. `render.yaml` crea el servicio Docker.
2. Render despliega `main` solo cuando los checks de GitHub pasan, y no cambia el tráfico a la versión
   nueva hasta que `/healthz` responde.
3. Comprueba la versión: `curl https://<app>.onrender.com/healthz` → `{"status":"ok","version":"<sha>"}`.

El plan gratuito duerme el servicio tras 15 min sin tráfico: la primera visita tarda ~1 min (la app
muestra "Despertando…").

### Vuelta atrás

- **Revert por PR:** `git revert <sha>` en una rama, PR, CI verde, merge → se despliega la versión anterior.
- **Rollback inmediato:** dashboard de Render → el servicio → _Events_ → _Rollback_ en un deploy previo.

Un despliegue cierra las salas abiertas (viven en memoria): no mergees durante una partida.

## Cambios desde el móvil con Claude

1. App de Claude → **Code** → repo `cuadrillapp` → describe el cambio.
2. La sesión en la nube se prepara sola (`.claude/settings.json` → `scripts/cloud-setup.sh`), implementa
   en una rama, pasa `make verify` y abre un PR.
3. Revisa y mergea el PR desde la app de GitHub; Render despliega tras los checks.

## Prueba en dispositivos reales

Antes de usarla en una fiesta, comprueba en un Android y un iPhone:

- [ ] Instalar (Android: botón "Instalar"; iPhone: Compartir → Añadir a inicio) y abrir desde el icono:
      sin barra del navegador.
- [ ] Nada tapado por el notch ni la barra de gestos.
- [ ] La pantalla no se apaga durante la votación.
- [ ] Bloquear el móvil 30 s y volver: sigues en la sala con tus notas.
