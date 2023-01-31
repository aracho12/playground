export pes=/home/aracho/8_suncat-orr/PES-model-for-ORR
alias pes='dir_now=$PWD
cd $pes 
git pull
git add *
git commit -m "."
git push
cd $dir_now'
export server='burning'
alias viburning='vi ~/bin/playground/alias-burning.sh'

#VASP
export VASP535=/TGM/Apps/VASP_OLD/bin/5.3.5/NORMAL
export VASP632=/TGM/Apps/VASP/VASP_BIN/6.3.2

export 535vtst=$VASP535/vasp.5.3.5_31MAR2014_GRP7_NORMAL_VTST.x
export 632vaspsol=$VASP632/vasp.6.3.2.vaspsol.std.x
