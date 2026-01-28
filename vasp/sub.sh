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

# Function to process a single folder
process_folder() {
    local folder_path="$1"
    local job_name="$2"
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

# If no arguments, process current folder
if [ $# -eq 0 ]; then
    # Get job name
    read -p "Enter job name: " job_name
    
    if [ -z "$job_name" ]; then
        echo "Error: Job name cannot be empty"
        exit 1
    fi
    
    echo "Processing current folder..."
    process_folder "." "$job_name"
    exit $?
fi

# If 2 arguments, process folder range
if [ $# -eq 2 ]; then
    start_folder="$1"
    end_folder="$2"
    
    # Get base job name
    read -p "Enter base job name: " base_job_name
    
    if [ -z "$base_job_name" ]; then
        echo "Error: Job name cannot be empty"
        exit 1
    fi
    
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
        
        process_folder "$folder" "$job_name"
        
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