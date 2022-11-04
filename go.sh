#!/bin/bash

path=$(grep --color=auto $1 ~/.sublist | gawk '{print $6}')
bash $happy/se.sh $1
cd $path
ls
