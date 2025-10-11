#!/usr/bin/env bash
set -euo pipefail
#
# Safe Branch Cleanup Script
# Removes all remote branches except those explicitly whitelisted.
# Default whitelist: main V1.00D
#
# Features:
#  - Dry run by default (no deletions unless --apply)
#  - Creates backup tags for each branch tip before deletion
#  - Optional deletion of local branches with --also-local
#  - Configurable whitelist via WHITELIST env var (space-separated names)
#
# Usage:
#   ./scripts/safe-branch-cleanup.sh
#   ./scripts/safe-branch-cleanup.sh --apply
#   ./scripts/safe-branch-cleanup.sh --apply --also-local
#   WHITELIST="main V1.00D release" ./scripts/safe-branch-cleanup.sh --apply
#
# NOTE: This script does NOT filter out branches with open PRs.
# Review the dry-run output before applying.

WHITELIST="${WHITELIST:-main V1.00D}"
APPLY=false
ALSO_LOCAL=false
NONINTERACTIVE=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply) APPLY=true ;; 
    --also-local) ALSO_LOCAL=true ;; 
    -y|--yes) NONINTERACTIVE=true ;; 
    -h|--help)
      grep '^#' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1;
      ;;
  esac
  shift
done

command -v git >/dev/null || { echo "git not found"; exit 1; }
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "Not a git repository"; exit 1; }

git fetch --all --prune

WL_REGEX="$(printf '%s\n' $WHITELIST | sed 's/[.[*^$()+?{}|]/\\&/g' | paste -sd'|' -)"
[[ -n "$WL_REGEX" ]] || { echo "Whitelist is empty"; exit 1; }

mapfile -t REMOTES < <(git branch -r --format='%(refname:short)' | sed -n 's#^origin/##p')

TO_DELETE=()
for b in "${REMOTES[@]}"; do
  if [[ "$b" =~ ^($WL_REGEX)$ ]]; then
    continue
  fi
  TO_DELETE+=("$b")
done

echo "Whitelist: $WHITELIST"
echo "Remote branches to delete:"
if ((${#TO_DELETE[@]})); then
  printf '  %s\n' "${TO_DELETE[@]}"
else
  echo "  <none>"
fi

if ! $APPLY; then
  echo
  echo "Dry run only. Re-run with --apply to actually delete."
  exit 0
fi

if ((${#TO_DELETE[@]}==0)); then
  echo "Nothing to delete."
  exit 0
fi

if ! $NONINTERACTIVE; then
  read -r -p "Delete ${#TO_DELETE[@]} remote branches? [y/N] " ans
  [[ "$ans" =~ ^[Yy]$ ]] || { echo "Aborted."; exit 1; }
fi

TS=$(date +%Y%m%d-%H%M%S)
echo "Creating backup tags..."
for b in "${TO_DELETE[@]}"; do
  sha=$(git rev-parse "origin/$b" 2>/dev/null || true)
  if [[ -n "$sha" ]]; then
    tag="backup/${b//\//_}-$TS"
    git tag -a "$tag" "$sha" -m "Backup of $b before deletion"
  fi
done
git push --tags

echo "Deleting remote branches..."
for b in "${TO_DELETE[@]}"; do
  echo "  Deleting origin/$b"
  git push origin --delete "$b" || echo "  Failed (maybe protected/missing)"
done

if $ALSO_LOCAL; then
  echo "Deleting local counterparts..."
  for b in "${TO_DELETE[@]}"; do
    if git show-ref --verify --quiet "refs/heads/$b"; then
      git branch -D "$b" || true
    fi
  done
fi

echo "Cleanup complete."