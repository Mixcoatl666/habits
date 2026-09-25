# Especificación: MVP de hábitos de estudio

## Contexto y objetivo

Las personas que estudian necesitan una forma sencilla de registrar su constancia diaria sin distraerse con configuraciones o estadísticas avanzadas. El objetivo del MVP es permitir que un estudiante cree hábitos diarios, registre su cumplimiento en el día actual y consulte su racha vigente mediante una experiencia predecible y comprensible.

## Usuarios

El usuario principal es un estudiante individual que lleva el seguimiento local de sus propios hábitos. No necesita una cuenta, colaboración con otras personas ni conocimientos técnicos.

## Historias de usuario

- **HU-1:** Como estudiante, quiero crear un hábito para empezar a seguirlo.
- **HU-2:** Como estudiante, quiero marcar un hábito como realizado hoy para mantener su registro.
- **HU-3:** Como estudiante, quiero listar mis hábitos y sus rachas para conocer mi constancia.

## Requisitos funcionales

### RF-1: Crear hábitos

El sistema debe permitir crear un hábito mediante un nombre no vacío. Debe recortar los espacios exteriores y conservar las mayúsculas y minúsculas introducidas para mostrar el nombre.

**Criterios de aceptación (EARS):**

- Cuando el usuario proporcione un nombre válido que no exista, el sistema deberá crear el hábito y confirmar la operación en español.
- Si el nombre está vacío o contiene únicamente espacios, el sistema deberá rechazarlo sin alterar los datos existentes.
- Si ya existe el mismo nombre después de recortar los espacios exteriores e ignorar diferencias entre mayúsculas y minúsculas, el sistema deberá rechazar el duplicado sin alterar los datos existentes.

### RF-2: Registrar el cumplimiento de hoy

El sistema debe permitir registrar como máximo un cumplimiento por hábito y día natural, usando la fecha local del dispositivo.

**Criterios de aceptación (EARS):**

- Cuando el usuario marque hoy un hábito existente que aún no esté realizado, el sistema deberá registrar el cumplimiento y confirmar la operación.
- Si el hábito ya está realizado hoy, el sistema deberá finalizar correctamente, conservar un único registro e informar que ya estaba realizado.
- Si el hábito indicado no existe, el sistema deberá informar del error y no modificar ningún dato.

### RF-3: Listar hábitos

El sistema debe mostrar todos los hábitos con su nombre y su racha vigente, ordenados alfabéticamente sin distinguir entre mayúsculas y minúsculas.

**Criterios de aceptación (EARS):**

- Cuando existan hábitos, el sistema deberá mostrar cada uno con su racha expresada en días.
- Si no existe ningún hábito, el sistema deberá mostrar un mensaje específico en español y finalizar correctamente.

### RF-4: Calcular la racha vigente

El sistema debe calcular la racha como el número de días naturales consecutivos en los que el hábito fue realizado.

**Criterios de aceptación (EARS):**

- Cuando exista un cumplimiento hoy, el sistema deberá contar la secuencia de días consecutivos que termina hoy.
- Cuando todavía no exista un cumplimiento hoy pero sí exista uno ayer, el sistema deberá contar la secuencia de días consecutivos que termina ayer.
- Si no existe un cumplimiento ni hoy ni ayer, el sistema deberá mostrar una racha de cero días.
- Si falta un día dentro de una secuencia de cumplimientos, el sistema deberá terminar la racha en ese punto.

### RF-5: Conservar la información

El sistema debe conservar los hábitos y sus cumplimientos entre ejecuciones y proteger el último estado válido ante errores.

**Criterios de aceptación (EARS):**

- Después de una operación exitosa que cambie la información, el sistema deberá conservar su resultado para ejecuciones posteriores.
- Si los datos existentes son ilegibles o inválidos, el sistema deberá finalizar con error, explicarlo en español y no reemplazarlos.
- Si no se puede conservar un cambio, el sistema deberá mantener intacto el último estado válido e informar del fallo.

## Requisitos no funcionales

- **RNF-1 — Claridad:** todos los mensajes visibles para el usuario deben estar en español y ser claros y accionables.
- **RNF-2 — Previsibilidad:** el comportamiento relacionado con el día actual debe ser determinista respecto de la fecha local del dispositivo.
- **RNF-3 — Verificabilidad:** cada criterio de aceptación, regla de racha y comportamiento de error debe contar con pruebas automatizadas.
- **RNF-4 — Resultado observable:** el usuario debe poder distinguir las operaciones fallidas de las exitosas.
- **RNF-5 — Facilidad de uso:** las tres acciones del MVP deben poder realizarse sin conocimientos técnicos ni configuración previa.

## Casos límite

- El nombre está vacío o contiene únicamente espacios.
- El nombre contiene espacios exteriores que deben recortarse.
- Un nombre nuevo solo difiere de otro existente por mayúsculas, minúsculas o espacios exteriores.
- Se intenta marcar un hábito inexistente.
- Se marca el mismo hábito más de una vez en el mismo día.
- Se solicita el listado cuando todavía no hay hábitos.
- Un hábito fue completado ayer, pero todavía no hoy.
- Existe uno o más días omitidos entre cumplimientos.
- Los datos existentes son ilegibles o no son válidos.
- Ocurre un fallo al conservar un cambio.

## Fuera de alcance

- Renombrar o eliminar hábitos.
- Desmarcar cumplimientos.
- Registrar o corregir fechas pasadas o futuras.
- Configurar una zona horaria diferente de la fecha local del dispositivo.
- Definir frecuencias distintas de la diaria.
- Consultar la racha histórica máxima u otras estadísticas.
- Usar cuentas, sincronización o colaboración entre personas.
- Proporcionar una interfaz gráfica o recordatorios.
- Importar o exportar información.

## Criterios de finalización

- Las tres historias de usuario pueden completarse con el comportamiento descrito.
- Todos los requisitos funcionales cumplen sus criterios de aceptación.
- Los casos de error preservan el último estado válido y ofrecen información comprensible al usuario.
- Todos los criterios de aceptación y casos límite aplicables están cubiertos por pruebas automatizadas y estas pasan correctamente.
- La especificación y el comportamiento observable del producto no se contradicen.

## Dudas abiertas

No quedan dudas abiertas para el alcance actual. Cualquier duda nueva deberá registrarse con la marca **[NECESITA ACLARACIÓN]** antes de iniciar su implementación.
