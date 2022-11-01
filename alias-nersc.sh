alias qdel='scancel'
alias vbash='vi ~/.bash_profile'
alias sbash='source ~/.bash_profile'
alias viner='vi ~/bin/playground/alias-nersc.sh'
#/home/aracho/8_suncat-orr/PES-model-for-ORR
export pes=/global/cscratch1/sd/aracho/PES/PES-model-for-ORR
alias pes='dir_now=$PWD
cd /global/cscratch1/sd/aracho/PES/PES-model-for-ORR
git pull
git add *
git commit -m "."
git push
cd $dir_now'
export jobtype='slurm'
export server='nersc'
alias mystat='squeue -o "%.10F %.8u %.15j %.5P %.6Q %.2t %.2Y %M" -S "t,-Q" | grep " aracho "'
alias qstat='mc sacct.sh'
alias pot='python $happy/POTCAR_54.py'
