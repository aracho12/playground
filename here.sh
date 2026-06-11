#!/bin/bash

if [[ $HOME == '/global/homes/a/aracho' ]] ; then
	if [[ $SCRATCH == '/global/cscratch1/sd/aracho' ]] ; then
		here='cori'
	elif [[ $SCRATCH == '/pscratch/sd/a/aracho' ]] ; then
		here='perl'
	fi
elif [[ $HOME == '/home/aracho' ]] ; then
	here='burning'
else
	echo -e "where am I...?"
	return 0
fi

export here=$here
#echo -e "here: $here"

