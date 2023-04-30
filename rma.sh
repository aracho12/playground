#!/bin/bash
echo -e "\033[93;03m ---------------"
echo -e "\033[93m   File delete "
echo -e " --------------- \033[1;31;03m"

du -sh

rma(){
	echo -e "\033[1;31m rm WAVECAR CHG* AECC* \033[0m"
	rm WAVECAR CHG* vasprun.xml AECC*
}

if [[ -n $2 ]] ; then
	SET=$(seq -f "%02g" $1 $2)
	for i in $SET
	do
    	if test -d "$i"* ; then
			cd "$i"*
			rma		
        	cd ..
		else
    		echo -e "\033[93m $i : directory is not existed \033[93;03m"
		fi
	done
else
	rma
fi

du -sh
