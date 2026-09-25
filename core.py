"""Domain rules for study habits and streaks."""

from dataclasses import dataclass, field
from datetime import date, timedelta


class HabitError(Exception):
    """Base class for habit domain errors."""


class InvalidHabitNameError(HabitError):
    """Raised when a habit name is empty after trimming."""


class DuplicateHabitError(HabitError):
    """Raised when a habit name is already in use."""


class HabitNotFoundError(HabitError):
    """Raised when a requested habit does not exist."""


@dataclass(slots=True)
class Habit:
    """A study habit and its unique completion dates."""

    name: str
    completions: set[date] = field(default_factory=set)

    def __post_init__(self) -> None:
        trimmed_name = self.name.strip()
        if not trimmed_name:
            raise InvalidHabitNameError

        self.name = trimmed_name
        self.completions = set(self.completions)


def create_habit(habits: list[Habit], name: str) -> Habit:
    """Create and append a uniquely named habit."""
    habit = Habit(name=name)
    comparison_key = habit.name.casefold()

    if any(existing.name.casefold() == comparison_key for existing in habits):
        raise DuplicateHabitError

    habits.append(habit)
    return habit


def mark_habit_done(habits: list[Habit], name: str, completed_on: date) -> bool:
    """Record a completion and report whether a new date was added."""
    comparison_key = name.strip().casefold()
    habit = next(
        (
            existing
            for existing in habits
            if existing.name.casefold() == comparison_key
        ),
        None,
    )
    if habit is None:
        raise HabitNotFoundError

    previous_count = len(habit.completions)
    habit.completions.add(completed_on)
    return len(habit.completions) > previous_count


def calculate_streak(completions: set[date], today: date) -> int:
    """Return the current streak ending today or yesterday."""
    yesterday = today - timedelta(days=1)
    if today in completions:
        current_day = today
    elif yesterday in completions:
        current_day = yesterday
    else:
        return 0

    streak = 0
    while current_day in completions:
        streak += 1
        current_day -= timedelta(days=1)

    return streak
