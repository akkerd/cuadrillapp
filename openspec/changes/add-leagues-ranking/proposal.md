# Proposal

## Why

Los concursos entre el mismo grupo de amigos se repiten (cada fiesta, cada cena), pero con salas efímeras se pierde quién ganó qué. Queremos agrupar los concursos en **ligas** privadas de cada grupo y mostrar un ranking acumulado, sin obligar a los jugadores a crearse cuentas: solo quien crea concursos que se guardan inicia sesión con Google.

Depende de `add-live-voting` (salas, votación y resultados en vivo) y se implementa después de él.

## What Changes

- Inicio de sesión con Google (opcional para jugar, necesario para crear concursos que se guardan).
- **Ligas**: cada concurso guardado pertenece a una liga; quien juega un concurso de una liga pasa a ser miembro de esa liga.
- Al crear una sala con sesión iniciada, el sistema sugiere la liga: si el usuario no ha participado en ninguna, se crea una nueva; si ha participado en una, se preselecciona; si ha participado en varias, se muestran todas. También puede crear una liga nueva o jugar sin guardar.
- Al unirse a una sala de liga, el jugador ve la lista de jugadores de la liga para elegirse ("¿Quién eres?") o crear uno nuevo; la identidad entre concursos se reconoce por nombre normalizado.
- Al revelar resultados en una sala de liga, se guardan las notas finales y posiciones (nunca las notas individuales).
- Ranking de liga con medallero (🥇🥈🥉), media, mejor nota e historial de concursos, visible solo para los miembros de la liga.
- Gestión básica de liga por su dueño: renombrar la liga, renombrar y fusionar jugadores, borrar concursos.
- Base de datos persistente (Postgres gestionado gratuito) para cuentas, ligas y resultados.

## Capabilities

### New Capabilities

- `accounts`: inicio y cierre de sesión con Google, datos mínimos, vinculación de participaciones del dispositivo y acceso de prueba fuera de producción.
- `leagues`: creación de ligas, elección de liga al crear sala, membresía, identidad de jugador por nombre y selección "¿Quién eres?", acceso privado y gestión por el dueño.
- `league-ranking`: guardado de resultados al revelar, cálculo y visualización del ranking de liga e historial de concursos.

### Modified Capabilities

Ninguna. Los comportamientos de `rooms`, `participants` y `results` definidos en `add-live-voting` se mantienen; las salas sin liga siguen funcionando igual.

## Impact

- Servidor: base de datos (esquema, migraciones), autenticación, API REST para ligas, sesión de usuario en la conexión en tiempo real.
- Web: botón de login y avatar, selector de liga al crear, selector "¿Quién eres?" en el perfil, pantallas de ligas y ranking, botón "🏆 Liga" en resultados.
- Infraestructura: proyecto Postgres en Neon (free), cliente OAuth de Google (paso manual del usuario en Google Cloud Console), nuevas variables de entorno en Render. CI y sesiones de Claude en la nube siguen sin necesitar secretos (SQLite en tests, Postgres efímero en CI y login de prueba).
- Datos personales: nombre, email y avatar de Google de quien inicia sesión; nombres y emojis de jugadores dentro de cada liga.

## Out of Scope

- Ranking público entre ligas o ligas abiertas a desconocidos.
- Otros proveedores de login (Apple, email/contraseña).
- Guardar notas individuales o estadísticas por votante.
- Estadísticas por categoría a lo largo de la liga (solo la nota final de cada concurso cuenta para el ranking).
- Invitaciones a ligas sin haber jugado un concurso de ella.
