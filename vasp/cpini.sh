#!/bin/bash

# cpini.sh: Copy ase_vasp.py (and run_slurm.sh if not already present) from $HOME
# Usage: cpini.sh [source_directory]
#
# 동작:
#   run_slurm.sh가 이미 있으면 → ase_vasp.py 만 복사 (run file 덮어쓰기 방지)
#   run_slurm.sh가 없으면     → ase_vasp.py + run_slurm.sh 모두 복사

cpini() {
    src="$1"
    # restart.json도 없으면 같이 복사
    for f in restart.json ase_vasp.py; do
        if [ -f "$src/$f" ]; then
            cp "$src/$f" .
        fi
    done
    # run_slurm.sh: 현재 폴더에 없을 때만 복사
    if [ ! -f "run_slurm.sh" ]; then
        if [ -f "$src/run_slurm.sh" ]; then
            cp "$src/run_slurm.sh" .
        fi
    fi
}

if [ -z "$1" ]; then
    src="$HOME"
    # ase_vasp.py는 항상 최신 버전으로 복사
    if [ -f "$src/ase_vasp.py" ]; then
        cp "$src/ase_vasp.py" .
        echo "  Copied: ase_vasp.py"
    else
        echo "  Warning: ase_vasp.py not found in \$HOME"
    fi
    # run_slurm.sh: 없을 때만 복사
    if [ ! -f "run_slurm.sh" ]; then
        if [ -f "$src/run_slurm.sh" ]; then
            cp "$src/run_slurm.sh" .
            echo "  Copied: run_slurm.sh"
        else
            echo "  Warning: run_slurm.sh not found in \$HOME"
        fi
    else
        echo "  Skipped: run_slurm.sh (already exists, keeping local version)"
    fi
else
    cpini "$1"
fi