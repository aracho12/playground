runfile='run_slurm.sh'

if [ -f $runfile ]; then
    sbatch $runfile
else
    echo "Error: $runfile does not exist"
    exit 1
fi