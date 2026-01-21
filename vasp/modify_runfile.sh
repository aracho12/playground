#!/bin/bash

# Script to modify job name and partition in SLURM job script
# Usage: modify_runfile.sh [-p partition] [-j job_name] [runfile]
# Default runfile: run_slurm.sh

# Default runfile name
DEFAULT_RUNFILE="run_slurm.sh"

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
    echo "Usage: $0 [-p partition] [-j job_name] [runfile]"
    echo "Example: $0 -j my_calculation"
    echo "Example: $0 -p nehalem"
    echo "Example: $0 -j my_job -p nehalem_8c custom_run.sh"
    echo "Default runfile: $DEFAULT_RUNFILE"
    echo ""
    echo "Partition shorthands:"
    echo "  neh, nehalem -> nehalem_8c"
    exit 1
fi

# Check if runfile exists
if [ ! -f "$RUNFILE" ]; then
    echo "Error: File not found: $RUNFILE"
    exit 1
fi

# Create backup of original file
BACKUP=".${RUNFILE}.bak"
cp "$RUNFILE" "$BACKUP"
echo "Backup created: $BACKUP"

# Modify partition if specified
if [ -n "$PARTITION" ]; then
    # Expand partition shorthand
    EXPANDED_PARTITION=$(expand_partition "$PARTITION")
    
    # Check if the file contains SBATCH -p line
    if ! grep -q "^#SBATCH -p" "$RUNFILE"; then
        echo "Error: No '#SBATCH -p' line found in $RUNFILE"
        exit 1
    fi
    
    # Prompt for number of nodes
    echo "Changing partition to: $EXPANDED_PARTITION"
    read -p "How many nodes do you want to use? " NODE_COUNT
    
    # Validate node count
    if ! [[ "$NODE_COUNT" =~ ^[0-9]+$ ]]; then
        echo "Error: Invalid node count. Must be a positive integer."
        exit 1
    fi
    
    # Modify the partition
    sed -i.tmp "s/^#SBATCH -p.*/#SBATCH -p $EXPANDED_PARTITION/" "$RUNFILE"
    rm -f "${RUNFILE}.tmp"
    
    # Check if the file contains SBATCH -N line and modify it
    if grep -q "^#SBATCH -N" "$RUNFILE"; then
        sed -i.tmp "s/^#SBATCH -N.*/#SBATCH -N $NODE_COUNT/" "$RUNFILE"
        rm -f "${RUNFILE}.tmp"
        echo "Partition updated to: $EXPANDED_PARTITION"
        echo "Node count updated to: $NODE_COUNT"
    else
        # Add the node count line after the partition line
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

# Modify the job name if specified
if [ -n "$JOB_NAME" ]; then
    # Check if the file contains SBATCH -J line
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

echo ""
echo "Original file backed up to: $BACKUP"
