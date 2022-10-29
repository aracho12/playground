#!/bin/bash

# ----------- :: Information :: --------------
# version : 2.0
# date : 2021-10-30
# developer : Ara
# --------------- :: note :: -----------------
# Node Information
# Name	 Sub / Run / Que / Ava
# aracho  27 /  27 /  00 /  00
# --------------------------------------------

rm ~/.data
touch ~/.data 
for i in aracho g1 g2 g3 g4 g5
do
	que=$(qstat | grep " $i" | wc -l)
	R=$(squeue | grep " $i" | grep " R " | wc -l)
	Q=$(squeue | grep " $i" | grep " PD " | wc -l)
	eq=$(pestat | grep " $i" | grep idle | wc -l)
	echo "$i  $que $R $Q $eq" >> ~/.data 
done
total_sub=$(squeue | wc -l)
total_run=$(squeue | grep " R " | wc -l)
total_q=$(squeue | grep " PD " | wc -l)
total_e=$(pestat | grep idle | wc -l)
echo "total $total_sub $total_run $total_q $total_e" >> ~/.data

#echo " * Available_Queue   Waiting"
echo "——————- ——————————————-———————"
printf '\033[95mName\t Sub / Run / Que / Ava \n\033[37m\e[0m'
echo "——————- ——————————————-———————"
cat ~/.data | while read name que R Q eq
do
	printf '%s\t  %02d /  %02d /  %02d /  %02d \n' "$name" "$que" "$R" "$Q" "$eq"
done
echo "——————- ——————————————-———————"
echo ""

echo -e "$(date +%Y)-$(date +%m)-$(date +%d) $(date +%H):$(date +%M)"

