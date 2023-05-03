#!/bin/bash

SET=$(seq -f "%02g" $1 $2)
for i in $SET
do
	if test -d "$i"* ; then
		if [ ! -d ../../"$i" ]; then
  			mkdir -p ../../"$i"
		fi
		cd "$i"*
		echo -e $i: cp restart.json ../../$i
		cp restart.json ../../$i
		cd ..
	fi
done
