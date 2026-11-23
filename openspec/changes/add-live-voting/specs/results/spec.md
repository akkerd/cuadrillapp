# Spec Delta

## Purpose

Define cómo se calculan y se muestran los resultados de un concurso: media por categoría, nota final, rankings con empates, revelado con podio y cómo seguir jugando después.

## ADDED Requirements

### Requirement: Media por categoría
La nota de un concursante en una categoría SHALL ser la media aritmética de las notas recibidas en esa categoría, junto con el número de notas recibidas. Si no recibió ninguna, su nota en esa categoría queda vacía.

#### Scenario: Media simple
- **WHEN** un concursante recibe 6,00, 7,50 y 9,00 en "Gracioso"
- **THEN** su media en "Gracioso" es 7,50 con 3 notas

### Requirement: Nota final
La nota final de un concursante SHALL ser la media de sus medias por categoría, contando solo las categorías en las que recibió al menos una nota. Un concursante sin ninguna nota queda "Sin votos" al final del ranking general.

#### Scenario: Nota final con dos categorías
- **WHEN** un concursante tiene 7,50 en "Gracioso" y 8,50 en "Estilo"
- **THEN** su nota final es 8,00

#### Scenario: Concursante sin votos
- **WHEN** un concursante no recibió ninguna nota
- **THEN** aparece al final del ranking general marcado como "Sin votos"

### Requirement: Rankings y empates
El sistema SHALL ordenar a los concursantes de mayor a menor nota en un ranking general y en un ranking por cada categoría. Las comparaciones MUST hacerse sobre el valor exacto, y los empates comparten posición (por ejemplo 1, 1, 3). Las notas se muestran redondeadas a 2 decimales.

#### Scenario: Empate en primera posición
- **WHEN** dos concursantes tienen exactamente la misma nota final más alta
- **THEN** ambos aparecen en la posición 1 y el siguiente en la posición 3

### Requirement: Revelar resultados
Un admin SHALL cerrar la votación y revelar los resultados con un único botón. Al revelar, los resultados se calculan y se congelan, y todos los dispositivos muestran a la vez un podio animado que descubre el tercer, segundo y primer puesto, con confeti para el ganador.

#### Scenario: Revelado sincronizado
- **WHEN** un admin pulsa "Revelar"
- **THEN** todos los participantes ven la animación del podio al mismo tiempo y nadie puede cambiar notas

#### Scenario: Movimiento reducido
- **WHEN** el dispositivo tiene activada la preferencia de reducir movimiento
- **THEN** el podio se muestra sin animaciones ni confeti

### Requirement: Consulta de resultados
En la fase de resultados, cada participante SHALL poder ver el ranking general y el de cada categoría, con la media y el número de notas de cada concursante, sin ver notas individuales.

#### Scenario: Pestaña de categoría
- **WHEN** un participante toca la pestaña "😂 Gracioso" en resultados
- **THEN** ve el ranking de esa categoría con medias y número de notas

### Requirement: Reabrir y nueva ronda
Desde resultados, un admin SHALL poder reabrir la votación conservando todas las notas, o empezar una nueva ronda que vuelve al lobby conservando participantes y categorías y borrando todas las notas.

#### Scenario: Reabrir
- **WHEN** un admin pulsa "Reabrir"
- **THEN** la sala vuelve a votación con las notas anteriores intactas y editables

#### Scenario: Nueva ronda
- **WHEN** un admin pulsa "Otra" y confirma
- **THEN** la sala vuelve al lobby con los mismos participantes y categorías y sin notas
