alias fstat='date -d yesterday |sacct --format="JobID,JobName%30,Partition,Elapsed,NCPUS,State" | grep roma | grep -e PENDING -e RUNNING -e COMPLETED -e TIMEOUT'
