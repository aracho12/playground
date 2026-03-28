#!/bin/bash

# update_inputs.sh: Deploy latest run_slurm.sh and ase_vasp.py to $HOME
# Usage: update_inputs.sh

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
play="${play:-$(dirname "$script_dir")}"  # playground root

files=(
    "$play/tars/run_slurm.sh"
    "$play/ase/ase_vasp.py"
)

echo "Deploying input files to \$HOME ($HOME)..."
for src in "${files[@]}"; do
    fname="$(basename "$src")"
    if [ -f "$src" ]; then
        cp "$src" "$HOME/$fname"
        echo "  Updated: $fname"
    else
        echo "  Warning: $src not found, skipping"
    fi
done
echo "Done."
