#!/bin/bash
#set -e

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

# --------- input file check ----------- #

all_exist () {
    local filename
    for filename; do
    ls $filename > /dev/null 2>&1  && continue
    echo -e "\033[32m\e[1m   $filename\033[31m\e[0m dose NOT exist\033[37m"
    error=$(echo "error")
    done
    return 0
}

# ASE calculation	
if test -e restart.json ; then
	all_exist restart.json
    if [[ -z $error ]]; then
        #echo "All input files exist"
        :
    else
        echo -e "\033[91m\e[1mXX STOP submission of run file XX\033[37m"
        exit 1
    fi

	if test -e initial_"${PWD##*/}".json ; then
		echo -e "\033[93minitial_"${PWD##*/}".json : is already existed \033[0m"
	else
		cp restart.json initial_"${PWD##*/}".json
	fi

	if test -e run_slurm.sh ; then
		runpath=run_slurm.sh
	fi

	#project/script folder 접근
	$sub $runpath > .submitted
	cp $runpath ./run_submit.sh
	more .submitted
	py=$(grep python $runpath | grep -v "#" | grep -v "if_finish_let_me_know.py" | gawk '{print $2}')
	calpy=`echo $py | rev | cut -d'/' -f1 | rev`
	#incar=$(grep --color=auto python $runpath | grep -v "#" | grep -v "for_a_happy_life")
#	echo -e "\033[93m ----- Information of ${PWD##*/} ----- "
	#echo -e $incar
#	echo -e "python $SCRATCH/$proj/script/\033[33m$calpy\033[37m\e[0m"
#	echo -e "\033[0m -------------------------------------"
elif test -e *.py ; then
	if test -e run_slurm.sh ; then
		runpath=run_slurm.sh
	fi
	$sub $runpath > .submitted
else
# manual calculation
    all_exist POSCAR INCAR KPOINTS POTCAR $runfile
    if [[ -z $error ]]; then
        #echo "All input files exist"
        mp=$(more POSCAR)
        [[ -z $mp ]] && echo -e "\033[32m\e[1m    POSCAR \033[31m\e[0mis EMPTY" && echo -e "\033[91m\e[1mXX STOP submission of run file XX\033[37m" && exit 1
    else
        neb=$(grep LCLIMB INCAR)
        if [[ -z $neb ]]; then
            echo -e "\033[91m\e[1mXX STOP submission of run file XX\033[37m"
            exit 1
        else
            echo -e "\033[32m\e[1m  This is NEB Calculation \033[31m\e[0m"
        fi
    fi
    beef=$(grep BEEF INCAR)
    if [[ -n $beef ]]; then
        if test -e vdw_kernel.bindat ; then
            :
        else
            echo -e "\033[32m\e[1m  vdw_kernel.bindat doesn't exist.. copy this file..\033[31m\e[0m"
            cp $HOME/vdw_kernel.bindat .
        fi
    else
        :
    fi

    if test -e POSCAR_"${PWD##*/}"_initial ; then
        echo -e "\033[1;31mjob of ${PWD##*/} :\033[0m"
        echo -e "\033[93mPOSCAR_"${PWD##*/}"_initial : is already existed \033[0m"
        $sub $runfile > .submitted
        more .submitted
    else
        echo -e "\033[1;31mjob of ${PWD##*/} :\033[0m"
        echo -e "\033[93mcp POSCAR POSCAR_"${PWD##*/}"_initial \033[0m"
        $sub $runfile > .submitted ;cp POSCAR POSCAR_"${PWD##*/}"_initial
        more .submitted
    fi

    isif=$(grep ISIF INCAR)
    echo -e "\033[93m ----- Information of ${PWD##*/} ----- "
    echo -e "ISIF  : $isif"
    echo -e "\033[0m -------------------------------------"
fi

jobID=$(more .submitted)
jobID=`echo $jobID | awk 'match($0,/[0-9]+/){print substr($0, RSTART, RLENGTH)}'`
dat=$(echo "$(date +%Y)-$(date +%m)-$(date +%d)")
mv .submitted .submitted_${dat}_${jobID}

if [ $jobtype == 'slurm' ]; then
	scontrol show jobid -dd $jobID > out12345
	jobname=$(grep  "JobName=" out12345 | gawk '{print $2}')
	stt=$(grep "JobState" out12345 | gawk '{print $1}')
	queue=$(grep "Partition=" out12345 | gawk '{print $1}')
	nodes=$(grep "TRES=" out12345 | cut -d ',' -f1)
	#out=$(grep 'WorkDir' out12345)
	workdir=${PWD##}
	echo $dat" "$jobID" "${queue:10}" "${jobname:8}" "${nodes:12}" "$workdir > .me
else
	qstat -f $jobID > out12345
	jobname=$(grep  "Job_Name" out12345 | gawk '{print $3}')
	stt=$(grep "job_state" out12345 | gawk '{print $3}')
	queue=$(grep "queue" out12345 | gawk '{print $3}')
	nodes=$(grep "node" out12345 | gawk '{print $3}')
	out=$(grep 'WorkDir' out12345)
	workdir=${PWD##}
	echo $dat" "$jobID" "$queue" "$jobname" "$nodes" "$workdir > .me
fi

me=$(more .me)
echo $me
echo $me >> $HOME/.sublist
	
if [ -f out12345 ] ; then
        rm out12345
fi
stderr=$(ls STDERR*  2> temp_err.txt)
stdout=$(ls stdout*  2> temp_err.txt)
if [[ -n $stderr ]] ; then
	mv $stderr .$stderr
fi
if [[ -n $stdout ]] ; then
	mv $stdout .$stdout
fi

if [ -f temp_err.txt ]; then
	rm temp_err.txt
fi
