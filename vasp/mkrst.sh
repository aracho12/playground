#!/bin/bash

# Usage: mkrst.sh <start_num> <end_num> <prefix>
# Example: mkrst.sh 01 05 h2o
# This will process h2o_01.json through h2o_05.json

if [ $# -ne 3 ]; then
    echo "Usage: $0 <start_num> <end_num> <prefix>"
    echo "Example: $0 01 05 h2o"
    exit 1
fi

START_NUM=$1
END_NUM=$2
PREFIX=$3

# Convert start and end numbers to integers for comparison
start_int=$(printf "%d" "$START_NUM")
end_int=$(printf "%d" "$END_NUM")

# Loop through each number from start to end
for ((i=start_int; i<=end_int; i++)); do
    # Format number with zero padding (e.g., 01, 02, etc.)
    num=$(printf "%02d" "$i")
    
    # Define folder and file paths
    folder="$num"
    source_file="${PREFIX}_${num}.json"
    dest_file="$folder/restart.json"
    
    # 1) Create folder if it doesn't exist
    if [ ! -d "$folder" ]; then
        mkdir -p "$folder"
        echo "Created folder: $folder"
    fi
    
    # 2) Skip if restart.json already exists OR if source file doesn't exist
    if [ -f "$dest_file" ]; then
        echo "Skipping $num: restart.json already exists in $folder/"
        continue
    fi
    
    if [ ! -f "$source_file" ]; then
        echo "Skipping $num: $source_file does not exist"
        continue
    fi
    
    # 3) Move the file
    mv "$source_file" "$dest_file"
    echo "Moved $source_file -> $dest_file"
done
