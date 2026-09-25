"""Unit tests for habit domain rules."""

import unittest
from datetime import date, timedelta

from habits.core import (
    DuplicateHabitError,
    Habit,
    HabitNotFoundError,
    InvalidHabitNameError,
    calculate_streak,
    create_habit,
    mark_habit_done,
)


class HabitModelTests(unittest.TestCase):
    """Verify the habit model invariants."""

    def test_habits_have_independent_completion_sets(self) -> None:
        first_habit = Habit("Reading")
        second_habit = Habit("Writing")

        self.assertIsNot(first_habit.completions, second_habit.completions)


class CreateHabitTests(unittest.TestCase):
    """Verify creation and name normalization rules."""

    def test_creates_habit_with_trimmed_display_name(self) -> None:
        habits: list[Habit] = []

        created_habit = create_habit(habits, "  Study Python  ")

        self.assertEqual("Study Python", created_habit.name)
        self.assertEqual([created_habit], habits)
        self.assertEqual(set(), created_habit.completions)

    def test_preserves_display_name_case(self) -> None:
        created_habit = create_habit([], "Practice PyTHon")

        self.assertEqual("Practice PyTHon", created_habit.name)

    def test_rejects_empty_or_whitespace_only_name(self) -> None:
        for invalid_name in ("", "   ", "\t\n"):
            with self.subTest(name=invalid_name):
                habits: list[Habit] = []

                with self.assertRaises(InvalidHabitNameError):
                    create_habit(habits, invalid_name)

                self.assertEqual([], habits)

    def test_rejects_exact_duplicate_without_changing_collection(self) -> None:
        habits = [Habit("Read notes")]

        with self.assertRaises(DuplicateHabitError):
            create_habit(habits, "Read notes")

        self.assertEqual([Habit("Read notes")], habits)

    def test_rejects_duplicate_ignoring_case_and_outer_spaces(self) -> None:
        habits = [Habit("Straße")]

        with self.assertRaises(DuplicateHabitError):
            create_habit(habits, "  STRASSE  ")

        self.assertEqual([Habit("Straße")], habits)


class MarkHabitDoneTests(unittest.TestCase):
    """Verify daily completion rules."""

    def setUp(self) -> None:
        self.habits = [Habit("Study Python")]
        self.today = date(2026, 9, 25)

    def test_records_completion_once(self) -> None:
        was_added = mark_habit_done(self.habits, "Study Python", self.today)

        self.assertTrue(was_added)
        self.assertEqual({self.today}, self.habits[0].completions)

    def test_repeated_completion_is_idempotent(self) -> None:
        mark_habit_done(self.habits, "Study Python", self.today)

        was_added = mark_habit_done(self.habits, "study python", self.today)

        self.assertFalse(was_added)
        self.assertEqual({self.today}, self.habits[0].completions)

    def test_finds_habit_ignoring_case_and_outer_spaces(self) -> None:
        was_added = mark_habit_done(self.habits, "  STUDY PYTHON  ", self.today)

        self.assertTrue(was_added)

    def test_missing_habit_does_not_change_state(self) -> None:
        original_habits = [Habit(habit.name, habit.completions) for habit in self.habits]

        with self.assertRaises(HabitNotFoundError):
            mark_habit_done(self.habits, "Mathematics", self.today)

        self.assertEqual(original_habits, self.habits)


class CalculateStreakTests(unittest.TestCase):
    """Verify current streak calculations."""

    def setUp(self) -> None:
        self.today = date(2026, 9, 25)

    def test_counts_streak_ending_today(self) -> None:
        completions = {
            self.today,
            self.today - timedelta(days=1),
            self.today - timedelta(days=2),
        }

        self.assertEqual(3, calculate_streak(completions, self.today))

    def test_keeps_streak_ending_yesterday(self) -> None:
        completions = {
            self.today - timedelta(days=1),
            self.today - timedelta(days=2),
        }

        self.assertEqual(2, calculate_streak(completions, self.today))

    def test_returns_zero_without_recent_completion(self) -> None:
        cases = (set(), {self.today - timedelta(days=2)})

        for completions in cases:
            with self.subTest(completions=completions):
                self.assertEqual(0, calculate_streak(completions, self.today))

    def test_stops_at_first_missing_day(self) -> None:
        completions = {
            self.today,
            self.today - timedelta(days=1),
            self.today - timedelta(days=3),
        }

        self.assertEqual(2, calculate_streak(completions, self.today))

    def test_counts_single_day_streak(self) -> None:
        for completion in (self.today, self.today - timedelta(days=1)):
            with self.subTest(completion=completion):
                self.assertEqual(1, calculate_streak({completion}, self.today))


if __name__ == "__main__":
    unittest.main()
