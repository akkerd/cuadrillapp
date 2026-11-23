# Spec Delta

## Purpose

Define quién está en una sala y cómo se presenta: perfil con emoji y nombre, rol de concursante o solo votante, participantes manuales sin móvil, y cómo se sale o se saca a alguien de la sala.

## ADDED Requirements

### Requirement: Perfil de participante
Al entrar en una sala, cada participante SHALL elegir un emoji de una lista curada de emojis graciosos (con botón de emoji aleatorio) y un nombre de 1 a 16 caracteres. El sistema MUST recordar en el dispositivo el último emoji y nombre usados para proponerlos la próxima vez.

#### Scenario: Emoji aleatorio
- **WHEN** el visitante pulsa el botón de dado en la pantalla de perfil
- **THEN** el emoji cambia a otro de la lista al azar

#### Scenario: Perfil recordado
- **WHEN** un visitante que ya jugó antes en ese dispositivo entra en otra sala
- **THEN** el emoji y el nombre aparecen precargados y puede entrar con un solo toque

### Requirement: Nombre único en la sala
El nombre MUST ser único dentro de la sala sin distinguir mayúsculas, tildes ni espacios sobrantes. Varios participantes MAY tener el mismo emoji.

#### Scenario: Nombre repetido
- **WHEN** un visitante intenta entrar como "dani" y ya hay un "Dani" en la sala
- **THEN** el sistema rechaza el perfil con el aviso "Nombre en uso"

### Requirement: Rol de participante
Cada participante SHALL tener un rol: **concursante** (recibe puntuaciones y también puntúa) o **solo votante** (puntúa pero no recibe). El rol por defecto es concursante. El participante puede cambiar su propio rol y los admins el de cualquiera, solo mientras la sala está en lobby.

#### Scenario: Cambio de rol en lobby
- **WHEN** un participante cambia su rol a solo votante durante el lobby
- **THEN** deja de aparecer como concursante para todos

#### Scenario: Rol bloqueado durante la votación
- **WHEN** un participante intenta cambiar su rol con la votación abierta
- **THEN** el sistema no permite el cambio

### Requirement: Unirse con la votación en curso
El sistema SHALL permitir unirse a una sala en cualquier fase. Quien se une durante la votación elige rol al crear su perfil y puede votar inmediatamente; si entra como concursante, pasa a ser puntuable por los demás.

#### Scenario: Concursante tardío
- **WHEN** alguien se une como concursante con la votación abierta
- **THEN** aparece en la lista de concursantes a puntuar de todos los demás votantes

### Requirement: Participantes manuales
Los admins SHALL poder añadir participantes manuales (personas sin móvil) indicando emoji, nombre y rol. Los participantes manuales cuentan para el límite de la sala, se muestran con un indicador de "sin móvil", nunca se desconectan y nunca pueden ser admins.

#### Scenario: Añadir amigo sin móvil
- **WHEN** un admin añade a "Abuela 👵" como concursante
- **THEN** aparece en la lista con el indicador de sin móvil y los demás pueden puntuarla

### Requirement: Salir de la sala
Un participante SHALL poder salir voluntariamente tras confirmar. Al salir se elimina de la sala junto con las puntuaciones que dio y recibió, salvo que la sala esté en fase de resultados, en cuyo caso los resultados ya revelados no cambian.

#### Scenario: Salir durante la votación
- **WHEN** un concursante sale con la votación abierta
- **THEN** desaparece de la lista y sus puntuaciones dadas y recibidas se descartan

#### Scenario: Salir tras los resultados
- **WHEN** un participante sale estando la sala en resultados
- **THEN** los resultados mostrados a los demás no cambian

### Requirement: Expulsar participantes
Los admins SHALL poder sacar de la sala a cualquier otro participante (incluidos manuales y otros admins) tras confirmar. El expulsado MUST ver un aviso ("Fuera 👋") y volver al inicio; sus puntuaciones se tratan igual que al salir. El expulsado MAY volver a entrar con el código como participante nuevo.

#### Scenario: Expulsión
- **WHEN** un admin saca a un participante conectado
- **THEN** el participante desaparece de la lista de todos y en su móvil aparece el aviso de expulsión

#### Scenario: Un admin no se expulsa a sí mismo
- **WHEN** un admin abre las acciones sobre su propio perfil
- **THEN** no aparece la opción de expulsar
