#!/usr/bin/env bash
# Fail if the public tree (or a staged commit message) contains private-repo fingerprints.
# Allowed: PROVENANCE.md and the prereg-luna-modes-lock witness may name the private lock.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PATTERN='mulit_agent_jev|/home/azvyagintsev|github\.com/[^/]+/multi_agent_jev/'
ALLOW='^(PROVENANCE\.md|.*ORIGINAL_COMMIT\.txt)$'

hits="$(rg -n -I --glob '!.git/**' --glob '!scripts/check_no_private_leak.sh' \
  -e 'mulit_agent_jev' -e '/home/azvyagintsev' -e 'github.com/.*/multi_agent_jev/' . || true)"

bad=""
while IFS= read -r line; do
  [[ -z "$line" ]] && continue
  file="${line%%:*}"
  if [[ "$file" =~ $ALLOW ]]; then
    continue
  fi
  # PROVENANCE may mention the private repo name without a URL — already on allow list.
  bad+="$line"$'\n'
done <<< "$hits"

# Binary / PDF scan
pdf_hits="$(strings article/Luna.pdf 2>/dev/null | rg -n 'multi_agent_jev|mulit_agent_jev|/home/azvyagintsev' || true)"

if [[ -n "$bad" || -n "$pdf_hits" ]]; then
  echo "PRIVATE LEAK into luna_life — refuse commit/push:" >&2
  [[ -n "$bad" ]] && printf '%s' "$bad" >&2
  [[ -n "$pdf_hits" ]] && echo "article/Luna.pdf:" >&2 && printf '%s\n' "$pdf_hits" >&2
  exit 1
fi

echo "check_no_private_leak: ok"
