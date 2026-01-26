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
alias jl='jupyter-lab --no-browser'
export PATH=/Users/aracho/.local/bin:$PATH
export PYTHONPATH=/Users/aracho/.local/bin:$PYTHONPATH
export PYTHONPATH=/Users/aracho/bin/CATMAP_source/catmap:$PYTHONPATH
export PYTHONPATH=/Users/aracho/bin/ase-notebook:$PYTHONPATH
export crada=/Users/aracho/Google\ Drive/My\ Drive/CRADA-Projects
alias happy='dir_now=$PWD
cd ~/bin/for_a_happy_life
git pull origin master
git add *
git commit -m "."
git push origin master
cd $dir_now'

export PYTHONPATH=/Users/aracho/bin/co2r-mkm-model:$PYTHONPATH
alias sdf='ssh -X -Y aracho@s3dflogin.slac.stanford.edu'
export s3df='aracho@s3dflogin.slac.stanford.edu'
export scpsdf='scp -r aracho@s3dflogin.slac.stanford.edu:'
alias tars='ssh -X -Y aracho@tars.kaist.ac.kr'
alias totars='$happy/util/transfer_to_tars.sh'
alias fromtars='$play/tars/transfer_from_tars.sh'
alias baktars='$play/tars/backup_tars.sh'
