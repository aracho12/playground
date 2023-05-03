# --- Color --- #

LS_COLORS=$LS_COLORS:'*DONE=01;4;31:di=1;36:*.py=1;38;5;123:*.cif=01;35:*.txt=01;35:*.dat=01;35:*NCAR=1;4;38;5;214:*POINTS=1;4;38;5;214:*POSCAR=1;4;38;5;214:*OTCAR=1;4;38;5;214:*WAVECAR=00;38;5;214:*CHGCAR=00;38;5;214:*CHG=00;38;5;130:*DOSCAR=00;38;5;214:*PROCAR=00;38;5;130:*CONTCAR=1;38;5;214:*OUTCAR=1;38;5;214:*IBZKPT=00;38;5;130:*EIGENVAL=00;38;5;130:*REPORT=00;38;5;130:*XDATCAR=00;38;5;130:*PCDAT=00;38;5;130:*OSZICAR=1;38;5;214:*.out=00;38;5;130:*restart.json=1;4;38;5;214:*.sh=01;35' ; export LS_COLORS

export re='\e[0m' # regular
export bd='\e[1m' # color + bold
export it='\e[3m'
export bi='\e[3m\e[1m'
export line='\e[4m' # underline
export strike='\e[9m' # strikethrough
export dW='\033[37m\e[0m' # default white
export R='\033[31m' # red
export G='\033[32m' # green
export Y='\033[33m' # yellow
export Bl='\033[34m' # blue
export Ma='\033[35m' # magenta
export Cy='\033[36m' # cyan
export W='\033[37m' # white
export Gr='\033[90m' # bright black
export bR='\033[91m' # bright Red
export bG='\033[92m' # bright Green
export bY='\033[93m' # bright yellow
export bBl='\033[94m' # bright blue
export bMa='\033[95m' # bright magenta
export bCy='\033[96m' # bright cyan
export bW='\033[97m' # bright white

# --- Basic --- # 
if [[ $SHELL == '/bin/bash' ]] ; then
	alias vbash='vi ~/.bashrc'
	alias sbash='source ~/.bashrc'
	alias ls='ls --color=auto -h --group-directories-first'
	alias l='ls --color=auto -h --group-directories-first'
elif [[ $SHELL == '/bin/zsh' ]] ; then
	alias vbash='vi ~/.zshrc'
	alias vzsh='vi ~/.zshrc'
	alias sbash='source ~/.zshrc'
	alias szsh='source ~/.zshrc'
	alias ls='ls --color=auto'
	alias l='ls --color=auto'
else
	alias ls='ls'
fi

alias ..='cd ..'
alias ...='cd ../..'
alias c='clear'
alias cls='clear;ls'
alias grep='grep --color=always'
alias la='ls -la'
alias dush='du -h | sort -rh | head -20'
alias rm='~/bin/rm_mv'
alias sh='/bin/bash'
alias py='python'

# --- Git --- #
gitupdate(){
	dir_now=$PWD
	cd $1
	git pull
	git add *
	git commit -m "."
	git push
#	chmod 644 *
#	chmod 755 ./*/
	cd $dir_now
}

mc(){
	bash $happy/$1
}

incar(){
    if test -e INCAR ; then
        if grep -q $1 INCAR ; then
            sed -i "/$1/c\ $1 = $2" INCAR
        else
            echo " $1 = $2" >> INCAR
        fi
        grep $1 INCAR
    elif test -e run_relax.py ; then
        new=run_relax.py
        if grep -q $1 $new ; then
            sed -i "/$1/c\      $1 = $2," $new
        else
            sed -i "/ispin/a\      $1 = $2," $new
        fi
        grep $1 $new
    fi
}

alias orange='dir_now=$PWD
cd ~/bin/orange
git pull
cd $dir_now'
alias happy='dir_now=$PWD
cd ~/bin/for_a_happy_life
git pull
git add *
git commit -m "."
git push
cd $dir_now'
alias play='dir_now=$PWD
cd ~/bin/playground
git pull
git add *
git commit -m "."
git push
cd $dir_now'
alias aloha='dir_now=$PWD
cd ~/bin/aloha
git pull
cd $dir_now'
alias pull='git pull'
alias push='git push'
alias getbader='chgsum.pl AECCAR0 AECCAR2
bader CHGCAR -ref CHGCAR_sum'

# --- VARIABLES --- #
export VTST_PATH=~/bin/vtstscripts-1022
export ASE_VASP_VDW=~/bin/vdw_kernel
export happy=~/bin/for_a_happy_life
export aloha=~/bin/aloha
export orange=~/bin/orange
export play=~/bin/playground


# --- PATH --- #
export PYTHONPATH=~/bin:$PYTHONPATH
export PYTHONPATH=$happy:$PYTHONPATH
export PYTHONPATH=$aloha:$PYTHONPATH
export PATH=~/bin:$PATH
export PATH=$happy:$PATH
export PATH=~/bin/vaspkit.1.2.5/bin:$PATH
export ASE_VASP_VDW=~/bin

# --- ASE --- #
alias convf='ase convert -f -n -1 OUTCAR final_with_calculator.json && ls'
alias convr='ase convert -f -n -1 OUTCAR restart.json && ls'
alias pickle='python3 -m ase.io.trajectory *.traj'


# --- Alias --- #
alias cmc='cd $happy'
alias cgrun='bash $happy/cgrun.sh'
alias qdel='bash $happy/qdel.sh'
alias se='bash $happy/se.sh'
alias to='sec2hhmmdd.sh'
alias go='. $happy/go.sh'
alias showatoms='python $happy/showatoms.py'
alias mvc='mv CONTCAR POSCAR ; ls'
alias fix='python $happy/fixslab.py'
alias E0='grep E0 OSZICAR'
alias PBE='grep PBE POTCAR'
alias sub='bash $happy/sub_only_one_job.sh'
alias mystat='bash $happy/mystat.sh'
alias pot='python $happy/POTCAR.py'
alias con2cif='$VTST_PATH/pos2cif.pl CONTCAR && ls'
alias pos2cif='$VTST_PATH/pos2cif.pl POSCAR && ls'
alias dos='cp ~/bin/sumoDOS* .; python ./sumoDOS.py'
alias send.sh='bash $happy/send.sh'
alias ag='bash $happy/ag.sh'
alias vialias='vi $play/alias.sh'
alias cgrun='bash $happy/cgrun.sh'
alias mvc='mv CONTCAR POSCAR ; ls'
alias cs='source cs.sh'
alias ckrun='ckrun.sh'
alias cg='bash $happy/sg.sh'
alias rus='bash $happy/srus.sh'
alias ac='bash $happy/ag.sh CONTCAR'
alias ap='bash $happy/ag.sh POSCAR'
alias ts='bash $happy/ts.sh'
alias cnt='mc t2.sh'
alias set.sh='bash $happy/start.sh'
alias restart='mc restart.sh'
alias sub.sh='bash $happy/sub.sh'
alias jobllist='mc joblist.sh'
alias fstat='mc t1.sh'
alias te.sh='mc te.sh'
alias cgn='bash $happy/cgnode.sh'
alias here='echo $server'
alias scp.sh='bash $happy/scp.sh'
alias repeat='bash $happy/repeat.sh'
alias sym='python $happy/rearrange_symbols.py'
alias inneb.sh='bash $happy/inneb.sh'
alias cgtime='bash $happy/cgtime.sh'
alias lasub='ls -la */.sub*'
alias ts.sh='bash $happy/duration.sh'
alias rmchg='bash $happy/rmchg.sh'
alias resub='bash $happy/resub.sh'
alias rma='bash $happy/rma.sh'
alias mvc='bash $happy/mvc.sh'
alias resizecell='python $happy/change_cell_size.py'
alias getid='source $happy/getid.sh'

# --- Research --- #
alias wf='python $happy/wf_cal.py'
alias getrst='python $happy/get_restart.py'
alias getrst.sh='bash $happy/restart.sh'
alias getchg='python $happy/getchg.py'
alias gm='bash $happy/getmetal.sh'
alias getallmag='python $happy/get_allmagmoms.py'
alias getmag='python $happy/get_magmom.py'
alias chg='chgsum.pl AECCAR0 AECCAR2 && bader CHGCAR -ref CHGCAR_sum && rm CHG AECC* && ls'
alias pes='bash $happy/gitpes.sh'
export jobtype='slurm'
alias cdb='mc cdback.sh'
alias cprn='mc cprn.sh'
alias zpe='python $happy/ZPE.py'
alias cohp='mc cohp.sh'
alias cpcohp='cp ~/cohp.py .'
alias neb.sh='mc neb.sh'
alias nebplot='python $happy/nebplot.py'
alias dat2csv='python $happy/dat2csv.py'
alias neb2img='python $happy/neb2img.py'
alias fixatom='python $happy/fixatom.py'
alias findo='python $happy/find_o_type.py'
alias fp='python $happy/find_o_type.py POSCAR'
alias fc='python $happy/find_o_type.py CONTCAR'
alias distance='python $happy/getdistance_pair.py'
alias showimg='python $happy/show_ini_fin.py'
alias hbond='python $happy/hbond.py'
# --- PtORR --- #
alias ptwater='python $happy/pt-water.py'
# --- INCAR --- #
alias cpmd='bash $happy/cpmd.sh'
# --- TRASH --- #

~/bin/empty_basket 2

# remove files which have been more than certain days in (home)/_TRASH
