---
name: brickowl
description: Use BrickOwl's verified API for catalog lookup, store inventory, orders, wishlists, user details, and bulk requests with safe marketplace-write handling.
version: 1.0.0
---

# BrickOwl AFOL skill

Use this skill when the user asks for BrickOwl catalog lookup, BrickOwl store inventory, BrickOwl orders, BrickOwl wishlist creation, or BrickOwl marketplace listing management.

Source of truth:
- OpenAPI: `references/openapi/brickowl.yaml`
- Brick Directory MCP guidance: `references/prompts/brickowl-tools.txt`
- Source inventory: `docs/source-inventory.md#brickowl`

Do not scrape vendor docs when these checked-in references already answer the endpoint shape. If the checked-in spec is insufficient, report the gap instead of inventing parameters.

## Authentication

Required environment variable:

```bash
export BRICKOWL_API_KEY=...
```

Never print, commit, log, or paste the real API key. Examples must reference `$BRICKOWL_API_KEY` only.

BrickOwl auth placement is quirky and important:
- GET endpoints send `key` as a query parameter.
- POST endpoints send `key` in the `application/x-www-form-urlencoded` request body.

That is why generated clients that blindly put `key` in the query string for POST are not safe to adopt without fixing auth placement.

Base URL:

```bash
BRICKOWL_BASE_URL=${BRICKOWL_BASE_URL:-https://api.brickowl.com/v1}
```

## Safety rules

Read-only by default:
- `GET /catalog/search`
- `GET /catalog/id_lookup`
- `GET /inventory/list`
- `GET /order/list`
- `GET /order/view`
- `GET /user`

Mutating operations require explicit user confirmation in the current conversation before execution:
- `POST /inventory/create`
- `POST /inventory/update`
- `POST /wishlist/create_list`
- `POST /bulk` whenever any embedded request mutates data
- inventory deletion through `inventory/update` with `delete=true`

Stored credentials are not permission. Before any mutation, restate the exact action, lot/item identifiers, quantity, price, condition, wishlist name, or bulk request list and wait for an explicit confirmation such as "yes, create it" or "confirm update lot 123".

If the user asks to "sell", "list", "update inventory", or "delete lot" without naming a platform and both BrickLink/BrickOwl could apply, ask which marketplace to use before mutating anything.

## Endpoint coverage

| Workflow | Method/path | Safety | Notes |
|---|---|---|---|
| Catalog search | `GET /catalog/search` | read | Search by text query; do not use it as the first choice for known external IDs. |
| Known-ID lookup | `GET /catalog/id_lookup` | read | Preferred for known IDs such as LEGO set numbers, BrickLink item numbers, design IDs, and item numbers. |
| Inventory list | `GET /inventory/list` | read | Lists the authenticated store inventory; may include private lot notes and pricing. |
| Inventory create | `POST /inventory/create` | write | Creates a marketplace lot. Requires explicit confirmation. |
| Inventory update/delete | `POST /inventory/update` | write/destructive | Updates price, quantity, notes, sale status, or deletes with `delete=true`. Requires explicit confirmation. |
| Orders list | `GET /order/list` | read | Filter by status when needed. Treat buyer/order details as private. |
| Order details | `GET /order/view` | read | Requires `order_id`; may return addresses/email. Do not expose unnecessarily. |
| Wishlist create | `POST /wishlist/create_list` | write | Creates a wishlist. Requires explicit confirmation. |
| User details | `GET /user` | read | Smoke-check endpoint for configured credentials. |
| Bulk requests | `POST /bulk` | conditional | Read-only bulk is allowed; any embedded write requires explicit confirmation. Rate limit is lower than normal endpoints. |

## Known BrickOwl lookup quirk

Use `catalog/id_lookup` for known external IDs. Do not abuse `catalog/search` as an ID lookup tool.

Good:

```bash
curl -sS "$BRICKOWL_BASE_URL/catalog/id_lookup?key=$BRICKOWL_API_KEY&id=75192-1&type=Set&id_type=set_number"
```

Also useful `id_type` values from the verified spec:
- `item_no`
- `design_id`
- `bl_item_no`
- `set_number`

Use `catalog/search` only when the user gives a fuzzy text query or asks to browse/search by words:

```bash
curl -sS --get "$BRICKOWL_BASE_URL/catalog/search" \
  --data-urlencode "key=$BRICKOWL_API_KEY" \
  --data-urlencode "query=Millennium Falcon" \
  --data-urlencode "type=Set" \
  --data-urlencode "page=1"
```

## Read-only workflows

### Check credentials / current user

```bash
curl -sS "$BRICKOWL_BASE_URL/user?key=$BRICKOWL_API_KEY"
```

### List inventory

```bash
curl -sS "$BRICKOWL_BASE_URL/inventory/list?key=$BRICKOWL_API_KEY&page=1"
```

Notes:
- Inventory lots use BrickOwl lot IDs, not LEGO set numbers.
- Output may include personal notes, prices, costs, and store data; summarize carefully.

### List orders

```bash
curl -sS --get "$BRICKOWL_BASE_URL/order/list" \
  --data-urlencode "key=$BRICKOWL_API_KEY" \
  --data-urlencode "status=Pending" \
  --data-urlencode "page=1"
```

### View an order

```bash
curl -sS --get "$BRICKOWL_BASE_URL/order/view" \
  --data-urlencode "key=$BRICKOWL_API_KEY" \
  --data-urlencode "order_id=12345"
```

Order details may include buyer email and shipping/billing addresses. Do not quote PII unless the user specifically needs it.

## Mutating workflows

Do not run these until the user explicitly confirms the exact action.

### Create an inventory lot

Required fields from the verified spec: `boid`, `quantity`, `price`, `condition`, plus `key`. `condition` is a lowercase BrickOwl condition ID such as `news`, `newc`, `newi`, `usedc`, `usedi`, `usedn`, `usedg`, `useda`, or `other`; plain `New` is not valid for `inventory/create`.

Confirmation prompt shape:

```text
Confirm BrickOwl inventory create: BOID <boid>, quantity <qty>, price <price>, condition <condition>, optional color_id <color_id>, optional external_id <external_id>.
```

Execution after confirmation:

```bash
curl -sS -X POST "$BRICKOWL_BASE_URL/inventory/create" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "key=$BRICKOWL_API_KEY" \
  --data-urlencode "boid=$BOID" \
  --data-urlencode "quantity=$QUANTITY" \
  --data-urlencode "price=$PRICE" \
  --data-urlencode "condition=$CONDITION" \
  --data-urlencode "color_id=$COLOR_ID" \
  --data-urlencode "external_id=$EXTERNAL_ID"
```

### Update an inventory lot

Use `lot_id` or `external_lot_id`, plus only the fields the user asked to change. For quantity, distinguish:
- `absolute_quantity`: set quantity to this exact value.
- `relative_quantity`: add/subtract this amount.

Confirmation prompt shape:

```text
Confirm BrickOwl lot update: lot_id <lot_id> / external_lot_id <external_lot_id>; changes: <fields>.
```

Execution after confirmation:

```bash
curl -sS -X POST "$BRICKOWL_BASE_URL/inventory/update" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "key=$BRICKOWL_API_KEY" \
  --data-urlencode "lot_id=$LOT_ID" \
  --data-urlencode "absolute_quantity=$ABSOLUTE_QUANTITY" \
  --data-urlencode "price=$PRICE" \
  --data-urlencode "condition=$CONDITION" \
  --data-urlencode "for_sale=$FOR_SALE" \
  --data-urlencode "public_note=$PUBLIC_NOTE" \
  --data-urlencode "personal_note=$PERSONAL_NOTE"
```

### Delete an inventory lot

Deletion is modeled through `inventory/update` with `delete=true`. This is destructive and needs an especially explicit confirmation naming the lot ID.

```bash
curl -sS -X POST "$BRICKOWL_BASE_URL/inventory/update" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "key=$BRICKOWL_API_KEY" \
  --data-urlencode "lot_id=$LOT_ID" \
  --data-urlencode "delete=true"
```

### Create a wishlist

Confirmation prompt shape:

```text
Confirm BrickOwl wishlist creation: name "<name>", description "<description>".
```

Execution after confirmation:

```bash
curl -sS -X POST "$BRICKOWL_BASE_URL/wishlist/create_list" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "key=$BRICKOWL_API_KEY" \
  --data-urlencode "name=$WISHLIST_NAME" \
  --data-urlencode "description=$WISHLIST_DESCRIPTION"
```

### Bulk requests

Bulk has a lower rate limit: 200 requests/minute. Inspect every embedded request before deciding whether it is read-only or mutating.

If any embedded request is POST to inventory or wishlist endpoints, require explicit confirmation for the whole batch and summarize each write. Do not hide writes inside a bulk payload.

```bash
curl -sS -X POST "$BRICKOWL_BASE_URL/bulk" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "key=$BRICKOWL_API_KEY" \
  --data-urlencode "requests=$BULK_REQUESTS_JSON"
```

## BrickOwl limitations and routing

BrickOwl API does not provide marketplace offer data from other sellers. If the user asks for current marketplace prices/offers on BrickOwl, explain that limitation and suggest BrickLink pricing if available, or direct them to BrickOwl.com for manual marketplace browsing.

BrickOwl is appropriate for:
- validating BrickOwl catalog IDs / BOIDs
- managing the authenticated user's own BrickOwl inventory
- viewing the authenticated user's BrickOwl orders
- creating BrickOwl wishlists

It is not appropriate for API-based cross-seller price discovery.

## Printing Press status

The Printing Press BrickOwl spike was reviewed but not adopted as committed generated CLI output. Use the spike as endpoint coverage reference only until generated BrickOwl clients correctly handle POST auth in the request body and provide strong write-safety annotations. See the parent spike decision in PR #4 if available; do not depend on generated files being present in this repository.

## Verification

Read-only smoke checks only, and only when `BRICKOWL_API_KEY` is configured:

```bash
: "${BRICKOWL_API_KEY:?Set BRICKOWL_API_KEY first}"
BRICKOWL_BASE_URL=${BRICKOWL_BASE_URL:-https://api.brickowl.com/v1}
curl -fsS "$BRICKOWL_BASE_URL/user?key=$BRICKOWL_API_KEY" >/tmp/brickowl-user.json
```

Repository validation:

```bash
scripts/validate-skills.sh
```
