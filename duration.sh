#!/bin/bash
seconds2time ()
{
   T=$1
   D=$((T/60/60/24))
   H=$((T/60/60%24))
   M=$((T/60%60))
   S=$((T%60))

   if [[ ${D} != 0 ]]
   then
      printf '%d-%02d:%02d:%02d' $D $H $M $S
   else
      printf '%02d:%02d:%02d' $H $M $S
   fi
}

path=$PWD
if test -e ".jobnumber" ; then
    id=$(more .jobnumber)
elif test -e ".me" ; then
    ls=$(more .me)
    array=($ls)
    id=${array[1]}
fi

if test -e "OUTCAR" ; then
	out=$(grep "Elapsed time" OUTCAR)
	if [[ -z $out ]]; then
        jobnum=$id
		if [ $here == 'burning' ] ; then
        	run=$(qstat | grep $jobnum)
			time="Running"
		elif [ $here == 'cori' ] || [ $here == 'perl' ] ; then
			run=$(squeue --me | grep $jobnum)
			time=$(sqs | grep $jobnum | awk '{printf $7}')
		fi
        if [[ -z $run ]]; then
			time="ERROR"
        fi
	else
		out_l=($out)
		seconds=${out_l[3]}
		int=${seconds%.*}
		time=$(seconds2time $int)
	fi
else
	time="Not sub"
fi

echo $time
