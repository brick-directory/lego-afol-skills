# AGENTS.md — lego-afol-skills

This repository stores agent skills and supporting references for LEGO AFOL integrations.

## Source of truth

- The Brick Directory source repository is the source of truth for integration shape.
- Copied OpenAPI specs live in `references/openapi/` and must be refreshed with `scripts/sync-from-brick-directory.sh`.
- Copied MCP/domain prompts live in `references/prompts/` and must be refreshed with the same script.
- Do not scrape vendor docs or hand-edit copied specs/prompts when Brick Directory already has verified sources.
- If a spec is missing from Brick Directory, document the gap in the PR instead of inventing endpoint contracts.

## Secrets and credentials

- Never commit API keys, passwords, OAuth tokens, cookies, or real user identifiers.
- Skills may reference credentials only as environment variables, for example `REBRICKABLE_API_KEY` or `BRICKLINK_TOKEN_SECRET`.
- Examples must use placeholders such as `$REBRICKABLE_API_KEY`; never paste real values.
- Store local credentials in an ignored `.env` file outside committed docs.

## Write safety

- Marketplace, inventory, collection, wishlist, order, feedback, coupon, member-note, and other mutating operations must be marked clearly.
- Skill instructions must require explicit user intent before any external mutation.
- Default examples should be read-only. If a write example is necessary, make confirmation boundaries obvious and prefer dry-run language.

## Repository workflow

- Work on a branch; do not commit directly to `main`.
- Run `scripts/validate-skills.sh` before committing.
- Keep copied references in sync with Brick Directory by running `scripts/sync-from-brick-directory.sh <path-to-brick-directory>` instead of manual edits.
- Commit generated reference updates together with the script or skill change that requires them.
- Open a pull request for review; do not merge your own PR.

## Skill conventions

- One integration per skill unless a later orchestration skill intentionally composes multiple integrations.
- Every `SKILL.md` must include YAML frontmatter with `name`, `description`, and `version`.
- Every skill must document required environment variables, read-only smoke checks, write-safety rules, and links to the relevant files under `references/`.
- Prefer concise, agent-actionable workflows over exhaustive vendor prose.
