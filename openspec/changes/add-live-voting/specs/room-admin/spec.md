# Spec Delta

## Purpose

Define quién controla una sala: permisos de admin, cómo se conceden y retiran, y cómo pasa el control automáticamente para que una sala nunca se quede sin nadie que la gestione.

## ADDED Requirements

### Requirement: Permisos de admin
Solo los admins SHALL poder: editar el título, gestionar categorías, añadir participantes manuales, expulsar, cambiar roles ajenos, conceder o quitar admin, votar en nombre de participantes manuales y cambiar la fase del concurso. El sistema MUST rechazar estas acciones si las envía alguien sin permisos.

#### Scenario: Acción sin permiso
- **WHEN** un participante que no es admin intenta iniciar la votación
- **THEN** el sistema rechaza la acción y la sala no cambia

#### Scenario: Controles ocultos
- **WHEN** un participante sin permisos ve el lobby
- **THEN** no ve los controles de admin

### Requirement: Varios admins
Una sala SHALL admitir varios admins a la vez. Un admin puede conceder admin a cualquier participante con móvil y quitárselo a cualquier otro admin. Cada admin se identifica con una corona visible para todos.

#### Scenario: Conceder admin
- **WHEN** un admin concede admin a otro participante con móvil
- **THEN** ese participante muestra la corona y ve los controles de admin

#### Scenario: Participante manual
- **WHEN** un admin abre las acciones sobre un participante manual
- **THEN** no aparece la opción de hacerlo admin

### Requirement: Siempre al menos un admin
El sistema MUST impedir que un admin se quite a sí mismo el permiso si es el único admin de la sala.

#### Scenario: Último admin
- **WHEN** el único admin intenta quitarse el permiso
- **THEN** el sistema lo impide

### Requirement: Sucesión de admin
Cuando una sala se quede sin admins presentes, el sistema SHALL nombrar admin automáticamente al participante con móvil conectado que lleve más tiempo en la sala. Un admin deja de estar presente al salir, al ser expulsado o tras 60 segundos desconectado.

#### Scenario: El admin sale
- **WHEN** el único admin sale de la sala
- **THEN** el participante conectado que se unió antes pasa a ser admin y todos lo ven con la corona

#### Scenario: El admin pierde la conexión un momento
- **WHEN** el único admin se desconecta y vuelve antes de 60 segundos
- **THEN** sigue siendo el único admin y no se nombra a nadie más

#### Scenario: El admin tarda en volver
- **WHEN** el único admin lleva más de 60 segundos desconectado
- **THEN** se nombra admin al siguiente participante por orden de llegada; cuando el admin original vuelve, conserva también su permiso

#### Scenario: Nadie con móvil conectado
- **WHEN** no queda ningún participante con móvil conectado
- **THEN** no se nombra a nadie y se aplica la sucesión en cuanto alguien vuelva a conectarse
