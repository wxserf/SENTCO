#!/bin/bash
# Script to rename 'master' branch references to 'main' in workflow and doc files
# Usage: ./rename-master-to-main.sh
set -euo pipefail

# Find GitHub Actions workflow files (.yml or .yaml)
if [ -d .github/workflows ]; then
  find .github/workflows -type f \( -name '*.yml' -o -name '*.yaml' \) | while read -r file; do
    if grep -q master "$file"; then
      sed -i 's/master/main/g' "$file"
      echo "Updated $file"
    fi
  done
fi

# Update Markdown documentation files
find . -path ./.git -prune -o -name '*.md' -type f -print | while read -r doc; do
  if grep -q master "$doc"; then
    sed -i 's/master/main/g' "$doc"
    echo "Updated $doc"
  fi
done
