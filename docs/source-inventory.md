# Brick Directory integration source inventory

This inventory is the source map for building `brick-directory/lego-afol-skills` skills. It is intentionally based on Brick Directory's checked-in OpenAPI specs, MCP prompt files, controller mappings, and Anthropic directory submission guide, not on freshly-scraped vendor docs.

## Source roots

- Brick Directory source repo: `/home/openclaw/.openclaw/workspace/development/projects/telegraphic-dev/brick-directory`
- LEGO AFOL skills repo: `/home/openclaw/.openclaw/workspace/development/projects/brick-directory/lego-afol-skills`
- Plan: `.hermes/plans/2026-05-09_072135-lego-afol-skills.md`

## Integration-to-skill map

| Future skill | OpenAPI/spec source | MCP prompt source | Current Brick Directory tool names | Auth env vars for standalone skill | Write/destructive surface |
|---|---|---|---|---|---|
| `skills/rebrickable/SKILL.md` | `backend/libs/rebrickable-client/src/main/resources/openapi/api-spec.yaml` | `backend/apps/brick-directory-mcp-server/src/main/resources/prompts/rebrickable-tools.txt` | `bd_get_rebrickable_user_set_lists`, `bd_create_rebrickable_set_list`, `bd_update_rebrickable_set_list`, `bd_delete_rebrickable_set_list`, `bd_get_rebrickable_sets_in_list`, `bd_add_rebrickable_sets_to_list`, `bd_update_rebrickable_set_in_list`, `bd_remove_rebrickable_set_from_list`, `bd_get_all_rebrickable_user_sets`, `bd_get_rebrickable_user_part_lists`, `bd_create_rebrickable_part_list`, `bd_delete_rebrickable_part_list`, `bd_get_rebrickable_parts_in_list`, `bd_add_rebrickable_part_to_list`, `bd_update_rebrickable_part_in_list`, `bd_remove_rebrickable_part_from_list`, `bd_get_all_rebrickable_user_parts`, `bd_get_all_rebrickable_user_minifigs`, `bd_get_rebrickable_user_profile`, `bd_get_rebrickable_lost_parts`, `bd_add_rebrickable_lost_part`, `bd_update_rebrickable_lost_part`, `bd_remove_rebrickable_lost_part`, `bd_analyze_rebrickable_build_requirements` | `REBRICKABLE_API_KEY`; user workflows also need `REBRICKABLE_USER_TOKEN` or an explicit token-generation flow using username/password only when the user intentionally asks | Writes: user token creation, lost parts create/update/delete, part list create/update/delete, set list create/update/delete, adding/removing/updating parts and sets, collection sync. Treat all list/collection/lost-part mutations as explicit-intent only. |
| `skills/brickset/SKILL.md` | `backend/libs/brickset-client/src/main/resources/openapi/api-spec.yaml` | `backend/apps/brick-directory-mcp-server/src/main/resources/prompts/brickset-tools.txt`; `brickset-private-tools.txt` | Public/read: `bd_get_brickset_reviews`, `bd_get_brickset_instructions`, `bd_get_brickset_additional_images`, `bd_get_brickset_details`. Private/read+write: `bd_get_my_brickset_collection`, `bd_get_my_brickset_wishlist`, `bd_get_my_brickset_notes`, `bd_add_to_brickset_collection`, `bd_remove_from_brickset_collection`, `bd_add_to_brickset_wishlist`, `bd_remove_from_brickset_wishlist`, `bd_update_brickset_collection_item` | `BRICKSET_API_KEY`; private workflows need `BRICKSET_USERNAME` + `BRICKSET_PASSWORD` or a persisted `BRICKSET_USER_HASH` | Writes: `setCollection` for collection/wishlist add, remove, update, notes/rating/quantity. Require explicit user intent. Login itself is not destructive but uses credentials. |
| `skills/brickowl/SKILL.md` | `backend/libs/brickowl-client/src/main/resources/openapi/api-spec.yaml` | `backend/apps/brick-directory-mcp-server/src/main/resources/prompts/brickowl-tools.txt` | `bd_get_my_brickowl_inventory`, `bd_create_brickowl_listing`, `bd_update_brickowl_listing`, `bd_delete_brickowl_listing` | `BRICKOWL_API_KEY` | Writes: inventory create/update/delete, wishlist create, bulk requests when they wrap mutations. Despite current prompt saying no approval is required, standalone skill should still require explicit user intent for marketplace/listing writes. Use `catalog/id_lookup` for known ID lookups. |
| `skills/bricklink/SKILL.md` | `backend/libs/bricklink-client/src/main/resources/openapi/api-spec.yaml` | `backend/apps/brick-directory-mcp-server/src/main/resources/prompts/bricklink-tools.txt` | Brick Directory currently exposes only `bd_get_bricklink_set_price_breakdown` as a dedicated BrickLink prompt-backed tool; shared LEGO tools also expose `bd_get_bricklink_prices`, `bd_get_bricklink_colors`, and `bd_translate_rebrickable_to_bricklink` | `BRICKLINK_CONSUMER_KEY`, `BRICKLINK_CONSUMER_SECRET`, `BRICKLINK_TOKEN`, `BRICKLINK_TOKEN_SECRET` | Writes: order updates/status/payment/drive-thru, inventory create/update/delete, feedback/replies, coupons create/update/delete, member notes create/update/delete. Pricing breakdown is read-only but high-cost/quota-heavy and should ask approval before large fan-out. |
| `skills/brickeconomy/SKILL.md` | `backend/libs/brickeconomy-client/src/main/resources/openapi/api-spec.yaml` | `backend/apps/brick-directory-mcp-server/src/main/resources/prompts/brickeconomy-tools.txt` | `bd_get_my_brickeconomy_collection`, `bd_get_my_brickeconomy_minifigs`, `bd_get_my_brickeconomy_sales_ledger`, `bd_generate_brickeconomy_import_csv`, `bd_analyze_set_investment`, `bd_find_best_performing_sets`; value lookups are also routed through shared `bd_get_price` | `BRICKECONOMY_API_KEY` | Verified spec is GET-only. CSV generation is local output, not external mutation. Still note API rate limits and avoid unnecessary fan-out. |
| `skills/brick-directory/SKILL.md` | No checked-in Brick Directory public OpenAPI spec found; derive from controllers until `references/openapi/brick-directory-public.yaml` exists | Shared LEGO tool surface in `LegoTools.java`; Anthropic guide list under `internal-guides/anthropic-directory-submission.md` | `bd_get_set_name`, `bd_get_set_details`, `bd_get_set_image`, `bd_get_set_alternates`, `bd_search_sets`, `bd_get_part_details`, `bd_get_part_image`, `bd_search_parts`, `bd_get_minifig_details`, `bd_search_minifigs`, `bd_search_elements`, `bd_get_rebrickable_colors`, `bd_get_all_themes`, `bd_get_all_part_types`, `bd_find_similar_sets_by_parts`, `bd_get_price` and shared BrickLink/translation tools | `BRICK_DIRECTORY_BASE_URL`; optional `BRICK_DIRECTORY_ACCESS_TOKEN` only for authenticated MCP/account endpoints, not for public/details endpoints | Public/details endpoints below are read-only. Authenticated account/admin/chat endpoints exist in the app but should stay out of the public skill unless separately scoped. |

## Endpoint matrix from verified OpenAPI specs

### Rebrickable

Source: `backend/libs/rebrickable-client/src/main/resources/openapi/api-spec.yaml`

| Method | Path | operationId | Summary | Safety |
|---|---|---|---|---|
| GET | `/lego/colors/` | `lego_colors_list` | Get a list of all Colors. | read |
| GET | `/lego/colors/{id}/` | `lego_colors_read` | Get details about a specific Color. | read |
| GET | `/lego/elements/{element_id}/` | `lego_elements_read` | Get details about a specific Element ID. | read |
| GET | `/lego/minifigs/` | `lego_minifigs_list` | Get a list of Minifigs. | read |
| GET | `/lego/minifigs/{set_num}/` | `lego_minifigs_read` | Get details for a specific Minifig. | read |
| GET | `/lego/minifigs/{set_num}/parts/` | `lego_minifigs_parts_list` | Get a list of all Inventory Parts in this Minifig. | read |
| GET | `/lego/minifigs/{set_num}/sets/` | `lego_minifigs_sets_list` | Get a list of Sets a Minifig has appeared in. | read |
| GET | `/lego/part_categories/` | `lego_part_categories_list` | Get a list of all Part Categories. | read |
| GET | `/lego/part_categories/{id}/` | `lego_part_categories_read` | Get details about a specific Part Category. | read |
| GET | `/lego/parts/` | `lego_parts_list` | Get a list of Parts. | read |
| GET | `/lego/parts/{part_num}/` | `lego_parts_read` | Get details about a specific Part. | read |
| GET | `/lego/parts/{part_num}/colors/` | `lego_parts_colors_list` | Get a list of all Colors a Part has appeared in. | read |
| GET | `/lego/parts/{part_num}/colors/{color_id}/` | `lego_parts_colors_read` | Get details about a specific Part/Color combination. | read |
| GET | `/lego/parts/{part_num}/colors/{color_id}/sets/` | `lego_parts_colors_sets_list` | Get a list of all Sets the Part/Color combination has appeard in. | read |
| GET | `/lego/sets/` | `lego_sets_list` | Get a list of Sets, optionally filtered by any of the below parameters. | read |
| GET | `/lego/sets/{set_num}/` | `lego_sets_read` | Get details for a specific Set. | read |
| GET | `/lego/sets/{set_num}/alternates/` | `lego_sets_alternates_list` | Get a list of MOCs which are Alternate Builds of a specific Set - i.e. all parts in the MOC can | read |
| GET | `/lego/sets/{set_num}/minifigs/` | `lego_sets_minifigs_list` | Get a list of all Inventory Minifigs in this Set. | read |
| GET | `/lego/sets/{set_num}/parts/` | `lego_sets_parts_list` | Get a list of all Inventory Parts in this Set. | read |
| GET | `/lego/sets/{set_num}/sets/` | `lego_sets_sets_list` | Get a list of all Inventory Sets in this Set. | read |
| GET | `/lego/themes/` | `lego_themes_list` | Return all Themes | read |
| GET | `/lego/themes/{id}/` | `lego_themes_read` | Return details for a specific Theme | read |
| GET | `/swagger/` | `swagger_list` |  | read |
| POST | `/users/_token/` | `users__token_create` | Generate a User Token to be used for authorising user account actions in subsequent calls. Username can be either | write |
| GET | `/users/badges/` | `users_badges_list` | Get a list of all the available Badges | read |
| GET | `/users/badges/{id}/` | `users_badges_read` | Get details about a specific Badge | read |
| GET | `/users/{user_token}/allparts/` | `users_allparts_list` | Get a list of all the Parts in all the user's Part Lists as well as the Parts inside Sets in the user's Set Lists. | read |
| GET | `/users/{user_token}/build/{set_num}/` | `users_build_read` | Find out how many parts the user needs to build the specified Set. | read |
| GET | `/users/{user_token}/lost_parts/` | `users_lost_parts_list` | Get a list of all the Lost Parts from the user's LEGO collection. | read |
| POST | `/users/{user_token}/lost_parts/` | `users_lost_parts_create` | Add one or more Lost Parts to the user. | write |
| DELETE | `/users/{user_token}/lost_parts/{id}/` | `users_lost_parts_delete` | Remove the Lost Part from the user. | destructive/write |
| GET | `/users/{user_token}/minifigs/` | `users_minifigs_list` | Get a list of all the Minifigs in all the user's Sets. Note that this is a read-only list as Minifigs are | read |
| GET | `/users/{user_token}/partlists/` | `users_partlists_list` | Get a list of all the user's Part Lists. | read |
| POST | `/users/{user_token}/partlists/` | `users_partlists_create` | Add a new Part List. | write |
| GET | `/users/{user_token}/partlists/{list_id}/` | `users_partlists_read` | Get details about a specific Part List. | read |
| PUT | `/users/{user_token}/partlists/{list_id}/` | `users_partlists_update` | Replace an existing Part List's details. | write |
| PATCH | `/users/{user_token}/partlists/{list_id}/` | `users_partlists_partial_update` | Update an existing Part List's details. | write |
| DELETE | `/users/{user_token}/partlists/{list_id}/` | `users_partlists_delete` | Delete a Part List and all it's Parts. | destructive/write |
| GET | `/users/{user_token}/partlists/{list_id}/parts/` | `users_partlists_parts_list` | Get a list of all the Parts in a specific Part List. | read |
| POST | `/users/{user_token}/partlists/{list_id}/parts/` | `users_partlists_parts_create` | Add one or more Parts to the Part List. | write |
| GET | `/users/{user_token}/partlists/{list_id}/parts/{part_num}/{color_id}/` | `users_partlists_parts_read` | Get details about a specific Part in the Part List. | read |
| PUT | `/users/{user_token}/partlists/{list_id}/parts/{part_num}/{color_id}/` | `users_partlists_parts_update` | Replace an existing Part's details in the Part List. | write |
| DELETE | `/users/{user_token}/partlists/{list_id}/parts/{part_num}/{color_id}/` | `users_partlists_parts_delete` | Delete a Part from the Part List. | destructive/write |
| GET | `/users/{user_token}/parts/` | `users_parts_list` | Get a list of all the Parts in all the user's Part Lists. | read |
| GET | `/users/{user_token}/profile/` | `users_profile_read` | Get details about a specific user. | read |
| GET | `/users/{user_token}/setlists/` | `users_setlists_list` | Get a list of all the user's Set Lists. | read |
| POST | `/users/{user_token}/setlists/` | `users_setlists_create` | Add a new Set List. | write |
| GET | `/users/{user_token}/setlists/{list_id}/` | `users_setlists_read` | Get details about a specific Set List. | read |
| PUT | `/users/{user_token}/setlists/{list_id}/` | `users_setlists_update` | Replace an existing Set List's details. | write |
| PATCH | `/users/{user_token}/setlists/{list_id}/` | `users_setlists_partial_update` | Update an existing Set List's details. | write |
| DELETE | `/users/{user_token}/setlists/{list_id}/` | `users_setlists_delete` | Delete a Set List and all it's Sets. | destructive/write |
| GET | `/users/{user_token}/setlists/{list_id}/sets/` | `users_setlists_sets_list` | Get a list of all the Sets in a specific Set List. | read |
| POST | `/users/{user_token}/setlists/{list_id}/sets/` | `users_setlists_sets_create` | Add one or more Sets to the Set List. Always send as JSON array. | write |
| GET | `/users/{user_token}/setlists/{list_id}/sets/{set_num}/` | `users_setlists_sets_read` | Get details about a specific Set in the Set List. | read |
| PUT | `/users/{user_token}/setlists/{list_id}/sets/{set_num}/` | `users_setlists_sets_update` | Replace an existing Set's details in the Set List. | write |
| PATCH | `/users/{user_token}/setlists/{list_id}/sets/{set_num}/` | `users_setlists_sets_partial_update` | Update an existing Set's details in the Set List. | write |
| DELETE | `/users/{user_token}/setlists/{list_id}/sets/{set_num}/` | `users_setlists_sets_delete` | Delete a Set from the Set List. | destructive/write |
| GET | `/users/{user_token}/sets/` | `users_sets_list` | Get a list of all the Sets in the user's LEGO collection. | read |
| POST | `/users/{user_token}/sets/` | `users_sets_create` | Add one or more Sets to the user's LEGO collection. Existing Sets are unaffected. | write |
| POST | `/users/{user_token}/sets/sync/` | `users_sets_sync_create` | Synchronise a user's Sets to the POSTed list. | write |
| GET | `/users/{user_token}/sets/{set_num}/` | `users_sets_read` | Get details about a specific Set in the user's LEGO collection. | read |
| PUT | `/users/{user_token}/sets/{set_num}/` | `users_sets_update` | Update an existing Set's quantity in all Set Lists. This PUT call is different to others in that it will create | write |
| DELETE | `/users/{user_token}/sets/{set_num}/` | `users_sets_delete` | Delete the Set from all the user's Set Lists. | destructive/write |

### Brickset

Source: `backend/libs/brickset-client/src/main/resources/openapi/api-spec.yaml`

| Method | Path | operationId | Summary | Safety |
|---|---|---|---|---|
| POST | `/getSets` | `getSets` | Get sets by various parameters | read |
| POST | `/getAdditionalImages` | `getAdditionalImages` | Get additional images for a set | read |
| POST | `/getInstructions2` | `getInstructions2` | Get building instructions for a set | read |
| POST | `/getReviews` | `getReviews` | Get user reviews for a set | read |
| POST | `/login` | `login` | Authenticate user and obtain user hash token | auth |
| POST | `/setCollection` | `setCollection` | Modify user's collection or wishlist | write |
| POST | `/getUserNotes` | `getUserNotes` | Get all user notes for sets | read |

### BrickOwl

Source: `backend/libs/brickowl-client/src/main/resources/openapi/api-spec.yaml`

| Method | Path | operationId | Summary | Safety |
|---|---|---|---|---|
| GET | `/catalog/search` | `n/a` | Search the catalog | read |
| GET | `/catalog/id_lookup` | `n/a` | Look up item by ID | read |
| GET | `/inventory/list` | `n/a` | List store inventory | read |
| POST | `/inventory/update` | `n/a` | Update inventory lot | write |
| POST | `/inventory/create` | `n/a` | Create inventory lot | write |
| GET | `/order/list` | `n/a` | List orders | read |
| GET | `/order/view` | `n/a` | View order details | read |
| POST | `/wishlist/create_list` | `n/a` | Create wishlist | write |
| GET | `/user` | `n/a` | Get user details | read |
| POST | `/bulk` | `n/a` | Bulk requests | write |

### BrickLink

Source: `backend/libs/bricklink-client/src/main/resources/openapi/api-spec.yaml`

| Method | Path | operationId | Summary | Safety |
|---|---|---|---|---|
| GET | `/orders` | `n/a` | Get orders | read |
| GET | `/orders/{order_id}` | `n/a` | Get order | read |
| PUT | `/orders/{order_id}` | `n/a` | Update order | write |
| GET | `/orders/{order_id}/items` | `n/a` | Get order items | read |
| GET | `/orders/{order_id}/messages` | `n/a` | Get order messages | read |
| GET | `/orders/{order_id}/feedback` | `n/a` | Get order feedback | read |
| PUT | `/orders/{order_id}/status` | `n/a` | Update order status | write |
| PUT | `/orders/{order_id}/payment_status` | `n/a` | Update payment status | write |
| POST | `/orders/{order_id}/drive_thru` | `n/a` | Send drive thru | write |
| GET | `/inventories` | `n/a` | Get store inventories | read |
| POST | `/inventories` | `n/a` | Create store inventory/inventories | write |
| GET | `/inventories/{inventory_id}` | `n/a` | Get store inventory | read |
| PUT | `/inventories/{inventory_id}` | `n/a` | Update store inventory | write |
| DELETE | `/inventories/{inventory_id}` | `n/a` | Delete store inventory | destructive/write |
| GET | `/items/{type}/{no}` | `n/a` | Get item | read |
| GET | `/items/{type}/{no}/images/{color_id}` | `n/a` | Get item image | read |
| GET | `/items/{type}/{no}/supersets` | `n/a` | Get supersets | read |
| GET | `/items/{type}/{no}/subsets` | `n/a` | Get subsets | read |
| GET | `/items/{type}/{no}/price` | `n/a` | Get price guide | read |
| GET | `/items/{type}/{no}/colors` | `n/a` | Get known colors | read |
| GET | `/feedback` | `n/a` | Get feedback list | read |
| POST | `/feedback` | `n/a` | Post feedback | write |
| GET | `/feedback/{feedback_id}` | `n/a` | Get feedback | read |
| POST | `/feedback/{feedback_id}/reply` | `n/a` | Reply feedback | write |
| GET | `/colors` | `n/a` | Get color list | read |
| GET | `/colors/{color_id}` | `n/a` | Get color | read |
| GET | `/categories` | `n/a` | Get category list | read |
| GET | `/categories/{category_id}` | `n/a` | Get category | read |
| GET | `/notifications` | `n/a` | Get notifications | read |
| GET | `/coupons` | `n/a` | Get coupons | read |
| POST | `/coupons` | `n/a` | Create coupon | write |
| GET | `/coupons/{coupon_id}` | `n/a` | Get coupon | read |
| PUT | `/coupons/{coupon_id}` | `n/a` | Update coupon | write |
| DELETE | `/coupons/{coupon_id}` | `n/a` | Delete coupon | destructive/write |
| GET | `/settings/shipping_methods` | `n/a` | Get shipping methods | read |
| GET | `/settings/shipping_methods/{method_id}` | `n/a` | Get shipping method | read |
| GET | `/members/{username}/ratings` | `n/a` | Get member rating | read |
| GET | `/members/{username}/my_notes` | `n/a` | Get member note | read |
| POST | `/members/{username}/my_notes` | `n/a` | Create member note | write |
| PUT | `/members/{username}/my_notes` | `n/a` | Update member note | write |
| DELETE | `/members/{username}/my_notes` | `n/a` | Delete member note | destructive/write |
| GET | `/item_mapping/{type}/{no}` | `n/a` | Get ElementID | read |
| GET | `/item_mapping/{element_id}` | `n/a` | Get item number | read |

### BrickEconomy

Source: `backend/libs/brickeconomy-client/src/main/resources/openapi/api-spec.yaml`

| Method | Path | operationId | Summary | Safety |
|---|---|---|---|---|
| GET | `/set/{setNumber}` | `getSet` | Get a set | read |
| GET | `/minifig/{minifigNumber}` | `getMinifig` | Get a minifig | read |
| GET | `/collection/sets` | `getCollectionSets` | Get my sets | read |
| GET | `/collection/minifigs` | `getCollectionMinifigs` | Get my minifigs | read |
| GET | `/salesledger` | `getSalesLedger` | Get my sales ledger | read |
## Brick Directory public/details endpoints

No dedicated OpenAPI file was found for Brick Directory's own public/details controllers. The source of truth for now is the Spring controller code in `backend/apps/brick-directory-mcp-server/src/main/java/directory/brick/app/mcp/controller/` plus the tool constants in `LegoTools.java`.

| Method | Public/details path | Controller source | Current tool coverage | Notes |
|---|---|---|---|---|
| GET | `/api/entities/sets/{setNum}?includeSummary=true&includeContent=false&context=...` | `EntityController.java` | `bd_get_set_details`, `bd_get_set_name`, `bd_get_set_image`, `bd_get_set_alternates`, `bd_find_similar_sets_by_parts` cover related data through MCP tools | Read-only JSON `EntityDetailsResponse`; can include summary, content, contextual suggestions, and structured data. |
| GET | `/api/entities/parts/{partNum}?includeSummary=true&includeContent=false&context=...` | `EntityController.java` | `bd_get_part_details`, `bd_get_part_image`, `bd_search_parts` | Read-only JSON details for part pages/hover/chat. |
| GET | `/api/entities/minifigs/{figNum}?includeSummary=true&includeContent=false&context=...` | `EntityController.java` | `bd_get_minifig_details`, `bd_search_minifigs` | Read-only JSON details for minifigure pages/hover/chat. |
| GET | `/api/entities/elements/{elementId}?includeSummary=true&includeContent=false&context=...` | `EntityController.java` | `bd_search_elements`; details are implemented via `getElementDetailsByIdCommand` internally | Read-only JSON details for LEGO element IDs. |
| GET | `/api/sets/{setNum}/details` | `SetController.java` | `bd_get_set_details` overlaps but renders through tool/service layer | Read-only structured set details from `SetDetailService`. |
| GET | `/api/sets/{setNum}/summary` | `SetController.java` | `bd_get_set_details` can provide summaries | Read-only summary payload. |
| GET | `/api/sets/{setNum}/parts` | `SetController.java` | `bd_get_set_details` / parts detail workflows overlap | Read-only enriched parts list; returns 404 when no enriched parts. |
| GET | `/api/sets/{setNum}/markdown` | `SetController.java` | `bd_get_set_details` uses markdown rendering internally | Read-only plain text markdown rendering. |

## Prompt/tool guidance to preserve in skills

- Rebrickable prompt requires color names and theme names where possible; Brick Directory resolves them to IDs. It also has hybrid pagination with an auto-fetch safety limit of 500 items.
- Brickset prompt says review/opinion questions should use Brickset reviews before pricing tools. Public tools do not require user auth; collection/wishlist tools do.
- BrickOwl prompt states the API cannot fetch marketplace offers from other sellers; its Brick Directory tool surface is inventory/listing management. Keep the known quirk: use `catalog/id_lookup` for ID lookups, not generic `catalog/search`, when identifying known IDs.
- BrickLink prompt exposes a high-cost price breakdown tool that requires an explicit approval parameter in Brick Directory because it can make 200+ API calls and run for minutes. Preserve that approval gate in the standalone skill.
- BrickEconomy prompt says specific price inquiries should prefer the unified Brick Directory `bd_get_price` flow, trying BrickEconomy first and falling back to BrickLink. For standalone BrickEconomy, document its 100 requests/day and 4 requests/minute limits.
- Multi-service ambiguity is real: if a user asks to manage "my collection" or "sell this" without naming a platform and multiple services are configured, ask which service(s) to use before mutating anything.

## Auth environment variables

| Integration | Required/optional env vars | Notes |
|---|---|---|
| Rebrickable | `REBRICKABLE_API_KEY`; optional `REBRICKABLE_USER_TOKEN` | User token can be generated via `/users/_token/`, but username/password handling must be deliberate and never logged. |
| Brickset | `BRICKSET_API_KEY`; optional `BRICKSET_USERNAME`, `BRICKSET_PASSWORD`, `BRICKSET_USER_HASH` | Public reads use API key. Private collection/wishlist operations need a user hash from login or a stored hash. |
| BrickOwl | `BRICKOWL_API_KEY` | Spec uses query parameter `key`; skill should read from env and never print it. |
| BrickLink | `BRICKLINK_CONSUMER_KEY`, `BRICKLINK_CONSUMER_SECRET`, `BRICKLINK_TOKEN`, `BRICKLINK_TOKEN_SECRET` | OAuth 1.0; treat all four as secrets. |
| BrickEconomy | `BRICKECONOMY_API_KEY` | Spec sends API key in `x-apikey` header. |
| Brick Directory | `BRICK_DIRECTORY_BASE_URL`; optional `BRICK_DIRECTORY_ACCESS_TOKEN` | Public/details endpoints can work with base URL only. Auth token should be optional and scoped to future authenticated workflows. |

## Write/destructive policy for generated skills

Default rule: a skill may read with configured credentials, but any operation that changes a vendor account, marketplace listing, order, collection, wishlist, note, coupon, feedback, or local persisted user data requires explicit user intent in the current conversation. Do not infer permission from stored credentials.

Clearly mark these as mutating:

- Rebrickable: all `POST`, `PUT`, `PATCH`, and `DELETE` under `/users/{user_token}/...`, especially list delete/sync and lost parts.
- Brickset: `setCollection` for collection/wishlist/note/rating/quantity changes; `login` handles credentials but is not itself a user-data mutation.
- BrickOwl: `inventory/create`, `inventory/update`, `wishlist/create_list`, and `bulk` when used for writes. `DELETE` listing is present in Brick Directory tools even though the verified OpenAPI matrix models inventory mutation via POST endpoints.
- BrickLink: all order, inventory, feedback, coupon, and member-note writes/deletes.
- BrickEconomy: none in the verified OpenAPI spec.
- Brick Directory public/details endpoints: none in the public/details matrix above.

## Gaps to close before implementation PRs

1. Generate or hand-author `references/openapi/brick-directory-public.yaml` from `EntityController.java` and `SetController.java`; no checked-in public OpenAPI spec currently exists for these endpoints.
2. Decide whether standalone skills should call vendor APIs directly with curl/CLI snippets or wrap generated clients. The inventory above supports either path.
3. Normalize tool names: Brick Directory's Java methods use camelCase internally, but MCP/exported tool names are mostly `bd_*` snake case. Skills should document the exported names.
4. Reconcile BrickOwl prompt safety: current prompt says no approval required; this skills repo should still require explicit user intent for writes because marketplace listing changes are real external side effects.
