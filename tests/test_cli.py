"""Tests for the command-line parser and entry point."""

import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from habits.cli import build_parser, main
from habits.core import Habit
from habits.storage import StorageError, load_habits, save_habits


TODAY = date(2026, 9, 25)


class CommandParserTests(unittest.TestCase):
    """Verify the three MVP commands and their arguments."""

    def test_recognizes_supported_commands(self) -> None:
        cases = (
            (["add", "Study Python"], "add", "Study Python"),
            (["done", "Study Python"], "done", "Study Python"),
            (["list"], "list", None),
        )

        parser = build_parser()
        for arguments, expected_command, expected_name in cases:
            with self.subTest(arguments=arguments):
                namespace = parser.parse_args(arguments)
                self.assertEqual(expected_command, namespace.command)
                self.assertEqual(expected_name, getattr(namespace, "name", None))

    def test_rejects_missing_or_extra_arguments_with_exit_code_two(self) -> None:
        invalid_arguments = ([], ["add"], ["done"], ["list", "extra"])
        parser = build_parser()

        for arguments in invalid_arguments:
            with self.subTest(arguments=arguments):
                with self.assertRaises(SystemExit) as raised:
                    parser.parse_args(arguments)

                self.assertEqual(2, raised.exception.code)


class ModuleEntryPointTests(unittest.TestCase):
    """Verify help and invalid command behavior through the module entry point."""

    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "habits", *arguments],
            capture_output=True,
            check=False,
            text=True,
        )

    def test_help_is_in_spanish_and_lists_commands(self) -> None:
        result = self.run_cli("--help")

        self.assertEqual(0, result.returncode)
        self.assertEqual("", result.stderr)
        self.assertIn("uso:", result.stdout)
        self.assertIn("Gestiona hábitos de estudio diarios.", result.stdout)
        self.assertIn("Muestra esta ayuda y termina.", result.stdout)
        self.assertNotIn("show this help", result.stdout)
        for command in ("add", "done", "list"):
            self.assertIn(command, result.stdout)

    def test_unknown_command_returns_exit_code_two_in_spanish(self) -> None:
        result = self.run_cli("unknown")

        self.assertEqual(2, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertIn("Error: argumentos no válidos.", result.stderr)
        self.assertIn("uso:", result.stderr)


class CliCommandTestCase(unittest.TestCase):
    """Provide isolated storage and captured command output."""

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.data_path = Path(self.temporary_directory.name) / "habits.json"

    def run_main(self, *arguments: str) -> tuple[int, str, str]:
        output = StringIO()
        error = StringIO()
        exit_code = main(
            list(arguments),
            data_path=self.data_path,
            today=TODAY,
            output=output,
            error=error,
        )
        return exit_code, output.getvalue(), error.getvalue()


class AddCommandTests(CliCommandTestCase):
    """Verify the add command contract."""

    def test_adds_and_persists_trimmed_habit(self) -> None:
        result = self.run_main("add", "  Study Python  ")

        self.assertEqual((0, "Hábito creado: Study Python\n", ""), result)
        self.assertEqual(
            [Habit("Study Python")],
            load_habits(self.data_path, today=TODAY),
        )

    def test_rejects_empty_name_without_writing(self) -> None:
        result = self.run_main("add", "   ")

        self.assertEqual(
            (2, "", "Error: el nombre del hábito no puede estar vacío.\n"),
            result,
        )
        self.assertFalse(self.data_path.exists())

    def test_rejects_duplicate_without_changing_file(self) -> None:
        self.run_main("add", "Study Python")
        original_data = self.data_path.read_bytes()

        result = self.run_main("add", "  STUDY PYTHON  ")

        self.assertEqual(
            (2, "", "Error: ya existe un hábito con ese nombre.\n"),
            result,
        )
        self.assertEqual(original_data, self.data_path.read_bytes())


class DoneCommandTests(CliCommandTestCase):
    """Verify the done command contract."""

    def setUp(self) -> None:
        super().setUp()
        save_habits([Habit("Study Python")], self.data_path, today=TODAY)

    def test_records_and_persists_completion(self) -> None:
        result = self.run_main("done", "study python")

        self.assertEqual(
            (0, "Hábito completado hoy: Study Python\n", ""),
            result,
        )
        habits = load_habits(self.data_path, today=TODAY)
        self.assertEqual({TODAY}, habits[0].completions)

    def test_repeated_completion_is_success_without_saving(self) -> None:
        self.run_main("done", "Study Python")

        with patch("habits.cli.save_habits") as mocked_save:
            result = self.run_main("done", "Study Python")

        self.assertEqual(
            (0, "El hábito ya estaba completado hoy: Study Python\n", ""),
            result,
        )
        mocked_save.assert_not_called()
        habits = load_habits(self.data_path, today=TODAY)
        self.assertEqual({TODAY}, habits[0].completions)

    def test_missing_habit_returns_two_without_changing_file(self) -> None:
        original_data = self.data_path.read_bytes()

        result = self.run_main("done", "Mathematics")

        self.assertEqual(
            (2, "", "Error: no existe un hábito con ese nombre.\n"),
            result,
        )
        self.assertEqual(original_data, self.data_path.read_bytes())


class ListCommandTests(CliCommandTestCase):
    """Verify listing, sorting, and streak presentation."""

    def test_lists_empty_collection(self) -> None:
        result = self.run_main("list")

        self.assertEqual((0, "No hay hábitos registrados.\n", ""), result)

    def test_lists_habits_alphabetically_with_current_streaks(self) -> None:
        habits = [
            Habit("Zeta"),
            Habit(
                "alpha",
                {TODAY - timedelta(days=1), TODAY - timedelta(days=2)},
            ),
            Habit("Beta", {TODAY}),
        ]
        save_habits(habits, self.data_path, today=TODAY)

        result = self.run_main("list")

        self.assertEqual(
            (
                0,
                "alpha — racha: 2 días\n"
                "Beta — racha: 1 día\n"
                "Zeta — racha: 0 días\n",
                "",
            ),
            result,
        )


class CliStorageErrorTests(CliCommandTestCase):
    """Verify user-facing persistence errors."""

    def test_validation_error_returns_one_without_replacing_data(self) -> None:
        original_data = b"{not-json"
        self.data_path.write_bytes(original_data)

        result = self.run_main("list")

        self.assertEqual(
            (
                1,
                "",
                "Error: no se pudieron leer los datos; "
                "el archivo existente no fue modificado.\n",
            ),
            result,
        )
        self.assertEqual(original_data, self.data_path.read_bytes())

    def test_read_error_returns_one(self) -> None:
        with patch("habits.cli.load_habits", side_effect=StorageError):
            result = self.run_main("list")

        self.assertEqual(
            (
                1,
                "",
                "Error: no se pudieron leer los datos; "
                "el archivo existente no fue modificado.\n",
            ),
            result,
        )

    def test_write_error_returns_one_without_reporting_success(self) -> None:
        save_habits([Habit("Existing")], self.data_path, today=TODAY)
        original_data = self.data_path.read_bytes()

        with patch("habits.cli.save_habits", side_effect=StorageError):
            result = self.run_main("add", "New habit")

        self.assertEqual(
            (
                1,
                "",
                "Error: no se pudieron guardar los cambios; "
                "se conservó el estado anterior.\n",
            ),
            result,
        )
        self.assertEqual(original_data, self.data_path.read_bytes())


if __name__ == "__main__":
    unittest.main()
