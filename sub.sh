#!/bin/bash

# -------------- set up --------------- #
IFS='/' read -r -a scratch <<< "$SCRATCH"
len=${#scratch[@]}
IFS='/' read -r -a cpwd <<< "${PWD##}"
proj=${cpwd[$len]}
runfile='run_slurm.sh'
runpath=$SCRATCH/$proj/script/$runfile
py=$(grep python $runpath | grep -v "#" | grep -v "if_finish_let_me_know.py" | gawk '{print $2}')
calpy=`echo $py | rev | cut -d'/' -f1 | rev`
job_name=$(grep job-name $runpath)
IFS='=' read -r -a jobname2 <<< "$job_name"
job_name=${jobname2[1]}


echo -e "\033[93;03m————————————————————————\n submit run_slurm.sh \n———————————————————————— \033[0m "

if [[ -z $2 ]] ; then
	RUN=1
	if [[ -z $1 ]] ; then
		read -p ">> job name ?: " name
		if [ -z $name ] ; then
			if [ -f .me ] ; then
				name=$(more .me | gawk '{print $4}')
			else
				name=$job_name
			fi
		fi
	else
		name=$1
	fi
elif [[ -z $3 ]] ; then
	RUN=2
	INI=$1
	FIN=$2
	read -p ">> job name ?: " name
elif [[ -n $3 ]] ; then
	RUN=2
	if [ -n ${$1//[0-9]/} ] ; then
		name=$1
		INI=$2
		FIN=$3
	elif [ -n ${$3//[0-9]/} ] ; then
		name=$3
		INI=$1
		FIN=$2
	fi
fi

if [ $RUN == 1 ] ; then
	echo -e "\033[93;03m————————————————————————"
	echo -e "job name: $name"
	echo -e "job type: $calpy"
	echo -e "\033[93;03m————————————————————————"$bW
	read -p ">> do you want to change job type ?: " y
	if [ "$y" == "y" ] ; then
		bash $happy/joblist.sh
		read -p "$bW>> which calculation ?:" cal
		bash $happy/cgrun.sh $cal
		bash $happy/srus.sh $name
		bash $happy/sub_only_one_job.sh
	elif [ "$y" == "n" ] ; then
		bash $happy/srus.sh $name
		bash $happy/sub_only_one_job.sh
	else
		exit 1
	fi
elif [ $RUN == 2 ] ; then
	echo -e "\033[93;03m———————————————————————————————————————————————————————————————————————— "
	echo -e "submit jobs from $INI to $FIN"
    echo -e "job base name: $name"
    echo -e "job type: $calpy"
    echo -e "\033[93;03m———————————————————————————————————————————————————————————————————————— $bW"
	read -p ">> do you want to change job type ?: " y
	if [ "$y" == "y" ] ; then
		bash $happy/joblist.sh
		read -p "which calculation ?:" cal
		bash $happy/cgrun.sh $cal
	elif [ "$y" == "n" ] ; then
		:
	fi
	SET=$(seq -f "%02g" $INI $FIN)
	if test -d "$INI" ; then
		:
	else
		bash $happy/start.sh $INI $FIN
	fi
	for i in $SET
	do
		if test -d "$i"* ; then
			cd "$i"*
			bash $happy/srus.sh "$name"_"$i"
			bash $happy/sub_only_one_job.sh
			cd ..
		else
			echo -e "\033[38;5;243m $i : directory is not existed \033[0m"
		fi
	done
fi
