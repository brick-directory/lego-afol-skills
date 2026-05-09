---
name: bricklink
description: "Use when working with BrickLink marketplace data and seller-account workflows: orders, inventory, item lookup, images, supersets/subsets, price guides, colors, feedback, coupons, notifications, shipping methods, and member notes."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [lego, afol, bricklink, marketplace, inventory, pricing]
    related_skills: []
---

# BrickLink AFOL Skill

## Overview

Use this skill to call BrickLink's OAuth 1.0 API from an agent workflow using the verified Brick Directory OpenAPI copy at `references/openapi/bricklink.yaml` and the Brick Directory MCP prompt guidance at `references/prompts/bricklink-tools.txt`.

BrickLink is a real marketplace. Reads are usually safe, but account writes can change listings, order state, buyer/seller feedback, coupons, and private member notes. Stored credentials are not permission to mutate anything. Mutating operations require explicit user intent in the current conversation.

## Required Environment Variables

Set all four OAuth 1.0 credentials in the shell or an ignored `.env` file. Never commit values.

```bash
export BRICKLINK_CONSUMER_KEY="..."
export BRICKLINK_CONSUMER_SECRET="..."
export BRICKLINK_TOKEN="..."
export BRICKLINK_TOKEN_SECRET="..."
```

The production API base URL from the verified spec is:

```bash
export BRICKLINK_BASE_URL="https://api.bricklink.com/api/store/v1"
```

`BRICKLINK_BASE_URL` is optional; default to the value above if unset.

## Source References

- OpenAPI source: `references/openapi/bricklink.yaml`
- Brick Directory prompt source: `references/prompts/bricklink-tools.txt`
- Source inventory and safety matrix: `docs/source-inventory.md`

Do not scrape vendor docs as a replacement for these checked-in sources. If the skill and the copied OpenAPI disagree, inspect Brick Directory's source repo and update the copied references through the repo script before changing behavior.

## Auth Pattern

Use OAuth 1.0a signing. The simplest repeatable smoke pattern is Python with `requests-oauthlib`:

```bash
python - <<'PY'
import os, sys, requests
from requests_oauthlib import OAuth1

base = os.getenv("BRICKLINK_BASE_URL", "https://api.bricklink.com/api/store/v1")
required = [
    "BRICKLINK_CONSUMER_KEY",
    "BRICKLINK_CONSUMER_SECRET",
    "BRICKLINK_TOKEN",
    "BRICKLINK_TOKEN_SECRET",
]
missing = [name for name in required if not os.getenv(name)]
if missing:
    sys.exit("missing env vars: " + ", ".join(missing))

auth = OAuth1(
    os.environ["BRICKLINK_CONSUMER_KEY"],
    os.environ["BRICKLINK_CONSUMER_SECRET"],
    os.environ["BRICKLINK_TOKEN"],
    os.environ["BRICKLINK_TOKEN_SECRET"],
)
resp = requests.get(f"{base}/colors", auth=auth, timeout=30)
print(resp.status_code)
print(resp.text[:1000])
resp.raise_for_status()
PY
```

If `requests-oauthlib` is missing, install it only with user approval when working in a persistent environment:

```bash
python -m pip install requests-oauthlib
```

## Safety Rules

### Allowed without extra confirmation

Read-only calls are safe to run once credentials and the requested target are clear:

- Orders: list/view orders, order items, order messages, order feedback.
- Inventory: list/view store inventory.
- Catalog: item details, item images, supersets, subsets, price guide, known colors, categories, color metadata, item mapping.
- Account/reference: feedback list/view, notifications, coupons list/view, shipping methods, member ratings, member notes read.

Still avoid needless fan-out. Price and inventory loops can consume quota and take time.

### Requires explicit user intent before every write

Before a write, restate the exact platform, operation, target ID/user/order, payload summary, and whether it is destructive. Proceed only after the user clearly asks for that write in the current conversation.

Mutating BrickLink surfaces:

- Orders: `PUT /orders/{order_id}`, `PUT /orders/{order_id}/status`, `PUT /orders/{order_id}/payment_status`, `POST /orders/{order_id}/drive_thru`.
- Inventory: `POST /inventories`, `PUT /inventories/{inventory_id}`, `DELETE /inventories/{inventory_id}`.
- Feedback: `POST /feedback`, `POST /feedback/{feedback_id}/reply`.
- Coupons: `POST /coupons`, `PUT /coupons/{coupon_id}`, `DELETE /coupons/{coupon_id}`.
- Member notes: `POST /members/{username}/my_notes`, `PUT /members/{username}/my_notes`, `DELETE /members/{username}/my_notes`.

### Destructive operations

Deletes and irreversible marketplace/account changes are destructive. Ask for confirmation immediately before execution even if the user discussed the goal earlier. Do not batch destructive operations unless the user explicitly approves the batch and the exact list of IDs.

### Ambiguous marketplace requests

If the user says “update my listing”, “message the buyer”, “leave feedback”, “create a coupon”, or “note this member” without enough target detail, ask for the missing order ID, inventory ID, coupon ID, username, or payload. Guessing here is how a bot becomes a tiny marketplace goblin.

## Endpoint Coverage

| Area | Method/path | Safety | Use |
|---|---|---|---|
| Orders | `GET /orders` | read | List orders by `direction`, `status`, `filed`. |
| Orders | `GET /orders/{order_id}` | read | View one order. |
| Orders | `PUT /orders/{order_id}` | write | Update order details. Requires explicit intent. |
| Orders | `GET /orders/{order_id}/items` | read | View order line items. |
| Orders | `GET /orders/{order_id}/messages` | read | View order messages. |
| Orders | `GET /orders/{order_id}/feedback` | read | View order feedback. |
| Orders | `PUT /orders/{order_id}/status` | write | Update order status. Requires explicit intent. |
| Orders | `PUT /orders/{order_id}/payment_status` | write | Update payment status. Requires explicit intent. |
| Orders | `POST /orders/{order_id}/drive_thru` | write | Send drive-thru message/action. Requires explicit intent. |
| Inventory | `GET /inventories` | read | List store inventory by item type/status/category/color. |
| Inventory | `POST /inventories` | write | Create inventory lot(s). Requires explicit intent. |
| Inventory | `GET /inventories/{inventory_id}` | read | View one inventory lot. |
| Inventory | `PUT /inventories/{inventory_id}` | write | Update inventory lot. Requires explicit intent. |
| Inventory | `DELETE /inventories/{inventory_id}` | destructive/write | Delete inventory lot. Requires immediate confirmation. |
| Items | `GET /items/{type}/{no}` | read | Item lookup. |
| Items | `GET /items/{type}/{no}/images/{color_id}` | read | Item image lookup. |
| Items | `GET /items/{type}/{no}/supersets` | read | Sets containing this item. |
| Items | `GET /items/{type}/{no}/subsets` | read | Contents of set/lot/item. |
| Items | `GET /items/{type}/{no}/price` | read | Price guide. |
| Items | `GET /items/{type}/{no}/colors` | read | Known colors for item. |
| Feedback | `GET /feedback` | read | List feedback. |
| Feedback | `POST /feedback` | write | Post feedback. Requires explicit intent. |
| Feedback | `GET /feedback/{feedback_id}` | read | View feedback. |
| Feedback | `POST /feedback/{feedback_id}/reply` | write | Reply to feedback. Requires explicit intent. |
| Catalog | `GET /colors`, `GET /colors/{color_id}` | read | Color list/details. |
| Catalog | `GET /categories`, `GET /categories/{category_id}` | read | Category list/details. |
| Account | `GET /notifications` | read | Notifications. |
| Coupons | `GET /coupons`, `GET /coupons/{coupon_id}` | read | Coupon list/details. |
| Coupons | `POST /coupons`, `PUT /coupons/{coupon_id}` | write | Create/update coupon. Requires explicit intent. |
| Coupons | `DELETE /coupons/{coupon_id}` | destructive/write | Delete coupon. Requires immediate confirmation. |
| Shipping | `GET /settings/shipping_methods`, `GET /settings/shipping_methods/{method_id}` | read | Shipping methods. |
| Members | `GET /members/{username}/ratings` | read | Member rating. |
| Members | `GET /members/{username}/my_notes` | read | Read private note for member. |
| Members | `POST /members/{username}/my_notes`, `PUT /members/{username}/my_notes` | write | Create/update private note. Requires explicit intent. |
| Members | `DELETE /members/{username}/my_notes` | destructive/write | Delete private note. Requires immediate confirmation. |
| Mapping | `GET /item_mapping/{type}/{no}`, `GET /item_mapping/{element_id}` | read | Map BrickLink item numbers and LEGO Element IDs. |

## Read-Only Examples

### Smoke check: colors

```bash
python - <<'PY'
import os, requests
from requests_oauthlib import OAuth1
base = os.getenv("BRICKLINK_BASE_URL", "https://api.bricklink.com/api/store/v1")
auth = OAuth1(os.environ["BRICKLINK_CONSUMER_KEY"], os.environ["BRICKLINK_CONSUMER_SECRET"], os.environ["BRICKLINK_TOKEN"], os.environ["BRICKLINK_TOKEN_SECRET"])
r = requests.get(f"{base}/colors", auth=auth, timeout=30)
r.raise_for_status()
print(r.json())
PY
```

### Item lookup

BrickLink item `type` values are API-specific. Common examples are `SET`, `PART`, `MINIFIG`, `BOOK`, `GEAR`, `CATALOG`, and `INSTRUCTION`; verify from the copied spec and actual API response when in doubt.

```bash
export TYPE="SET" NO="75192-1"
python - <<'PY'
import os, requests
from requests_oauthlib import OAuth1
base = os.getenv("BRICKLINK_BASE_URL", "https://api.bricklink.com/api/store/v1")
auth = OAuth1(os.environ["BRICKLINK_CONSUMER_KEY"], os.environ["BRICKLINK_CONSUMER_SECRET"], os.environ["BRICKLINK_TOKEN"], os.environ["BRICKLINK_TOKEN_SECRET"])
r = requests.get(f"{base}/items/{os.environ['TYPE']}/{os.environ['NO']}", auth=auth, timeout=30)
r.raise_for_status()
print(r.json())
PY
```

### Price guide

Price guide is read-only, but still be deliberate about filters because repeated calls across a full set inventory can fan out quickly.

```bash
export TYPE="SET" NO="75192-1" COLOR_ID="0" CONDITION="N" CURRENCY="EUR"
python - <<'PY'
import os, requests
from requests_oauthlib import OAuth1
base = os.getenv("BRICKLINK_BASE_URL", "https://api.bricklink.com/api/store/v1")
auth = OAuth1(os.environ["BRICKLINK_CONSUMER_KEY"], os.environ["BRICKLINK_CONSUMER_SECRET"], os.environ["BRICKLINK_TOKEN"], os.environ["BRICKLINK_TOKEN_SECRET"])
params = {
    "color_id": os.environ.get("COLOR_ID", "0"),
    "guide_type": "sold",
    "new_or_used": os.environ.get("CONDITION", "N"),
    "currency_code": os.environ.get("CURRENCY", "EUR"),
}
r = requests.get(f"{base}/items/{os.environ['TYPE']}/{os.environ['NO']}/price", params=params, auth=auth, timeout=30)
r.raise_for_status()
print(r.json())
PY
```

### Known colors for a part

```bash
export TYPE="PART" NO="3001"
python - <<'PY'
import os, requests
from requests_oauthlib import OAuth1
base = os.getenv("BRICKLINK_BASE_URL", "https://api.bricklink.com/api/store/v1")
auth = OAuth1(os.environ["BRICKLINK_CONSUMER_KEY"], os.environ["BRICKLINK_CONSUMER_SECRET"], os.environ["BRICKLINK_TOKEN"], os.environ["BRICKLINK_TOKEN_SECRET"])
r = requests.get(f"{base}/items/{os.environ['TYPE']}/{os.environ['NO']}/colors", auth=auth, timeout=30)
r.raise_for_status()
print(r.json())
PY
```

### Supersets and subsets

Use supersets to find where a part appears. Use subsets to inspect set contents. Keep `break_minifigs` and `break_subsets` explicit because they change result shape.

```bash
export TYPE="PART" NO="3001" COLOR_ID="5"
python - <<'PY'
import os, requests
from requests_oauthlib import OAuth1
base = os.getenv("BRICKLINK_BASE_URL", "https://api.bricklink.com/api/store/v1")
auth = OAuth1(os.environ["BRICKLINK_CONSUMER_KEY"], os.environ["BRICKLINK_CONSUMER_SECRET"], os.environ["BRICKLINK_TOKEN"], os.environ["BRICKLINK_TOKEN_SECRET"])
params = {"color_id": os.environ["COLOR_ID"]}
r = requests.get(f"{base}/items/{os.environ['TYPE']}/{os.environ['NO']}/supersets", params=params, auth=auth, timeout=30)
r.raise_for_status()
print(r.json())
PY
```

## Mutating Workflow Template

Use this pattern for writes. Do not hide the confirmation boundary inside a script.

1. Read current state first when possible: order, inventory lot, coupon, feedback, or member note.
2. Draft the exact payload locally.
3. Show the user a concise confirmation:
   - BrickLink account operation.
   - Endpoint and method.
   - Target ID/user/order.
   - Payload summary.
   - Whether it is destructive.
4. Execute only after explicit approval in the current conversation.
5. Re-read the changed resource and report the verified result.

Example confirmation text:

```text
This will update BrickLink inventory lot 123456: quantity 4 -> 3, price EUR 0.18 -> EUR 0.20. This changes a live marketplace listing. Reply "update BrickLink inventory 123456" to proceed.
```

## High-Cost Price Breakdown Guidance

Brick Directory's prompt exposes `getSetPriceBreakdown` / `bd_get_bricklink_set_price_breakdown` as an expensive workflow that can make 200+ API calls and run for several minutes. Preserve that approval gate in standalone workflows:

- First explain that the operation can be slow and quota-heavy.
- Ask before fan-out across a full set inventory.
- Cache or save intermediate data when doing repeated analysis.
- Prefer single item price guide calls for quick questions.
- Do not recompute totals manually when Brick Directory has already returned pre-calculated totals.

## Common Pitfalls

1. Treating credentials as consent. They are not. Writes still require explicit user intent.
2. Forgetting OAuth1. BrickLink is not a bearer-token API; all requests must be signed.
3. Running full set price breakdowns for casual questions. Start with targeted item or set price guide calls unless the user approved the fan-out.
4. Guessing item type or color ID. Use `/colors`, `/items/{type}/{no}/colors`, and item mapping endpoints instead of inventing IDs.
5. Mutating the wrong marketplace. If BrickLink and BrickOwl are both configured and the user only says “my store”, ask which platform before writing.
6. Posting feedback or member notes from an inferred tone. Draft first; let the user approve exact text.
7. Bulk inventory changes without a reviewed ID list. Require the exact inventory IDs and payload summary before touching live listings.

## Verification Checklist

- [ ] `BRICKLINK_CONSUMER_KEY`, `BRICKLINK_CONSUMER_SECRET`, `BRICKLINK_TOKEN`, and `BRICKLINK_TOKEN_SECRET` are referenced only as env vars.
- [ ] Read-only smoke check uses `GET /colors` or another harmless endpoint.
- [ ] Price guide and item lookup examples are read-only.
- [ ] Inventory/order/feedback/coupon/member-note writes require explicit user intent.
- [ ] Destructive deletes require immediate confirmation with exact IDs.
- [ ] Endpoint coverage matches `references/openapi/bricklink.yaml`.
- [ ] Large price-breakdown fan-out asks approval before execution.
