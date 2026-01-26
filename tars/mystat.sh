#!/bin/bash
squeue -u aracho --format="%8A %20P %4C %5D %20j %2t %8M %8Q %V" | awk '
BEGIN { OFS=" " }
NR==1 {
    sub("SUBMIT_TIME", "SUBMIT_TIME")
    print
}
NR>1 {
    if ($NF ~ /^[0-9]{4}-[0-9]{2}-[0-9]{2}T/) {
        gsub("T", "_", $NF)
        sub(":[0-9]{2}$", "", $NF)
    }
    print
}' | column -t
