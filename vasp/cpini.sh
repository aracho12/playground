#!/bin/bash

# cpini.sh: Copy ase_vasp.py and run_slurm.sh from home when restart.json exists
# Usage: cpini.sh [source_directory]
# If no argument provided, copies from $HOME when restart.json exists in current directory

cpini() {
    src="$1"
    # Check and copy each file if it exists in $1
    for f in restart.json run_slurm.sh ase_vasp.py; do
        if [ -f "$src/$f" ]; then
            cp "$src/$f" .
        fi
    done
}

if [ -z "$1" ]; then
    # Check if restart.json exists in current directory
    src="$HOME"
    for f in run_slurm.sh ase_vasp.py; do
        if [ -f "$src/$f" ]; then
            cp "$src/$f" .
            echo "  Copied: $f"
        else
            echo "  Warning: $f not found in \$HOME"
        fi
    done
else
    cpini "$1"
fi