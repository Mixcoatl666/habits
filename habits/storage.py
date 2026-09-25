"""Local persistence for study habits."""

import json
import os
import tempfile
from datetime import date
from pathlib import Path

from habits.core import Habit


DATA_VERSION = 1


class StorageError(Exception):
    """Raised when stored data cannot be read or written."""


class InvalidDataError(StorageError):
    """Raised when stored data does not match the expected schema."""


def default_data_path() -> Path:
    """Return the user-local path for the habits document."""
    return Path.home() / ".habits-cli" / "habits.json"


def load_habits(
    path: Path | None = None,
    *,
    today: date | None = None,
) -> list[Habit]:
    """Load and fully validate habits from a JSON document."""
    data_path = path if path is not None else default_data_path()
    current_date = today if today is not None else date.today()

    try:
        raw_data = data_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    except UnicodeDecodeError as error:
        raise InvalidDataError from error
    except OSError as error:
        raise StorageError from error

    try:
        document = json.loads(raw_data)
    except json.JSONDecodeError as error:
        raise InvalidDataError from error

    return _document_to_habits(document, current_date)


def save_habits(
    habits: list[Habit],
    path: Path | None = None,
    *,
    today: date | None = None,
) -> None:
    """Validate and atomically save habits to a JSON document."""
    data_path = path if path is not None else default_data_path()
    current_date = today if today is not None else date.today()
    document = _habits_to_document(habits, current_date)
    temporary_path: Path | None = None

    try:
        data_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=data_path.parent,
            prefix=f".{data_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            json.dump(document, temporary_file, ensure_ascii=False, indent=2)
            temporary_file.write("\n")
            temporary_file.flush()
            os.fsync(temporary_file.fileno())

        os.replace(temporary_path, data_path)
        temporary_path = None
    except OSError as error:
        raise StorageError from error
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass


def _document_to_habits(document: object, today: date) -> list[Habit]:
    if type(document) is not dict or set(document) != {"version", "habits"}:
        raise InvalidDataError
    if type(document["version"]) is not int or document["version"] != DATA_VERSION:
        raise InvalidDataError

    stored_habits = document["habits"]
    if type(stored_habits) is not list:
        raise InvalidDataError

    habits: list[Habit] = []
    seen_names: set[str] = set()
    for stored_habit in stored_habits:
        if type(stored_habit) is not dict or set(stored_habit) != {
            "name",
            "completions",
        }:
            raise InvalidDataError

        name = stored_habit["name"]
        if type(name) is not str or not name or name != name.strip():
            raise InvalidDataError
        comparison_key = name.casefold()
        if comparison_key in seen_names:
            raise InvalidDataError
        seen_names.add(comparison_key)

        stored_completions = stored_habit["completions"]
        if type(stored_completions) is not list:
            raise InvalidDataError
        completions = _parse_completion_dates(stored_completions, today)
        habits.append(Habit(name, set(completions)))

    return habits


def _parse_completion_dates(values: list[object], today: date) -> list[date]:
    completions: list[date] = []
    for value in values:
        if type(value) is not str:
            raise InvalidDataError
        try:
            completion = date.fromisoformat(value)
        except ValueError as error:
            raise InvalidDataError from error
        if completion.isoformat() != value or completion > today:
            raise InvalidDataError
        completions.append(completion)

    if completions != sorted(completions) or len(completions) != len(set(completions)):
        raise InvalidDataError
    return completions


def _habits_to_document(habits: list[Habit], today: date) -> dict[str, object]:
    stored_habits: list[dict[str, object]] = []
    seen_names: set[str] = set()

    for habit in habits:
        if type(habit) is not Habit:
            raise InvalidDataError
        if type(habit.name) is not str or not habit.name or habit.name != habit.name.strip():
            raise InvalidDataError

        comparison_key = habit.name.casefold()
        if comparison_key in seen_names:
            raise InvalidDataError
        seen_names.add(comparison_key)

        if type(habit.completions) is not set:
            raise InvalidDataError
        for completion in habit.completions:
            if type(completion) is not date or completion > today:
                raise InvalidDataError

        stored_habits.append(
            {
                "name": habit.name,
                "completions": [
                    completion.isoformat()
                    for completion in sorted(habit.completions)
                ],
            }
        )

    return {"version": DATA_VERSION, "habits": stored_habits}
