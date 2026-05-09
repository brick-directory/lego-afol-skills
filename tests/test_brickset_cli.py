from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path
from unittest import mock
from urllib.parse import parse_qs, urlparse

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "skills" / "brickset" / "scripts"))

import brickset_cli  # noqa: E402


class FakeResponse:
    def __init__(self, payload: dict[str, object]):
        self.payload = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return self.payload


class BricksetCliTests(unittest.TestCase):
    def test_getsets_posts_form_with_api_key_user_hash_and_params_json(self) -> None:
        captured = {}

        def fake_urlopen(request, timeout):
            captured["method"] = request.get_method()
            captured["url"] = request.full_url
            captured["data"] = request.data.decode()
            captured["content_type"] = request.get_header("Content-type")
            captured["timeout"] = timeout
            return FakeResponse({"status": "success", "sets": []})

        with mock.patch.dict(os.environ, {"BRICKSET_API_KEY": "secret"}, clear=True), mock.patch("urllib.request.urlopen", fake_urlopen), mock.patch("sys.stdout"):
            rc = brickset_cli.main(["details", "--set-number", "10270-1"])

        self.assertEqual(rc, 0)
        self.assertEqual(captured["method"], "POST")
        self.assertEqual(urlparse(captured["url"]).path, "/api/v3.asmx/getSets")
        self.assertEqual(captured["content_type"], "application/x-www-form-urlencoded")
        body = parse_qs(captured["data"], keep_blank_values=True)
        self.assertEqual(body["apiKey"], ["secret"])
        self.assertEqual(body["userHash"], [""])
        self.assertEqual(json.loads(body["params"][0]), {"setNumber": "10270-1"})

    def test_media_endpoint_quirks_use_set_id_or_set_number_as_specified(self) -> None:
        captured_paths_and_bodies = []

        def fake_urlopen(request, timeout):
            captured_paths_and_bodies.append((urlparse(request.full_url).path, parse_qs(request.data.decode(), keep_blank_values=True)))
            return FakeResponse({"status": "success"})

        with mock.patch.dict(os.environ, {"BRICKSET_API_KEY": "secret"}, clear=True), mock.patch("urllib.request.urlopen", fake_urlopen), mock.patch("sys.stdout"):
            self.assertEqual(brickset_cli.main(["images", "--set-id", "30142"]), 0)
            self.assertEqual(brickset_cli.main(["reviews", "--set-id", "30142"]), 0)
            self.assertEqual(brickset_cli.main(["instructions", "--set-number", "10270-1"]), 0)

        self.assertEqual(captured_paths_and_bodies[0][0], "/api/v3.asmx/getAdditionalImages")
        self.assertEqual(captured_paths_and_bodies[0][1]["setID"], ["30142"])
        self.assertEqual(captured_paths_and_bodies[1][0], "/api/v3.asmx/getReviews")
        self.assertEqual(captured_paths_and_bodies[1][1]["setID"], ["30142"])
        self.assertEqual(captured_paths_and_bodies[2][0], "/api/v3.asmx/getInstructions2")
        self.assertEqual(captured_paths_and_bodies[2][1]["setNumber"], ["10270-1"])

    def test_private_reads_require_user_hash(self) -> None:
        with mock.patch.dict(os.environ, {"BRICKSET_API_KEY": "secret"}, clear=True), mock.patch("urllib.request.urlopen") as urlopen, mock.patch("sys.stderr"):
            rc = brickset_cli.main(["collection"])

        self.assertEqual(rc, 2)
        urlopen.assert_not_called()

    def test_collection_set_requires_yes_or_dry_run(self) -> None:
        with mock.patch.dict(os.environ, {"BRICKSET_API_KEY": "secret", "BRICKSET_USER_HASH": "hash"}, clear=True), mock.patch("urllib.request.urlopen") as urlopen, mock.patch("sys.stderr"):
            rc = brickset_cli.main(["collection-set", "--set-id", "30142", "--own", "1"])

        self.assertEqual(rc, 2)
        urlopen.assert_not_called()

    def test_dry_run_does_not_require_api_key_and_redacts_credentials(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch("urllib.request.urlopen") as urlopen, mock.patch("sys.stdout") as stdout:
            rc = brickset_cli.main(["collection-set", "--dry-run", "--set-id", "30142", "--own", "1", "--qty-owned", "2"])

        self.assertEqual(rc, 0)
        urlopen.assert_not_called()
        output = "".join(call.args[0] for call in stdout.write.call_args_list if call.args)
        self.assertIn('"apiKey": "[from BRICKSET_API_KEY]"', output)
        self.assertIn('"userHash": "[from BRICKSET_USER_HASH]"', output)
        self.assertIn('"path": "/setCollection"', output)
        self.assertIn('\\"own\\":1', output)
        self.assertIn('\\"qtyOwned\\":2', output)

    def test_collection_set_yes_posts_params_json_with_user_hash(self) -> None:
        captured = {}

        def fake_urlopen(request, timeout):
            captured["url"] = request.full_url
            captured["data"] = request.data.decode()
            return FakeResponse({"status": "success"})

        with mock.patch.dict(os.environ, {"BRICKSET_API_KEY": "secret", "BRICKSET_USER_HASH": "hash"}, clear=True), mock.patch("urllib.request.urlopen", fake_urlopen), mock.patch("sys.stdout"):
            rc = brickset_cli.main(["collection-set", "--yes", "--set-id", "30142", "--want", "1", "--rating", "5"])

        self.assertEqual(rc, 0)
        self.assertEqual(urlparse(captured["url"]).path, "/api/v3.asmx/setCollection")
        body = parse_qs(captured["data"], keep_blank_values=True)
        self.assertEqual(body["apiKey"], ["secret"])
        self.assertEqual(body["userHash"], ["hash"])
        self.assertEqual(body["setID"], ["30142"])
        self.assertEqual(json.loads(body["params"][0]), {"want": 1, "rating": 5})

    def test_login_omits_user_hash_and_uses_username_password_env(self) -> None:
        captured = {}

        def fake_urlopen(request, timeout):
            captured["url"] = request.full_url
            captured["data"] = request.data.decode()
            return FakeResponse({"status": "success", "hash": "userhash"})

        env = {"BRICKSET_API_KEY": "secret", "BRICKSET_USERNAME": "tester", "BRICKSET_PASSWORD": "password"}
        with mock.patch.dict(os.environ, env, clear=True), mock.patch("urllib.request.urlopen", fake_urlopen), mock.patch("sys.stdout"):
            rc = brickset_cli.main(["login"])

        self.assertEqual(rc, 0)
        self.assertEqual(urlparse(captured["url"]).path, "/api/v3.asmx/login")
        body = parse_qs(captured["data"], keep_blank_values=True)
        self.assertEqual(body["apiKey"], ["secret"])
        self.assertEqual(body["username"], ["tester"])
        self.assertEqual(body["password"], ["password"])
        self.assertNotIn("userHash", body)


if __name__ == "__main__":
    unittest.main()
