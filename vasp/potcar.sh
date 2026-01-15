#!/bin/bash

# Script to generate POTCAR file from POSCAR
# Reads element names from line 6 of POSCAR and concatenates individual POTCAR files

# Check if POSCAR file exists
if [ ! -f "POSCAR" ]; then
    echo "Error: POSCAR file not found in current directory"
    exit 1
fi

# Path to POTCAR directory
POTCAR_DIR="/apps/programs/vasp/potpaw_PBE.54"

# Check if POTCAR directory exists
if [ ! -d "$POTCAR_DIR" ]; then
    echo "Error: POTCAR directory not found: $POTCAR_DIR"
    exit 1
fi

# Read line 6 from POSCAR to get element names
elements=$(sed -n '6p' POSCAR)

# Check if elements were found
if [ -z "$elements" ]; then
    echo "Error: Could not read elements from line 6 of POSCAR"
    exit 1
fi

echo "Elements found: $elements"

# Remove existing POTCAR if it exists
if [ -f "POTCAR" ]; then
    echo "Removing existing POTCAR file..."
    rm POTCAR
fi

# Concatenate POTCAR files for each element
for element in $elements; do
    potcar_file="${POTCAR_DIR}/${element}/POTCAR"
    
    if [ ! -f "$potcar_file" ]; then
        echo "Error: POTCAR file not found for element: $element"
        echo "Expected path: $potcar_file"
        exit 1
    fi
    
    echo "Adding POTCAR for $element..."
    cat "$potcar_file" >> POTCAR
done

echo "POTCAR file created successfully!"
