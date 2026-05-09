# afol-skills

Agent skills and small CLIs for AFOL integrations.

This repository is meant to be skills-first: agents should be able to use each integration directly from environment variables and a repo-local CLI, without depending on any separate app.

## Layout

```text
.
├── AGENTS.md                         # repo conventions for agents and contributors
├── README.md                         # this overview
├── docs/
│   └── skill-packaging-pattern.md     # provider skill package template
├── references/
│   ├── SOURCE.md                     # public provenance notes for checked-in references
│   ├── SHA256SUMS                    # drift detection for checked-in references
│   ├── openapi/                      # checked-in API references
│   │   ├── rebrickable.yaml
│   │   ├── brickset.yaml
│   │   ├── brickowl.yaml
│   │   ├── bricklink.yaml
│   │   └── brickeconomy.yaml
│   └── prompts/                      # checked-in domain guidance
├── scripts/
│   └── validate-skills.sh             # baseline repo and skill hygiene checks
├── skills/
│   ├── afol/
│   │   ├── SKILL.md                   # Meta-router over provider skills
│   │   ├── references/                # Orchestration references bundled with the skill archive
│   │   └── scripts/                   # Routing/credential-readiness CLI
│   ├── brickowl/
│   │   ├── SKILL.md                   # BrickOwl skill
│   │   ├── references/                # BrickOwl references bundled with the skill archive
│   │   └── scripts/                   # BrickOwl CLI wrapper and implementation
│   ├── brickset/
│   │   ├── SKILL.md                   # Brickset skill
│   │   ├── references/                # Brickset references bundled with the skill archive
│   │   └── scripts/                   # Brickset CLI wrapper and implementation
│   └── rebrickable/
│       ├── SKILL.md                   # Rebrickable skill
│       ├── references/                # Rebrickable references bundled with the skill archive
│       └── scripts/                   # Rebrickable CLI wrapper and implementation
└── tests/
    ├── test_afol_cli.py          # AFOL router unit tests
    ├── test_brickowl_cli.py           # BrickOwl CLI unit tests
    ├── test_brickset_cli.py           # Brickset CLI unit tests
    └── test_rebrickable_cli.py        # Rebrickable CLI unit tests
```

## Skill packaging pattern

Provider skills should follow the BrickOwl package shape documented in
`docs/skill-packaging-pattern.md`: keep `SKILL.md`, the runtime CLI wrapper and
implementation, OpenAPI references, and prompt references under
`skills/<provider>/`. Repo-global `scripts/` is reserved for repository
maintenance, not provider runtime CLIs.

## AFOL meta-router

Use the meta skill when the task is broad and the right provider is not obvious:

```bash
skills/afol/scripts/afol route "What is set 10236-1 worth?"
skills/afol/scripts/afol route "Find parts for Millennium Falcon"
skills/afol/scripts/afol credentials
```

The meta skill does not call external APIs. It routes agents to the provider skills below and reports credential readiness without printing secret values.

## BrickOwl CLI

Set credentials through environment variables:

```bash
export BRICKOWL_API_KEY=...
```

Read-only examples:

```bash
skills/brickowl/scripts/brickowl user
skills/brickowl/scripts/brickowl id-lookup --id 75192-1 --type Set --id-type set_number
skills/brickowl/scripts/brickowl catalog-search --query "Millennium Falcon" --type Set --page 1
skills/brickowl/scripts/brickowl inventory-list --page 1
```

Mutating commands require explicit `--yes`; inspect with `--dry-run` first:

```bash
skills/brickowl/scripts/brickowl inventory-create --dry-run --boid 123 --quantity 1 --price 9.99 --condition news
```

## Brickset CLI

Set credentials through environment variables:

```bash
export BRICKSET_API_KEY=...
export BRICKSET_USER_HASH=...      # optional, for private collection/wishlist/notes flows
```

Read-only examples:

```bash
skills/brickset/scripts/brickset details --set-number 10270-1
skills/brickset/scripts/brickset instructions --set-number 10270-1
skills/brickset/scripts/brickset images --set-id 30142
skills/brickset/scripts/brickset reviews --set-id 30142
```

Mutating collection/wishlist commands require explicit `--yes`; inspect with `--dry-run` first:

```bash
skills/brickset/scripts/brickset collection-set --dry-run --set-id 30142 --own 1 --qty-owned 1
```

## Rebrickable CLI

Set credentials through environment variables:

```bash
export REBRICKABLE_API_KEY=...
export REBRICKABLE_USER_TOKEN=...  # optional; needed for user collection endpoints
```

Read-only examples:

```bash
skills/rebrickable/scripts/rebrickable sets --search "Millennium Falcon" --page-size 5
skills/rebrickable/scripts/rebrickable set --set-num 75192-1
skills/rebrickable/scripts/rebrickable parts --part-num 3001
skills/rebrickable/scripts/rebrickable profile
```

Mutating commands require explicit `--yes`; inspect with `--dry-run` first:

```bash
skills/rebrickable/scripts/rebrickable add-sets-to-list --dry-run --list-id 123 --sets-json '[{"set_num":"8043-1","quantity":1}]'
```

## Validate

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
scripts/validate-skills.sh
```

Current baseline checks:

- required repo files exist
- checked-in OpenAPI specs and key prompt files exist
- checked-in reference checksums are current
- Python CLI compiles
- committed text files outside checked-in generated references end with a newline
- `skills/**/SKILL.md` files include frontmatter, env-var docs, reference links, and write-safety notes

## Safety rules

- Secrets are referenced only as environment variables; real values are never committed.
- Marketplace, inventory, collection, wishlist, order, feedback, coupon, or member-note mutations must require explicit user intent.
- Read-only examples are preferred; write examples must make the confirmation boundary painfully obvious.
