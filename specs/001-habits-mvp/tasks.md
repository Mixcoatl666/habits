# Tareas: MVP de hábitos de estudio

Las tareas se ejecutan en este orden. Cada una está limitada a 20–30 minutos.

- [x] **T001 — Preparar la estructura mínima del paquete y la suite de pruebas** *(20 min; RF-1–RF-5, habilitadora)*
  **Hecho cuando:** los módulos previstos pueden importarse y `python -m unittest discover -s tests -v` ejecuta una prueba mínima correctamente.

- [x] **T002 — Implementar el modelo de hábito y la creación con nombres normalizados** *(30 min; RF-1)*
  **Hecho cuando:** las pruebas demuestran que se recortan espacios, se conserva el nombre visible y se rechazan nombres vacíos o duplicados mediante comparación `casefold`.

- [x] **T003 — Implementar el registro diario de cumplimiento** *(25 min; RF-2)*
  **Hecho cuando:** las pruebas demuestran que se registra la fecha recibida una sola vez, repetirla es idempotente y un hábito inexistente no modifica el estado.

- [x] **T004 — Implementar el cálculo de la racha vigente** *(25 min; RF-4)*
  **Hecho cuando:** las pruebas cubren rachas terminadas hoy o ayer, cero cumplimientos, cumplimientos antiguos, un solo día y secuencias interrumpidas.

- [x] **T005 — Resolver la ubicación de datos y cargar estados ausentes o válidos** *(25 min; RF-5)*
  **Hecho cuando:** un archivo ausente produce una colección vacía y el JSON válido del plan se convierte correctamente al modelo de dominio usando una ruta sustituible en tests.

- [x] **T006 — Validar la raíz, versión y colección del documento JSON** *(25 min; RF-5)*
  **Hecho cuando:** las pruebas rechazan JSON mal formado, raíz incorrecta, versión distinta de `1`, campos desconocidos y una colección de hábitos inválida.

- [x] **T007 — Validar nombres y fechas de cada hábito cargado** *(30 min; RF-1, RF-2, RF-5)*
  **Hecho cuando:** las pruebas rechazan nombres vacíos o duplicados, fechas no ISO, imposibles, futuras, repetidas o desordenadas, sin aceptar parcialmente el documento.

- [x] **T008 — Serializar el estado en el formato JSON canónico** *(20 min; RF-1, RF-2, RF-5)*
  **Hecho cuando:** las pruebas confirman versión, nombres Unicode conservados, fechas ordenadas, UTF-8 y una recarga sin pérdida de información.

- [x] **T009 — Implementar la escritura atómica y sus fallos controlados** *(30 min; RF-5)*
  **Hecho cuando:** las pruebas demuestran que se escribe mediante un temporal en el mismo directorio y que un fallo de escritura o reemplazo deja intacto el último archivo válido.

- [x] **T010 — Crear el punto de entrada y el análisis general de comandos** *(25 min; RF-1, RF-2, RF-3)*
  **Hecho cuando:** `python -m habits` reconoce `add`, `done` y `list`, muestra ayuda en español y devuelve código `2` para comandos o argumentos inválidos.

- [x] **T011 — Conectar el comando `add` con dominio y persistencia** *(30 min; RF-1, RF-5)*
  **Hecho cuando:** las pruebas de CLI verifican mensajes, canales y códigos de salida para creación válida, nombre vacío y duplicado, además de la persistencia del hábito.

- [x] **T012 — Conectar el comando `done` con dominio y persistencia** *(30 min; RF-2, RF-5)*
  **Hecho cuando:** las pruebas de CLI verifican el primer cumplimiento, la repetición idempotente con código `0`, el hábito inexistente con código `2` y la ausencia de fechas duplicadas.

- [x] **T013 — Conectar el comando `list` con el cálculo de rachas** *(30 min; RF-3, RF-4, RF-5)*
  **Hecho cuando:** las pruebas verifican listado vacío, orden alfabético con `casefold`, rachas correctas y la flexión exacta de `día` y `días`.

- [x] **T014 — Traducir fallos de persistencia al contrato de la CLI** *(25 min; RF-5)*
  **Hecho cuando:** los errores de lectura, validación y escritura salen por stderr con mensajes en español, código `1` y sin reemplazar ni reiniciar los datos existentes.

- [x] **T015 — Completar las pruebas de aceptación entre ejecuciones** *(30 min; RF-1–RF-5)*
  **Hecho cuando:** un flujo con almacenamiento temporal crea, lista, marca y vuelve a listar en ejecuciones separadas, obteniendo las salidas y rachas especificadas.

- [x] **T016 — Ejecutar la verificación final y cerrar la trazabilidad** *(20 min; RF-1–RF-5)*
  **Hecho cuando:** toda la suite pasa, cada criterio de aceptación tiene al menos una prueba identificable, no se accede a los datos reales del usuario y no existen dependencias externas ni mensajes visibles en otro idioma.
