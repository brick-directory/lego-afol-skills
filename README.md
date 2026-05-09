# lego-afol-skills

Agent skills and small CLIs for LEGO AFOL integrations.

This repository is meant to be skills-first: agents should be able to use each integration directly from environment variables and a repo-local CLI, without depending on any separate app.

## Layout

```text
.
├── AGENTS.md                         # repo conventions for agents and contributors
├── README.md                         # this overview
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
│   ├── brickowl/
│   │   ├── SKILL.md                   # BrickOwl skill
│   │   ├── references/                # BrickOwl references bundled with the skill archive
│   │   └── scripts/
│   │       ├── brickowl               # BrickOwl CLI wrapper
│   │       └── brickowl_cli.py        # BrickOwl CLI implementation
│   └── rebrickable/
│       ├── SKILL.md                   # Rebrickable skill
│       ├── references/                # Rebrickable references bundled with the skill archive
│       └── scripts/
│           ├── rebrickable            # Rebrickable CLI wrapper
│           └── rebrickable_cli.py     # Rebrickable CLI implementation
└── tests/
    ├── test_brickowl_cli.py           # BrickOwl CLI unit tests
    └── test_rebrickable_cli.py        # Rebrickable CLI unit tests
```

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
