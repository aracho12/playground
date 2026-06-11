

alias pestat='pbs_status | head -n 2
pbs_status | grep normal
pbs_status | grep norm_skl
pbs_status | grep long'
alias dct='dir_now=$PWD
cd /scratch/x2431a03/dct
git pull
git add *
git commit -m "."
git push
cd $dir_now'
alias cprnf='bash $mc/cprn.sh final_with_calculator.json'
alias cprn='bash $mc/cprn.sh'
alias cdb='source $mc/cdback.sh'
export jobtype='pbs'
alias vinurion='vi $play/alias-x2431.sh'
