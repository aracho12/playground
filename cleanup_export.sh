#!/bin/bash
# cleanup_export.sh — Keep only qm_0/ and solute/ in a CES2 export directory.
#
# Usage:
#   cleanup_export.sh           # dry run: show what would be deleted
#   cleanup_export.sh --delete  # actually delete

set -euo pipefail

KEEP=("qm_0" "solute")
DRY_RUN=1

if [ "${1:-}" == "--delete" ]; then
    DRY_RUN=0
fi

# Safety: must be run from a directory that has both qm_0/ and solute/
for dir in "${KEEP[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "ERROR: '$dir' not found. Run this from the export directory."
        exit 1
    fi
done

# Collect targets
targets=()
while IFS= read -r -d '' item; do
    name=$(basename "$item")
    skip=0
    for k in "${KEEP[@]}"; do
        [ "$name" == "$k" ] && skip=1 && break
    done
    [ $skip -eq 0 ] && targets+=("$item")
done < <(find . -maxdepth 1 ! -name "." -print0 | sort -z)

if [ ${#targets[@]} -eq 0 ]; then
    echo "Nothing to remove."
    exit 0
fi

echo "### Will remove:"
for t in "${targets[@]}"; do
    echo "  $t"
done
echo ""

if [ $DRY_RUN -eq 1 ]; then
    echo "Dry run — nothing deleted. Run with --delete to actually remove."
else
    read -rp "Delete ${#targets[@]} items? [y/N] " confirm
    if [ "${confirm,,}" != "y" ]; then
        echo "Aborted."
        exit 0
    fi
    for t in "${targets[@]}"; do
        rm -rf "$t"
        echo "  removed: $t"
    done
    echo "Done."
fi
