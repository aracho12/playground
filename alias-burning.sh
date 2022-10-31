export pes=/home/aracho/8_suncat-orr/PES-model-for-ORR
alias pes='dir_now=$PWD
cd $pes 
git pull
git add *
git commit -m "."
git push
cd $dir_now'
