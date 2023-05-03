#!/bin/bash
# ----------- :: Information :: ----------------
# By Ara Cho, POSTECH, Korea @10/30/2021
# --------------- :: note :: -------------------
# Show table of calculation results  
# ----------------------------------------------

exec 2>/dev/null

source $happy/here.sh

dir=""
all_dir=$(ls -d */)
for fol in $all_dir 
do
	if [[ $fol =~ ^[0-9] ]]; then
		dir="$dir $fol"
	fi
done


rm ~/.data ; touch ~/.data
rm ~/.e0 ; touch ~/.e0

for i in $dir
do
	#echo $i
	cd $i
	path=$PWD
	if test -e ".jobnumber" ; then
		id=$(more .jobnumber)
	elif test -e .me ; then
		id=$(cat .me |awk '{printf $2}')
	fi

    if test -e "OUTCAR" ; then
        string=$(grep "Voluntary" OUTCAR)
        if [[ -z $string ]]; then
			if [ $here == 'burning' ] ; then
            	qstat_jn=$(qstat | grep $id)
			elif [ $here == 'cori' ] || [ $here == 'perl' ] ; then
				qstat_jn=$(squeue --me | grep $id)
			fi
            if [[ -z $qstat_jn ]]; then
                stat="Stopped"
            else
                stat="Running.."
            fi
        else
            stat="Finished"
        fi
    else
        if test -e ".me" ; then
			if [[ $here == 'cori' || $here == 'perl' ]]; then
				qg=$(squeue --me | grep "$id " | grep " PD " )
			else
            	qg=$(qstat | grep "$id " | grep " Q ")
			fi
            if [[ -z $qg ]]; then
                stat="Not_Sub"
            else
                stat="Queue"
            fi
        else
            stat="Not_Sub"
        fi
    fi

	if test -e "OSZICAR" ; then
		E0_list=$(grep E0 OSZICAR | tail -1)
		if [[ -z $E0_list ]]; then
			iter=0
			E0=0.000
			dE='-'
		else
			E0_array=($E0_list)
        	E0_org=${E0_array[4]}
        	iter=${E0_array[0]}
        	E0=$(echo "$E0_org" |awk '{printf "%.5f", $1}')
        	dE=$(echo "${E0_array[7]}" |cut -c 2- |awk '{printf "%.4f", $1}')
		fi
	else
		if test -e "final_with_calculator.json" ; then
			E0=$(grep 'energy' final_with_calculator.json | head -1 | awk '{printf "%.5f", $2}')
		else
			E0='-'
		fi
		iter='-'
		dE='-'
	fi

		# KPOINTS
	if test -e "KPOINTS" ; then
		ks=$(head -4 KPOINTS | tail -1)
		ks_list=($ks)
		k1=${ks_list[0]}; k2=${ks_list[1]}; k3=${ks_list[2]}
		kpts=$(echo "$k1×$k2×$k3")
		echo -e "$E0" >> ~/.e0
	else
		kpts="No_input"
	fi

	time=$(bash $happy/duration.sh)
	echo -e "$E0" >> ~/.e0
	echo -e "$i $iter $E0 $dE $stat $kpts $time " >> ~/.data
	#echo $kpts
	cd ..
done

# most_stable 
MIN=$(cat ~/.e0 | sort -n | head -1)
echo $MIN


printf '\033[95mFol           iter      E0      dE      relE   Status     Kpts     Time\n\033[37m\e[0m'
echo "————————————— ————— ————————— ——————— ——————— ————————— —————————— ——————————"
cat ~/.data | while read i iter e0 de stat kpts time
do
	rel=$(echo $e0 $MIN | awk '{printf "%.2f", $1 - $2}')
	if [[ -z $rel ]]; then
		rel="Not_Sub"
	fi
	printf '%-14s %-3s %-10s %-8s %-6s %-10s %-10s %-12s \n' "$i" "$iter" "$e0" "$de" "$rel" "$stat" "$kpts" "$time"
done

