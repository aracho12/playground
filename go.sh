#!/bin/bash

CURRENT_USER=$(whoami)
FIRST_CHAR="${CURRENT_USER:0:1}"

echo "CURRENT PATH: $(pwd)"
echo "JOBID: $1"

if [ "$FIRST_CHAR" = "x" ]; then
    # PBS scheduler (username starts with 'x')
    workdir=$(qstat -f "$1" 2>/dev/null \
        | sed 's/\x1b\[[0-9;]*[a-zA-Z]//g' \
        | sed ':a;N;$!ba;s/\n[[:space:]]\+//g' \
        | grep -o 'PBS_O_WORKDIR=[^,]*' \
        | cut -d'=' -f2 \
        | tr -d '\r' \
        | sed 's/[[:space:]]*$//')

    if [ -z "$workdir" ]; then
        echo "JobID $1 not found"
    else
        cd "$workdir"
    fi

else
    # SLURM scheduler (default)
    a=$(scontrol show job "$1" 2>/dev/null | grep WorkDir)

    if [ -z "$a" ]; then
        echo "JobID $1 not found"
    else
        cd "${a#*=}"
    fi
fi

echo "CHANGED PATH: $(pwd)"
