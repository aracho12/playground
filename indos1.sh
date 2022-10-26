#!/bin/bash
# ----------- :: Information :: ----------------
# By Ara Cho, POSTECH, Korea @09/22/2022
# --------------- :: note :: -------------------
# generate incar for dos calculation
# ----------------------------------------------

echo -e "\033[1;31;03m—————————————————————————— \033[93;03m"
echo -e "   step1 :: SCF calculation       "
echo -e "\033[1;31;03m—————————————————————————— \033[93;03m"
echo -e "\033[1;31m proper INCAR :\033[0m"
echo -e "\033[1;31;03m—————————————————————— \033[93;03m"
echo -e "NSW = 0"
echo -e "IBRION = -1 "
echo -e "LCHARG = .TRUE."
echo -e "LWAVE = .FALSE."
echo -e "\033[1;31;03m—————————————————————— \033[93;03m"

if test -e INCAR; then
	echo " "
	echo -e "\033[1;31m 현재 INCAR 정보 :\033[0m"
	grep NSW INCAR
	grep IBRION INCAR
	grep LCHARG INCAR
	grep LWAVE INCAR
elif test -e run_relax.py; then
	new="run_dos1.py"
	cp run_relax.py $new
	echo -e "\033[1;31m 현재 INCAR 정보 :\033[0m"
	grep nsw run_relax.py
	grep ibrion run_relax.py
	grep lcharg run_relax.py
	grep lwave run_relax.py
else
	echo " "
	echo -e "\033[93mINCAR or python file don't exist :\033[0m"
	break
fi

echo -e "\033[1;31;03m—————————————————————— \033[93;03m"
while :
do
	read -p "INCAR 수정하기? (y or n) " d
	if [[ "$d" == "y" || "$d" == "n" ]]; then
		break
	else
		echo "choose y or n"
	fi
done
echo -e "\033[1;31;03m—————————————————————— \033[93;03m"
echo " "

incar(){
	if grep -q $1 INCAR ; then
		sed -i "/$1/c\ $1 = $2" INCAR
	else
		echo " $1 = $2" >> INCAR
	fi
}

python(){
	if grep -q $1 $new ; then
		sed -i "/$1/c\      $1 = $2," $new
	fi
}

if [ "$d" == "y" ]; then
	if test -e INCAR; then
		incar NSW 0
		incar IBRION -1
		incar LWAVE .FALSE.
		incar LCHARG .TRUE.
	elif test -e $new; then
		python nsw 0
		python ibrion -1
		python lwave False
		python lcharg True
	fi
elif [ "$d" == "n" ]; then
	break

else
	break
fi

if test -e INCAR; then
    echo " "
    echo -e "\033[1;31m 현재 INCAR 정보 :\033[0m"
    grep NSW INCAR
    grep IBRION INCAR
    grep LCHARG INCAR
    grep LWAVE INCAR
elif test -e run_relax.py; then
    echo -e "\033[1;31m 현재 INCAR 정보 :\033[0m"
    grep nsw $new
    grep ibrion $new
    grep lcharg $new
    grep lwave $new
else
    echo " "
    echo -e "\033[93mINCAR or python file don't exist :\033[0m"
    break
fi


echo -e $G"after scf calculation, do nscf calculation using CHGCAR"$dW
