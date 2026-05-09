#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd -- "$SCRIPT_DIR/.." && pwd)
cd "$REPO_ROOT"

failures=0
fail() {
  echo "error: $*" >&2
  failures=$((failures + 1))
}

check_file_exists() {
  local path=$1
  [[ -f "$path" ]] || fail "missing required file: $path"
}

check_trailing_newline() {
  local path=$1
  [[ ! -s "$path" ]] && return 0
  local last_byte
  last_byte=$(tail -c 1 "$path" | od -An -t x1 | tr -d '[:space:]')
  [[ "$last_byte" == "0a" ]] || fail "missing trailing newline: $path"
}

required_files=(
  README.md
  AGENTS.md
  scripts/brickowl
  scripts/brickowl_cli.py
  scripts/validate-skills.sh
  references/SOURCE.md
  references/SHA256SUMS
  references/openapi/rebrickable.yaml
  references/openapi/brickset.yaml
  references/openapi/brickowl.yaml
  references/openapi/bricklink.yaml
  references/openapi/brickeconomy.yaml
  skills/brickowl/SKILL.md
  tests/test_brickowl_cli.py
)

for path in "${required_files[@]}"; do
  check_file_exists "$path"
done

for prompt in \
  references/prompts/rebrickable-tools.txt \
  references/prompts/brickset-tools.txt \
  references/prompts/brickset-private-tools.txt \
  references/prompts/brickowl-tools.txt \
  references/prompts/bricklink-tools.txt \
  references/prompts/brickeconomy-tools.txt; do
  check_file_exists "$prompt"
done

if [[ -f scripts/brickowl_cli.py ]]; then
  python3 -m py_compile scripts/brickowl_cli.py || fail "scripts/brickowl_cli.py does not compile"
fi

if [[ -d skills ]]; then
  while IFS= read -r -d '' skill; do
    rel=${skill#./}
    if ! sed -n '1p' "$skill" | grep -qx -- '---'; then
      fail "$rel must start with YAML frontmatter delimiter"
    fi
    if [[ $(grep -n '^---$' "$skill" | wc -l | tr -d ' ') -lt 2 ]]; then
      fail "$rel must contain closing YAML frontmatter delimiter"
    fi
    grep -Eq '^name:[[:space:]]*[^[:space:]]+' "$skill" || fail "$rel frontmatter must include name"
    grep -Eq '^description:[[:space:]]*.+' "$skill" || fail "$rel frontmatter must include description"
    grep -Eq '^version:[[:space:]]*.+' "$skill" || fail "$rel frontmatter must include version"
    grep -Eq '(^|[^A-Z0-9_])[A-Z][A-Z0-9_]{2,}(_[A-Z0-9]+)*($|[^A-Z0-9_])' "$skill" || fail "$rel should document required env vars by name"
    grep -Eq 'references/(openapi|prompts)/' "$skill" || fail "$rel should link to checked-in OpenAPI or prompt references"
    grep -Eiq 'explicit (user )?(intent|approval|confirmation)|require[s]? confirmation|read-only|dry-run' "$skill" || fail "$rel should document write safety / read-only behavior"
  done < <(find skills -type f -name SKILL.md -print0 | sort -z)
else
  fail "missing skills/ directory"
fi

while IFS= read -r -d '' path; do
  check_trailing_newline "$path"
done < <(find . -type f \
  ! -path './.git/*' \
  ! -path './references/openapi/*' \
  ! -path './references/prompts/*' \
  ! -path './*/__pycache__/*' \
  ! -name '*.pyc' \
  -print0)

if [[ -f references/SHA256SUMS ]]; then
  sha256sum --check --quiet references/SHA256SUMS || fail "reference checksums are stale"
fi

if (( failures > 0 )); then
  echo "validation failed with $failures issue(s)" >&2
  exit 1
fi

echo "validation passed"
