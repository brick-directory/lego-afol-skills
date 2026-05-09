---
name: brickeconomy
description: Use BrickEconomy for LEGO set/minifig valuation, collection performance, and sales-ledger analysis from the verified Brick Directory OpenAPI surface.
version: 1.0.0
platforms: [linux, macos]
metadata:
  hermes:
    tags: [lego, afol, brickeconomy, valuation, collection, investment]
---

# BrickEconomy AFOL Skill

Use this skill when the user asks about LEGO set values, minifig values, BrickEconomy collection valuation, collection growth, investment performance, or sales-ledger profit/loss.

Source of truth for this skill is Brick Directory's copied verified sources:

- `references/openapi/brickeconomy.yaml`
- `references/prompts/brickeconomy-tools.txt`
- `docs/source-inventory.md`

Do not invent endpoint shape from memory or scrape vendor docs. If the OpenAPI spec and prompt disagree, inspect both and prefer the verified OpenAPI contract for request/response shape.

## Credentials and setup

Required:

- `BRICKECONOMY_API_KEY` — sent as the `x-apikey` HTTP header.

Optional:

- `BRICKECONOMY_BASE_URL` — defaults to `https://www.brickeconomy.com/api/v1`.

Never print, log, commit, or paste the API key value. Examples must use `$BRICKECONOMY_API_KEY`, not real secrets.

Recommended shell guard before live calls:

```bash
: "${BRICKECONOMY_API_KEY:?Set BRICKECONOMY_API_KEY in your environment}"
BASE_URL="${BRICKECONOMY_BASE_URL:-https://www.brickeconomy.com/api/v1}"
```

## API coverage

All operations in the verified spec are read-only `GET` calls.

| Workflow | Method/path | Operation | Notes |
|---|---|---|---|
| Set value | `GET /set/{setNumber}` | `getSet` | Accepts set numbers with or without variant suffix, for example `10236` or `10236-1`. Optional `currency` query parameter. |
| Minifig value | `GET /minifig/{minifigNumber}` | `getMinifig` | Accepts BrickEconomy minifig numbers such as `sw0509`. Optional `currency` query parameter. |
| Collection sets | `GET /collection/sets` | `getCollectionSets` | Returns the user's set collection with paid price, current value, growth, acquisition, condition, and collection fields. Optional `currency` query parameter. |
| Collection minifigs | `GET /collection/minifigs` | `getCollectionMinifigs` | Returns the user's minifig collection with paid price, current value, growth, acquisition, and collection fields. Optional `currency` query parameter. |
| Sales ledger | `GET /salesledger` | `getSalesLedger` | Returns set and minifig sale records with sale price, fees/shipping, quantity, buy price, dates, condition, and notes. |

Supported currency codes from the spec: `USD`, `GBP`, `CAD`, `AUD`, `CNY`, `KRW`, `EUR`, `JPY`, `CHF`, `INR`, `BRL`, `RUB`, `ZAR`, `MXN`, `SGD`, `HKD`, `SEK`, `NZD`, `NOK`, `TRY`, `DKK`, `PLN`. Default is `USD`.

Known BrickEconomy limits from `references/prompts/brickeconomy-tools.txt`: 100 requests/day and 4 requests/minute. Be stingy: one collection call is better than N individual set calls when analyzing a user's portfolio.

## Safety

The verified BrickEconomy spec in `references/openapi/brickeconomy.yaml` is read-only. There are no marketplace, collection mutation, wishlist mutation, or delete endpoints in this skill.

Still be careful:

- Treat the returned collection and sales ledger as private financial/account data.
- Do not call the collection or sales ledger endpoints unless the user asked for personal collection/sales analysis.
- Do not fan out across many set/minifig lookups unless the user asked for a bulk analysis and the rate limit budget is acceptable.
- If a future BrickEconomy spec adds mutating endpoints, require explicit user intent in the current conversation before using them.

## Read-only smoke examples

Set value lookup:

```bash
: "${BRICKECONOMY_API_KEY:?Set BRICKECONOMY_API_KEY}"
BASE_URL="${BRICKECONOMY_BASE_URL:-https://www.brickeconomy.com/api/v1}"
curl -fsS \
  -H "x-apikey: $BRICKECONOMY_API_KEY" \
  "$BASE_URL/set/10236-1?currency=EUR" \
  | jq '.data | {set_number, name, currency, current_value_new, current_value_used, forecast_value_new_2_years, forecast_value_new_5_years, rolling_growth_12months}'
```

Minifig value lookup:

```bash
: "${BRICKECONOMY_API_KEY:?Set BRICKECONOMY_API_KEY}"
BASE_URL="${BRICKECONOMY_BASE_URL:-https://www.brickeconomy.com/api/v1}"
curl -fsS \
  -H "x-apikey: $BRICKECONOMY_API_KEY" \
  "$BASE_URL/minifig/sw0509?currency=USD" \
  | jq '.data | {minifig_number, name, currency, current_value_new, set_count, year}'
```

Collection set snapshot:

```bash
: "${BRICKECONOMY_API_KEY:?Set BRICKECONOMY_API_KEY}"
BASE_URL="${BRICKECONOMY_BASE_URL:-https://www.brickeconomy.com/api/v1}"
curl -fsS \
  -H "x-apikey: $BRICKECONOMY_API_KEY" \
  "$BASE_URL/collection/sets?currency=EUR" \
  | jq '.data | keys'
```

Collection minifig snapshot:

```bash
: "${BRICKECONOMY_API_KEY:?Set BRICKECONOMY_API_KEY}"
BASE_URL="${BRICKECONOMY_BASE_URL:-https://www.brickeconomy.com/api/v1}"
curl -fsS \
  -H "x-apikey: $BRICKECONOMY_API_KEY" \
  "$BASE_URL/collection/minifigs?currency=EUR" \
  | jq '.data | keys'
```

Sales ledger snapshot:

```bash
: "${BRICKECONOMY_API_KEY:?Set BRICKECONOMY_API_KEY}"
BASE_URL="${BRICKECONOMY_BASE_URL:-https://www.brickeconomy.com/api/v1}"
curl -fsS \
  -H "x-apikey: $BRICKECONOMY_API_KEY" \
  "$BASE_URL/salesledger" \
  | jq '.data | keys'
```

These smoke examples are read-only. They verify auth, endpoint reachability, and top-level response shape without changing any BrickEconomy account data.

## Response-grounded analysis rules

Higher-level workflows must be grounded in fields returned by the API response. Do not use hardcoded growth rates, made-up forecasts, generic LEGO investment heuristics, or cached values unless the user explicitly provided them.

When answering valuation questions:

1. Call `GET /set/{setNumber}` or `GET /minifig/{minifigNumber}`.
2. Quote the response's `currency` and specific value fields used.
3. Distinguish new/sealed value from used/complete value when both exist.
4. Use forecast fields only when present in the response.
5. Say when a field is absent rather than filling the gap with guesses.

Useful set fields include:

- `current_value_new`
- `current_value_used`
- `current_value_used_low`
- `current_value_used_high`
- `forecast_value_new_2_years`
- `forecast_value_new_5_years`
- `rolling_growth_lastyear`
- `rolling_growth_12months`
- `price_events_new`
- `price_events_used`
- `retired`, `released_date`, `retired_date`, `availability`

Useful minifig fields include:

- `current_value_new`
- `price_events_new`
- `set_count`
- `sets`
- `theme`, `subtheme`, `year`, `released_date`

When answering collection questions:

1. Prefer `GET /collection/sets` or `GET /collection/minifigs` over per-item fan-out.
2. Compute totals, top performers, and loss-makers from returned `paid_price`, `current_value`, and `growth` fields.
3. If the response contains period/history objects, derive trends from those periods instead of assuming a trend.
4. Preserve condition and named collection fields where relevant.

Example collection analysis grounded in returned data:

```bash
curl -fsS -H "x-apikey: $BRICKECONOMY_API_KEY" "$BASE_URL/collection/sets?currency=EUR" \
  | jq '
    .data.sets
    | sort_by(.growth // -999999)
    | reverse
    | map({set_number, name, condition, paid_price, current_value, growth})
    | .[0:10]
  '
```

If the exact array key differs, inspect `.data` first and adapt to the response. The principle is non-negotiable: derive the ranking from response fields, not assumptions.

When answering sales-ledger questions:

1. Call `GET /salesledger`.
2. Use sale fields from the response: `sale_price_total`, `sale_price_unit`, `sale_price_shipping`, `sale_price_fees`, `sale_quantity`, `sale_date`, and `currency`.
3. Use buy fields from the response: `buy_price`, `buy_date`, `buy_condition`, and notes when relevant.
4. Compute profit/loss from returned numbers only. A conservative formula is `sale_price_total - sale_price_shipping - sale_price_fees - buy_price` if those fields are present and semantically appropriate for the user's question.
5. State the formula used when reporting profit/loss.

Example ledger calculation scaffold:

```bash
curl -fsS -H "x-apikey: $BRICKECONOMY_API_KEY" "$BASE_URL/salesledger" \
  | jq '
    .data.sets
    | map({
        set_number,
        name,
        currency,
        sale_date,
        sale_price_total,
        sale_price_shipping,
        sale_price_fees,
        buy_price,
        estimated_profit: ((.sale_price_total // 0) - (.sale_price_shipping // 0) - (.sale_price_fees // 0) - (.buy_price // 0))
      })
  '
```

Inspect `.data` before depending on array names; the verified schema says the sales-ledger response has a `data` object containing set and minifig sale objects.

## Choosing BrickEconomy vs other LEGO skills

Use BrickEconomy directly for:

- Set and minifig market value.
- Forecasts and price event history from BrickEconomy.
- Personal collection valuation and growth.
- Sales ledger analysis.

Do not use BrickEconomy for:

- Parts pricing — `references/prompts/brickeconomy-tools.txt` says parts go to BrickLink in Brick Directory's unified pricing flow.
- Reviews or instructions — use Brickset.
- Buildability and owned/missing parts — use Rebrickable.
- Marketplace availability/listings/orders — use BrickLink or BrickOwl.

For a Brick Directory MCP session, the prompt says simple price inquiries should prefer the unified `bd_get_price` flow because it tries BrickEconomy first and falls back to BrickLink. In this standalone skill, call BrickEconomy endpoints directly when the user asked specifically for BrickEconomy data or when this is the only loaded LEGO pricing skill.

## Error handling

Common responses from the verified OpenAPI spec:

- `400` — bad request, usually malformed set/minifig number or invalid currency.
- `401` — missing/invalid `BRICKECONOMY_API_KEY`.
- `403` — key is valid but not allowed for this endpoint/account.
- `404` — requested set or minifig was not found.
- `429` — rate limit exceeded; stop retrying and report the limit.

On `429`, do not loop. BrickEconomy is rate-limited to 100 requests/day and 4 requests/minute according to the copied prompt guidance.
