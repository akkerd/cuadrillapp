# Spec Delta

## Purpose

Define la experiencia de la app en el móvil: PWA instalable a pantalla completa, tono visual festivo con iconos y palabras cortas, pantalla siempre encendida durante la partida y comportamiento ante conexión lenta o nuevas versiones.

## ADDED Requirements

### Requirement: App instalable
La app SHALL ser instalable en la pantalla de inicio de Android e iOS con nombre, icono y color propios, y al abrirse desde el icono MUST ocupar toda la pantalla sin barra del navegador (pantalla completa donde el sistema lo permita y modo standalone en el resto).

#### Scenario: Abrir desde el icono
- **WHEN** el usuario abre la app instalada desde la pantalla de inicio
- **THEN** la app se muestra sin la barra de direcciones del navegador

### Requirement: Ayuda de instalación
Si la app se usa desde el navegador sin instalar, el sistema SHALL ofrecer un botón "Instalar": en Android lanza la instalación nativa y en iOS muestra una mini guía visual de dos pasos (Compartir → Añadir a inicio).

#### Scenario: iPhone sin instalar
- **WHEN** un usuario de iPhone pulsa "Instalar" en Safari
- **THEN** ve la mini guía con los iconos de Compartir y Añadir a inicio

### Requirement: Pantalla completa desde el navegador
En navegadores que lo soporten, el sistema SHALL ofrecer un botón para alternar pantalla completa sin instalar la app.

#### Scenario: Android en Chrome
- **WHEN** el usuario pulsa el botón de pantalla completa en Chrome Android
- **THEN** la app pasa a ocupar toda la pantalla

### Requirement: Pantalla encendida
Mientras el usuario esté dentro de una sala, el sistema SHALL evitar que la pantalla se apague en los dispositivos que lo permitan, y liberar ese bloqueo al salir de la sala.

#### Scenario: Votación larga
- **WHEN** un participante está en la pantalla de votación sin tocar el móvil durante varios minutos
- **THEN** la pantalla sigue encendida

### Requirement: Diseño móvil
La interfaz SHALL estar diseñada para móvil en vertical (de 360 px de ancho en adelante), respetar las zonas seguras (notch y barra de gestos) y usar objetivos táctiles de al menos 44 px.

#### Scenario: iPhone con notch
- **WHEN** la app se abre instalada en un iPhone con notch
- **THEN** ningún control queda tapado por el notch ni por la barra de gestos

### Requirement: Tono visual y textos
La UI SHALL usar una paleta colorida y desenfadada, tipografía redondeada, emojis y animaciones suaves. Cada botón MUST combinar un icono con como máximo dos palabras cortas en español; los avisos y errores MUST ser de una a tres palabras con emoji.

#### Scenario: Botones principales
- **WHEN** un usuario está en la pantalla de inicio
- **THEN** ve botones del estilo "➕ Crear" y "🚪 Unirse", sin frases explicativas

### Requirement: Estado de conexión
El sistema SHALL mostrar un indicador discreto cuando se pierda la conexión con el servidor y reintentar solo. Si el servidor tarda en responder al abrir la app (arranque en frío), MUST mostrar una pantalla de espera animada en lugar de un error.

#### Scenario: Servidor dormido
- **WHEN** un usuario abre la app y el servidor tarda 40 segundos en arrancar
- **THEN** ve una animación de espera ("Despertando…") y la app continúa sola cuando el servidor responde

### Requirement: Actualizaciones de la app
Cuando haya una nueva versión desplegada, el sistema SHALL avisar con un botón "Actualizar" y nunca MUST recargar la app por sí solo mientras el usuario esté dentro de una sala.

#### Scenario: Nueva versión en mitad de la votación
- **WHEN** se despliega una versión nueva mientras un usuario vota
- **THEN** la app no se recarga y muestra el aviso para actualizar cuando quiera

### Requirement: Accesibilidad básica
El texto y los botones SHALL tener contraste suficiente sobre los fondos de colores, los botones de solo icono MUST tener nombre accesible, y las animaciones MUST respetar la preferencia de reducir movimiento.

#### Scenario: Lector de pantalla
- **WHEN** un lector de pantalla recorre un botón de solo icono
- **THEN** anuncia su función (por ejemplo "Compartir sala")
