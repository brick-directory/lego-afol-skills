import importlib.util
import os
import pathlib
import sys
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
CLI_PATH = ROOT / "skills" / "afol" / "scripts" / "afol_cli.py"

spec = importlib.util.spec_from_file_location("afol_cli", CLI_PATH)
afol_cli = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = afol_cli
spec.loader.exec_module(afol_cli)


class AfolCliTest(unittest.TestCase):
    def test_routes_valuation_to_brickeconomy_first(self):
        result = afol_cli.route("What is set 10236-1 worth?")

        self.assertEqual(result["providers"][0], "brickeconomy")
        self.assertIn("bricklink", result["providers"])
        self.assertIn("valuation", result["reason"])

    def test_routes_catalog_questions_to_rebrickable_first(self):
        result = afol_cli.route("Find parts for Millennium Falcon")

        self.assertEqual(result["providers"][0], "rebrickable")
        self.assertIn("brickset", result["providers"])

    def test_credentials_redact_values(self):
        with mock.patch.dict(os.environ, {"BRICKECONOMY_API_KEY": "secret-value"}, clear=True):
            rows = afol_cli.credentials()

        brickeconomy = next(row for row in rows if row["provider"] == "brickeconomy")
        rebrickable = next(row for row in rows if row["provider"] == "rebrickable")

        self.assertTrue(brickeconomy["ready"])
        self.assertEqual(brickeconomy["missing_required"], [])
        self.assertFalse(rebrickable["ready"])
        self.assertNotIn("secret-value", repr(rows))


if __name__ == "__main__":
    unittest.main()
