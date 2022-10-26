#!/bin/bash
# ----------- :: Information :: ----------------
# By Ara Cho, POSTECH, Korea @10/30/2021
# --------------- :: note :: -------------------
# Show table of calculation results 
#
# ----------------------------------------------

dir=$(ls -d */)
#echo $dir
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
            qstat_jn=$(qstat | grep $id)
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
            qg=$(qstat | grep "$id " | grep " Q ")
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
		iter='-'
		E0='-'
		dE='-'
	fi
		# KPOINTS
	if test -e "KPOINTS" ; then
		ks=$(head -4 KPOINTS | tail -1)
		ks_list=($ks)
		k1=${ks_list[0]}; k2=${ks_list[1]}; k3=${ks_list[2]}
		kpts=$(echo "$k1 × $k2 × $k3")
		echo -e "$E0" >> ~/.e0
	else
		kpts="No_input"
	fi
	echo -e "$E0" >> ~/.e0
	echo -e "$i $iter $E0 $dE $stat $kpts" >> ~/.data
	cd ..
done

# most_stable 
MIN=$(cat ~/.e0 | sort -n | head -1)
echo $MIN


printf '\033[95mFol           iter      E0      dE      relE   Status     Kpts \n\033[37m\e[0m'
echo "————————————— ————— ————————— ——————— ——————— ————————— —————————— "
cat ~/.data | while read i iter e0 de stat kpts
do
	rel=$(echo $e0 $MIN | awk '{printf "%.2f", $1 - $2}')
	if [[ -z $rel ]]; then
		rel="Not_Sub"
	fi
	printf '%-14s %-3s %-10s %-8s %-6s %-10s %-10s\n' "$i" "$iter" "$e0" "$de" "$rel" "$stat" "$kpts"
done
