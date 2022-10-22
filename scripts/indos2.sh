#!/bin/bash
# ----------- :: Information :: ----------------
# By Ara Cho, POSTECH, Korea @09/22/2022
# --------------- :: note :: -------------------
# generate incar for dos calculation
# ----------------------------------------------

echo -e "\033[1;31;03m—————————————————————————— \033[93;03m"
echo -e "   step2 :: DOS calculation       "
echo -e "\033[1;31;03m—————————————————————————— \033[93;03m"
echo -e "\033[1;31m proper INCAR :\033[0m"
echo -e "\033[1;31;03m—————————————————————— \033[93;03m"
echo -e "ISTART = 1"
echo -e "ICHARG = 11"
echo -e "LORBIT = 11"
echo -e "NEDOS = 1000"
echo -e "ISMEAR = -5"
echo -e "EMIN = -15"
echo -e "EMAX = 10"
echo -e "LCHARG = .FASLE."
echo -e "\033[1;31;03m—————————————————————— \033[93;03m"

base="run_dos1.py"
new="run_dos2.py"

if test -e INCAR; then
	echo " "
	echo -e "\033[1;31m 현재 INCAR 정보 :\033[0m"
	grep ISTART INCAR
	grep ICHARG INCAR
	grep LORBIT INCAR
	grep NEDOS INCAR
	grep ISMEAR INCAR
	grep LCHARG INCAR
	grep EMIN INCAR
	grep EMAX INCAR
elif test -e $base; then
	cp $base $new
	echo -e "\033[1;31m 현재 INCAR 정보 :\033[0m"
	grep istart $base
	grep icharg $base
	grep lorbit $base
	grep ismear $base
	grep lcharg $base
	grep nedos $base
	grep emin $base
	grep emax $base
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
	else
		sed -i "/ldipol/a\      $1 = $2," $new
	fi
}

if [ "$d" == "y" ]; then
	if test -e INCAR; then
		incar ISTART 1
		incar ICHARG 11
		incar LORBIT 11
		incar NEDOS 1000
		incar ISMEAR -5
		incar EMIN -15
		incar EMAX 10
		incar LCHARG .False.
	elif test -e $new; then
		python istart 1
		python icharg 11
		python lorbit 11
		python ismear -5
		python nedos 1000
		python emin -15
		python emax 10
		python lcharg False
	fi
elif [ "$d" == "n" ]; then
	break

else
	break
fi
if test -e INCAR; then
    echo " "
    echo -e "\033[1;31m 현재 INCAR 정보 :\033[0m"
    grep ISTART INCAR
    grep ICHARG INCAR
    grep LORBIT INCAR
    grep NEDOS INCAR
    grep ISMEAR INCAR
    grep LCHARG INCAR
    grep EMIN INCAR
    grep EMAX INCAR
elif test -e $new; then
    echo -e "\033[1;31m $new 정보 :\033[0m"
    grep istart $new
    grep icharg $new
    grep lorbit $new
    grep ismear $new
    grep lcharg $new
    grep nedos $new
    grep emin $new
    grep emax $new
else
    echo " "
    echo -e "\033[93mINCAR or python file don't exist :\033[0m"
    break
fi

if test -e $new; then
	echo -e $bG" add this line to your run_dos2.py "$dW
	more $mc/check_chargcar.txt
fi
