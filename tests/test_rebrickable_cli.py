from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path
from unittest import mock
from urllib.parse import parse_qs, urlparse

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "skills" / "rebrickable" / "scripts"))

import rebrickable_cli  # noqa: E402


class FakeResponse:
    def __init__(self, payload: dict[str, object] | list[object] | None = None):
        self.payload = b"" if payload is None else json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return self.payload


class RebrickableCliTests(unittest.TestCase):
    def test_get_places_api_key_in_authorization_header(self) -> None:
        captured = {}

        def fake_urlopen(request, timeout):
            captured["method"] = request.get_method()
            captured["url"] = request.full_url
            captured["data"] = request.data
            captured["authorization"] = request.get_header("Authorization")
            captured["timeout"] = timeout
            return FakeResponse({"set_num": "75192-1"})

        with mock.patch.dict(os.environ, {"REBRICKABLE_API_KEY": "secret"}, clear=False), mock.patch("urllib.request.urlopen", fake_urlopen), mock.patch("sys.stdout"):
            rc = rebrickable_cli.main(["set", "--set-num", "75192-1"])

        self.assertEqual(rc, 0)
        self.assertEqual(captured["method"], "GET")
        self.assertIsNone(captured["data"])
        self.assertEqual(captured["authorization"], "key secret")
        parsed = urlparse(captured["url"])
        self.assertEqual(parsed.path, "/api/v3/lego/sets/75192-1/")

    def test_catalog_search_uses_search_query_parameter(self) -> None:
        captured = {}

        def fake_urlopen(request, timeout):
            captured["url"] = request.full_url
            return FakeResponse({"results": []})

        with mock.patch.dict(os.environ, {"REBRICKABLE_API_KEY": "secret"}, clear=False), mock.patch("urllib.request.urlopen", fake_urlopen), mock.patch("sys.stdout"):
            rc = rebrickable_cli.main(["sets", "--search", "falcon", "--page-size", "1"])

        self.assertEqual(rc, 0)
        query = parse_qs(urlparse(captured["url"]).query)
        self.assertEqual(query["search"], ["falcon"])
        self.assertEqual(query["page_size"], ["1"])
        self.assertNotIn("query", query)

    def test_add_sets_to_list_sends_json_array(self) -> None:
        captured = {}

        def fake_urlopen(request, timeout):
            captured["method"] = request.get_method()
            captured["url"] = request.full_url
            captured["data"] = request.data.decode()
            captured["content_type"] = request.get_header("Content-type")
            captured["authorization"] = request.get_header("Authorization")
            return FakeResponse([{"set_num": "8043-1"}])

        with mock.patch.dict(os.environ, {"REBRICKABLE_API_KEY": "secret", "REBRICKABLE_USER_TOKEN": "user-token"}, clear=False), mock.patch("urllib.request.urlopen", fake_urlopen), mock.patch("sys.stdout"):
            rc = rebrickable_cli.main(
                [
                    "add-sets-to-list",
                    "--yes",
                    "--list-id",
                    "123",
                    "--sets-json",
                    '[{"set_num":"8043-1","quantity":1}]',
                ]
            )

        self.assertEqual(rc, 0)
        self.assertEqual(captured["method"], "POST")
        self.assertEqual(urlparse(captured["url"]).path, "/api/v3/users/user-token/setlists/123/sets/")
        self.assertEqual(captured["content_type"], "application/json")
        self.assertEqual(captured["authorization"], "key secret")
        self.assertIsInstance(json.loads(captured["data"]), list)

    def test_add_sets_to_list_rejects_non_array_json(self) -> None:
        with mock.patch.dict(os.environ, {"REBRICKABLE_API_KEY": "secret", "REBRICKABLE_USER_TOKEN": "user-token"}, clear=False), mock.patch("urllib.request.urlopen") as urlopen, mock.patch("sys.stderr"):
            rc = rebrickable_cli.main(["add-sets-to-list", "--yes", "--list-id", "123", "--sets-json", '{"set_num":"8043-1"}'])

        self.assertEqual(rc, 2)
        urlopen.assert_not_called()

    def test_mutating_command_requires_yes_or_dry_run(self) -> None:
        with mock.patch.dict(os.environ, {"REBRICKABLE_API_KEY": "secret", "REBRICKABLE_USER_TOKEN": "user-token"}, clear=False), mock.patch("urllib.request.urlopen") as urlopen, mock.patch("sys.stderr"):
            rc = rebrickable_cli.main(["remove-set-from-list", "--list-id", "123", "--set-num", "8043-1"])

        self.assertEqual(rc, 2)
        urlopen.assert_not_called()

    def test_dry_run_does_not_require_api_key_and_redacts_header(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch("urllib.request.urlopen") as urlopen, mock.patch("sys.stdout") as stdout:
            rc = rebrickable_cli.main(
                [
                    "add-part-to-list",
                    "--dry-run",
                    "--user-token",
                    "user-token",
                    "--list-id",
                    "456",
                    "--part-num",
                    "3001",
                    "--color-id",
                    "72",
                    "--quantity",
                    "4",
                ]
            )

        self.assertEqual(rc, 0)
        urlopen.assert_not_called()
        output = "".join(call.args[0] for call in stdout.write.call_args_list if call.args)
        self.assertIn('"Authorization": "key [from REBRICKABLE_API_KEY]"', output)
        self.assertIn('"part_num": "3001"', output)
        self.assertNotIn("secret", output)

    def test_user_command_requires_user_token(self) -> None:
        with mock.patch.dict(os.environ, {"REBRICKABLE_API_KEY": "secret"}, clear=True), mock.patch("urllib.request.urlopen") as urlopen, mock.patch("sys.stderr"):
            rc = rebrickable_cli.main(["profile"])

        self.assertEqual(rc, 2)
        urlopen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
