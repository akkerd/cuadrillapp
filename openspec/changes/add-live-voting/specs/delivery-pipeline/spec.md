# Spec Delta

## Purpose

Define cómo llega un cambio de código a producción de forma segura y verificable, también cuando lo hace Claude desde una sesión en la nube pedida desde el móvil: checks obligatorios, despliegue automático, comprobación de versión y vuelta atrás.

## ADDED Requirements

### Requirement: Verificación con un solo comando
El repositorio SHALL ofrecer un único comando de verificación que ejecute lint, comprobación de tipos, tests unitarios y de integración, build de producción y tests end-to-end en un navegador móvil emulado, y que termine con error si cualquiera falla.

#### Scenario: Verificación local o en la nube
- **WHEN** un desarrollador o Claude ejecuta el comando de verificación en un checkout limpio tras instalar dependencias
- **THEN** se ejecutan todas las comprobaciones y el resultado indica claramente si todo pasó

### Requirement: Checks en cada PR
Cada pull request y cada push a main SHALL ejecutar automáticamente la verificación completa en CI y publicar el resultado como check del commit. Si fallan los tests end-to-end, el informe del fallo MUST quedar descargable desde la ejecución.

#### Scenario: PR con un test roto
- **WHEN** se abre un PR que rompe un test
- **THEN** el check aparece en rojo en el PR y el informe se puede descargar

### Requirement: Main protegida
La rama main MUST aceptar cambios solo mediante pull request con el check de verificación en verde; los pushes directos a main MUST rechazarse.

#### Scenario: Push directo
- **WHEN** alguien intenta hacer push directo a main
- **THEN** GitHub lo rechaza

### Requirement: Despliegue automático tras checks
Cada commit que llegue a main SHALL desplegarse automáticamente en producción solo después de que su verificación en CI haya pasado; un commit con checks en rojo MUST NOT desplegarse.

#### Scenario: Merge de un PR verde
- **WHEN** se mergea a main un PR con checks en verde y la verificación de main pasa
- **THEN** la nueva versión queda desplegada sin intervención manual

### Requirement: Despliegue sin caída por versiones rotas
El servicio SHALL exponer un endpoint de salud que responda con estado correcto y el identificador del commit desplegado. Un despliegue cuya versión nueva no responda correctamente en el endpoint de salud MUST NOT sustituir a la versión que está funcionando.

#### Scenario: Comprobar la versión desplegada
- **WHEN** se consulta el endpoint de salud tras un despliegue
- **THEN** responde correcto e indica el commit de main recién mergeado

#### Scenario: Versión que no arranca
- **WHEN** la versión nueva falla al arrancar
- **THEN** la versión anterior sigue atendiendo a los usuarios

### Requirement: Vuelta atrás
El proyecto SHALL documentar un procedimiento de vuelta atrás que restaure la versión anterior en minutos, ya sea revirtiendo el commit en main mediante PR o reactivando un despliegue anterior en el proveedor de hosting.

#### Scenario: Revertir un cambio roto
- **WHEN** se mergea en main el revert de un cambio problemático
- **THEN** la versión anterior queda desplegada siguiendo el mismo flujo con checks

### Requirement: Flujo de cambios con Claude
El repositorio SHALL incluir instrucciones para agentes que obliguen a trabajar en una rama, ejecutar la verificación completa antes de publicar, abrir un PR con un resumen corto y comprobar tras el merge que el endpoint de salud muestra el nuevo commit. Una sesión de Claude en la nube MUST poder instalar dependencias y navegadores de test sin pasos manuales ni secretos.

#### Scenario: Cambio pedido desde el móvil
- **WHEN** el usuario pide desde la app de Claude en el móvil un cambio en el repositorio
- **THEN** Claude lo implementa en una rama, pasa la verificación y abre un PR que el usuario puede mergear desde el móvil

### Requirement: Sin secretos en el repositorio
El repositorio y los logs de CI MUST NOT contener secretos; la configuración sensible vive solo en las variables de entorno del proveedor de hosting o en los secretos de GitHub.

#### Scenario: Revisión de configuración
- **WHEN** se inspeccionan los ficheros del repositorio y los logs de CI
- **THEN** no aparece ninguna credencial ni token
