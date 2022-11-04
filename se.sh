#!/bin/bash

if [[ -n $1 ]] ; then
	ls=$(grep --color=auto $1 ~/.sublist)
	#echo $ls
	array=($ls)
	id=${array[1]}
	path=${array[-1]}
	left=${array[@]/$path}
	echo $left
fi
if [[ -z $1 ]]; then
	path=$PWD
	if test -e ".jobnumber" ; then
		id=$(more .jobnumber)
	elif test -e ".me" ; then
		ls=$(more .me)
		array=($ls)
		id=${array[1]}
	fi
fi

echo -e "PWD: \033[33m$path\033[37m\e[0m"
cd $path
if test -e "OUTCAR" ; then
	string=$(grep "Voluntary" OUTCAR)
	if [[ -z $string ]]; then
		qstat_jn=$(qstat | grep $id)
		if [[ -z $qstat_jn ]]; then
			stt="ERROR"
		else
			stt="RUNNING"
		fi
	else
		stt="COMPLETED"
	fi
else
	stt="PENDING"
fi

if test -e "KPOINTS" ; then
	ks=$(head -4 KPOINTS | tail -1)
	ks_list=($ks)
	k1=${ks_list[0]}; k2=${ks_list[1]}; k3=${ks_list[2]}
	kpts=$(echo " $k1"×"$k2"×"$k3")
else
	kpts='-'
fi

if test -e "OSZICAR" ; then
	if test -e "OUTCAR" ; then
		:
	else
		stt="FINISHED"
	fi
	E0_list=$(grep E0 OSZICAR | tail -1)
	E0_array=($E0_list)
	E0_org=${E0_array[4]}
	if [[ -z $E0_list ]] ; then
		iter='0'
	else
		iter=${E0_array[0]}
	fi
	dE=$(echo "${E0_array[7]}" |cut -c 2- |awk '{printf "%.3f", $1}')
	E0=$(echo "$E0_org" |awk '{printf "%.5f", $1}')
else
	iter='-'
	E0='-'
	dE='-'
fi


if test -e "INCAR" ; then
	gga=$(grep GGA INCAR)
	if [[ $gga == *"BF"* ]]; then
		gga="BEEF"
	elif [[ $gga =~ "RP" ]]; then
		gga="RPBE"
	elif [[ $gga =~ "PE" ]]; then
		gga="PBE"
	fi
else
	gga="-"
fi
line="======================================================"
echo -e $line
(
printf '\t iter\t E0\t dE\t Status\t KPOINTS\t XC\n' 
printf '\033[95m\t%s\t%s\t%s\t%s\t%s\t%s\033[37m' "$iter" "$E0" "$dE" "$stt" "$kpts" "$gga" 
) | column -t -s $'\t'
echo -e $line

