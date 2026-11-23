# Spec Delta

## Purpose

Permite iniciar sesión con una cuenta de Google para crear concursos que se guardan en ligas y para ver las ligas propias desde cualquier dispositivo, sin que jugar requiera cuenta.

## ADDED Requirements

### Requirement: Inicio de sesión con Google
El sistema SHALL permitir iniciar sesión con una cuenta de Google desde la pantalla de inicio con un botón "Entrar". Tras iniciar sesión, la app MUST mostrar el avatar del usuario en lugar del botón y mantener la sesión al cerrar y reabrir la app.

#### Scenario: Login correcto
- **WHEN** un visitante pulsa "Entrar" y autoriza con su cuenta de Google
- **THEN** vuelve a la app con su avatar visible en la pantalla de inicio

#### Scenario: Sesión persistente
- **WHEN** un usuario con sesión iniciada cierra la app y la vuelve a abrir días después
- **THEN** sigue con la sesión iniciada

#### Scenario: Login cancelado
- **WHEN** el visitante cancela la autorización en Google
- **THEN** vuelve a la pantalla de inicio sin sesión y con un aviso corto

### Requirement: Cerrar sesión
Un usuario con sesión iniciada SHALL poder cerrarla desde el menú de su avatar. Cerrar sesión MUST NOT afectar a las salas en las que esté jugando.

#### Scenario: Cerrar sesión
- **WHEN** el usuario pulsa "Salir" en el menú del avatar
- **THEN** la app vuelve a mostrar el botón "Entrar"

### Requirement: Jugar sin cuenta
Unirse a una sala, votar y ver resultados SHALL seguir funcionando sin iniciar sesión, tanto en salas sin liga como en salas de liga.

#### Scenario: Invitado en sala de liga
- **WHEN** un visitante sin sesión se une con el código a una sala de liga
- **THEN** puede elegir su jugador, votar y ver resultados sin que se le pida iniciar sesión

### Requirement: Datos mínimos
De la cuenta de Google el sistema MUST guardar solo el identificador de la cuenta, el nombre, el email y la URL del avatar, y MUST NOT mostrar el email a otros usuarios.

#### Scenario: Email privado
- **WHEN** otro miembro de la liga consulta el ranking
- **THEN** no ve el email de ningún usuario

### Requirement: Vincular participaciones del dispositivo
Al iniciar sesión, el sistema SHALL vincular a la cuenta los jugadores de liga que ese dispositivo haya usado en concursos anteriores, siempre que esos jugadores no estén ya vinculados a otra cuenta.

#### Scenario: Jugué como invitado y luego inicio sesión
- **WHEN** alguien que jugó como "Diego" en la liga "Los Primos" desde su móvil sin sesión inicia sesión después en ese móvil
- **THEN** la liga "Los Primos" aparece entre sus ligas y "Diego" queda vinculado a su cuenta

### Requirement: Acceso de prueba fuera de producción
El sistema SHALL ofrecer un inicio de sesión de prueba sin Google, solo cuando se ejecute fuera de producción con el acceso de prueba activado explícitamente, para que los tests automáticos y las sesiones de desarrollo no necesiten credenciales reales. En producción MUST estar siempre desactivado.

#### Scenario: Producción
- **WHEN** el servicio arranca en producción con el acceso de prueba activado por error
- **THEN** el servicio se niega a arrancar y registra el motivo
