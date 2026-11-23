# Spec Delta

## Purpose

Agrupa los concursos de un mismo grupo de amigos en ligas privadas, reconoce a cada jugador entre concursos por su nombre y decide quién puede ver y gestionar cada liga.

## ADDED Requirements

### Requirement: Crear sala con o sin liga
Al pulsar "Crear", un usuario con sesión iniciada SHALL pasar por el paso de elegir liga. Un visitante sin sesión MUST poder elegir entre "Entrar" (iniciar sesión para guardar en liga) y "Sin guardar" (sala sin liga, como en `add-live-voting`).

#### Scenario: Sin sesión
- **WHEN** un visitante sin sesión pulsa "Crear"
- **THEN** ve las opciones "Entrar" y "Sin guardar"

#### Scenario: Sala rápida
- **WHEN** el visitante elige "Sin guardar"
- **THEN** se crea una sala sin liga cuyos resultados no se guardan

### Requirement: Sugerencia de liga al crear
El paso de liga SHALL basarse en las ligas en las que el usuario ha participado (como jugador o dueño): con ninguna, propone crear una liga nueva con nombre editable; con una, la preselecciona como opción principal; con varias, las muestra todas ordenadas por uso más reciente. Como opciones secundarias MUST ofrecer "Nueva" y "Sin liga".

#### Scenario: Primera vez
- **WHEN** un usuario sin ligas crea su primera sala
- **THEN** se le propone una liga nueva con un nombre por defecto editable y, al confirmar, la sala queda asociada a esa liga

#### Scenario: Una sola liga
- **WHEN** un usuario que solo ha participado en "Los Primos" pulsa "Crear"
- **THEN** "Los Primos" aparece preseleccionada y puede crear la sala con un toque

#### Scenario: Varias ligas
- **WHEN** un usuario que ha participado en tres ligas pulsa "Crear"
- **THEN** ve las tres, la más reciente primero, y elige una

### Requirement: Liga visible en la sala
Una sala asociada a una liga SHALL mostrar el nombre de la liga a todos los participantes durante toda la partida.

#### Scenario: Unirse a sala de liga
- **WHEN** alguien entra en una sala de la liga "Los Primos"
- **THEN** ve "🏆 Los Primos" en la cabecera de la sala

### Requirement: Elegir jugador al unirse
Al crear su perfil en una sala de liga, el participante SHALL ver los jugadores existentes de la liga (emoji + nombre) bajo "¿Quién eres?" para elegirse con un toque, o la opción "Nuevo" para escribir un nombre. Elegir un jugador precarga su nombre y emoji, que se pueden cambiar.

#### Scenario: Me elijo de la lista
- **WHEN** Lucas, que jugó antes en la liga, se une y toca "🐸 Lucas" en la lista
- **THEN** entra con ese nombre y emoji y sus resultados de este concurso se suman a los de "Lucas" en la liga

#### Scenario: Preselección
- **WHEN** un dispositivo o una cuenta ya usó un jugador de esa liga
- **THEN** ese jugador aparece preseleccionado

#### Scenario: Jugador ocupado
- **WHEN** un jugador de la liga ya está en uso por otro participante de la sala
- **THEN** aparece deshabilitado en la lista

### Requirement: Identidad por nombre
Dentro de una liga, dos participaciones con el mismo nombre normalizado (sin distinguir mayúsculas, tildes ni espacios sobrantes) SHALL contar como el mismo jugador. Un nombre nuevo que no coincide con ninguno crea un jugador nuevo en la liga al guardarse los resultados.

#### Scenario: Escribe su nombre en vez de elegirlo
- **WHEN** alguien elige "Nuevo" y escribe "lucas " en una liga donde existe "Lucas"
- **THEN** se le asigna el jugador "Lucas" de la liga

### Requirement: Jugadores vinculados a una cuenta
Un jugador de liga vinculado a una cuenta de Google SHALL poder elegirse solo desde un dispositivo con esa cuenta, o por un admin al añadirlo como participante manual; a los demás les aparece con candado. Al elegir un jugador sin vincular con la sesión iniciada, el sistema MUST vincularlo a esa cuenta.

#### Scenario: Jugador con candado
- **WHEN** un invitado intenta elegir o escribir el nombre de un jugador vinculado a otra cuenta
- **THEN** el sistema no se lo permite y muestra "🔒 En uso"

#### Scenario: Vinculación al jugar
- **WHEN** un usuario con sesión elige el jugador sin vincular "Sara"
- **THEN** "Sara" queda vinculada a su cuenta

### Requirement: Membresía de liga
Todo participante de una sala de liga, incluidos los participantes manuales y los solo votantes, SHALL quedar como jugador de la liga cuando se guarden los resultados del concurso, y su dispositivo MUST recordar el acceso a esa liga.

#### Scenario: Invitado tras el concurso
- **WHEN** se guardan los resultados de un concurso en el que participó un invitado
- **THEN** ese invitado puede abrir el ranking de la liga desde "🏆 Ligas" en su dispositivo

### Requirement: Liga privada
Una liga SHALL ser visible solo para sus miembros: usuarios con sesión vinculados a un jugador o dueños de la liga, y dispositivos que hayan participado en alguno de sus concursos. El sistema MUST NOT listar ligas públicamente y MUST responder a cualquier otro acceso como si la liga no existiera.

#### Scenario: Acceso ajeno
- **WHEN** alguien que no es miembro intenta abrir la dirección de una liga
- **THEN** ve "No existe"

#### Scenario: Mis ligas
- **WHEN** un miembro abre "🏆 Ligas"
- **THEN** ve solo las ligas de las que es miembro

### Requirement: Gestión de la liga
El dueño de una liga (quien la creó) SHALL poder renombrarla, renombrar jugadores y fusionar dos jugadores en uno. Al fusionar, todos los resultados pasan al jugador que se conserva; la fusión MUST rechazarse si ambos están vinculados a cuentas distintas.

#### Scenario: Fusionar duplicados
- **WHEN** el dueño fusiona "Dani" con "Daniel" conservando "Daniel"
- **THEN** "Dani" desaparece y sus concursos cuentan para "Daniel" en el ranking

#### Scenario: Fusión imposible
- **WHEN** el dueño intenta fusionar dos jugadores vinculados a cuentas distintas
- **THEN** el sistema rechaza la fusión

### Requirement: Borrar un concurso guardado
El dueño de la liga y quien creó el concurso SHALL poder borrar un concurso guardado de la liga, tras confirmar; el ranking se recalcula sin él.

#### Scenario: Concurso de prueba
- **WHEN** el dueño borra un concurso de prueba del historial
- **THEN** desaparece del historial y deja de contar en el ranking
