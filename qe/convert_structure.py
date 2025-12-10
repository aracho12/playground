#!/usr/bin/env python3
"""
Convert Quantum ESPRESSO input files to various formats with optional visualization.
"""

import argparse
import glob
import os
import sys
from pathlib import Path

from ase.io import read, write
from ase.visualize import view


def find_qe_input_files(directory="."):
    """
    Find all .in files in the specified directory.
    
    Args:
        directory: Directory to search for .in files
        
    Returns:
        List of .in file paths
    """
    pattern = os.path.join(directory, "*.in")
    files = glob.glob(pattern)
    return sorted(files)


def convert_structure(input_file, output_formats=None, visualize=False, output_dir=None):
    """
    Convert Quantum ESPRESSO input file to specified formats.
    
    Args:
        input_file: Path to the QE input file (.in)
        output_formats: List of output formats (e.g., ['xyz', 'cif'])
        visualize: Whether to visualize the structure
        output_dir: Directory to save output files (default: same as input)
    """
    if output_formats is None:
        output_formats = ['xyz', 'cif']
    
    # Read the structure from QE input file
    try:
        atoms = read(input_file, format='espresso-in')
        print(f"Successfully read structure from: {input_file}")
        print(f"  Formula: {atoms.get_chemical_formula()}")
        print(f"  Number of atoms: {len(atoms)}")
    except Exception as e:
        print(f"Error reading {input_file}: {e}", file=sys.stderr)
        return False
    
    # Determine output directory
    if output_dir is None:
        output_dir = os.path.dirname(input_file) or "."
    
    # Create base filename (remove .in extension)
    base_name = Path(input_file).stem
    
    # Convert to specified formats
    for fmt in output_formats:
        output_file = os.path.join(output_dir, f"{base_name}.{fmt}")
        try:
            write(output_file, atoms)
            print(f"  Saved: {output_file}")
        except Exception as e:
            print(f"  Error saving {output_file}: {e}", file=sys.stderr)
    
    # Visualize if requested
    if visualize:
        try:
            print("  Opening visualization...")
            view(atoms)
        except Exception as e:
            print(f"  Error visualizing structure: {e}", file=sys.stderr)
    
    return True


def main():
    """Main function to handle command-line arguments and execute conversion."""
    parser = argparse.ArgumentParser(
        description='Convert Quantum ESPRESSO input files to XYZ and CIF formats',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert a specific file to XYZ and CIF
  %(prog)s -i input.in
  
  # Convert and visualize
  %(prog)s -i input.in --visualize
  
  # Convert all .in files in current directory
  %(prog)s --all
  
  # Convert to only XYZ format
  %(prog)s -i input.in -f xyz
  
  # Save without visualization
  %(prog)s -i input.in --no-visualize
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        '-i', '--input',
        type=str,
        help='Input QE file (.in) to convert'
    )
    input_group.add_argument(
        '--all',
        action='store_true',
        help='Convert all .in files in the current directory'
    )
    
    # Output options
    parser.add_argument(
        '-f', '--formats',
        nargs='+',
        default=['xyz', 'cif'],
        choices=['xyz', 'cif', 'pdb', 'json', 'extxyz'],
        help='Output format(s) (default: xyz cif)'
    )
    parser.add_argument(
        '-o', '--output-dir',
        type=str,
        help='Output directory (default: same as input file)'
    )
    
    # Visualization options
    viz_group = parser.add_mutually_exclusive_group()
    viz_group.add_argument(
        '-v', '--visualize',
        action='store_true',
        default=False,
        help='Visualize the structure after conversion'
    )
    viz_group.add_argument(
        '--no-visualize',
        action='store_true',
        help='Do not visualize (default behavior)'
    )
    
    args = parser.parse_args()
    
    # Determine input files
    input_files = []
    
    if args.input:
        # Single file specified
        if not os.path.exists(args.input):
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        input_files = [args.input]
    elif args.all:
        # Find all .in files
        input_files = find_qe_input_files()
        if not input_files:
            print("No .in files found in the current directory.", file=sys.stderr)
            sys.exit(1)
        print(f"Found {len(input_files)} .in file(s):")
        for f in input_files:
            print(f"  - {f}")
        print()
    else:
        # Try to auto-detect .in files
        input_files = find_qe_input_files()
        if len(input_files) == 0:
            print("No .in files found. Please specify an input file with -i or use --all", 
                  file=sys.stderr)
            parser.print_help()
            sys.exit(1)
        elif len(input_files) == 1:
            print(f"Auto-detected: {input_files[0]}")
            print()
        else:
            print(f"Found {len(input_files)} .in files. Please specify one with -i or use --all:")
            for f in input_files:
                print(f"  - {f}")
            sys.exit(1)
    
    # Process each file
    success_count = 0
    for input_file in input_files:
        if convert_structure(
            input_file,
            output_formats=args.formats,
            visualize=args.visualize,
            output_dir=args.output_dir
        ):
            success_count += 1
        print()
    
    # Summary
    if len(input_files) > 1:
        print(f"Conversion complete: {success_count}/{len(input_files)} files processed successfully")
    
    sys.exit(0 if success_count == len(input_files) else 1)


if __name__ == "__main__":
    main()