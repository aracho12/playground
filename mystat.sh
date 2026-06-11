#!/bin/bash
# ----------- :: Information :: --------------
# version : 1.0 
# date : 2021-10-30
# update : 2022-09-21
# developer : Ara
# --------------- :: note :: -----------------
# Showing my submission
# --------------------------------------------
if [ $jobtype == 'pbs' ]; then
    sub='qsub'
else
    jobtype='slurm'
    sub='sbatch'
fi

rm ~/.mystat
touch ~/.mystat
qstat -u "$(whoami)" > ~/.mystat
if [ $jobtype == 'pbs' ]; then
	qstat -fw -u "$(whoami)" > ~/.out12345
fi
queue_info ()
{
	cat ~/.mystat | grep " $1 " > ~/.mystat_temp
	cat ~/.mystat_temp | while read jobn user que jobname se1 nds tsk me1 tm R tm2
	do
		if [ $jobtype == 'pbs' ]; then
			jobname=$(grep -A 1 $jobn ~/.out12345 | head -2 | tail -1 | gawk '{print $3}')
		fi		
		printf "%-8s $2;1m%-5s\033[37m\e[0m %-20s %-3s %-4s %-2s %s\n" "$jobn" "$que" "$jobname" "$nds" "$tsk" "$R" "$tm2"
	done
}
if [ $jobtype == 'pbs' ]; then
	echo "JobID        Queue  JobName           NDS Node  S  Elap"
	echo "———————————— —————— ————————————————— ——— ———— —— ——————"
	queue_info normal '\e[33'
	#queue_info skl '\e[33'
	#queue_info knl '\e[32'
else
	echo "JobID    Queue JobName              NDS Node S  Elap"
	echo "———————— ————— ———————————————————— ——— ———— —— ——————"
	queue_info g1 '\e[91'
	queue_info g2 '\e[33'
	queue_info g3 '\e[32'
	queue_info g4 '\e[35'
	queue_info g5 '\e[36'
	queue_info gpu '\e[33'
fi
echo -e "$(date +%Y)-$(date +%m)-$(date +%d) $(date +%H):$(date +%M)"

if [ -f ~/.out12345 ] ; then
        rm ~/.out12345
fi
