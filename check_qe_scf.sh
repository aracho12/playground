#!/usr/bin/env bash

# Usage:
#   ./check_qe_scf.sh pw.out
#
# What it checks:
#   1) final convergence message
#   2) estimated scf accuracy trend
#   3) large oscillation of total energy
#   4) negative rho warnings
#   5) c_bands not converged warnings

outfile="${1:-pw.out}"

if [ ! -f "$outfile" ]; then
    echo "Error: file '$outfile' not found."
    exit 1
fi

echo "========================================"
echo " QE SCF convergence check for: $outfile"
echo "========================================"
echo

# 1) Did QE explicitly say it converged?
if grep -q "convergence has been achieved" "$outfile"; then
    echo "[OK] QE says: convergence has been achieved"
    converged_msg="yes"
else
    echo "[WARN] No 'convergence has been achieved' message found"
    converged_msg="no"
fi

echo

# 2) Print SCF iteration / accuracy / total energy summary
awk '
/iteration #/ {
    iter=$3
}
/total energy/ {
    E=$5
}
/estimated scf accuracy/ {
    acc=$5
    printf("iter=%-4s   Etot=%-18s   scf_acc=%s\n", iter, E, acc)
}
' "$outfile"

echo

# 3) Judge trend from last several scf accuracies
awk '
/estimated scf accuracy/ {
    n++
    acc[n]=$5+0
}
END {
    if (n==0) {
        print "[WARN] No SCF accuracy lines found."
        exit
    }

    print "Last SCF accuracies:"
    start = (n>5 ? n-4 : 1)
    for (i=start; i<=n; i++) {
        printf("  %d: %.6e\n", i, acc[i])
    }

    # Check whether accuracy is generally decreasing
    improve=0
    worsen=0
    for (i=2; i<=n; i++) {
        if (acc[i] < acc[i-1]) improve++
        else if (acc[i] > acc[i-1]) worsen++
    }

    print ""
    if (acc[n] < 1e-6) {
        print "[GOOD] Final estimated scf accuracy is very small (< 1e-6 Ry)."
    } else if (acc[n] < 1e-4) {
        print "[OK] Final estimated scf accuracy is reasonably small (< 1e-4 Ry)."
    } else if (acc[n] < 1e-2) {
        print "[WARN] SCF accuracy is still not very tight."
    } else {
        print "[BAD] SCF accuracy is large. Convergence looks poor."
    }

    if (improve > worsen) {
        print "[INFO] Accuracy trend is mostly improving."
    } else if (worsen > improve) {
        print "[WARN] Accuracy trend is worsening or oscillating."
    } else {
        print "[INFO] Accuracy trend is mixed."
    }
}
' "$outfile"

echo

# 4) Count negative rho warnings
neg_count=$(grep -c "negative rho" "$outfile" 2>/dev/null)
if [ "$neg_count" -gt 0 ]; then
    echo "[WARN] 'negative rho' appeared $neg_count time(s)"
else
    echo "[OK] No 'negative rho' warning found"
fi

# 5) Count band convergence warnings
cbands_count=$(grep -c "c_bands: .*eigenvalues not converged" "$outfile" 2>/dev/null)
if [ "$cbands_count" -gt 0 ]; then
    echo "[WARN] 'c_bands not converged' appeared $cbands_count time(s)"
else
    echo "[OK] No 'c_bands not converged' warning found"
fi

echo

# 6) Check total energy oscillation roughly
awk '
/total energy/ {
    n++
    E[n]=$5+0
}
END {
    if (n < 2) {
        print "[INFO] Not enough total energy data to analyze oscillation."
        exit
    }

    maxjump=0
    for (i=2; i<=n; i++) {
        d=E[i]-E[i-1]
        if (d<0) d=-d
        if (d>maxjump) maxjump=d
    }

    printf("[INFO] Maximum |ΔE| between successive SCF steps = %.6e Ry\n", maxjump)

    if (maxjump < 1e-4) {
        print "[GOOD] Total energy changes are tiny."
    } else if (maxjump < 1e-2) {
        print "[OK] Total energy is settling."
    } else {
        print "[WARN] Total energy changes are still large or oscillatory."
    }
}
' "$outfile"

echo
echo "============ Final quick judgment ============"

if [ "$converged_msg" = "yes" ]; then
    echo "Result: SCF converged."
else
    last_acc=$(awk '/estimated scf accuracy/ {x=$5} END {if (x=="") print "NA"; else print x}' "$outfile")

    if [ "$last_acc" = "NA" ]; then
        echo "Result: Unable to judge. No SCF accuracy found."
    else
        awk -v acc="$last_acc" '
        BEGIN {
            if (acc < 1e-4)
                print "Result: Probably converging well, but final convergence message is missing."
            else if (acc < 1e-2)
                print "Result: Converging, but not yet fully settled."
            else
                print "Result: Not converging well or strongly oscillating."
        }'
    fi
fi

echo "============================================="