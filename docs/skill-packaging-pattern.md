# Skill packaging pattern

Use `skills/brickowl/` as the reference implementation for provider-specific AFOL skills.

## Expected package shape

Each provider should be self-contained under `skills/<provider>/` so it can be copied, archived, or installed without depending on repo-global runtime files:

```text
skills/<provider>/
├── SKILL.md
├── scripts/
│   ├── <provider>           # small executable wrapper
│   └── <provider>_cli.py    # implementation, or equivalent language/runtime
└── references/
    ├── openapi/
    │   └── <provider>.yaml
    └── prompts/
        └── <provider>-tools.txt
```

Rules:

- `SKILL.md` is the agent-facing entrypoint. It must document when to use the skill, required env vars, read-only smoke checks, write-safety boundaries, and the bundled reference files.
- `scripts/<provider>` should be the stable command agents run. Keep it thin; put real logic in `scripts/<provider>_cli.py` or another implementation file in the same skill package.
- `references/openapi/*.yaml` and `references/prompts/*.txt` inside the skill are the source files that travel with the skill archive.
- Repo-global `references/` may keep aggregate or provenance copies, but provider skills must not require those paths at runtime.
- Repo-global `scripts/` is for repository maintenance only, such as `scripts/validate-skills.sh`. Do not put provider runtime CLIs there.

## Credentials and redaction

Credentials must be environment-variable only.

- Document required names explicitly, for example `BRICKOWL_API_KEY`.
- Examples may show placeholders like `$BRICKOWL_API_KEY` or `export BRICKOWL_API_KEY=...`.
- Never commit, print, log, or paste real API keys, passwords, OAuth tokens, cookies, account IDs, order addresses, buyer data, or other private account data.
- Dry-run output must redact secrets. Prefer labels such as `[from BRICKOWL_API_KEY]` over echoing values.
- `.env` is local-only and ignored; do not reference private local values in docs, tests, PR bodies, or comments.

## Write safety

Default examples should be read-only.

Marketplace, inventory, collection, wishlist, order, feedback, coupon, member-note, and any other mutating operation must require explicit user intent in the current conversation. CLI implementations should enforce that mechanically with `--yes` for writes and `--dry-run` where useful.

For write workflows, the skill should tell the agent to restate the exact mutation before asking for confirmation: provider, operation, item/lot/order identifiers, quantity, price, condition, list name, and any batch payload summary.

## Live smoke tests

Local validation is required for every PR:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
scripts/validate-skills.sh
git diff --check
```

When real credentials are available in the environment, run one read-only live smoke check per provider. For BrickOwl, the reference smoke check is:

```bash
skills/brickowl/scripts/brickowl user
```

Live smoke-test rules:

- Do not print private account data in PR bodies, comments, docs, or task handoffs.
- Report only that the smoke check passed, failed, or was skipped because credentials were unavailable.
- If output is needed for debugging, redact account identifiers, emails, addresses, order data, and tokens before sharing.
- Never run mutating live tests unless the task explicitly asks for them and the user confirms the exact operation.

## Adding the next provider skill

1. Create `skills/<provider>/SKILL.md` with frontmatter and agent-actionable workflows.
2. Add the provider CLI wrapper and implementation under `skills/<provider>/scripts/`.
3. Copy the provider OpenAPI spec and prompt guidance into `skills/<provider>/references/`.
4. Keep examples read-only unless demonstrating a guarded `--dry-run` write.
5. Add or update unit tests for the provider CLI.
6. Run validation and open a PR.

BrickOwl is the model: self-contained skill archive, env-var credentials, guarded mutations, local tests, and optional read-only live smoke checks.
