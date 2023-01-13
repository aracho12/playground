all_exist () {
    local filename
    for filename; do
    ls $filename > /dev/null 2>&1  && continue
    echo -e "$filename dose NOT exist"
    error=$(echo "error")
    done
    return 0
}

all_exist POSCAR INCAR KPOINTS POTCAR run_slurm.sh

[[ -z $error ]] && echo "All files exist"
