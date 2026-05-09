from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path
from unittest import mock
from urllib.parse import parse_qs, urlparse

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "skills" / "bricklink" / "scripts"))

import bricklink_cli  # noqa: E402


ENV = {
    "BRICKLINK_API_CONSUMER_KEY": "consumer-key",
    "BRICKLINK_API_CONSUMER_SECRET": "consumer-secret",
    "BRICKLINK_API_TOKEN_VALUE": "token-value",
    "BRICKLINK_API_TOKEN_SECRET": "token-secret",
}


class FakeResponse:
    def __init__(self, payload: dict[str, object]):
        self.payload = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return self.payload


class BrickLinkCliTests(unittest.TestCase):
    def test_get_uses_oauth_header_not_query_or_body(self) -> None:
        captured = {}

        def fake_urlopen(request, timeout):
            captured["method"] = request.get_method()
            captured["url"] = request.full_url
            captured["data"] = request.data
            captured["auth"] = request.get_header("Authorization")
            captured["timeout"] = timeout
            return FakeResponse({"meta": {"code": 200}, "data": []})

        with mock.patch.dict(os.environ, ENV, clear=False), mock.patch("urllib.request.urlopen", fake_urlopen), mock.patch("sys.stdout"):
            rc = bricklink_cli.main(["item-price", "--type", "SET", "--no", "75192-1", "--guide-type", "sold", "--new-or-used", "N", "--currency-code", "EUR"])

        self.assertEqual(rc, 0)
        self.assertEqual(captured["method"], "GET")
        self.assertIsNone(captured["data"])
        parsed = urlparse(captured["url"])
        self.assertEqual(parsed.path, "/api/store/v1/items/SET/75192-1/price")
        query = parse_qs(parsed.query)
        self.assertEqual(query["guide_type"], ["sold"])
        self.assertEqual(query["currency_code"], ["EUR"])
        self.assertNotIn("oauth_consumer_key", query)
        self.assertTrue(captured["auth"].startswith("OAuth "))
        self.assertIn('oauth_consumer_key="consumer-key"', captured["auth"])
        self.assertIn('oauth_token="token-value"', captured["auth"])

    def test_post_uses_oauth_header_and_json_body(self) -> None:
        captured = {}

        def fake_urlopen(request, timeout):
            captured["method"] = request.get_method()
            captured["url"] = request.full_url
            captured["data"] = request.data.decode()
            captured["auth"] = request.get_header("Authorization")
            captured["content_type"] = request.get_header("Content-type")
            return FakeResponse({"meta": {"code": 200}, "data": {"inventory_id": 123}})

        with mock.patch.dict(os.environ, ENV, clear=False), mock.patch("urllib.request.urlopen", fake_urlopen), mock.patch("sys.stdout"):
            rc = bricklink_cli.main(["inventory-create", "--yes", "--json", '{"quantity":2,"unit_price":"1.25"}'])

        self.assertEqual(rc, 0)
        self.assertEqual(captured["method"], "POST")
        self.assertEqual(urlparse(captured["url"]).path, "/api/store/v1/inventories")
        body = json.loads(captured["data"])
        self.assertEqual(body["quantity"], 2)
        self.assertNotIn("oauth_consumer_key", body)
        self.assertEqual(captured["content_type"], "application/json")
        self.assertIn('oauth_consumer_key="consumer-key"', captured["auth"])

    def test_mutating_command_requires_yes_or_dry_run(self) -> None:
        with mock.patch.dict(os.environ, ENV, clear=False), mock.patch("urllib.request.urlopen") as urlopen, mock.patch("sys.stderr"):
            rc = bricklink_cli.main(["inventory-delete", "--inventory-id", "123"])

        self.assertEqual(rc, 2)
        urlopen.assert_not_called()

    def test_dry_run_does_not_require_credentials_and_redacts_auth(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch("urllib.request.urlopen") as urlopen, mock.patch("sys.stdout") as stdout:
            rc = bricklink_cli.main(["coupon-delete", "--dry-run", "--coupon-id", "44"])

        self.assertEqual(rc, 0)
        urlopen.assert_not_called()
        output = "".join(call.args[0] for call in stdout.write.call_args_list if call.args)
        self.assertIn('"auth": "OAuth1 from BRICKLINK_API_* environment variables"', output)
        self.assertIn('"path": "/coupons/44"', output)
        self.assertNotIn("consumer-key", output)

    def test_item_mapping_uses_part_mapping_endpoint_quirk(self) -> None:
        captured = {}

        def fake_urlopen(request, timeout):
            captured["url"] = request.full_url
            return FakeResponse({"meta": {"code": 200}, "data": []})

        with mock.patch.dict(os.environ, ENV, clear=False), mock.patch("urllib.request.urlopen", fake_urlopen), mock.patch("sys.stdout"):
            rc = bricklink_cli.main(["item-mapping", "--type", "PART", "--no", "3001", "--color-id", "5"])

        self.assertEqual(rc, 0)
        parsed = urlparse(captured["url"])
        self.assertEqual(parsed.path, "/api/store/v1/item_mapping/PART/3001")
        self.assertEqual(parse_qs(parsed.query)["color_id"], ["5"])

    def test_element_mapping_uses_single_element_id_endpoint_quirk(self) -> None:
        captured = {}

        def fake_urlopen(request, timeout):
            captured["url"] = request.full_url
            return FakeResponse({"meta": {"code": 200}, "data": {}})

        with mock.patch.dict(os.environ, ENV, clear=False), mock.patch("urllib.request.urlopen", fake_urlopen), mock.patch("sys.stdout"):
            rc = bricklink_cli.main(["element-mapping", "--element-id", "4211111"])

        self.assertEqual(rc, 0)
        self.assertEqual(urlparse(captured["url"]).path, "/api/store/v1/item_mapping/4211111")


if __name__ == "__main__":
    unittest.main()
