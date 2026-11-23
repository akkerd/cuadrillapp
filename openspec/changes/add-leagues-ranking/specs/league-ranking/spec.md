# Spec Delta

## Purpose

Guarda el resultado de cada concurso de una liga y muestra a sus miembros un ranking acumulado con medallero, medias e historial de concursos.

## ADDED Requirements

### Requirement: Guardar resultados al revelar
Al revelar los resultados de una sala de liga, el sistema SHALL guardar el concurso (título, fecha, categorías) y, por cada concursante, su nota final, su posición en el ranking general y sus medias por categoría. Si se reabre la votación y se vuelve a revelar, el guardado MUST sustituir al anterior del mismo concurso. Un concurso sin ninguna nota MUST NOT guardarse.

#### Scenario: Guardado al revelar
- **WHEN** un admin revela los resultados en una sala de la liga "Los Primos"
- **THEN** el concurso aparece en el historial de "Los Primos" con su podio

#### Scenario: Revelar dos veces
- **WHEN** un admin reabre la votación, se cambian notas y se vuelve a revelar
- **THEN** la liga tiene un único registro de ese concurso con los resultados nuevos

#### Scenario: Nueva ronda en la misma sala
- **WHEN** un admin empieza "Otra" ronda y la revela
- **THEN** se guarda como un concurso distinto en la misma liga

### Requirement: Fallo al guardar
Si el guardado falla, los resultados SHALL mostrarse igualmente en la sala, y los admins MUST ver un aviso "⚠️ Sin guardar" con un botón "Reintentar".

#### Scenario: Base de datos no disponible
- **WHEN** la base de datos no responde al revelar
- **THEN** todos ven el podio y los admins ven el aviso con "Reintentar"

### Requirement: Privacidad de las notas
El sistema MUST NOT guardar notas individuales ni quién puntuó a quién; solo los agregados por concursante descritos en "Guardar resultados al revelar".

#### Scenario: Datos guardados
- **WHEN** se inspecciona lo guardado de un concurso
- **THEN** solo contiene medias, posiciones y número de notas por concursante

### Requirement: Clasificación de la liga
El ranking de una liga SHALL incluir a cada jugador que haya sido concursante en al menos un concurso guardado, con: medallas de oro, plata y bronce (posiciones 1, 2 y 3 del ranking general de cada concurso, compartidas en empates), concursos jugados como concursante, media de sus notas finales y mejor nota final. Por defecto MUST ordenarse por oros, luego platas, luego bronces y luego media, de mayor a menor.

#### Scenario: Medallero
- **WHEN** Leo ganó 2 concursos y Ana ganó 1 y quedó segunda en 3
- **THEN** Leo aparece por encima de Ana

#### Scenario: Empate compartido
- **WHEN** dos concursantes empatan en primera posición en un concurso
- **THEN** ambos suman un oro

#### Scenario: Solo votante
- **WHEN** un jugador de la liga solo ha participado como votante
- **THEN** no aparece en la clasificación pero puede ver la liga

### Requirement: Orden por media
El usuario SHALL poder cambiar el orden del ranking a "Media" (media de notas finales de mayor a menor) con un toque.

#### Scenario: Cambiar orden
- **WHEN** un miembro toca "Media" en el ranking
- **THEN** la lista se reordena por media de notas finales

### Requirement: Historial de concursos
La liga SHALL mostrar el historial de concursos guardados, del más reciente al más antiguo, con título, fecha y podio, y al tocar uno MUST mostrar su ranking general y por categorías tal como se guardó.

#### Scenario: Consultar un concurso antiguo
- **WHEN** un miembro toca "Halloween 🎃" en el historial
- **THEN** ve el ranking general y por categorías de ese concurso

### Requirement: Acceso desde resultados
En la pantalla de resultados de una sala de liga, el sistema SHALL mostrar el botón "🏆 Liga" que abre el ranking de la liga ya actualizado con el concurso recién guardado.

#### Scenario: Ver la liga tras revelar
- **WHEN** un participante pulsa "🏆 Liga" tras revelar
- **THEN** ve el ranking de la liga incluyendo el concurso que acaba de terminar
