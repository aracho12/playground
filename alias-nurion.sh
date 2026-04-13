alias happy='dir_now=$PWD
cd ~/bin/for_a_happy_life
git pull
cd $dir_now'
alias play='dir_now=$PWD
cd ~/bin/playground
git pull
cd $dir_now'
qstart() {
  qstat -f "$1" | grep 'estimated.start_time'
}