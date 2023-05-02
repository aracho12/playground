#!/bin/bash
IFS='/' read -r -a scratch <<< "$SCRATCH"
len=${#scratch[@]}
IFS='/' read -r -a cpwd <<< "${PWD##}"
proj=${cpwd[$len]}
runpath=$SCRATCH/$proj/script
export run=$runpath
cd $runpath

