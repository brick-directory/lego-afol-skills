# lego-afol-skills

Agent skills and reference material for LEGO AFOL integrations.

This repo is the stable home for Brick Directory-derived skills that help agents work with LEGO data providers such as Rebrickable, Brickset, BrickOwl, BrickLink, and BrickEconomy. The goal is to keep skill UX concise while grounding endpoint details in Brick Directory's verified OpenAPI specs and current MCP prompt guidance.

## Layout

```text
.
├── AGENTS.md                         # repo conventions for agents and contributors
├── README.md                         # this overview
├── references/
│   ├── SOURCE.md                     # copied-reference mapping
│   ├── SHA256SUMS                    # drift detection for copied references
│   ├── openapi/                      # verified OpenAPI specs copied from Brick Directory
│   │   ├── rebrickable.yaml
│   │   ├── brickset.yaml
│   │   ├── brickowl.yaml
│   │   ├── bricklink.yaml
│   │   └── brickeconomy.yaml
│   └── prompts/                      # MCP prompt guidance copied from Brick Directory
└── scripts/
    ├── sync-from-brick-directory.sh  # refresh copied references from source
    └── validate-skills.sh            # baseline repo and skill hygiene checks
```

Future integration skills should live under `skills/<integration>/SKILL.md`.

## Refresh references

```bash
scripts/sync-from-brick-directory.sh /path/to/brick-directory
```

The script copies the verified specs and prompt files, then refreshes `references/SHA256SUMS`. Do not hand-edit files under `references/openapi/` or `references/prompts/`; fix the Brick Directory source or resync from it.

## Validate

```bash
scripts/validate-skills.sh
```

Current baseline checks:

- required repo files exist
- copied OpenAPI specs and key prompt files exist
- copied reference checksums are current
- committed text files outside copied references end with a newline
- any future `skills/**/SKILL.md` files include frontmatter, env-var docs, reference links, and write-safety notes

## Safety rules

- Secrets are referenced only as environment variables; real values are never committed.
- Mutating marketplace, inventory, collection, wishlist, order, feedback, coupon, or member-note operations must require explicit user intent.
- Read-only examples are preferred; write examples must make the confirmation boundary painfully obvious.
