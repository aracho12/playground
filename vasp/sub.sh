#!/bin/bash

# Usage: 
#   sub.sh                    - Submit job in current folder
#   sub.sh <start> <end>      - Submit jobs in folders from start to end
# Example: 
#   sub.sh                    - Submit in current folder
#   sub.sh 01 05              - Process folders 01, 02, 03, 04, 05

# Get the directory where the script is located
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
play="${play:-$HOME}"

VALID_MODES="slab sp fiscs vib charge dos wf gas"

# Function to process a single folder
process_folder() {
    local folder_path="$1"
    local job_name="$2"
    local vasp_mode="$3"
    local runfile='run_slurm.sh'

    # Check if ase_vasp.py or run_slurm.sh is missing, then run cpini.sh
    if [ ! -f "ase_vasp.py" ] || [ ! -f "$runfile" ]; then
        echo "Missing ase_vasp.py or $runfile. Running cpini.sh..."
        if [ -f "$script_dir/cpini.sh" ]; then
            bash "$script_dir/cpini.sh"
        elif [ -f "$play/vasp/cpini.sh" ]; then
            bash "$play/vasp/cpini.sh"
        else
            echo "Warning: cpini.sh not found, skipping file copy..."
        fi
    fi

    # Check if runfile exists
    if [ ! -f "$runfile" ]; then
        echo "Error: $runfile does not exist in $folder_path"
        return 1
    fi

    # Patch VASP_MODE in runfile
    if grep -q "^VASP_MODE=" "$runfile"; then
        sed -i.tmp "s/^VASP_MODE=.*/VASP_MODE=$vasp_mode/" "$runfile"
        rm -f "${runfile}.tmp"
        echo "  VASP_MODE set to: $vasp_mode"
    else
        echo "  Warning: VASP_MODE line not found in $runfile — mode not patched"
    fi

    # Modify job name if the file contains #SBATCH -J line
    if grep -q "^#SBATCH -J" "$runfile"; then
        if [ -f "$script_dir/modify_runfile.sh" ]; then
            bash "$script_dir/modify_runfile.sh" -j "$job_name" "$runfile"
        elif [ -f "$play/vasp/modify_runfile.sh" ]; then
            bash "$play/vasp/modify_runfile.sh" -j "$job_name" "$runfile"
        else
            # Fallback: use sed directly
            sed -i.tmp "s/^#SBATCH -J.*/#SBATCH -J $job_name/" "$runfile"
            rm -f "${runfile}.tmp"
        fi
    fi

    # Submit the job
    echo "Submitting job: $job_name"
    sbatch "$runfile"
    return 0
}

# Helper: prompt for VASP mode with validation
prompt_vasp_mode() {
    local mode
    read -p "Enter VASP mode [${VALID_MODES}] (default: slab): " mode
    mode="${mode:-slab}"
    if ! echo "$VALID_MODES" | grep -qw "$mode"; then
        echo "Error: Unknown mode '$mode'. Valid modes: $VALID_MODES"
        exit 1
    fi
    echo "$mode"
}

# If no arguments, process current folder
if [ $# -eq 0 ]; then
    default_job_name="$(basename "$PWD")"
    read -p "Enter job name (default: $default_job_name): " job_name
    job_name="${job_name:-$default_job_name}"

    vasp_mode=$(prompt_vasp_mode)

    echo "Processing current folder..."
    process_folder "." "$job_name" "$vasp_mode"
    exit $?
fi

# If 2 arguments, process folder range
if [ $# -eq 2 ]; then
    start_folder="$1"
    end_folder="$2"

    # Get base job name
    default_job_name="$(basename "$PWD")"
    read -p "Enter base job name (default: $default_job_name): " base_job_name
    base_job_name="${base_job_name:-$default_job_name}"

    vasp_mode=$(prompt_vasp_mode)
    
    # Detect format (leading zeros or not) from input
    if [[ "$start_folder" =~ ^0[0-9]+$ ]]; then
        # Input has leading zeros, use %02d format
        format="%02d"
        start_num=$((10#$start_folder))  # Force base-10 interpretation
        end_num=$((10#$end_folder))
    else
        # No leading zeros, use %d format
        format="%d"
        start_num=$((10#$start_folder))
        end_num=$((10#$end_folder))
    fi
    
    if [ "$start_num" -gt "$end_num" ]; then
        echo "Error: Start folder number must be less than or equal to end folder number"
        exit 1
    fi
    
    # Iterate through folders
    current_num=$start_num
    while [ "$current_num" -le "$end_num" ]; do
        # Format folder number (preserve input format)
        folder=$(printf "$format" "$current_num")
        
        if [ ! -d "$folder" ]; then
            echo "Warning: Folder $folder does not exist, skipping..."
            current_num=$((current_num + 1))
            continue
        fi
        
        echo ""
        echo "$Y Processing folder: $folder $dW"
        cd "$folder" || {
            echo "Error: Cannot enter folder $folder"
            current_num=$((current_num + 1))
            continue
        }
        
        # Construct job name: base_name_folder
        job_name="${base_job_name}_${folder}"

        process_folder "$folder" "$job_name" "$vasp_mode"
        
        # Return to parent directory
        cd ..
        
        current_num=$((current_num + 1))
    done
    
    echo ""
    echo "All jobs submitted!"
    exit 0
fi

# Invalid usage
echo "Usage: $0 [<start_folder> <end_folder>]"
echo "  No arguments: Submit job in current folder"
echo "  Two arguments: Process folders from start to end"
echo "Example: $0"
echo "Example: $0 01 05"
exit 1