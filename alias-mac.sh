export pes=/Users/aracho/Dropbox/0_Research/0_My_Publications/24_2022_PES-model/PES-model-for-ORR
alias pes='dir_now=$PWD
cd $pes
git pull
git add *
git commit -m "."
git push
cd $dir_now'
alias vimac='vi $play/alias-mac.sh'
alias dct='dir_now=$PWD
cd /Users/aracho/Dropbox/0_Research/0_My_Publications/dct
git pull
git add *
git commit -m "."
git push
cd $dir_now'
