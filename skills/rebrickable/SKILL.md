---
name: rebrickable
description: Use the Rebrickable API for LEGO catalog lookups and explicitly requested user collection workflows, grounded in Brick Directory's verified OpenAPI and MCP prompt references.
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [lego, afol, rebrickable, catalog, collection]
---

# Rebrickable AFOL Skill

Use this skill when a user asks for Rebrickable-backed LEGO catalog data or Rebrickable account workflows: colors, elements, minifigs, part categories, parts, sets, themes, set lists, part lists, all owned parts/sets/minifigs, build analysis, and lost parts.

## Source of truth

Do not scrape or reinterpret vendor docs from scratch. This skill is grounded in copied Brick Directory sources:

- OpenAPI: `references/openapi/rebrickable.yaml`
- Current MCP prompt guidance: `references/prompts/rebrickable-tools.txt`
- Cross-integration inventory and safety matrix: `docs/source-inventory.md`
- Original source repo path used to create the copied references: `/home/openclaw/.openclaw/workspace/development/projects/telegraphic-dev/brick-directory`

If endpoint behavior is unclear, inspect `references/openapi/rebrickable.yaml` first, then the prompt guidance. Do not invent unsupported parameters.

## Environment variables

Required for API calls:

- `REBRICKABLE_API_KEY` — API key used in the `Authorization` header.

Optional for private/user workflows:

- `REBRICKABLE_USER_TOKEN` — existing Rebrickable user token for `/users/{user_token}/...` endpoints.
- `REBRICKABLE_USERNAME` and `REBRICKABLE_PASSWORD` — only for intentionally generating a token through `POST /users/_token/`; prefer `REBRICKABLE_USER_TOKEN` when available.

Never commit real values. Examples must use placeholders such as `$REBRICKABLE_API_KEY` and `$REBRICKABLE_USER_TOKEN`.

## Auth and base URL

Base URL from the verified spec:

```bash
REBRICKABLE_BASE_URL="https://rebrickable.com/api/v3"
```

Use the API key as an authorization header. The Rebrickable convention is `Authorization: key <api-key>`:

```bash
-H "Authorization: key $REBRICKABLE_API_KEY"
```

Private endpoints also include the user token in the URL path. Treat the token like a secret; do not print it in logs or summaries.

## Safety rules

Default to read-only operations. Writes require explicit user intent in the user's request, not vague implication.

Read-only is fine without extra confirmation when credentials are already configured:

- catalog lookups and searches
- reading user profile, set lists, part lists, all parts, all sets, minifigs, lost parts
- build requirement analysis

Explicit user intent is required before any mutation:

- generate user token with username/password: `POST /users/_token/`
- create, update, or delete set lists
- add, update, remove, sync, or delete sets in a user collection/list
- create, update, or delete part lists
- add, update, or remove parts in a part list
- add, update, or remove lost parts

Destructive operations require especially clear wording, e.g. "delete list 42" or "remove set 10497-1 from my Rebrickable list". If the user asks to "sync" a collection, explain that sync can replace remote state and ask for explicit confirmation unless they already clearly requested that exact operation.

When both Rebrickable and another collection provider are available and the user says only "my collection", ask which service to use before mutating. If only Rebrickable is configured, mention that Rebrickable is the service being used.

## Endpoint coverage

### Public catalog and metadata

| Method | Path | Operation | Use |
|---|---|---|---|
| GET | `/lego/colors/` | `lego_colors_list` | List colors. |
| GET | `/lego/colors/{id}/` | `lego_colors_read` | Color details. |
| GET | `/lego/elements/{element_id}/` | `lego_elements_read` | Element details. |
| GET | `/lego/minifigs/` | `lego_minifigs_list` | Search/list minifigs. |
| GET | `/lego/minifigs/{set_num}/` | `lego_minifigs_read` | Minifig details. |
| GET | `/lego/minifigs/{set_num}/parts/` | `lego_minifigs_parts_list` | Parts in a minifig. |
| GET | `/lego/minifigs/{set_num}/sets/` | `lego_minifigs_sets_list` | Sets containing a minifig. |
| GET | `/lego/part_categories/` | `lego_part_categories_list` | List part categories. |
| GET | `/lego/part_categories/{id}/` | `lego_part_categories_read` | Part category details. |
| GET | `/lego/parts/` | `lego_parts_list` | Search/list parts. |
| GET | `/lego/parts/{part_num}/` | `lego_parts_read` | Part details. |
| GET | `/lego/parts/{part_num}/colors/` | `lego_parts_colors_list` | Known colors for a part. |
| GET | `/lego/parts/{part_num}/colors/{color_id}/` | `lego_parts_colors_read` | Specific part/color details. |
| GET | `/lego/parts/{part_num}/colors/{color_id}/sets/` | `lego_parts_colors_sets_list` | Sets containing a part/color combination. |
| GET | `/lego/sets/` | `lego_sets_list` | Search/list sets with filters. |
| GET | `/lego/sets/{set_num}/` | `lego_sets_read` | Set details. |
| GET | `/lego/sets/{set_num}/alternates/` | `lego_sets_alternates_list` | Alternate builds/MOCs for a set. |
| GET | `/lego/sets/{set_num}/minifigs/` | `lego_sets_minifigs_list` | Minifigs in a set. |
| GET | `/lego/sets/{set_num}/parts/` | `lego_sets_parts_list` | Inventory parts in a set. |
| GET | `/lego/sets/{set_num}/sets/` | `lego_sets_sets_list` | Sub-sets in a set. |
| GET | `/lego/themes/` | `lego_themes_list` | List themes. |
| GET | `/lego/themes/{id}/` | `lego_themes_read` | Theme details. |
| GET | `/users/badges/` | `users_badges_list` | List available badges. |
| GET | `/users/badges/{id}/` | `users_badges_read` | Badge details. |

### User/private workflows

| Method | Path | Operation | Safety |
|---|---|---|---|
| POST | `/users/_token/` | `users__token_create` | Auth write; explicit intent only. |
| GET | `/users/{user_token}/profile/` | `users_profile_read` | Read. |
| GET | `/users/{user_token}/allparts/` | `users_allparts_list` | Read all owned/listed parts including set contents. |
| GET | `/users/{user_token}/build/{set_num}/` | `users_build_read` | Read build requirements for a set. |
| GET | `/users/{user_token}/minifigs/` | `users_minifigs_list` | Read minifigs from user's sets. |
| GET | `/users/{user_token}/parts/` | `users_parts_list` | Read all parts in user's part lists. |
| GET | `/users/{user_token}/sets/` | `users_sets_list` | Read all sets in user's collection. |
| POST | `/users/{user_token}/sets/` | `users_sets_create` | Write; add sets. |
| POST | `/users/{user_token}/sets/sync/` | `users_sets_sync_create` | Write; collection sync/replacement risk. |
| GET | `/users/{user_token}/sets/{set_num}/` | `users_sets_read` | Read specific owned set. |
| PUT | `/users/{user_token}/sets/{set_num}/` | `users_sets_update` | Write; update quantity/list placement. |
| DELETE | `/users/{user_token}/sets/{set_num}/` | `users_sets_delete` | Destructive write; remove from all set lists. |
| GET | `/users/{user_token}/setlists/` | `users_setlists_list` | Read set lists. |
| POST | `/users/{user_token}/setlists/` | `users_setlists_create` | Write; create set list. |
| GET | `/users/{user_token}/setlists/{list_id}/` | `users_setlists_read` | Read set list details. |
| PUT/PATCH | `/users/{user_token}/setlists/{list_id}/` | `users_setlists_update`, `users_setlists_partial_update` | Write; rename/change set list. |
| DELETE | `/users/{user_token}/setlists/{list_id}/` | `users_setlists_delete` | Destructive write; deletes list and contained entries. |
| GET | `/users/{user_token}/setlists/{list_id}/sets/` | `users_setlists_sets_list` | Read sets in a list. |
| POST | `/users/{user_token}/setlists/{list_id}/sets/` | `users_setlists_sets_create` | Write; add sets. Send JSON array. |
| GET | `/users/{user_token}/setlists/{list_id}/sets/{set_num}/` | `users_setlists_sets_read` | Read specific list entry. |
| PUT/PATCH | `/users/{user_token}/setlists/{list_id}/sets/{set_num}/` | `users_setlists_sets_update`, `users_setlists_sets_partial_update` | Write; update list entry. |
| DELETE | `/users/{user_token}/setlists/{list_id}/sets/{set_num}/` | `users_setlists_sets_delete` | Destructive write; remove set from list. |
| GET | `/users/{user_token}/partlists/` | `users_partlists_list` | Read part lists. |
| POST | `/users/{user_token}/partlists/` | `users_partlists_create` | Write; create part list. |
| GET | `/users/{user_token}/partlists/{list_id}/` | `users_partlists_read` | Read part list details. |
| PUT/PATCH | `/users/{user_token}/partlists/{list_id}/` | `users_partlists_update`, `users_partlists_partial_update` | Write; rename/change part list. |
| DELETE | `/users/{user_token}/partlists/{list_id}/` | `users_partlists_delete` | Destructive write; deletes list and contained parts. |
| GET | `/users/{user_token}/partlists/{list_id}/parts/` | `users_partlists_parts_list` | Read parts in a list. |
| POST | `/users/{user_token}/partlists/{list_id}/parts/` | `users_partlists_parts_create` | Write; add parts. |
| GET | `/users/{user_token}/partlists/{list_id}/parts/{part_num}/{color_id}/` | `users_partlists_parts_read` | Read specific part list entry. |
| PUT | `/users/{user_token}/partlists/{list_id}/parts/{part_num}/{color_id}/` | `users_partlists_parts_update` | Write; update part quantity/details. |
| DELETE | `/users/{user_token}/partlists/{list_id}/parts/{part_num}/{color_id}/` | `users_partlists_parts_delete` | Destructive write; remove part from list. |
| GET | `/users/{user_token}/lost_parts/` | `users_lost_parts_list` | Read lost parts. |
| POST | `/users/{user_token}/lost_parts/` | `users_lost_parts_create` | Write; mark parts as lost. |
| DELETE | `/users/{user_token}/lost_parts/{id}/` | `users_lost_parts_delete` | Destructive write; remove lost-part record. |

## Read-only examples

Check required API key without mutating anything:

```bash
curl -fsS \
  -H "Authorization: key $REBRICKABLE_API_KEY" \
  "https://rebrickable.com/api/v3/lego/colors/?page_size=5"
```

Look up a set:

```bash
curl -fsS \
  -H "Authorization: key $REBRICKABLE_API_KEY" \
  "https://rebrickable.com/api/v3/lego/sets/10497-1/"
```

Search for sets, keeping result size bounded:

```bash
curl -fsS \
  -H "Authorization: key $REBRICKABLE_API_KEY" \
  "https://rebrickable.com/api/v3/lego/sets/?search=Galaxy%20Explorer&page_size=10"
```

List a user's set lists, if `REBRICKABLE_USER_TOKEN` is configured:

```bash
curl -fsS \
  -H "Authorization: key $REBRICKABLE_API_KEY" \
  "https://rebrickable.com/api/v3/users/$REBRICKABLE_USER_TOKEN/setlists/?page_size=20"
```

Analyze whether the user's collection can build a set:

```bash
curl -fsS \
  -H "Authorization: key $REBRICKABLE_API_KEY" \
  "https://rebrickable.com/api/v3/users/$REBRICKABLE_USER_TOKEN/build/10497-1/"
```

## Write examples: documentation only, not default action

Do not run these unless the user explicitly asks for the mutation and the target list/set/part is clear.

Create a set list only after explicit intent:

```bash
curl -fsS -X POST \
  -H "Authorization: key $REBRICKABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name":"Space builds","is_buildable":true}' \
  "https://rebrickable.com/api/v3/users/$REBRICKABLE_USER_TOKEN/setlists/"
```

Add sets to a list only after explicit intent. The verified spec notes this endpoint expects a JSON array:

```bash
curl -fsS -X POST \
  -H "Authorization: key $REBRICKABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '[{"set_num":"10497-1","quantity":1}]' \
  "https://rebrickable.com/api/v3/users/$REBRICKABLE_USER_TOKEN/setlists/$LIST_ID/sets/"
```

Delete operations are destructive. Confirm the exact target before running:

```bash
curl -fsS -X DELETE \
  -H "Authorization: key $REBRICKABLE_API_KEY" \
  "https://rebrickable.com/api/v3/users/$REBRICKABLE_USER_TOKEN/setlists/$LIST_ID/sets/10497-1/"
```

## Workflow guidance

1. Prefer public catalog endpoints for general LEGO facts.
2. Use `page_size` and filters to avoid unbounded pagination. Brick Directory's MCP prompt uses a 500-item safety cap for browse/list flows; copy that behavior when looping pages.
3. For part operations, the MCP prompt expects color names in user-facing language and resolves to IDs. If calling Rebrickable directly, resolve the color ID first through `/lego/colors/` or known catalog data before mutating part lists.
4. For theme filtering, resolve theme names through `/lego/themes/` before using theme IDs.
5. If a response is partial because of pagination limits, say so and offer the next page rather than silently pretending results are complete.
6. When handling multiple collection services, do not guess. Ask whether to use Rebrickable, Brickset, or both before mutating if more than one is configured.

## Smoke verification

These checks are safe and read-only:

```bash
# Verify references exist in this repo
[ -f references/openapi/rebrickable.yaml ] && [ -f references/prompts/rebrickable-tools.txt ]

# Verify the skill mentions the expected env vars and source references
grep -q 'REBRICKABLE_API_KEY' skills/rebrickable/SKILL.md
grep -q 'references/openapi/rebrickable.yaml' skills/rebrickable/SKILL.md
grep -q 'references/prompts/rebrickable-tools.txt' skills/rebrickable/SKILL.md

# Optional live API smoke, only when REBRICKABLE_API_KEY is set
curl -fsS \
  -H "Authorization: key $REBRICKABLE_API_KEY" \
  "https://rebrickable.com/api/v3/lego/colors/?page_size=1" >/tmp/rebrickable-colors-smoke.json
```

For repo validation, run:

```bash
scripts/validate-skills.sh
git diff --check
```
