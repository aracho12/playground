mvall(){
    to=$1
    # 각 패턴마다 존재하면 옮기기
    patterns1="AEC* *.dat *.py *.json *.traj"
    patterns2="CHG* OUT* CON* POS* *.sh *.log REPORT PCDAT"
    patterns3="out* err* IBZKPT* INCAR* KPOINTS* EIGENVAL* OSZICAR* WAVECAR* XDATCAR* vasprun.xml* DOSCAR*"
    patterns4="NOT_DONE DONE *.out POTCAR"

    for patterns in "$patterns1" "$patterns2" "$patterns3" "$patterns4"; do
        files=()
        # pattern별로 존재하는 파일만 files에 담기
        for f in $patterns; do
            # 파일이나 폴더가 실제로 있으면
            if compgen -G "$f" > /dev/null 2>&1; then
                files+=( $f )
            fi
        done
        # 옮길 파일 있으면 mv
        if [ ${#files[@]} -gt 0 ]; then
            mv "${files[@]}" "$to"
        fi
    done
}

mvall $1