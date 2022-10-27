#!/bin/bash

if test -e 'run_submit.sh' ; then
	echo -e $W"generate restart.json"$bW
	if test -e OUTCAR ; then
		ase convert -f -n -1 OUTCAR restart.json
	fi
	job_name=$(more .me | gawk '{print $4}')
	py=$(grep python run_submit.sh | grep -v "#" | grep -v "if_finish_let_me_know.py" | gawk '{print $2}')
	calpy=`echo $py | rev | cut -d'/' -f1 | rev`
	echo -e job name: $job_name
	echo -e job_type: $calpy
	bash $happy/srus.sh $job_name
	bash $happy/cgrun.sh $calpy
	bash $happy/sub_only_one_job.sh
fi
