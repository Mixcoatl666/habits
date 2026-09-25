"""Command-line interface for study habits."""

import argparse
import sys
from collections.abc import Sequence
from datetime import date
from pathlib import Path
from typing import TextIO

from habits.core import (
    DuplicateHabitError,
    Habit,
    HabitNotFoundError,
    InvalidHabitNameError,
    calculate_streak,
    create_habit,
    mark_habit_done,
)
from habits.storage import StorageError, load_habits, save_habits


class SpanishArgumentParser(argparse.ArgumentParser):
    """Argument parser with stable Spanish usage and error messages."""

    def format_usage(self) -> str:
        return super().format_usage().replace("usage:", "uso:", 1)

    def format_help(self) -> str:
        return super().format_help().replace("usage:", "uso:", 1)

    def error(self, message: str) -> None:
        del message
        self.print_usage(sys.stderr)
        self.exit(2, "Error: argumentos no válidos.\n")


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the three MVP commands."""
    parser = SpanishArgumentParser(
        prog="habits",
        description="Gestiona hábitos de estudio diarios.",
        add_help=False,
    )
    _add_help_option(parser)
    parser._optionals.title = "opciones"
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        title="comandos",
    )

    add_parser = subparsers.add_parser(
        "add",
        help="Crea un hábito.",
        description="Crea un hábito de estudio diario.",
        add_help=False,
    )
    _add_help_option(add_parser)
    add_parser._positionals.title = "argumentos posicionales"
    add_parser._optionals.title = "opciones"
    add_parser.add_argument("name", metavar="nombre", help="Nombre del hábito.")

    done_parser = subparsers.add_parser(
        "done",
        help="Marca un hábito como completado hoy.",
        description="Marca un hábito como completado hoy.",
        add_help=False,
    )
    _add_help_option(done_parser)
    done_parser._positionals.title = "argumentos posicionales"
    done_parser._optionals.title = "opciones"
    done_parser.add_argument("name", metavar="nombre", help="Nombre del hábito.")

    list_parser = subparsers.add_parser(
        "list",
        help="Lista los hábitos y sus rachas.",
        description="Lista los hábitos y sus rachas vigentes.",
        add_help=False,
    )
    _add_help_option(list_parser)
    list_parser._optionals.title = "opciones"

    return parser


def _add_help_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        help="Muestra esta ayuda y termina.",
    )


def main(
    arguments: Sequence[str] | None = None,
    *,
    data_path: Path | None = None,
    today: date | None = None,
    output: TextIO | None = None,
    error: TextIO | None = None,
) -> int:
    """Run one command and return its process exit code."""
    parser = build_parser()
    namespace = parser.parse_args(arguments)
    current_date = today if today is not None else date.today()
    output_stream = output if output is not None else sys.stdout
    error_stream = error if error is not None else sys.stderr

    try:
        habits = load_habits(data_path, today=current_date)
    except StorageError:
        print(
            "Error: no se pudieron leer los datos; "
            "el archivo existente no fue modificado.",
            file=error_stream,
        )
        return 1

    if namespace.command == "add":
        return _run_add(
            habits,
            namespace.name,
            data_path,
            current_date,
            output_stream,
            error_stream,
        )
    if namespace.command == "done":
        return _run_done(
            habits,
            namespace.name,
            data_path,
            current_date,
            output_stream,
            error_stream,
        )

    _run_list(habits, current_date, output_stream)
    return 0


def _run_add(
    habits: list[Habit],
    name: str,
    data_path: Path | None,
    today: date,
    output: TextIO,
    error: TextIO,
) -> int:
    try:
        habit = create_habit(habits, name)
    except InvalidHabitNameError:
        print(
            "Error: el nombre del hábito no puede estar vacío.",
            file=error,
        )
        return 2
    except DuplicateHabitError:
        print("Error: ya existe un hábito con ese nombre.", file=error)
        return 2

    if not _save_changes(habits, data_path, today, error):
        return 1

    print(f"Hábito creado: {habit.name}", file=output)
    return 0


def _run_done(
    habits: list[Habit],
    name: str,
    data_path: Path | None,
    today: date,
    output: TextIO,
    error: TextIO,
) -> int:
    try:
        was_added = mark_habit_done(habits, name, today)
    except HabitNotFoundError:
        print("Error: no existe un hábito con ese nombre.", file=error)
        return 2

    habit_name = next(
        habit.name
        for habit in habits
        if habit.name.casefold() == name.strip().casefold()
    )
    if not was_added:
        print(f"El hábito ya estaba completado hoy: {habit_name}", file=output)
        return 0

    if not _save_changes(habits, data_path, today, error):
        return 1

    print(f"Hábito completado hoy: {habit_name}", file=output)
    return 0


def _run_list(habits: list[Habit], today: date, output: TextIO) -> None:
    if not habits:
        print("No hay hábitos registrados.", file=output)
        return

    for habit in sorted(habits, key=lambda item: item.name.casefold()):
        streak = calculate_streak(habit.completions, today)
        unit = "día" if streak == 1 else "días"
        print(f"{habit.name} — racha: {streak} {unit}", file=output)


def _save_changes(
    habits: list[Habit],
    data_path: Path | None,
    today: date,
    error: TextIO,
) -> bool:
    try:
        save_habits(habits, data_path, today=today)
    except StorageError:
        print(
            "Error: no se pudieron guardar los cambios; "
            "se conservó el estado anterior.",
            file=error,
        )
        return False
    return True
