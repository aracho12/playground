mvall(){
    mv AEC* *.dat *.py *.json *.traj $1
    mv CHG* OUT* CON* POS* *.sh *.log REPORT PCDAT $1
    mv out* err* IBZKPT* INCAR* KPOINS* EIGENVAL* OSZICAR* WAVECAR* XDATCAR* vasprun.xml* CHGCAR* DOSCAR* $1
    mv NOT_DONE DONE $1 
}

mvall $1