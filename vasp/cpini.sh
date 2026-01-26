cpini() {
    src="$1"
    # Check and copy each file if it exists in $1
    for f in restart.json run_slurm.sh ase_vasp.py; do
        if [ -f "$src/$f" ]; then
            cp "$src/$f" .
        fi
    done
}

cpini $1