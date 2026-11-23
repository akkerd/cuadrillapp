# Spec Delta

## Purpose

Permite crear salas de concurso en tiempo real identificadas por un código corto, unirse a ellas desde el móvil y mantener la conexión aunque el móvil se bloquee o cambie de app.

## ADDED Requirements

### Requirement: Crear sala
El sistema SHALL permitir a cualquier visitante crear una sala nueva. Quien la crea entra como primer participante y como admin, y la sala empieza en la fase de lobby.

#### Scenario: Creación correcta
- **WHEN** un visitante pulsa "Crear" y completa su perfil
- **THEN** el sistema crea una sala en fase lobby, le asigna un código único y lo muestra como admin dentro de ella

### Requirement: Código de sala
Cada sala SHALL tener un código de 5 caracteres en mayúsculas, sin caracteres ambiguos (0, O, 1, I, L), único entre las salas activas. La entrada del código MUST ignorar mayúsculas/minúsculas y espacios.

#### Scenario: Código introducido en minúsculas
- **WHEN** un visitante escribe " abc23 " en el campo de código y la sala ABC23 existe
- **THEN** el sistema lo une a la sala ABC23

#### Scenario: Código inexistente
- **WHEN** un visitante introduce un código que no corresponde a ninguna sala activa
- **THEN** el sistema muestra un error corto ("No existe") y no lo une a ninguna sala

### Requirement: Compartir sala
Dentro de una sala, el sistema SHALL mostrar el código, un enlace directo y un código QR que abre ese enlace, además de un botón para compartir con las apps del móvil cuando el dispositivo lo soporte.

#### Scenario: Unirse por enlace
- **WHEN** un visitante abre el enlace directo de una sala activa
- **THEN** el sistema le lleva directamente a crear su perfil para esa sala, sin pedir el código

### Requirement: Título de la sala
La sala SHALL tener un título corto (1-30 caracteres, por defecto "Concurso") visible para todos y editable solo por admins.

#### Scenario: Admin cambia el título
- **WHEN** un admin cambia el título a "Halloween 🎃"
- **THEN** todos los participantes ven el nuevo título al instante

### Requirement: Sincronización en tiempo real
Todo cambio en el estado de la sala SHALL reflejarse en los dispositivos de todos los participantes conectados en menos de 1 segundo en condiciones normales de red, sin recargar la página.

#### Scenario: Llega un participante nuevo
- **WHEN** un participante se une a la sala
- **THEN** el resto de participantes lo ve aparecer en la lista sin hacer nada

### Requirement: Reconexión automática
Un participante que pierde la conexión (red, bloqueo de pantalla, cambio de app o recarga) SHALL conservar su plaza, su perfil, sus permisos y sus puntuaciones, y el sistema MUST reincorporarlo automáticamente a la misma plaza al recuperar la conexión desde el mismo dispositivo y navegador.

#### Scenario: Recarga de la página
- **WHEN** un participante recarga la app en mitad de la votación
- **THEN** vuelve a la sala con su mismo perfil y sus puntuaciones intactas, sin volver a introducir código ni nombre

#### Scenario: Estado desconectado visible
- **WHEN** un participante pierde la conexión
- **THEN** el resto lo ve atenuado como desconectado, pero sigue en la lista

### Requirement: Fin de vida de la sala
El sistema SHALL eliminar una sala cuando lleve 30 minutos sin ningún participante conectado. Un dispositivo que intente volver a una sala eliminada MUST ver un aviso de sala cerrada y la opción de volver al inicio.

#### Scenario: Sala abandonada
- **WHEN** pasan 30 minutos sin participantes conectados en una sala
- **THEN** la sala deja de existir y su código deja de ser válido

#### Scenario: Reinicio del servidor
- **WHEN** el servidor se reinicia (por ejemplo, por un despliegue) y un participante intenta reconectar
- **THEN** ve el aviso de sala cerrada y un botón para volver al inicio

### Requirement: Límites de sala
El sistema SHALL limitar cada sala a 30 participantes (incluidos los manuales) y rechazar la unión cuando la sala esté llena, con un mensaje corto ("Llena").

#### Scenario: Sala llena
- **WHEN** un visitante intenta unirse a una sala con 30 participantes
- **THEN** el sistema rechaza la unión y muestra "Llena"

### Requirement: Protección frente a abuso
El sistema MUST validar todos los datos que envían los clientes, rechazar los inválidos sin alterar la sala y limitar la frecuencia de acciones por conexión y la creación de salas por origen.

#### Scenario: Datos inválidos
- **WHEN** un cliente envía una acción con datos fuera de formato (por ejemplo, una nota de 11)
- **THEN** el sistema la rechaza con un error y el estado de la sala no cambia

#### Scenario: Ráfaga de acciones
- **WHEN** una conexión envía acciones por encima del límite de frecuencia
- **THEN** el sistema rechaza las acciones sobrantes sin afectar al resto de participantes
