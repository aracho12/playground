#!/bin/bash
IFS='/' read -r -a scratch <<< "$SCRATCH"
IFS='/' read -r -a cpwd <<< "${PWD##}"
scratch=("${scratch[@]}")
cpwd=("${cpwd[@]}")
if [[ $server == 'cori' ]] || [[ $server == 'perl']] ; then
    project=$(echo $PWD | cut -d'/' -f6)
    github=$(echo $PWD | cut -d'/' -f7)
    if [[ $project == 'PES' ]]; then
        if [[ $github == 'PES-model-for-ORR' ]] ; then
            echo -e $Cy"————————————————————————"
            echo -e    "   GITHUB TO CAL FOL"
            echo -e    "————————————————————————"$dW
            unset 'cpwd[1]'
            unset 'cpwd[2]'
            unset 'cpwd[3]'
            unset 'cpwd[4]'
            unset 'cpwd[5]'
            unset 'cpwd[6]'
            lst=$SCRATCH/PES/
        else
            echo -e $bY"————————————————————————"
            echo -e    "   CAL FOL TO GITHUB"
            echo -e    "————————————————————————"$dW
            unset 'cpwd[1]'
            unset 'cpwd[2]'
            unset 'cpwd[3]'
            unset 'cpwd[4]'
            unset 'cpwd[5]'
            lst=$SCRATCH/PES/PES-model-for-ORR/
        fi
    fi
elif [[ $server == 'kisti' ]] ; then
    if [[ ${PWD##} =~ "dct" ]] ; then
        unset 'cpwd[1]'
        unset 'cpwd[2]'
        unset 'cpwd[3]'
        unset 'cpwd[4]'
        lst="/scratch/x2431a03/"
    else
        unset 'cpwd[1]'
        unset 'cpwd[2]'
        #echo "after del cpwd:"${cpwd[@]}
        lst="/scratch/x2431a03/dct/Research_Note/"
    fi
fi
for path in ${cpwd[@]}
do
    lst+=$path/
done
lst="${lst:0:-1}"
if [ -n $1 ] ; then
    echo -e "cp -R $1 $lst"
    cp -R $1 $lst
fi
if [ $? -eq 0 ] ; then
    echo -e $G"copy complete"$W
else
    echo -e $R"copy Failure!"$W
fi
