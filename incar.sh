#!/bin/bash
#change INCAR option
if test -e INCAR ; then
    if grep -q $1 INCAR ; then
        sed -i "/$1/c\ $1 = $2" INCAR
    else
        echo " $1 = $2" >> INCAR
    fi
    grep $1 INCAR
elif test -e run_relax.py ; then
    new=run_relax.py
    if grep -q $1 $new ; then
        sed -i "/$1/c\      $1 = $2," $new
    else
        sed -i "/ispin/a\      $1 = $2," $new
    fi
    grep $1 $new
fi
