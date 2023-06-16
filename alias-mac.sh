alias vimac='vi $play/alias-mac.sh'
alias dct='dir_now=$PWD
cd /Users/aracho/Dropbox/0_Research/0_My_Publications/dct
git pull
git add *
git commit -m "."
git push
cd $dir_now'
export pes=/Users/aracho/Dropbox/0_Research/0_My_Publications/24_2023_PES-model/nersc

alias pes='$pes/backup aracho@perlmutter-p1.nersc.gov:/pscratch/sd/a/aracho/01_Pt_ORR_kinetic/. $pes/.'

alias eoga='open *.png'
