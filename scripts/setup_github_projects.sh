#!/usr/bin/env bash
# Create GitHub milestones and a project board using the GitHub CLI.
# Usage: ./scripts/setup_github_projects.sh <owner> <repo>

set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <owner> <repo>"
  exit 1
fi

owner="$1"
repo="$2"

milestones=(
  "Phase 1: MVP"
  "Phase 2: Industry & Market"
  "Phase 3: Corporation/Alliance Features"
  "Phase 4: Scaling & Polish"
)

for m in "${milestones[@]}"; do
  gh api -X POST \
    "repos/$owner/$repo/milestones" \
    -f title="$m" || true
done

# Create a classic project board named "Development Roadmap"
# Note: GitHub classic projects are deprecated but still supported.
# If using the newer Projects (beta), adjust the API endpoint accordingly.

gh api -X POST "repos/$owner/$repo/projects" -f name="Development Roadmap" || true

echo "Milestones and project board creation attempted."
