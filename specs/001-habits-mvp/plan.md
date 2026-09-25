# Plan técnico: MVP de hábitos de estudio

## 1. Objetivo y restricciones

Este plan traduce la especificación funcional en una implementación pequeña y mantenible. Se usará exclusivamente la biblioteca estándar de Python. La lógica de negocio permanecerá separada de la CLI, los datos se validarán antes de usarse y toda escritura será atómica. Los identificadores y comentarios del código estarán en inglés; todos los mensajes visibles para el usuario estarán en español.

**RF cubiertos:** RF-1, RF-2, RF-3, RF-4 y RF-5.

## 2. Estructura de módulos

| Módulo | Responsabilidad | Dependencias permitidas | RF cubiertos |
|---|---|---|---|
| `habits/core.py` | Definir el modelo de dominio, normalizar nombres, crear hábitos, registrar cumplimientos y calcular rachas. No imprime mensajes, no interpreta argumentos y no accede al sistema de archivos. | Biblioteca estándar; tipos de dominio propios. | RF-1, RF-2, RF-4 |
| `habits/storage.py` | Cargar, validar y guardar el documento JSON. Proteger el archivo válido anterior mediante escritura atómica. | Biblioteca estándar y tipos de dominio; nunca depende de la CLI. | RF-1, RF-2, RF-5 |
| `habits/cli.py` | Interpretar comandos, obtener la fecha local, coordinar dominio y persistencia, y convertir resultados o errores en mensajes y códigos de salida. | `core`, `storage` y biblioteca estándar. | RF-1, RF-2, RF-3, RF-4, RF-5 |
| `habits/__main__.py` | Ofrecer el punto de entrada `python -m habits` y delegar inmediatamente en la CLI. | `cli`. | RF-1, RF-2, RF-3 |
| `tests/test_core.py` | Verificar reglas de nombres, cumplimientos y rachas sin usar archivos ni CLI. | `unittest` y `core`. | RF-1, RF-2, RF-4 |
| `tests/test_storage.py` | Verificar carga, validación, persistencia y recuperación ante fallos con directorios temporales. | `unittest`, `tempfile` y `storage`. | RF-1, RF-2, RF-5 |
| `tests/test_cli.py` | Verificar comandos, mensajes, orden, flujos completos y códigos de salida con fecha y ruta de datos controladas. | `unittest` y módulos de la aplicación. | RF-1, RF-2, RF-3, RF-4, RF-5 |

El modelo de dominio representará cada hábito mediante su nombre de presentación y un conjunto de fechas de cumplimiento. Las operaciones públicas recibirán explícitamente la fecha que consideran «hoy»; así, el dominio no consultará el reloj ni dependerá de la interfaz.

## 3. Modelo de datos JSON

El archivo de datos residirá en el directorio personal del usuario, dentro de `.habits-cli/habits.json`. La ruta será resuelta por la capa de persistencia y podrá sustituirse internamente en las pruebas. Si el archivo no existe, se interpretará como un estado inicial sin hábitos.

### Esquema lógico

- La raíz es un objeto con dos campos obligatorios: `version` y `habits`.
- `version` es el entero `1`. Una versión distinta se rechaza para evitar interpretar datos incompatibles.
- `habits` es una lista de objetos.
- Cada hábito contiene:
  - `name`: cadena no vacía, ya recortada en sus extremos y conservada con sus mayúsculas originales.
  - `completions`: lista de fechas ISO `AAAA-MM-DD`, sin duplicados y ordenada ascendentemente.
- Los nombres deben ser únicos después de aplicar recorte exterior y comparación Unicode sin distinguir mayúsculas mediante `casefold`.
- Cada fecha debe ser una fecha de calendario válida y no puede ser posterior a la fecha local actual al cargar los datos.
- Los campos ausentes, tipos incorrectos, campos desconocidos, nombres duplicados, fechas duplicadas o fechas inválidas hacen que el documento completo sea inválido. No se intentará una reparación parcial.

**Ejemplo:**

```json
{
  "version": 1,
  "habits": [
    {
      "name": "Estudiar matemáticas",
      "completions": [
        "2026-09-23",
        "2026-09-24",
        "2026-09-25"
      ]
    },
    {
      "name": "Practicar Python",
      "completions": [
        "2026-09-25"
      ]
    }
  ]
}
```

### Escritura segura

1. Validar en memoria el estado completo que se desea guardar.
2. Crear el directorio de datos si todavía no existe.
3. Escribir el JSON completo en un archivo temporal ubicado en el mismo directorio que el archivo definitivo, usando UTF-8, fechas ordenadas, sangría estable y caracteres Unicode sin escapar cuando sea posible.
4. Vaciar los búferes y sincronizar el archivo temporal con el almacenamiento.
5. Reemplazar atómicamente el archivo definitivo por el temporal.
6. Si cualquier paso anterior al reemplazo falla, conservar sin cambios el archivo definitivo y eliminar el temporal cuando sea posible.

**RF cubiertos:** RF-1 por unicidad y conservación del nombre; RF-2 por un solo cumplimiento diario; RF-5 por validación, durabilidad y escritura atómica.

## 4. Algoritmo de cálculo de racha

La entrada será el conjunto de fechas de cumplimiento de un hábito y la fecha local considerada «hoy». La salida será un entero no negativo.

```text
CALCULAR_RACHA(cumplimientos, hoy):
    si hoy pertenece a cumplimientos:
        fecha_a_comprobar = hoy
    en caso contrario, si ayer pertenece a cumplimientos:
        fecha_a_comprobar = ayer
    en caso contrario:
        devolver 0

    racha = 0
    mientras fecha_a_comprobar pertenezca a cumplimientos:
        racha = racha + 1
        fecha_a_comprobar = fecha_a_comprobar - un día natural

    devolver racha
```

El cálculo usa fechas de calendario, no intervalos de 24 horas. Un cumplimiento hoy extiende la racha; si hoy sigue pendiente, la racha cerrada ayer continúa vigente; cualquier día omitido detiene el conteo.

**RF cubierto:** RF-4.

## 5. Contrato de la CLI

### Convenciones generales

- Invocación base: `python -m habits <comando>`.
- Los comandos y argumentos técnicos usan nombres en inglés; la ayuda y todos los mensajes al usuario se muestran en español.
- Las salidas exitosas se escriben en la salida estándar. Los errores se escriben en la salida de error.
- El nombre recibido se recorta solo en sus extremos. El nombre recortado y con sus mayúsculas originales se usa en mensajes y listados.
- La localización de un hábito por nombre ignora mayúsculas y minúsculas mediante `casefold`.
- La fecha de cada invocación se obtiene una sola vez al comenzar y se comparte con todas las operaciones de esa invocación.

### Comandos y salidas

| Acción | Invocación | Salida exitosa | Errores de uso o dominio | RF cubiertos |
|---|---|---|---|---|
| Crear | `python -m habits add "<nombre>"` | `Hábito creado: <nombre>` | Nombre vacío: `Error: el nombre del hábito no puede estar vacío.` Duplicado: `Error: ya existe un hábito con ese nombre.` | RF-1, RF-5 |
| Marcar hoy | `python -m habits done "<nombre>"` | Nuevo registro: `Hábito completado hoy: <nombre>` Ya registrado: `El hábito ya estaba completado hoy: <nombre>` | Inexistente: `Error: no existe un hábito con ese nombre.` | RF-2, RF-5 |
| Listar | `python -m habits list` | Una línea por hábito: `<nombre> — racha: <N> día` para 1 y `<nombre> — racha: <N> días` para cualquier otro valor. Sin hábitos: `No hay hábitos registrados.` | No recibe argumentos adicionales. | RF-3, RF-4, RF-5 |

El listado se ordena por el nombre recortado usando `casefold`, sin modificar el nombre mostrado. Marcar por segunda vez el mismo día es un éxito idempotente y no provoca una escritura innecesaria.

### Códigos de salida

| Código | Significado | Casos |
|---|---|---|
| `0` | Operación completada correctamente. | Creación, primer cumplimiento, cumplimiento ya existente, listado con datos y listado vacío. |
| `2` | Error corregible por el usuario. | Comando o argumentos inválidos, nombre vacío, nombre duplicado o hábito inexistente. |
| `1` | Error de datos o del entorno. | JSON ilegible o inválido, versión incompatible, imposibilidad de leer o guardar, o fallo inesperado controlado. |

Ante un error de lectura se mostrará `Error: no se pudieron leer los datos; el archivo existente no fue modificado.` Ante un error de escritura se mostrará `Error: no se pudieron guardar los cambios; se conservó el estado anterior.` Ninguno de estos casos intentará reiniciar los datos.

**RF cubiertos:** RF-1, RF-2, RF-3, RF-4 y RF-5.

## 6. Decisiones técnicas

| Decisión y justificación | Alternativa descartada | RF cubiertos |
|---|---|---|
| Usar solo biblioteca estándar para argumentos, fechas, JSON y archivos. Mantiene el stack pequeño y evita instalación adicional. | Bibliotecas externas para CLI, validación o persistencia; añaden dependencias innecesarias para tres comandos. | RF-1–RF-5 |
| Mantener dominio, persistencia e interfaz en módulos separados. Permite probar las reglas sin terminal ni disco y evita que los mensajes condicionen el dominio. | Concentrar toda la aplicación en un solo módulo; resulta inicialmente corto, pero mezcla responsabilidades y dificulta el mantenimiento. | RF-1–RF-5 |
| Usar un documento JSON versionado y legible. Es suficiente para un usuario y un volumen pequeño de registros. | SQLite; ofrece consultas y concurrencia que el MVP no necesita y aumenta la superficie conceptual. | RF-5 |
| Guardar fechas ISO y cumplimientos únicos ordenados. El formato es inequívoco, comparable y fácil de validar. | Marcas de tiempo; introducen horas y zonas horarias donde el dominio solo requiere días naturales. | RF-2, RF-4, RF-5 |
| Usar reemplazo atómico desde un temporal en el mismo directorio. Protege el último estado válido ante escrituras interrumpidas. | Escribir directamente sobre el archivo definitivo; puede dejar JSON truncado o corrupto. | RF-5 |
| Comparar nombres con recorte exterior y `casefold`, conservando el original para mostrarlo. Proporciona unicidad coherente para texto Unicode. | Comparar literalmente o usar solo `lower`; permitiría duplicados visuales o manejaría peor ciertos caracteres Unicode. | RF-1, RF-2 |
| Pasar «hoy» explícitamente al dominio y consultarlo una sola vez en la CLI. Hace deterministas las reglas y evita resultados inconsistentes al cruzar medianoche. | Consultar el reloj dentro de cada función; acopla el dominio al entorno y vuelve frágiles las pruebas. | RF-2, RF-4 |
| Rechazar por completo datos inválidos sin repararlos automáticamente. Evita pérdidas silenciosas y respeta el estado previo. | Descartar entradas erróneas o reiniciar el archivo; ocultaría corrupción y podría perder información. | RF-5 |
| Escribir las pruebas con `unittest` y utilidades estándar. Cumple la constitución y evita que la suite dependa de funciones exclusivas de otro framework. | Basar las pruebas en fixtures o extensiones específicas de `pytest`; no son necesarias para este alcance. | RF-1–RF-5 |

## 7. Estrategia de tests

Todas las pruebas controlarán explícitamente la fecha; ninguna dependerá del día real en que se ejecute. Los tests de persistencia usarán directorios temporales y nunca el archivo real del usuario. La suite se implementará con `unittest` y se ejecutará con `python -m unittest discover -s tests -v`; al ser compatible, también podrá ejecutarse mediante el comando de pruebas del repositorio cuando `pytest` esté disponible.

### Pruebas unitarias de dominio

- Crear un hábito válido, recortar espacios y conservar las mayúsculas mostradas. **RF-1**
- Rechazar un nombre vacío o compuesto solo por espacios sin cambiar el estado. **RF-1**
- Rechazar duplicados exactos y duplicados que solo difieran por mayúsculas o espacios exteriores. **RF-1**
- Registrar una fecha una sola vez y tratar la segunda marca del mismo día como éxito idempotente. **RF-2**
- Rechazar la marca de un hábito inexistente sin cambiar el estado. **RF-2**
- Calcular rachas que terminan hoy, que terminan ayer, de un solo día, con huecos, sin cumplimientos y con cumplimientos antiguos. **RF-4**

### Pruebas de persistencia

- Interpretar un archivo ausente como colección vacía. **RF-5**
- Guardar y volver a cargar nombres Unicode y fechas sin perder información. **RF-1, RF-2, RF-5**
- Rechazar JSON mal formado, versión desconocida, esquema incorrecto, campos desconocidos, nombres duplicados, fechas inválidas, futuras o repetidas. **RF-1, RF-2, RF-5**
- Simular fallos durante la escritura y durante el reemplazo para comprobar que el archivo válido anterior queda intacto y que no se informa éxito. **RF-5**
- Confirmar que el JSON guardado utiliza el orden y formato canónicos definidos. **RF-5**

### Pruebas de CLI y aceptación

- Verificar el texto, canal de salida y código de salida de cada resultado de `add`, `done` y `list`. **RF-1, RF-2, RF-3**
- Ejecutar el flujo crear, listar, marcar y volver a listar usando el mismo archivo temporal para comprobar persistencia y racha. **RF-1–RF-5**
- Verificar el listado vacío, el orden alfabético sin distinguir mayúsculas y la flexión `día`/`días`. **RF-3, RF-4**
- Verificar que una segunda marca diaria devuelve código `0`, informa la idempotencia y no duplica la fecha. **RF-2**
- Verificar código `2` para entradas corregibles y código `1` para lectura, validación o escritura fallida. **RF-1, RF-2, RF-5**
- Verificar que la ayuda, los mensajes de éxito y los errores visibles están en español. **RF-1, RF-2, RF-3, RF-5**

## 8. Criterio de implementación completa

La implementación estará completa cuando los tres comandos respeten el contrato anterior, el modelo JSON sea validado y escrito atómicamente, el dominio no dependa de la CLI ni del almacenamiento, y todas las pruebas unitarias y de aceptación relacionadas con RF-1 a RF-5 pasen sin utilizar los datos reales del usuario.
