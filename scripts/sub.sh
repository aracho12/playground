#!/bin/bash

echo -e "\033[93;03m————————————————————————\n qsub run_slurm.sh \n———————————————————————— \033[0m "
SET=$(seq -f "%02g" $1 $2)
for i in $SET
do
		if test -d "$i"* ; then
				cd "$i"*
				sub_only_one_job.sh
				cd ..
		else 
				echo -e "\033[38;5;243m $i : directory is not existed \033[0m"
		fi
done

