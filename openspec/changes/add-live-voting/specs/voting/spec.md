# Spec Delta

## Purpose

Define cómo se vota en un concurso: categorías, fases, puntuación de 0 a 10 en pasos de 0,25 por concursante y categoría, voto delegado para participantes sin móvil, progreso visible y anonimato de las notas.

## ADDED Requirements

### Requirement: Categorías
Los admins SHALL poder crear, editar, reordenar y borrar categorías mientras la sala esté en lobby. Cada categoría tiene un emoji y un nombre de 1 a 20 caracteres. Una sala admite de 1 a 8 categorías y el sistema MUST ofrecer sugerencias rápidas (por ejemplo 😂 Gracioso, 🎨 Original, 💪 Esfuerzo, 👗 Estilo).

#### Scenario: Añadir categoría sugerida
- **WHEN** un admin toca la sugerencia "😂 Gracioso"
- **THEN** la categoría se añade y todos la ven en el lobby

#### Scenario: Categorías bloqueadas
- **WHEN** un admin intenta añadir o borrar una categoría con la votación abierta
- **THEN** el sistema no lo permite

### Requirement: Fases del concurso
La sala SHALL pasar por las fases lobby → votación → resultados, y solo los admins cambian de fase. Para abrir la votación MUST existir al menos 1 categoría, al menos 1 concursante y al menos 2 participantes.

#### Scenario: Empezar sin categorías
- **WHEN** un admin intenta empezar la votación sin categorías
- **THEN** el botón aparece deshabilitado con un indicador de lo que falta

#### Scenario: Empezar la votación
- **WHEN** un admin pulsa "Votar" cumpliendo los requisitos
- **THEN** todos los dispositivos pasan a la pantalla de votación a la vez

### Requirement: Escala de puntuación
Cada nota SHALL ser un valor entre 0 y 10, ambos incluidos, en pasos de 0,25 (por ejemplo 7,25). El sistema MUST rechazar cualquier otro valor y MUST mostrar las notas con coma decimal.

#### Scenario: Nota válida
- **WHEN** un votante asigna 7,25 a un concursante en una categoría
- **THEN** la nota se guarda y se muestra como "7,25"

#### Scenario: Nota fuera de la escala
- **WHEN** un cliente envía una nota de 7,3 o de 10,25
- **THEN** el sistema la rechaza

### Requirement: Qué puntúa cada votante
Durante la votación, cada participante SHALL poder puntuar a cada concursante en cada categoría, excepto a sí mismo. Puntuar es opcional por concursante y categoría.

#### Scenario: Sin autovoto
- **WHEN** un concursante abre la pantalla de votación
- **THEN** no aparece él mismo entre los concursantes a puntuar, y el sistema rechaza cualquier nota a sí mismo

### Requirement: Control de puntuación táctil
La pantalla de votación SHALL permitir fijar cada nota con un deslizador de 0 a 10 que salta de 0,25 en 0,25 y con botones de −0,25 y +0,25, mostrando el valor en grande junto a un emoji que refleja la nota. Una nota sin asignar se muestra como "—" y se puede borrar.

#### Scenario: Ajuste fino
- **WHEN** un votante tiene 7,00 y pulsa "+"
- **THEN** la nota pasa a 7,25

### Requirement: Guardado y edición de notas
Cada nota SHALL guardarse en el servidor en cuanto se cambia, sin botón de enviar, y el votante MAY modificarla o borrarla mientras la votación siga abierta.

#### Scenario: Cambiar de opinión
- **WHEN** un votante cambia una nota de 6,00 a 8,50 con la votación abierta
- **THEN** solo cuenta la nota de 8,50

#### Scenario: Votación cerrada
- **WHEN** un votante intenta cambiar una nota tras revelar los resultados
- **THEN** el sistema rechaza el cambio

### Requirement: Voto delegado
Los admins SHALL poder puntuar en nombre de cualquier participante manual, seleccionando "Votar como" a ese participante. Las reglas de autovoto se aplican al participante representado.

#### Scenario: Admin vota por la abuela
- **WHEN** un admin elige "Votar como Abuela 👵" y puntúa a otros concursantes
- **THEN** las notas cuentan como de la Abuela, y la Abuela no aparece entre los concursantes a puntuar en ese modo

### Requirement: Progreso y "Listo"
Cada votante SHALL ver cuántas notas lleva del total posible y MAY marcarse como listo, pudiendo seguir editando mientras la votación esté abierta. Todos los participantes MUST ver quién está listo, y los admins además el progreso numérico de cada votante.

#### Scenario: Marcar listo
- **WHEN** un votante pulsa "Listo"
- **THEN** todos ven un check junto a su avatar

#### Scenario: Progreso para admins
- **WHEN** un admin mira la lista durante la votación
- **THEN** ve junto a cada votante cuántas notas lleva, por ejemplo "7/12"

### Requirement: Anonimato de las notas
Ningún participante, incluidos los admins, SHALL poder ver las notas individuales que ha dado otro participante. Solo se ven las propias y, para los admins, las emitidas en nombre de participantes manuales.

#### Scenario: Notas ajenas ocultas
- **WHEN** un admin consulta el estado de la sala durante la votación
- **THEN** no recibe las notas que han puesto otros participantes con móvil
