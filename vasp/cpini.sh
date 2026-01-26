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
    for f in run_slurm.sh ase_vasp.py; do
        if [ -f "~/$f" ]; then
            cp "~/$f" .
        fi
    done
else
    cpini $1
fi