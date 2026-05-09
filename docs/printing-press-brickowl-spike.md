# Printing Press BrickOwl spike

## Decision

Do not adopt CLI Printing Press output for the BrickOwl skill implementation yet.

Printing Press can generate and validate a working Go CLI/MCP skeleton from the verified Brick Directory BrickOwl OpenAPI spec, but the generated output is not a good durable skill source without manual patching. The main blockers are BrickOwl auth semantics and write-safety classification: the generated CLI treats `BRICKOWL_API_KEY` as a query parameter for all requests, while the source spec says GET requests use `key` in the query and POST requests use `key` in the request body; MCP tools also expose `key` as a required tool argument instead of relying cleanly on env-driven configuration. Mutating tools are not clearly classified as destructive, including inventory create/update/delete-by-flag and wishlist creation.

Use the generated candidate as a reference for endpoint coverage and command grouping only. Hand-author the BrickOwl skill first, then revisit Printing Press if upstream generation can model BrickOwl's per-method API-key placement and destructive/read-only annotations accurately.

## Installation/build result

Host baseline:

- `go` was not installed on `PATH`.
- `printing-press` was not installed on `PATH`.
- The published `cli-printing-press_linux_amd64.tar.gz` release asset does not run on this host because the host is `aarch64`.
- The published `cli-printing-press_linux_arm64.tar.gz` release asset runs successfully: `printing-press 4.2.0`.

For validation only, Go 1.26.3 linux/arm64 was downloaded under `/tmp/go1263` from `https://dl.google.com/go/go1.26.3.linux-arm64.tar.gz`. With that temporary Go toolchain, Printing Press generated and validated the candidate successfully.

Generation command:

```bash
PATH=/tmp/go1263/go/bin:$PATH /tmp/printing-press-bin-arm/printing-press generate \
  --spec references/openapi/brickowl.yaml \
  --name brickowl \
  --output generated/brickowl-pp-cli \
  --spec-source official \
  --force \
  --validate \
  --json
```

Validation output included:

- `PASS go mod tidy`
- `PASS govulncheck ./...`
- `PASS go vet ./...`
- `PASS go build ./...`
- `PASS build runnable binary`
- `PASS brickowl-pp-cli --help`
- `PASS brickowl-pp-cli version`
- `PASS brickowl-pp-cli doctor`

Additional local checks:

```bash
PATH=/tmp/go1263/go/bin:$PATH go test ./...
/tmp/printing-press-bin-arm/printing-press verify-skill --dir . --json
/tmp/printing-press-bin-arm/printing-press tools-audit . --json
```

Results:

- `go test ./...` passed.
- `verify-skill` passed with no findings.
- `tools-audit` returned `null` findings.

## Candidate shape inspected

Generated candidate path during the spike: `generated/brickowl-pp-cli/`.

The generated tree included:

- `cmd/brickowl-pp-cli/main.go`
- `cmd/brickowl-pp-mcp/main.go`
- endpoint commands under `internal/cli/`
- typed MCP tools under `internal/mcp/tools.go`
- `README.md`
- `SKILL.md`
- copied `spec.yaml`
- local SQLite/search/sync scaffolding

The generated source was about 660 KB after removing build artifacts. The validation build also produced binary/MCP bundle artifacts under `generated/brickowl-pp-cli/build/`, but those should not be committed.

## Auth handling

Positive:

- The generator detected `BRICKOWL_API_KEY` and documents it in `README.md` and `SKILL.md`.
- `internal/config/config.go` reads `BRICKOWL_API_KEY` and supports a config file at `~/.config/brickowl-pp-cli/config.toml`.
- `doctor` exists for setup validation.

Problems:

- `internal/client/client.go` applies env auth by setting `?key=<token>` for every method.
- BrickOwl's source spec says GET requests use `key` in the URL, but POST requests include `key` in the request body.
- POST commands still expose a `--key` body flag, so env-driven use and flag-driven use diverge.
- MCP tools require `key` as an explicit parameter on every endpoint, which is noisy for agents and risks pushing secrets into tool-call transcripts instead of keeping credentials in env/config.

Observed dry runs with `BRICKOWL_API_KEY=dummy`:

```text
GET /catalog/id_lookup?...&key=****ummy
POST /inventory/create?key=****ummy
  Body: {"boid":"123","condition":"new","price":1.23,"quantity":1}
```

The POST request shape does not match the BrickOwl spec.

## Command ergonomics

Positive:

- Root help is agent-friendly and includes `--agent`, `--json`, `--compact`, `--select`, `--dry-run`, `--no-input`, `--yes`, `--data-source`, and `--deliver`.
- `catalog list` maps to `/catalog/id_lookup`, which matches the project memory that ID lookup should prefer `catalog/id_lookup`, not catalog search.
- `which`, `doctor`, `agent-context`, `profile`, and `feedback` are useful agent affordances.

Problems:

- Generated names are mechanically accurate but sometimes awkward: `catalog list-search`, `order list-view`, `inventory create-update`.
- Read-only lookup is named `catalog list`, which hides that it is really ID lookup.
- Bulk/local sync/search scaffolding adds surface area that may distract from a concise skill UX for a 10-operation API.

## MCP/read-write annotations

Positive:

- GET endpoints are annotated with `WithReadOnlyHintAnnotation(true)` and `WithDestructiveHintAnnotation(false)`.
- Search/sql/context helper tools are read-only.

Problems:

- Mutating endpoints are only annotated with `WithDestructiveHintAnnotation(false)` and `WithOpenWorldHintAnnotation(true)`.
- `inventory_create` creates a marketplace inventory lot but is not destructive/write-classified.
- `inventory_create-update` can update fields and includes a `delete` flag, but is not destructive/write-classified.
- `wishlist_create` creates a remote wishlist but is not destructive/write-classified.
- The generated `SKILL.md` says agent mode expands to `--yes`, which is a bad default for marketplace mutation unless the skill separately requires explicit user intent.

For this repository's safety model, marketplace/list/collection writes must be painfully obvious and require explicit user intent. The generated annotations do not meet that bar.

## Generated SKILL.md quality

Positive:

- Has frontmatter, install guidance, command reference, auth setup, agent mode, response envelope, delivery, profiles, exit codes, MCP install notes, and direct-use flow.
- `verify-skill` passes, so referenced command/flag shapes match the generated code.

Problems:

- It is too generic and too long for the durable AFOL skill UX.
- It includes generated install paths to a public `printing-press-library` entry that does not exist for this unpublished local BrickOwl candidate.
- It does not incorporate Brick Directory's BrickOwl domain prompt details, notably the API limitation that BrickOwl does not expose other-seller marketplace offer data.
- It repeats `--key your-token-here` examples instead of consistently preferring `BRICKOWL_API_KEY`.
- It does not clearly require confirmation before inventory/listing/wishlist mutations.

## Fit for env-var driven use

Not good enough yet.

The generated CLI can read `BRICKOWL_API_KEY`, but the generated command/API surface still treats `key` as a normal operation parameter. For read-only GET requests this is workable; for POST requests it produces the wrong request placement for env auth and leaves agents with a confusing choice between env auth and `--key`/MCP `key` parameters.

A hand-authored BrickOwl skill can do better immediately:

- keep `BRICKOWL_API_KEY` in env/config only;
- teach agents `catalog/id_lookup` vs search directly;
- document BrickOwl's lack of other-seller marketplace pricing API;
- put explicit write-safety rules around inventory and wishlist mutations;
- use concise curl examples instead of a 60-file generated CLI.

## Prototype commit decision

Do not commit `generated/brickowl-pp-cli/` in this PR.

The candidate is mechanically interesting but not good enough to be a committed implementation prototype because it would add generated bulk while still needing hand patches for the two hardest parts: BrickOwl auth placement and mutating-operation safety. Committing it now would make the repo noisier without improving the durable skill implementation.

If Printing Press is revisited later, the acceptance bar should be:

1. POST env auth for BrickOwl is placed in the request body, not query.
2. MCP tools do not expose API keys as ordinary tool arguments when env/config auth is available.
3. Create/update/delete/wishlist operations are write/destructive annotated and the generated skill requires explicit user intent.
4. Generated skill text can be layered with Brick Directory's MCP prompt guidance without becoming noisy.
5. Build artifacts are excluded by default.
