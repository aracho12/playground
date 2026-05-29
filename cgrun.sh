#!/bin/bash
# ----------- :: Information :: ----------------
# By Ara Cho, POSTECH, Korea @09/14/2022
# --------------- :: note :: -------------------
# modification run file
# ----------------------------------------------

# -------------- set up --------------- #
IFS='/' read -r -a scratch <<< "$SCRATCH"
len=${#scratch[@]}
IFS='/' read -r -a cpwd <<< "${PWD##}"
proj=${cpwd[$len]}
runfile='run_slurm.sh'
runpath=$SCRATCH/$proj/script/$runfile


sed -i 's/^[^#]*script/#&/' $runpath
# if $1 exist
if [[ -n $1 ]]; then
	echo -e $re$bG'change to '$Y$bd$1$re$bG' setup'$dW
	sed -i '/^#.*script.*'"$1"'/s/^#//' $runpath
	#grep --color $1 $runpath
fi
