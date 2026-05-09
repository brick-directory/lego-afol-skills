---
name: brickset
description: Work with Brickset's LEGO set, media, review, collection, wishlist, and user-note APIs using Brick Directory's verified Brickset OpenAPI and MCP prompt guidance.
version: 1.0.0
---

# Brickset AFOL Skill

Use this skill when a user asks for Brickset-backed LEGO set details, extra images, building instructions, community reviews, or explicit Brickset account workflows such as collection, wishlist, ratings, quantities, and personal notes.

Source of truth for this skill:

- OpenAPI: `references/openapi/brickset.yaml`
- Public MCP guidance: `references/prompts/brickset-tools.txt`
- Private MCP guidance: `references/prompts/brickset-private-tools.txt`
- Inventory matrix: `docs/source-inventory.md#brickset`

Do not scrape Brickset vendor docs from scratch when these copied Brick Directory references answer the question.

## Credentials

Required for all Brickset calls:

- `BRICKSET_API_KEY` — Brickset API key.

Optional for private/user workflows:

- `BRICKSET_USER_HASH` — persisted user hash from Brickset `login`; preferred when already available.
- `BRICKSET_USERNAME` and `BRICKSET_PASSWORD` — only for obtaining a user hash when the user intentionally asks to authenticate or private workflows require it.

Credential rules:

- Never print, commit, or store actual credential values in docs, chat summaries, git commits, logs, or examples.
- Prefer `BRICKSET_USER_HASH` over username/password once available.
- If `BRICKSET_USER_HASH` is missing and login is needed, ask the user to provide credentials through the approved secret path; do not infer or expose them.
- Public reads still send `userHash=` as an empty form field unless a real user hash is intentionally used.

## API shape and Brickset quirks

Brickset API v3 is SOAP-ish/form-style despite being described by OpenAPI:

- Base URL: `https://brickset.com/api/v3.asmx`
- Every verified operation is `POST`.
- Body content type is `application/x-www-form-urlencoded`.
- `apiKey` is sent as a form field, not as JSON.
- `userHash` is a required form field for most read calls; for public calls send an empty string: `userHash=`.
- Complex filters and mutation payloads go in a `params` form field whose value is a JSON string.
- For set-scoped media/review calls, Brickset often wants internal numeric `setID`, not the public set number. Resolve it with `getSets` first.
- Set numbers may appear with or without variant suffix in user requests; normalize to the canonical Brickset/Rebrickable-style value when possible, e.g. `10270-1`.
- Do not convert these calls to JSON requests. That is the classic foot-gun here.

Reusable shell setup:

```bash
: "${BRICKSET_API_KEY:?set BRICKSET_API_KEY}"
BASE_URL="https://brickset.com/api/v3.asmx"
USER_HASH="${BRICKSET_USER_HASH:-}"
```

## Endpoint coverage

| Operation | Endpoint | Safety | Use for |
|---|---|---|---|
| `getSets` | `POST /getSets` | read | Search and details by set number, theme, year, query filters; returns internal `setID`. |
| `getAdditionalImages` | `POST /getAdditionalImages` | read | Extra images beyond the main thumbnail. Needs `setID`. |
| `getInstructions2` | `POST /getInstructions2` | read | PDF building instruction links. Uses public set number. |
| `getReviews` | `POST /getReviews` | read | Community reviews and ratings. Needs `setID`. |
| `login` | `POST /login` | auth | Obtain `userHash` from username/password. |
| `setCollection` | `POST /setCollection` | mutating | Add/remove/update owned collection, wishlist, quantity, notes, and rating. Needs `setID` and `userHash`. |
| `getUserNotes` | `POST /getUserNotes` | read/private | Fetch user's Brickset notes. Needs `userHash`. |

Brick Directory's current MCP tool names to preserve conceptually:

- Public: `bd_get_brickset_details`, `bd_get_brickset_additional_images`, `bd_get_brickset_instructions`, `bd_get_brickset_reviews`
- Private: `bd_get_my_brickset_collection`, `bd_get_my_brickset_wishlist`, `bd_get_my_brickset_notes`, `bd_add_to_brickset_collection`, `bd_remove_from_brickset_collection`, `bd_add_to_brickset_wishlist`, `bd_remove_from_brickset_wishlist`, `bd_update_brickset_collection_item`

## Public read workflows

### Search/details for a set

Use `getSets` for general set details and to resolve Brickset's internal `setID`.

```bash
curl -sS -X POST "$BASE_URL/getSets" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "apiKey=$BRICKSET_API_KEY" \
  --data-urlencode "userHash=$USER_HASH" \
  --data-urlencode 'params={"setNumber":"10270-1"}'
```

Useful `params` filters from the verified spec include set number plus Brickset-supported search/detail filters encoded as JSON. Keep the raw JSON string inside the form field.

### Additional images

First resolve `setID` via `getSets`, then:

```bash
curl -sS -X POST "$BASE_URL/getAdditionalImages" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "apiKey=$BRICKSET_API_KEY" \
  --data-urlencode "userHash=$USER_HASH" \
  --data-urlencode "setID=$SET_ID"
```

Use when users ask for extra photos, alternate angles, box backs, detail shots, or images beyond the main thumbnail.

### Building instructions

```bash
curl -sS -X POST "$BASE_URL/getInstructions2" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "apiKey=$BRICKSET_API_KEY" \
  --data-urlencode "userHash=$USER_HASH" \
  --data-urlencode 'setNumber=10270-1'
```

Return PDF links and explain instruction codes when helpful: BI numbers, version numbers, and booklet numbers.

### Reviews and opinions

When the user asks for opinions, community feedback, ratings, whether a set is good, or whether it is worth buying, use Brickset reviews before pricing tools.

Resolve `setID` with `getSets`, then:

```bash
curl -sS -X POST "$BASE_URL/getReviews" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "apiKey=$BRICKSET_API_KEY" \
  --data-urlencode "userHash=$USER_HASH" \
  --data-urlencode "setID=$SET_ID"
```

Summarize real review text and star ratings. Do not invent sentiment if there are no reviews.

## Private read workflows

### Obtain a user hash

Only use `login` when private workflows require it and the user has explicitly provided or approved credential use.

```bash
: "${BRICKSET_USERNAME:?set BRICKSET_USERNAME}"
: "${BRICKSET_PASSWORD:?set BRICKSET_PASSWORD}"

curl -sS -X POST "$BASE_URL/login" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "apiKey=$BRICKSET_API_KEY" \
  --data-urlencode "username=$BRICKSET_USERNAME" \
  --data-urlencode "password=$BRICKSET_PASSWORD"
```

The response contains `hash`. Store it as `BRICKSET_USER_HASH` in the user's approved secret storage if persistence is requested. Never commit it.

### Collection and wishlist reads

The verified OpenAPI exposes `getSets` with `userHash` and collection-aware fields. Use filters that match Brickset's collection/wanted semantics through the JSON `params` field; preserve the form-encoded JSON shape.

Owned collection example:

```bash
: "${BRICKSET_USER_HASH:?set BRICKSET_USER_HASH for private reads}"

curl -sS -X POST "$BASE_URL/getSets" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "apiKey=$BRICKSET_API_KEY" \
  --data-urlencode "userHash=$BRICKSET_USER_HASH" \
  --data-urlencode 'params={"owned":1}'
```

Wishlist/wanted example:

```bash
curl -sS -X POST "$BASE_URL/getSets" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "apiKey=$BRICKSET_API_KEY" \
  --data-urlencode "userHash=$BRICKSET_USER_HASH" \
  --data-urlencode 'params={"wanted":1}'
```

### User notes

```bash
curl -sS -X POST "$BASE_URL/getUserNotes" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "apiKey=$BRICKSET_API_KEY" \
  --data-urlencode "userHash=$BRICKSET_USER_HASH"
```

Use for personal set notes and note-backed collection context.

## Mutating workflows: explicit intent required

`setCollection` changes the user's real Brickset account immediately. It can add/remove owned status, add/remove wanted status, change quantity, update notes, and set ratings.

Before calling `setCollection`, require explicit user intent in the current conversation. Stored credentials are not permission. Acceptable intent is concrete, such as:

- "Add 10270-1 to my Brickset collection."
- "Remove 75192-1 from my Brickset wishlist."
- "Set my Brickset rating for 21325-1 to 5."
- "Update my Brickset notes for 10497-1 to ..."

If the user says only "my collection" and more than one collection provider is available, ask whether they mean Brickset, Rebrickable, or both before mutating anything.

Do not run mutating examples as smoke tests.

### Add to owned collection

After explicit intent and `setID` resolution:

```bash
: "${BRICKSET_USER_HASH:?set BRICKSET_USER_HASH for writes}"

curl -sS -X POST "$BASE_URL/setCollection" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "apiKey=$BRICKSET_API_KEY" \
  --data-urlencode "userHash=$BRICKSET_USER_HASH" \
  --data-urlencode "setID=$SET_ID" \
  --data-urlencode 'params={"own":1,"qtyOwned":1}'
```

### Remove from owned collection

```bash
curl -sS -X POST "$BASE_URL/setCollection" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "apiKey=$BRICKSET_API_KEY" \
  --data-urlencode "userHash=$BRICKSET_USER_HASH" \
  --data-urlencode "setID=$SET_ID" \
  --data-urlencode 'params={"own":0}'
```

### Add to wishlist

```bash
curl -sS -X POST "$BASE_URL/setCollection" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "apiKey=$BRICKSET_API_KEY" \
  --data-urlencode "userHash=$BRICKSET_USER_HASH" \
  --data-urlencode "setID=$SET_ID" \
  --data-urlencode 'params={"want":1}'
```

### Remove from wishlist

```bash
curl -sS -X POST "$BASE_URL/setCollection" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "apiKey=$BRICKSET_API_KEY" \
  --data-urlencode "userHash=$BRICKSET_USER_HASH" \
  --data-urlencode "setID=$SET_ID" \
  --data-urlencode 'params={"want":0}'
```

### Update quantity, notes, or rating

```bash
curl -sS -X POST "$BASE_URL/setCollection" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "apiKey=$BRICKSET_API_KEY" \
  --data-urlencode "userHash=$BRICKSET_USER_HASH" \
  --data-urlencode "setID=$SET_ID" \
  --data-urlencode 'params={"qtyOwned":2,"notes":"placeholder note","rating":5}'
```

Keep notes under Brickset's documented limit from the verified spec guidance: 1000 characters. Rating is 1-5.

## Read-only smoke checks

Use only read-only calls for validation.

1. Check env presence without printing values:

```bash
test -n "${BRICKSET_API_KEY:-}" && echo "BRICKSET_API_KEY is set"
```

2. Public set details smoke:

```bash
curl -sS -X POST "https://brickset.com/api/v3.asmx/getSets" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "apiKey=$BRICKSET_API_KEY" \
  --data-urlencode 'userHash=' \
  --data-urlencode 'params={"setNumber":"10270-1"}'
```

3. If `BRICKSET_USER_HASH` is configured, private notes read smoke:

```bash
curl -sS -X POST "https://brickset.com/api/v3.asmx/getUserNotes" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "apiKey=$BRICKSET_API_KEY" \
  --data-urlencode "userHash=$BRICKSET_USER_HASH"
```

Do not use `setCollection` in validation unless the user explicitly asks for a real Brickset account mutation.

## Response guidance

- Mention Brickset as the source when returning review, instruction, image, or collection data.
- For opinion questions, cite/summarize Brickset reviews first before switching to price/value analysis.
- For images and instructions, return direct URLs when the API provides them.
- For collection/wishlist writes, report exactly what service was changed: Brickset collection or Brickset wishlist.
- If an API response has `status: error`, surface the message and stop rather than pretending the operation succeeded.
