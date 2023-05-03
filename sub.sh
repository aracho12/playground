#!/bin/bash
# description: set job options before submit

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

source $happy/here.sh

if [[ -n $1 ]] && [[ -z $2 ]] ; then
	if [ $1 == '-r' ] ; then
		if test -e "run_submit.sh" ; then
			name=$(grep "job-name=" run_submit.sh | cut -d'=' -f2 | tr -d '"')
		else
			read -p ">> job name ?: " name
		fi
	fi
else
	read -p ">> job name ?: " name
fi

echo -e "\033[93;03m————————————————————————\n submit run_slurm.sh \n———————————————————————— \033[0m "

bash $happy/srus.sh $name

submit_info(){
	if [[ $server == 'cori' ]] || [[ $server == 'perl' ]] ; then
		vasp=vasp.5.4.4.vaspsol.vtst.x
		partition=$(grep "SBATCH -C" $runpath | gawk '{print $3}')

	else
		vasp=$(grep vasp_std= $runpath | grep -v "#" | rev | cut -d'=' -f1 | rev )
		partition=$(grep partition $runpath | cut -d'=' -f2)
	fi

	calpy=$(grep python $runpath | grep -v "#" | grep -v "if_finish_let_me_know.py" | gawk '{print $2}' | rev | cut -d'/' -f1 | rev)

	if [[ $jobtype == 'pbs' ]] ; then
		name=$(grep "PBS -N" $runpath | cut -d' ' -f3)
		vasp=vasp_5.4.1.vtst
		numnode=$(grep "#PBS -l select=" $runpath | cut -d'=' -f2 | cut -d':' -f1)
		node=$(grep "#PBS -l select=" $runpath | cut -d'=' -f3 | cut -d':' -f1)
		walltime=$(grep "#PBS -l walltime=" $runpath | cut -d'=' -f2)
		echo -e "\033[1;31;03m—————————— job info ——————————$Y$re"
		echo -e "      node: $numnode * $node"
		echo -e "  walltime: $walltime"
		echo -e "  job name: $name"
		echo -e "  job type: $calpy"
		echo -e "  vasp ver: $vasp"
		echo -e "\033[1;31;03m—————————————————————————————"$dW
	else
		node=$(grep tasks-per-node $runpath | cut -d'=' -f2)
		numnode=$(grep nodes= $runpath | cut -d'=' -f2)
		name=$(grep "job-name=" $runpath | cut -d'=' -f2)
		walltime=$(grep "#SBATCH -t" $runpath | gawk '{print $3}')
		if [ $here == 'cori' ] ; then
			echo -e "\033[1;31;03m—————————— job info ——————————$Y$re"
			echo -e "      node: $numnode * $node"
			echo -e "  walltime: $walltime"
			echo -e "  job name: $name"
			echo -e "  job type: $calpy"
			echo -e "  vasp ver: $vasp"
			echo -e "\033[1;31;03m—————————————————————————————"$dW		
		else
			echo -e "\033[1;31;03m—————————— job info ——————————$Y$re"
			echo -e " # of node: $numnode * $node"
			echo -e "  walltime: $walltime"
			echo -e "  job name: $name"
			echo -e "  job type: $calpy"
			echo -e "  vasp ver: $vasp"
			echo -e "\033[1;31;03m—————————————————————————————"$dW
		fi
	fi
}
menu(){
	if [[ $jobtype == 'pbs' ]] ; then
		echo -e "\033[93;03m————————————————————————"
		echo -e " cgt) walltime (hours)"
		echo -e " cal) job type"
		echo -e " cgn) number of node"
		echo -e "   i) check changed info"
		echo -e " sub) let's submit job!"
		echo -e "\033[93;03m————————————————————————$dW"
	elif [[ $here == 'burning' ]] ; then
		echo -e "\033[93;03m————————————————————————"
		echo -e "  cg) partition (g1, g2 ,g3, g4, g5, gpu)"
		echo -e " cal) job type"
		echo -e " cgn) number of node"
		echo -e "   i) check changed info"
		echo -e " cnt) check avaiable nodes"
		echo -e " sub) let's submit job!"
		echo -e "\033[93;03m————————————————————————$dW"
	elif [[ $server == 'cori' ]] ; then
		echo -e "\033[93;03m————————————————————————"
		echo -e " cgt) walltime (hours)"
		echo -e " cal) job type"
		echo -e " cgn) number of node"
		echo -e "   i) check changed info"
		echo -e " sub) let's submit job!"
		echo -e "\033[93;03m————————————————————————$dW"
	fi
}


change(){
	read -p ">> do you want to change something ?: " y
	if [ "$y" == "y" ] ; then
		menu
		while :
		do
			read -p ">> choose option you want to change : " op
			if [ "$op" == "a" ] || [ "$op" == "cg" ] ; then
				bash $happy/sg.sh
			elif [ "$op" == "b" ] || [ "$op" == "cgrun" ] || [ "$op" == "cal" ] ; then
        		bash $happy/joblist.sh
		        read -p ">> which calculation ?:" cal
				bash $happy/cgrun.sh $cal
			elif [ "$op" == "cgnode" ] || [ "$op" == "cgn" ] ; then
				read -p ">> how many node ?:" nn
				bash $happy/cgnode.sh  $nn
			elif [ "$op" == "cnt" ] ; then
				bash $happy/t2.sh
			elif [ "$op" == "i" ] ; then
				submit_info			
			elif [ "$op" == "cgt" ]  || [ "$op" == "cgtime" ] ; then
				bash $happy/cgtime.sh
			elif [ "$op" == "s" ] || [ "$op" == "sub" ] ; then
				break
			else
				submit_info
				menu
			fi
		done
	fi
}

submit_info
change
if [[ -z $2 ]] ; then
		bash $happy/sub_only_one_job.sh
elif [[ -n $2 ]] ; then
	INI=$1
	FIN=$2
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
			name=$(sed -e 's/^"//' -e 's/"$//' <<< $name)
			bash $happy/srus.sh "$name"_"$i"
			bash $happy/sub_only_one_job.sh
			cd ..
		else
			echo -e "\033[38;5;243m $i : directory is not existed \033[0m"
		fi
	done
fi
