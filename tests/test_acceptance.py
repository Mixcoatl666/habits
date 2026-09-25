"""End-to-end acceptance tests for the habits MVP."""

import tempfile
import unittest
from datetime import date
from io import StringIO
from pathlib import Path

from habits.cli import main
from habits.core import Habit
from habits.storage import load_habits


class HabitsMvpAcceptanceTests(unittest.TestCase):
    """Verify the complete workflow across independent invocations."""

    def test_create_list_complete_and_list_again(self) -> None:
        today = date(2026, 9, 25)
        with tempfile.TemporaryDirectory() as temporary_directory:
            data_path = Path(temporary_directory) / "habits.json"

            add_result = self.run_invocation(data_path, today, "add", "Study Python")
            first_list = self.run_invocation(data_path, today, "list")
            done_result = self.run_invocation(data_path, today, "done", "Study Python")
            second_list = self.run_invocation(data_path, today, "list")

            self.assertEqual((0, "Hábito creado: Study Python\n", ""), add_result)
            self.assertEqual(
                (0, "Study Python — racha: 0 días\n", ""),
                first_list,
            )
            self.assertEqual(
                (0, "Hábito completado hoy: Study Python\n", ""),
                done_result,
            )
            self.assertEqual(
                (0, "Study Python — racha: 1 día\n", ""),
                second_list,
            )
            self.assertEqual(
                [Habit("Study Python", {today})],
                load_habits(data_path, today=today),
            )

    def run_invocation(
        self,
        data_path: Path,
        today: date,
        *arguments: str,
    ) -> tuple[int, str, str]:
        output = StringIO()
        error = StringIO()
        exit_code = main(
            list(arguments),
            data_path=data_path,
            today=today,
            output=output,
            error=error,
        )
        return exit_code, output.getvalue(), error.getvalue()


if __name__ == "__main__":
    unittest.main()
