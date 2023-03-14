#!/bin/bash
# -------------- set up --------------- #
IFS='/' read -r -a scratch <<< "$SCRATCH"
len=${#scratch[@]}
IFS='/' read -r -a cpwd <<< "${PWD##}"
proj=${cpwd[$len]}
runfile='run_slurm.sh'
runpath=$SCRATCH/$proj/script/$runfile

if [ $jobtype == 'pbs' ]; then
    sub='qsub'
else
    jobtype='slurm'
    sub='sbatch'
fi
#---------------------------------------#

if test -e run_slurm.sh ; then
    run="./run_slurm.sh"
else
    #echo -e ~/$proj/script/run_slrum.sh
    #echo -e "\033[33m위 경로의 node 바꾸기\033[37m\e[0m"
    run=$runpath
fi

if [[ -z $1 ]] ; then
    read -p "how many hours? > " hours
else
    hours=$1
fi

if [ $jobtype == 'pbs' ]; then
    sed -i "/^#PBS -l walltime=/c\#PBS -l walltime=$hours:00:00" $run
fi
