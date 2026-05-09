# AGENTS.md — lego-afol-skills

This repository stores agent skills and supporting references for LEGO AFOL integrations.

## Source of truth

- Checked-in API references live in `references/openapi/`.
- Checked-in domain guidance lives in `references/prompts/`.
- Do not scrape vendor docs or hand-edit checked-in references when the existing reference already answers the endpoint shape.
- If a spec is missing or insufficient, document the gap in the PR instead of inventing endpoint contracts.
- Skills should provide a repo-local CLI when practical, so agents can execute workflows directly with environment variables.

## Secrets and credentials

- Never commit API keys, passwords, OAuth tokens, cookies, or real user identifiers.
- Skills may reference credentials only as environment variables, for example `BRICKOWL_API_KEY`.
- Examples must use placeholders such as `$BRICKOWL_API_KEY`; never paste real values.
- Store local credentials in an ignored `.env` file outside committed docs.

## Write safety

- Marketplace, inventory, collection, wishlist, order, feedback, coupon, member-note, and other mutating operations must be marked clearly.
- Skill instructions must require explicit user intent before any external mutation.
- CLIs should guard mutating operations with a flag such as `--yes` and offer `--dry-run` where useful.
- Default examples should be read-only. If a write example is necessary, make confirmation boundaries obvious and prefer dry-run language.

## Repository workflow

- Work on a branch; do not commit directly to `main`.
- Run `scripts/validate-skills.sh` before committing.
- Run relevant unit tests before committing CLI changes.
- Open a pull request for review; do not merge your own PR.

## Skill conventions

- One integration per skill unless a later orchestration skill intentionally composes multiple integrations.
- Use `skills/brickowl/` and `docs/skill-packaging-pattern.md` as the template for provider skills: keep `SKILL.md`, runtime CLI files, bundled OpenAPI references, and prompt references under `skills/<provider>/`.
- Do not put provider runtime scripts in repo-global `scripts/`; reserve that directory for repo maintenance scripts.
- Every `SKILL.md` must include YAML frontmatter with `name`, `description`, and `version`.
- Every skill must document required environment variables, read-only smoke checks, write-safety rules, and links to the relevant files under `references/`.
- Prefer concise, agent-actionable workflows over exhaustive vendor prose.
