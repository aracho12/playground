alias fstat='date -d yesterday |sacct --format="JobID,JobName%30,Partition,Elapsed,NCPUS,State" | grep roma | grep -e PENDING -e RUNNING -e COMPLETED -e TIMEOUT'
alias cpsn='bash $happy/sdf/cp_file_sync_sdf.sh'
alias rmsn='bash $happy/sdf/del_file_in_sdf.sh'
alias cpvp='cp ~/bin/vasp/* .'
