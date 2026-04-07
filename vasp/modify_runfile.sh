#!/bin/bash

# Script to modify job name and partition/queue in PBS or SLURM job scripts
# Automatically detects scheduler type from the runfile
# Usage: modify_runfile.sh [-p partition/queue] [-j job_name] [runfile]
# Default runfile: run_slurm.sh

# Default runfile name
DEFAULT_RUNFILE="run_slurm.sh"

# Function to detect scheduler type from runfile
detect_scheduler() {
    local file="$1"
    if grep -q "^#PBS" "$file"; then
        echo "PBS"
    elif grep -q "^#SBATCH" "$file"; then
        echo "SLURM"
    else
        echo "UNKNOWN"
    fi
}

# Function to expand partition shorthand
expand_partition() {
    local partition="$1"
    case "$partition" in
        neh|nehalem)
            echo "nehalem_8c"
            ;;
        *)
            echo "$partition"
            ;;
    esac
}

# Parse arguments
PARTITION=""
JOB_NAME=""
RUNFILE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -p)
            PARTITION="$2"
            shift 2
            ;;
        -j)
            JOB_NAME="$2"
            shift 2
            ;;
        *)
            if [ -z "$RUNFILE" ]; then
                RUNFILE="$1"
            fi
            shift
            ;;
    esac
done

# Set default runfile if not specified
RUNFILE="${RUNFILE:-$DEFAULT_RUNFILE}"

# Check if at least one modification is requested
if [ -z "$PARTITION" ] && [ -z "$JOB_NAME" ]; then
    echo "Usage: $0 [-p partition/queue] [-j job_name] [runfile]"
    echo ""
    echo "  Supports both PBS and SLURM job scripts (auto-detected)"
    echo ""
    echo "Examples:"
    echo "  $0 -j my_calculation"
    echo "  $0 -p normal run_pbs.sh"
    echo "  $0 -j my_job -p nehalem_8c custom_run.sh"
    echo ""
    echo "Default runfile: $DEFAULT_RUNFILE"
    echo ""
    echo "Partition shorthands (SLURM only):"
    echo "  neh, nehalem -> nehalem_8c"
    exit 1
fi

# Check if runfile exists
if [ ! -f "$RUNFILE" ]; then
    echo "Error: File not found: $RUNFILE"
    exit 1
fi

# Detect scheduler type
SCHEDULER=$(detect_scheduler "$RUNFILE")
echo "Detected scheduler: $SCHEDULER"

if [ "$SCHEDULER" = "UNKNOWN" ]; then
    echo "Error: Could not detect scheduler type. File must contain #PBS or #SBATCH directives."
    exit 1
fi

# Create backup of original file
BACKUP=".${RUNFILE}.bak"
cp "$RUNFILE" "$BACKUP"
echo "Backup created: $BACKUP"

# ─────────────────────────────────────────────
# Modify partition / queue if specified
# ─────────────────────────────────────────────
if [ -n "$PARTITION" ]; then
    if [ "$SCHEDULER" = "PBS" ]; then
        # PBS: queue is set with  #PBS -q <queue>
        if ! grep -q "^#PBS -q" "$RUNFILE"; then
            echo "Error: No '#PBS -q' line found in $RUNFILE"
            exit 1
        fi

        echo "Changing PBS queue to: $PARTITION"
        sed -i.tmp "s/^#PBS -q.*/#PBS -q $PARTITION/" "$RUNFILE"
        rm -f "${RUNFILE}.tmp"

        echo "Queue updated to: $PARTITION"
        echo ""
        echo "Modified line:"
        grep "^#PBS -q" "$RUNFILE"

    else
        # SLURM: partition is set with  #SBATCH -p <partition>
        EXPANDED_PARTITION=$(expand_partition "$PARTITION")

        if ! grep -q "^#SBATCH -p" "$RUNFILE"; then
            echo "Error: No '#SBATCH -p' line found in $RUNFILE"
            exit 1
        fi

        echo "Changing SLURM partition to: $EXPANDED_PARTITION"
        read -p "How many nodes do you want to use? " NODE_COUNT

        if ! [[ "$NODE_COUNT" =~ ^[0-9]+$ ]]; then
            echo "Error: Invalid node count. Must be a positive integer."
            exit 1
        fi

        sed -i.tmp "s/^#SBATCH -p.*/#SBATCH -p $EXPANDED_PARTITION/" "$RUNFILE"
        rm -f "${RUNFILE}.tmp"

        if grep -q "^#SBATCH -N" "$RUNFILE"; then
            sed -i.tmp "s/^#SBATCH -N.*/#SBATCH -N $NODE_COUNT/" "$RUNFILE"
            rm -f "${RUNFILE}.tmp"
            echo "Partition updated to: $EXPANDED_PARTITION"
            echo "Node count updated to: $NODE_COUNT"
        else
            sed -i.tmp "/^#SBATCH -p/a\\
#SBATCH -N $NODE_COUNT
" "$RUNFILE"
            rm -f "${RUNFILE}.tmp"
            echo "Partition updated to: $EXPANDED_PARTITION"
            echo "Node count line added: #SBATCH -N $NODE_COUNT"
        fi

        echo ""
        echo "Modified lines:"
        grep "^#SBATCH -p" "$RUNFILE"
        grep "^#SBATCH -N" "$RUNFILE"
    fi
fi

# ─────────────────────────────────────────────
# Modify job name if specified
# ─────────────────────────────────────────────
if [ -n "$JOB_NAME" ]; then
    if [ "$SCHEDULER" = "PBS" ]; then
        # PBS: job name is set with  #PBS -N <name>
        if ! grep -q "^#PBS -N" "$RUNFILE"; then
            echo "Error: No '#PBS -N' line found in $RUNFILE"
            exit 1
        fi

        sed -i.tmp "s/^#PBS -N.*/#PBS -N $JOB_NAME/" "$RUNFILE"
        rm -f "${RUNFILE}.tmp"

        echo "Job name updated to: $JOB_NAME"
        echo ""
        echo "Modified line:"
        grep "^#PBS -N" "$RUNFILE"

    else
        # SLURM: job name is set with  #SBATCH -J <name>
        if ! grep -q "^#SBATCH -J" "$RUNFILE"; then
            echo "Error: No '#SBATCH -J' line found in $RUNFILE"
            exit 1
        fi

        sed -i.tmp "s/^#SBATCH -J.*/#SBATCH -J $JOB_NAME/" "$RUNFILE"
        rm -f "${RUNFILE}.tmp"

        echo "Job name updated to: $JOB_NAME"
        echo ""
        echo "Modified line:"
        grep "^#SBATCH -J" "$RUNFILE"
    fi
fi

echo ""
echo "Original file backed up to: $BACKUP"
