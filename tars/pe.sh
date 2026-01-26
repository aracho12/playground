#!/bin/bash
# Show idle nodes count per partition

echo "=== Idle Nodes Summary ==="
pestat | awk '
NR>2 && $3 == "idle" {
    partition[$2]++
    nodes[$2] = nodes[$2] " " $1
}
END {
    printf "%-25s %s\n", "PARTITION", "IDLE_NODES"
    printf "%-25s %s\n", "-------------------------", "----------"
    for (p in partition) {
        printf "%-25s %d\n", p, partition[p]
    }
    # print ""
    # print "=== Idle Node Details ==="
    # for (p in partition) {
    #     print p ":"
    #     print "  " nodes[p]
    # }
}'
