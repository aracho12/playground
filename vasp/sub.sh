runfile='run_slurm.sh'

# 만약에 '#SBATCH -J JOB_NAME' 이 있으면, input 받아서 modify_runfile.sh -j 로 수정 후 제출
if grep -q "#SBATCH -J JOB_NAME" "$runfile"; then
    read -p "Enter job name: " job_name
    bash $play/vasp/modify_runfile.sh -j "$job_name" "$runfile"
fi

if [ -f $runfile ]; then
    sbatch $runfile
else
    echo "Error: $runfile does not exist"
    exit 1
fi