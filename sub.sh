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

bash $happy/srus.sh $name

submit_info(){
	vasp=$(grep /vasp. $runpath | grep -v "#" | rev | cut -d'/' -f1 | rev )
	node=$(grep ntasks-per-node $runpath | cut -d'=' -f2)
	numnode=$(grep --nodes= $runpath | cut -d'=' -f2)
	partition=$(grep partition $runpath | cut -d'=' -f2)
	calpy=$(grep python $runpath | grep -v "#" | grep -v "if_finish_let_me_know.py" | gawk '{print $2}' | rev | cut -d'/' -f1 | rev)
	name=$(grep "job-name=" $runpath | cut -d'=' -f2)
	echo -e "\033[1;31;03m—————————— job info ——————————$Y$re"
	echo -e " # of node: $numnode * $node"
	echo -e " partition: $partition"
	echo -e "  job name: $name"
	echo -e "  job type: $calpy"
	echo -e "  vasp ver: $vasp"
	echo -e "\033[1;31;03m—————————————————————————————"$dW
}

change(){
	read -p ">> do you want to change something ?: " y
	if [ "$y" == "y" ] ; then
        echo -e "\033[93;03m————————————————————————"
        echo -e " a) partition (g1, g2 ,g3, g4, g5, gpu)"
        echo -e " b) job type"
        echo -e " c) number of node"
        echo -e " i) check changed info"
		echo -e " s) let's submit job!"
        echo -e "\033[93;03m————————————————————————$bW"	
		while :
		do
			read -p ">> choose option you want to change : " op
			if [ "$op" == "a" ] || [ "$op" == "cg" ] ; then
				bash $happy/sg.sh
			elif [ "$op" == "b" ] || [ "$op" == "py" ]; then
        		bash $happy/joblist.sh
		        read -p "$bW>> which calculation ?:" cal
				bash $happy/cgrun.sh $cal
			elif [ "$op" == "c" ] || [ "$op" == "node" ] ; then
				read -p "$bW>> how many node ?:" nn
				bash $happy/cgnode.sh  $nn
			elif [ "$op" == "i" ] ; then
				submit_info
			elif [ "$op" == "s" ] ; then
				break
			else
				submit_info
			fi
		done
	fi
}

submit_info
change

if [ $RUN == 1 ] ; then
		bash $happy/sub_only_one_job.sh
elif [ $RUN == 2 ] ; then
	echo -e "\033[93;03m———————————————————————————————————————————————————————————————————————— "
	echo -e "submit jobs from $INI to $FIN"
    echo -e "\033[93;03m———————————————————————————————————————————————————————————————————————— $dW"
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
