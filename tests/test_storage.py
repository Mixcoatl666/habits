"""Unit tests for JSON persistence."""

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from habits.core import Habit
from habits.storage import InvalidDataError, StorageError, default_data_path, load_habits, save_habits


TODAY = date(2026, 9, 25)


class StorageTestCase(unittest.TestCase):
    """Provide an isolated data path for storage tests."""

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.data_path = Path(self.temporary_directory.name) / "habits.json"

    def write_document(self, document: object) -> None:
        self.data_path.write_text(json.dumps(document), encoding="utf-8")


class LoadHabitsTests(StorageTestCase):
    """Verify loading and validation of stored data."""

    def test_default_path_is_inside_user_home(self) -> None:
        expected_path = Path.home() / ".habits-cli" / "habits.json"

        self.assertEqual(expected_path, default_data_path())

    def test_missing_file_returns_empty_collection(self) -> None:
        self.assertEqual([], load_habits(self.data_path, today=TODAY))

    def test_loads_valid_document(self) -> None:
        self.write_document(
            {
                "version": 1,
                "habits": [
                    {
                        "name": "Estudiar matemáticas",
                        "completions": ["2026-09-23", "2026-09-24"],
                    }
                ],
            }
        )

        habits = load_habits(self.data_path, today=TODAY)

        self.assertEqual(
            [
                Habit(
                    "Estudiar matemáticas",
                    {date(2026, 9, 23), date(2026, 9, 24)},
                )
            ],
            habits,
        )

    def test_rejects_malformed_json(self) -> None:
        self.data_path.write_text("{not-json", encoding="utf-8")

        with self.assertRaises(InvalidDataError):
            load_habits(self.data_path, today=TODAY)

    def test_rejects_invalid_root_and_collection_schema(self) -> None:
        invalid_documents = (
            [],
            {"version": 1},
            {"habits": []},
            {"version": 1, "habits": [], "extra": True},
            {"version": 2, "habits": []},
            {"version": True, "habits": []},
            {"version": 1, "habits": {}},
        )

        for document in invalid_documents:
            with self.subTest(document=document):
                self.write_document(document)

                with self.assertRaises(InvalidDataError):
                    load_habits(self.data_path, today=TODAY)

    def test_rejects_invalid_habit_fields(self) -> None:
        invalid_habits = (
            {},
            {"name": "Reading"},
            {"name": "Reading", "completions": [], "extra": True},
            {"name": 7, "completions": []},
            {"name": "", "completions": []},
            {"name": " Reading ", "completions": []},
            {"name": "Reading", "completions": {}},
            {"name": "Reading", "completions": [7]},
            {"name": "Reading", "completions": ["not-a-date"]},
            {"name": "Reading", "completions": ["2026-02-30"]},
            {"name": "Reading", "completions": ["2026-09-26"]},
            {"name": "Reading", "completions": ["2026-09-24", "2026-09-24"]},
            {"name": "Reading", "completions": ["2026-09-24", "2026-09-23"]},
        )

        for habit in invalid_habits:
            with self.subTest(habit=habit):
                self.write_document({"version": 1, "habits": [habit]})

                with self.assertRaises(InvalidDataError):
                    load_habits(self.data_path, today=TODAY)

    def test_rejects_duplicate_names_using_casefold(self) -> None:
        self.write_document(
            {
                "version": 1,
                "habits": [
                    {"name": "Straße", "completions": []},
                    {"name": "STRASSE", "completions": []},
                ],
            }
        )

        with self.assertRaises(InvalidDataError):
            load_habits(self.data_path, today=TODAY)


class SaveHabitsTests(StorageTestCase):
    """Verify canonical and atomic writes."""

    def test_saves_canonical_unicode_json_and_round_trips(self) -> None:
        habits = [
            Habit(
                "Práctica",
                {date(2026, 9, 25), date(2026, 9, 23), date(2026, 9, 24)},
            )
        ]

        save_habits(habits, self.data_path, today=TODAY)

        raw_data = self.data_path.read_text(encoding="utf-8")
        document = json.loads(raw_data)
        self.assertIn("Práctica", raw_data)
        self.assertEqual(1, document["version"])
        self.assertEqual(
            ["2026-09-23", "2026-09-24", "2026-09-25"],
            document["habits"][0]["completions"],
        )
        self.assertEqual(habits, load_habits(self.data_path, today=TODAY))

    def test_atomic_replace_uses_same_directory(self) -> None:
        replacement_paths: list[tuple[Path, Path]] = []

        def record_replace(source: str | Path, destination: str | Path) -> None:
            source_path = Path(source)
            destination_path = Path(destination)
            replacement_paths.append((source_path, destination_path))
            self.assertEqual(destination_path.parent, source_path.parent)
            source_path.rename(destination_path)

        with patch("habits.storage.os.replace", side_effect=record_replace):
            save_habits([Habit("Reading")], self.data_path, today=TODAY)

        self.assertEqual(1, len(replacement_paths))
        self.assertTrue(self.data_path.exists())

    def test_replace_failure_preserves_existing_file(self) -> None:
        original_content = '{"original": true}'
        self.data_path.write_text(original_content, encoding="utf-8")

        with patch("habits.storage.os.replace", side_effect=OSError("replace failed")):
            with self.assertRaises(StorageError):
                save_habits([Habit("Reading")], self.data_path, today=TODAY)

        self.assertEqual(original_content, self.data_path.read_text(encoding="utf-8"))
        self.assertEqual([self.data_path], list(self.data_path.parent.iterdir()))

    def test_write_failure_preserves_existing_file(self) -> None:
        original_content = '{"original": true}'
        self.data_path.write_text(original_content, encoding="utf-8")

        with patch("habits.storage.json.dump", side_effect=OSError("write failed")):
            with self.assertRaises(StorageError):
                save_habits([Habit("Reading")], self.data_path, today=TODAY)

        self.assertEqual(original_content, self.data_path.read_text(encoding="utf-8"))
        self.assertEqual([self.data_path], list(self.data_path.parent.iterdir()))


if __name__ == "__main__":
    unittest.main()
