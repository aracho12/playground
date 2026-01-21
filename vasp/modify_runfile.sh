#!/bin/bash

# Script to modify job name in SLURM job script
# Usage: modify_runfile.sh <new_job_name> [runfile]
# Default runfile: run.slurm

# Default runfile name
DEFAULT_RUNFILE="run.slurm"

# Check arguments
if [ "$#" -eq 0 ] || [ "$#" -gt 2 ]; then
    echo "Usage: $0 <new_job_name> [runfile]"
    echo "Example: $0 my_calculation"
    echo "Example: $0 my_calculation custom_run.sh"
    echo "Default runfile: $DEFAULT_RUNFILE"
    exit 1
fi

NEW_JOB_NAME="$1"
RUNFILE="${2:-$DEFAULT_RUNFILE}"

# Check if runfile exists
if [ ! -f "$RUNFILE" ]; then
    echo "Error: File not found: $RUNFILE"
    exit 1
fi

# Check if the file contains SBATCH -J line
if ! grep -q "^#SBATCH -J" "$RUNFILE"; then
    echo "Error: No '#SBATCH -J' line found in $RUNFILE"
    exit 1
fi

# Create backup of original file
BACKUP=".${RUNFILE}.bak"
cp "$RUNFILE" "$BACKUP"
echo "Backup created: $BACKUP"

# Modify the job name
sed -i.tmp "s/^#SBATCH -J.*/#SBATCH -J $NEW_JOB_NAME/" "$RUNFILE"
rm -f "${RUNFILE}.tmp"

echo "Job name updated to: $NEW_JOB_NAME"
echo "Original file backed up to: $BACKUP"

# Show the change
echo ""
echo "Modified line:"
grep "^#SBATCH -J" "$RUNFILE"
