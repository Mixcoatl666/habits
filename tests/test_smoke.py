"""Smoke tests for the initial package structure."""

import importlib
import unittest


class PackageStructureTests(unittest.TestCase):
    """Verify that the planned application modules are importable."""

    def test_planned_modules_are_importable(self) -> None:
        module_names = (
            "habits",
            "habits.core",
            "habits.storage",
            "habits.cli",
            "habits.__main__",
        )

        for module_name in module_names:
            with self.subTest(module=module_name):
                imported_module = importlib.import_module(module_name)
                self.assertEqual(module_name, imported_module.__name__)


if __name__ == "__main__":
    unittest.main()
