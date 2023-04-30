#!/bin/bash

cpcon(){
	if test -e POSCAR ; then
		mv POSCAR .POSCAR_ini
	fi
	if test -e CONTCAR ; then
		mv CONTCAR POSCAR
		echo -e "\033[93m $dir_name : mv CONTCAR POSCAR \033[0m"
	else
		dir_name=${PWD##*/}
		echo -e "\033[93m $dir_name : CONTCAR is not existed \033[0m"
	fi
}

if [[ -n $2 ]] ; then
	SET=$(seq -f "%02g" $1 $2)
	for i in $SET
	do
    	if test -d "$i"* ; then
			cd "$i"*
			cpcon		
        	cd ..
		else
    		echo -e "\033[93m $i : directory is not existed"$dW
		fi
	done
else
	cpcon
fi