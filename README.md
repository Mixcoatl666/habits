# Habits CLI

Aplicación educativa de línea de comandos para registrar hábitos diarios de estudio, marcarlos como completados y consultar su racha vigente.

## Requisitos

- Python 3.12 o posterior.
- No requiere dependencias externas para ejecutarse.

## Uso

Desde la carpeta `habits-app`, consulta la ayuda:

```bash
python3 -m habits --help
```

Crea un hábito:

```bash
python3 -m habits add "Estudiar Python"
```

Márcalo como completado hoy:

```bash
python3 -m habits done "Estudiar Python"
```

Lista los hábitos y sus rachas:

```bash
python3 -m habits list
```

Si el intérprete de tu sistema se llama `python`, puedes usarlo en lugar de `python3`.

Los datos se guardan localmente en `~/.habits-cli/habits.json`. La aplicación valida el documento antes de usarlo y realiza escrituras atómicas para proteger el último estado válido.

## Tests

La suite está escrita con `unittest` y no accede a los datos reales del usuario:

```bash
python3 -m unittest discover -s tests -v
```

Si `pytest` está instalado como herramienta de desarrollo, también puede ejecutarse con:

```bash
pytest -q
```

## Desarrollo guiado por especificaciones

Este proyecto fue creado con una metodología de Spec-Driven Development (SDD). La constitución fija las reglas innegociables; la especificación define el qué y el porqué; el plan concreta las decisiones técnicas; y el listado de tareas mantiene la implementación verificable y trazable hasta sus requisitos funcionales.

## Créditos

El principal reconocimiento corresponde al [curso de SDD en YouTube](https://www.youtube.com/watch?v=5HaOxAAA5qI&t=2264s), cuya metodología guió la construcción de este proyecto.

- **Noah Noel Arredondo Torres:** autor y responsable del proyecto.
- **Codex, de OpenAI:** colaboración en la especificación, planificación, implementación y verificación.
