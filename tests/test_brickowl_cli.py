from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path
from unittest import mock
from urllib.parse import parse_qs, urlparse

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "skills" / "brickowl" / "scripts"))

import brickowl_cli  # noqa: E402


class FakeResponse:
    def __init__(self, payload: dict[str, object]):
        self.payload = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return self.payload


class BrickOwlCliTests(unittest.TestCase):
    def test_get_places_key_in_query_string(self) -> None:
        captured = {}

        def fake_urlopen(request, timeout):
            captured["method"] = request.get_method()
            captured["url"] = request.full_url
            captured["data"] = request.data
            captured["timeout"] = timeout
            return FakeResponse({"ok": True})

        with mock.patch.dict(os.environ, {"BRICKOWL_API_KEY": "secret"}, clear=False), mock.patch("urllib.request.urlopen", fake_urlopen), mock.patch("sys.stdout"):
            rc = brickowl_cli.main(["id-lookup", "--id", "75192-1", "--type", "Set", "--id-type", "set_number"])

        self.assertEqual(rc, 0)
        self.assertEqual(captured["method"], "GET")
        self.assertIsNone(captured["data"])
        parsed = urlparse(captured["url"])
        self.assertEqual(parsed.path, "/v1/catalog/id_lookup")
        query = parse_qs(parsed.query)
        self.assertEqual(query["key"], ["secret"])
        self.assertEqual(query["id"], ["75192-1"])
        self.assertEqual(query["id_type"], ["set_number"])

    def test_post_places_key_in_form_body(self) -> None:
        captured = {}

        def fake_urlopen(request, timeout):
            captured["method"] = request.get_method()
            captured["url"] = request.full_url
            captured["data"] = request.data.decode()
            captured["content_type"] = request.get_header("Content-type")
            return FakeResponse({"success": True, "lot_id": 123})

        with mock.patch.dict(os.environ, {"BRICKOWL_API_KEY": "secret"}, clear=False), mock.patch("urllib.request.urlopen", fake_urlopen), mock.patch("sys.stdout"):
            rc = brickowl_cli.main(
                [
                    "inventory-create",
                    "--yes",
                    "--boid",
                    "98765",
                    "--quantity",
                    "2",
                    "--price",
                    "1.25",
                    "--condition",
                    "news",
                ]
            )

        self.assertEqual(rc, 0)
        self.assertEqual(captured["method"], "POST")
        self.assertEqual(urlparse(captured["url"]).path, "/v1/inventory/create")
        body = parse_qs(captured["data"])
        self.assertEqual(body["key"], ["secret"])
        self.assertEqual(body["boid"], ["98765"])
        self.assertEqual(body["condition"], ["news"])
        self.assertEqual(captured["content_type"], "application/x-www-form-urlencoded")

    def test_mutating_command_requires_yes_or_dry_run(self) -> None:
        with mock.patch.dict(os.environ, {"BRICKOWL_API_KEY": "secret"}, clear=False), mock.patch("urllib.request.urlopen") as urlopen, mock.patch("sys.stderr"):
            rc = brickowl_cli.main(["inventory-delete", "--lot-id", "123"])

        self.assertEqual(rc, 2)
        urlopen.assert_not_called()

    def test_dry_run_does_not_require_api_key_and_redacts_key(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch("urllib.request.urlopen") as urlopen, mock.patch("sys.stdout") as stdout:
            rc = brickowl_cli.main(["inventory-delete", "--dry-run", "--lot-id", "123"])

        self.assertEqual(rc, 0)
        urlopen.assert_not_called()
        output = "".join(call.args[0] for call in stdout.write.call_args_list if call.args)
        self.assertIn('"key": "[from BRICKOWL_API_KEY]"', output)
        self.assertIn('"delete": "true"', output)

    def test_update_requires_identifier_and_change(self) -> None:
        with mock.patch.dict(os.environ, {"BRICKOWL_API_KEY": "secret"}, clear=False), mock.patch("urllib.request.urlopen") as urlopen, mock.patch("sys.stderr"):
            rc = brickowl_cli.main(["inventory-update", "--yes", "--price", "9.99"])

        self.assertEqual(rc, 2)
        urlopen.assert_not_called()

        with mock.patch.dict(os.environ, {"BRICKOWL_API_KEY": "secret"}, clear=False), mock.patch("urllib.request.urlopen") as urlopen, mock.patch("sys.stderr"):
            rc = brickowl_cli.main(["inventory-update", "--yes", "--lot-id", "123"])

        self.assertEqual(rc, 2)
        urlopen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
