from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path
from unittest import mock
from urllib.parse import parse_qs, urlparse

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "skills" / "brickeconomy" / "scripts"))

import brickeconomy_cli  # noqa: E402


class FakeResponse:
    def __init__(self, payload: dict[str, object]):
        self.payload = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return self.payload


class BrickEconomyCliTests(unittest.TestCase):
    def test_get_places_api_key_in_x_apikey_header_not_query(self) -> None:
        captured = {}

        def fake_urlopen(request, timeout):
            captured["method"] = request.get_method()
            captured["url"] = request.full_url
            captured["data"] = request.data
            captured["timeout"] = timeout
            captured["x_apikey"] = request.get_header("X-apikey")
            return FakeResponse({"data": {"set_number": "10236-1"}})

        with mock.patch.dict(os.environ, {"BRICKECONOMY_API_KEY": "secret"}, clear=False), mock.patch("urllib.request.urlopen", fake_urlopen), mock.patch("sys.stdout"):
            rc = brickeconomy_cli.main(["set", "--set-number", "10236-1", "--currency", "EUR"])

        self.assertEqual(rc, 0)
        self.assertEqual(captured["method"], "GET")
        self.assertIsNone(captured["data"])
        self.assertEqual(captured["x_apikey"], "secret")
        parsed = urlparse(captured["url"])
        self.assertEqual(parsed.path, "/api/v1/set/10236-1")
        query = parse_qs(parsed.query)
        self.assertNotIn("key", query)
        self.assertNotIn("apikey", query)
        self.assertEqual(query["currency"], ["EUR"])

    def test_minifig_uses_checked_in_endpoint_shape(self) -> None:
        captured = {}

        def fake_urlopen(request, timeout):
            captured["url"] = request.full_url
            return FakeResponse({"data": {"minifig_number": "sw0509"}})

        with mock.patch.dict(os.environ, {"BRICKECONOMY_API_KEY": "secret"}, clear=False), mock.patch("urllib.request.urlopen", fake_urlopen), mock.patch("sys.stdout"):
            rc = brickeconomy_cli.main(["minifig", "--minifig-number", "sw0509", "--currency", "USD"])

        self.assertEqual(rc, 0)
        self.assertEqual(urlparse(captured["url"]).path, "/api/v1/minifig/sw0509")

    def test_collection_sets_sends_currency_query(self) -> None:
        captured = {}

        def fake_urlopen(request, timeout):
            captured["url"] = request.full_url
            return FakeResponse({"data": []})

        with mock.patch.dict(os.environ, {"BRICKECONOMY_API_KEY": "secret"}, clear=False), mock.patch("urllib.request.urlopen", fake_urlopen), mock.patch("sys.stdout"):
            rc = brickeconomy_cli.main(["collection-sets", "--currency", "PLN"])

        self.assertEqual(rc, 0)
        parsed = urlparse(captured["url"])
        self.assertEqual(parsed.path, "/api/v1/collection/sets")
        self.assertEqual(parse_qs(parsed.query)["currency"], ["PLN"])

    def test_sales_ledger_has_no_currency_query_parameter(self) -> None:
        captured = {}

        def fake_urlopen(request, timeout):
            captured["url"] = request.full_url
            return FakeResponse({"data": []})

        with mock.patch.dict(os.environ, {"BRICKECONOMY_API_KEY": "secret"}, clear=False), mock.patch("urllib.request.urlopen", fake_urlopen), mock.patch("sys.stdout"):
            rc = brickeconomy_cli.main(["sales-ledger"])

        self.assertEqual(rc, 0)
        parsed = urlparse(captured["url"])
        self.assertEqual(parsed.path, "/api/v1/salesledger")
        self.assertEqual(parsed.query, "")

    def test_dry_run_does_not_require_api_key_and_redacts_header(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch("urllib.request.urlopen") as urlopen, mock.patch("sys.stdout") as stdout:
            rc = brickeconomy_cli.main(["set", "--dry-run", "--set-number", "10236-1", "--currency", "EUR"])

        self.assertEqual(rc, 0)
        urlopen.assert_not_called()
        output = "".join(call.args[0] for call in stdout.write.call_args_list if call.args)
        self.assertIn('"x-apikey": "[from BRICKECONOMY_API_KEY]"', output)
        self.assertIn('"path": "/set/10236-1"', output)
        self.assertIn('"currency": "EUR"', output)

    def test_live_call_requires_api_key(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch("urllib.request.urlopen") as urlopen, mock.patch("sys.stderr"):
            rc = brickeconomy_cli.main(["collection-minifigs"])

        self.assertEqual(rc, 2)
        urlopen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
