#!/bin/bash
# date: 2023-03-17
# Ara Cho, SUNCAT@Stanford
# description: neb analysis

menu(){
    echo -e "$R//NEB CALCULATION ANALYSIS"
    echo -e "\033[93;03m————————————————————————"
    echo -e " n) energy and force of images in the neb"
    echo -e " p) nebbarrier.pl; nebspline.pl -> .dat file"
    echo -e " e) spline.dat -> energy profile"
    echo -e " ii) initial image generation"
    echo -e " if) final image generation"
    echo -e " o) find oxygen type"
    echo -e " d) distance between two atoms"   
    echo -e " x) exit"   
    echo -e "\033[93;03m————————————————————————$dW"
}

change(){
    while :
    do
        read -p ">> choose option : " op
        if [ "$op" == "n" ] || [ "$op" == "nebef" ] ; then
            nebef.pl
        elif [ "$op" == "p" ] || [ "$op" == "barrier" ] || [ "$op" == "spline" ] ; then
            nebbarrier.pl
            nebspline.pl
            python $happy/dat2csv.py neb.dat
            python $happy/dat2csv.py spline.dat
        elif [ "$op" == "e" ] || [ "$op" == "e" ] ; then
            python $happy/nebplot.py
        elif [ "$op" == "ii" ] ; then
            python $happy/neb2img.py POSCAR
            # current directory name
            name=$(basename $(pwd))
            mv neb2img.png ${name}1_initial.png
            mv neb2repeat.png ${name}2_initial.png
        elif [ "$op" == "if" ] ; then
            python $happy/neb2img.py CONTCAR
            name=$(basename $(pwd))
            mv neb2img.png ${name}1_final.png
            mv neb2repeat.png ${name}2_final.png
        elif [ "$op" == "o" ] ; then
            read -p ">> inputfile name (i.g. 00/POSCAR) : " a1
            python $happy/find_o_type.py -i $a1
        elif [ "$op" == "d" ] ; then
            read -p ">> pairs? (i.g 1,2 1,3 ..) : " a1
            python $happy/getdistance_pair.py -p $a1
        elif [ "$op" == "x" ] ; then
            exit
        else
            menu
        fi
    done
}

menu
change
