#!/bin/bash

# ------------ set up ------------ #
IFS='/' read -r -a scratch <<< "$SCRATCH"
len=${#scratch[@]}
IFS='/' read -r -a cpwd <<< "${PWD##}"
proj=${cpwd[$len]}
runfile='run_slurm.sh'
run=$SCRATCH/$proj/script/$runfile

myid=$(logname)
burning=aracho
kisti=x2431a03

# -------------------------------- #
if test -e $runfile ; then
    run="./$runfile"
	echo -e "\033[33m modification location: \033[37m\e[0m"
    echo -e "here" 
else
	echo -e "\033[33m modification location: \033[37m\e[0m"
    echo -e ~/$proj/script/$runfile
fi

if [[ -n $1 ]]; then
	echo -e "\033[1;31m $runfile : "$1"  \033[0m"
	if [ $myid == $kisti ] ; then
    	sed -i "3s/.*/#PBS -N "$1"  /g" $run
	elif [ $myid == $burning ] ; then
    	sed -i "/job-name/c\#SBATCH --job-name=\""$1"\"" $run
	fi

