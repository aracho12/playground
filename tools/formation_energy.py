"""
Formation Energy Calculator Module

This module calculates formation energies from raw energies using reference states.
It can process data from TSV, CSV, or Excel files containing species energy data.

Usage:
    from tools.formation_energy import FormationEnergyCalculator
    
    # Initialize calculator
    calc = FormationEnergyCalculator('data.xlsx')
    
    # Calculate formation energies
    calc.calculate_formation_energies()
    
    # Save results
    calc.save('output.tsv')
    
    # Display results
    calc.display()
    
    # Get as database
    db = calc.to_db()
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path
from typing import Dict, Optional, List, Tuple
import warnings


class FormationEnergyCalculator:
    """
    Calculator for converting raw energies to formation energies.
    
    Attributes:
        df (pd.DataFrame): DataFrame containing the energy data
        ref_energies (Dict[str, float]): Reference energies for each element
        elements (List[str]): List of elements found in the dataset
    """
    
    def __init__(self, filepath: str, sheet_name: Optional[str] = None):
        """
        Initialize the calculator by loading data from a file.
        
        Args:
            filepath: Path to TSV, CSV, or Excel file containing energy data.
                     Expected columns: surface_name (or surface), site_name (or facet),
                     species_name (or species), raw_energy, type (or status or phase)
                     Optional: correction_energy (will be added to raw_energy)
            sheet_name: Optional sheet name for Excel files (default: first sheet or 'BEEF-vdW')
        """
        self.filepath = Path(filepath)
        self.sheet_name = sheet_name
        self.df = self._load_data(filepath, sheet_name)
        self._normalize_column_names()
        self._apply_energy_correction()
        self.ref_energies = {}
        self.elements = []
        
    def _load_data(self, filepath: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """Load data from TSV, CSV, or Excel file."""
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        # Determine file type and load accordingly
        if filepath.suffix.lower() in ['.xlsx', '.xls']:
            # Try to load specific sheet if provided
            if sheet_name:
                try:
                    df = pd.read_excel(filepath, sheet_name=sheet_name)
                    print(f"Loaded sheet: '{sheet_name}'")
                except Exception as e:
                    print(f"Could not load sheet '{sheet_name}': {e}")
                    print("Loading first sheet instead...")
                    df = pd.read_excel(filepath)
            else:
                # Try 'BEEF-vdW' sheet first, then default to first sheet
                try:
                    df = pd.read_excel(filepath, sheet_name='BEEF-vdW')
                    print(f"Loaded sheet: 'BEEF-vdW'")
                except:
                    df = pd.read_excel(filepath)
                    print(f"Loaded first sheet")
        elif filepath.suffix.lower() == '.tsv':
            df = pd.read_csv(filepath, sep='\t')
        elif filepath.suffix.lower() == '.csv':
            df = pd.read_csv(filepath)
        else:
            raise ValueError(f"Unsupported file format: {filepath.suffix}")
        
        return df
    
    def _normalize_column_names(self):
        """Normalize column names to standard format."""
        column_mapping = {
            'surface': 'surface_name',
            'facet': 'site_name',
            'species': 'species_name',
            'status': 'type',
            'phase': 'type'
        }
        
        # Create a case-insensitive mapping
        current_columns = {col.lower(): col for col in self.df.columns}
        rename_dict = {}
        
        for alternative, standard in column_mapping.items():
            if alternative in current_columns:
                rename_dict[current_columns[alternative]] = standard
        
        if rename_dict:
            self.df = self.df.rename(columns=rename_dict)
            print(f"Renamed columns: {rename_dict}")
        
        # Verify required columns exist
        required = ['species_name', 'raw_energy', 'type']
        missing = [col for col in required if col not in self.df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}. Available columns: {list(self.df.columns)}")
    
    def _apply_energy_correction(self):
        """
        Apply correction_energy to raw_energy if correction_energy column exists.
        Creates a new column 'corrected_energy' which is used for calculations.
        """
        if 'correction_energy' in self.df.columns:
            # Add correction to raw energy
            self.df['corrected_energy'] = self.df['raw_energy'] + self.df['correction_energy']
            print(f"Applied correction_energy to raw_energy")
            print(f"  Correction range: {self.df['correction_energy'].min():.6f} to {self.df['correction_energy'].max():.6f} eV")
        else:
            # No correction, just use raw energy
            self.df['corrected_energy'] = self.df['raw_energy']
            print("No correction_energy column found, using raw_energy as is")
    
    def _parse_formula(self, formula: str) -> Dict[str, int]:
        """
        Parse a chemical formula to extract element counts.
        
        Args:
            formula: Chemical formula string (e.g., 'C2H4', 'H2O')
        
        Returns:
            Dictionary mapping element symbols to counts
        """
        # Remove common suffixes and special characters
        formula = formula.replace('_ref', '').replace('_', '').replace('-', '').replace('+', '')
        
        # Skip slab
        if formula.lower() == 'slab':
            return {}
        
        # Pattern to match element symbol followed by optional number
        pattern = r'([A-Z][a-z]?)(\d*)'
        matches = re.findall(pattern, formula)
        
        composition = {}
        for element, count in matches:
            if element:  # Skip empty matches
                count = int(count) if count else 1
                composition[element] = composition.get(element, 0) + count
        
        return composition
    
    def _extract_elements(self) -> List[str]:
        """
        Extract all unique elements from species names in the dataset.
        
        Returns:
            List of element symbols
        """
        all_elements = set()
        
        for species in self.df['species_name'].unique():
            composition = self._parse_formula(species)
            all_elements.update(composition.keys())
        
        return sorted(list(all_elements))
    
    def _calculate_reference_energies(self):
        """
        Calculate reference energies for H, O, and C from gas/liquid phase species.
        
        Uses:
            E_ref(H) = 0.5 * E(H2)
            E_ref(O) = E(H2O) - E(H2)
            E_ref(C) = E(CO2) - 2 * E_ref(O)
        """
        # Get gas and liquid phase energies - both can be used as references
        gas_liquid_df = self.df[
            self.df['type'].str.lower().str.strip().isin(['gas', 'liquid'])
        ].copy()
        
        # Debug: print available data
        print(f"  Found {len(gas_liquid_df)} gas/liquid phase entries")
        if len(gas_liquid_df) > 0:
            print(f"  Reference species: {', '.join(gas_liquid_df['species_name'].unique()[:10])}")
        else:
            # Try to find any gas/liquid entries with different filtering
            print("  WARNING: No entries with type='gas' or 'liquid' found")
            print(f"  Available types: {self.df['type'].unique()}")
            print(f"  All species_name values: {self.df['species_name'].unique()[:20]}")
            # Fallback: use all data if no type filtering works
            gas_liquid_df = self.df.copy()
        
        # Helper function to get energy by species name
        def get_gas_energy(name: str) -> Optional[float]:
            # Try exact match first in gas/liquid data
            exact = gas_liquid_df[gas_liquid_df['species_name'] == name]
            if not exact.empty:
                return exact.iloc[0]['corrected_energy']
            
            # Try case-insensitive match
            matches = gas_liquid_df[gas_liquid_df['species_name'].str.lower() == name.lower()]
            if not matches.empty:
                return matches.iloc[0]['corrected_energy']
            
            # Try with _ref suffix
            ref_name = f"{name}_ref"
            ref_matches = gas_liquid_df[gas_liquid_df['species_name'].str.lower() == ref_name.lower()]
            if not ref_matches.empty:
                return ref_matches.iloc[0]['corrected_energy']
            
            # Try in entire dataframe if not found in gas/liquid
            all_exact = self.df[self.df['species_name'].str.lower() == name.lower()]
            if not all_exact.empty:
                found_type = all_exact.iloc[0]['type']
                print(f"  Note: Found {name} with type='{found_type}' (using as reference)")
                return all_exact.iloc[0]['corrected_energy']
            
            return None
        
        # Get H2 energy
        E_H2 = get_gas_energy('H2')
        if E_H2 is None:
            raise ValueError(f"H2 gas phase energy not found in dataset. Available species: {list(self.df['species_name'].unique())}")
        
        # Calculate E_ref(H)
        self.ref_energies['H'] = 0.5 * E_H2
        
        # Get H2O energy
        E_H2O = get_gas_energy('H2O')
        if E_H2O is None:
            raise ValueError(f"H2O gas phase energy not found in dataset. Available species: {list(self.df['species_name'].unique())}")
        
        # Calculate E_ref(O)
        self.ref_energies['O'] = E_H2O - E_H2
        
        # Get CO2 energy
        E_CO2 = get_gas_energy('CO2')
        if E_CO2 is not None:
            # Calculate E_ref(C)
            self.ref_energies['C'] = E_CO2 - 2 * self.ref_energies['O']
        
        print("Reference Energies:")
        for element, energy in self.ref_energies.items():
            print(f"  E_ref({element}) = {energy:.6f} eV")
    
    def _get_slab_energy(self, surface_name: str, site_name: str) -> Optional[float]:
        """
        Get the corrected energy of a slab for a given surface and site.
        
        Args:
            surface_name: Name of the surface
            site_name: Name of the site/facet
        
        Returns:
            Slab energy or None if not found
        """
        # Check if surface_name and site_name columns exist
        has_surface = 'surface_name' in self.df.columns
        has_site = 'site_name' in self.df.columns
        
        # Filter for slab entries
        slab_df = self.df[
            (self.df['type'].str.lower() == 'slab') |
            (self.df['species_name'].str.lower() == 'slab')
        ].copy()
        
        if slab_df.empty:
            return None
        
        # Try to find matching slab
        if has_surface and has_site:
            match = slab_df[
                (slab_df['surface_name'] == surface_name) &
                (slab_df['site_name'] == site_name)
            ]
            if not match.empty:
                return match.iloc[0]['corrected_energy']
        
        if has_surface:
            match = slab_df[slab_df['surface_name'] == surface_name]
            if not match.empty:
                return match.iloc[0]['corrected_energy']
        
        # Return first slab if no specific match
        return slab_df.iloc[0]['corrected_energy']
    
    def _calculate_formation_energy_for_row(self, row: pd.Series) -> Optional[float]:
        """
        Calculate formation energy for a single row.
        
        Args:
            row: DataFrame row containing species data
        
        Returns:
            Formation energy or None if cannot be calculated
        """
        species = row['species_name']
        corrected_energy = row['corrected_energy']  # Use corrected energy instead of raw
        phase_type = row['type'].lower()
        
        # Parse chemical formula
        composition = self._parse_formula(species)
        
        # If no composition could be parsed, skip
        if not composition:
            if phase_type == 'slab' or species.lower() == 'slab':
                return 0.0
            return None
        
        # Check if all elements have reference energies
        missing_refs = [elem for elem in composition.keys() if elem not in self.ref_energies]
        if missing_refs:
            warnings.warn(f"Cannot calculate formation energy for {species}: "
                         f"missing reference energies for {missing_refs}")
            return None
        
        # Calculate reference energy contribution
        ref_contribution = sum(
            count * self.ref_energies[elem]
            for elem, count in composition.items()
        )
        
        # For adsorbates, subtract slab energy
        if phase_type == 'ads':
            surface = row.get('surface_name', None)
            site = row.get('site_name', None)
            
            if surface is not None:
                slab_energy = self._get_slab_energy(surface, site)
                if slab_energy is not None:
                    formation_energy = corrected_energy - slab_energy - ref_contribution
                else:
                    warnings.warn(f"Slab energy not found for {species} on {surface}, {site}")
                    formation_energy = None
            else:
                warnings.warn(f"No surface information for adsorbate {species}")
                formation_energy = None
        else:
            # For gas phase, liquid phase, and slab
            if phase_type == 'slab' or species.lower() == 'slab':
                formation_energy = 0.0
            else:
                # Gas and liquid phases use the same calculation
                formation_energy = corrected_energy - ref_contribution
        
        return formation_energy
    
    def calculate_formation_energies(self):
        """
        Calculate formation energies for all species in the dataset.
        Adds a 'formation_energy' column to the DataFrame.
        """
        # Step 1: Extract elements
        print("Step 1: Extracting elements from species...")
        self.elements = self._extract_elements()
        print(f"Found elements: {', '.join(self.elements)}")
        
        # Step 2: Calculate reference energies
        print("\nStep 2: Calculating reference energies...")
        self._calculate_reference_energies()
        
        # Step 3: Calculate formation energies for all rows
        print("\nStep 3: Calculating formation energies...")
        self.df['formation_energy'] = self.df.apply(
            self._calculate_formation_energy_for_row,
            axis=1
        )
        
        # Count how many were successfully calculated
        calculated = self.df['formation_energy'].notna().sum()
        total = len(self.df)
        print(f"\nSuccessfully calculated formation energies for {calculated}/{total} entries")
        
        return self
    
    def save(self, filepath: str, format: Optional[str] = None):
        """
        Save the DataFrame with formation energies to a file.
        
        Args:
            filepath: Output file path
            format: File format ('tsv', 'csv', 'excel'). If None, inferred from filepath
        """
        filepath = Path(filepath)
        
        if format is None:
            format = filepath.suffix.lower().replace('.', '')
        
        if format == 'tsv':
            self.df.to_csv(filepath, sep='\t', index=False)
        elif format == 'csv':
            self.df.to_csv(filepath, index=False)
        elif format in ['xlsx', 'xls', 'excel']:
            self.df.to_excel(filepath, index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        print(f"\nSaved results to: {filepath}")
    
    def display(self, n: int = 10):
        """
        Display the DataFrame with formation energies.
        
        Args:
            n: Number of rows to display (default: 10, use None for all)
        """
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)
        
        if n is None:
            print(self.df)
        else:
            print(self.df.head(n))
        
        print(f"\nTotal entries: {len(self.df)}")
        print(f"Entries with formation energy: {self.df['formation_energy'].notna().sum()}")
    
    def to_db(self) -> pd.DataFrame:
        """
        Return the DataFrame for use as a database.
        
        Returns:
            DataFrame with all data including formation energies
        """
        return self.df.copy()
    
    def debug_info(self):
        """
        Print debugging information about the loaded data.
        Useful for troubleshooting issues.
        """
        print("="*80)
        print("DEBUG INFORMATION")
        print("="*80)
        print(f"\nDataFrame shape: {self.df.shape}")
        print(f"Columns: {list(self.df.columns)}")
        print(f"\nFirst 5 rows:")
        print(self.df.head())
        print(f"\nData types:")
        print(self.df.dtypes)
        
        # Check if correction was applied
        if 'correction_energy' in self.df.columns:
            print(f"\n✓ Correction energy applied")
            print(f"  Correction range: {self.df['correction_energy'].min():.6f} to {self.df['correction_energy'].max():.6f} eV")
        else:
            print(f"\n✗ No correction energy column found")
        
        print(f"\nUnique values in 'type' column:")
        print(self.df['type'].unique())
        print(f"\nValue counts for 'type':")
        print(self.df['type'].value_counts())
        print(f"\nUnique species names (first 20):")
        print(list(self.df['species_name'].unique())[:20])
        
        # Show reference species with corrected energy
        cols_to_show = ['species_name', 'type', 'raw_energy']
        if 'correction_energy' in self.df.columns:
            cols_to_show.append('correction_energy')
        if 'corrected_energy' in self.df.columns:
            cols_to_show.append('corrected_energy')
        
        print(f"\nSpecies with 'H2' in name:")
        h2_df = self.df[self.df['species_name'].str.contains('H2', case=False, na=False)]
        if not h2_df.empty:
            print(h2_df[cols_to_show])
        
        print(f"\nSpecies with 'H2O' in name:")
        h2o_df = self.df[self.df['species_name'].str.contains('H2O', case=False, na=False)]
        if not h2o_df.empty:
            print(h2o_df[cols_to_show])
        
        print(f"\nSpecies with 'CO2' in name:")
        co2_df = self.df[self.df['species_name'].str.contains('CO2', case=False, na=False)]
        if not co2_df.empty:
            print(co2_df[cols_to_show])
        
        print("="*80)
    
    def get_summary_statistics(self) -> pd.DataFrame:
        """
        Get summary statistics grouped by type.
        
        Returns:
            DataFrame with statistics
        """
        if 'formation_energy' not in self.df.columns:
            raise ValueError("Formation energies not calculated yet. Run calculate_formation_energies() first.")
        
        stats = self.df.groupby('type')['formation_energy'].agg([
            'count', 'mean', 'std', 'min', 'max'
        ]).round(4)
        
        return stats
    
    def filter_by_type(self, phase_type: str) -> pd.DataFrame:
        """
        Filter data by phase type.
        
        Args:
            phase_type: Type to filter by ('gas', 'ads', 'slab')
        
        Returns:
            Filtered DataFrame
        """
        return self.df[self.df['type'].str.lower() == phase_type.lower()].copy()
    
    def filter_by_surface(self, surface_name: str) -> pd.DataFrame:
        """
        Filter data by surface name.
        
        Args:
            surface_name: Surface to filter by
        
        Returns:
            Filtered DataFrame
        """
        if 'surface_name' not in self.df.columns:
            raise ValueError("surface_name column not found in dataset")
        
        return self.df[self.df['surface_name'] == surface_name].copy()


def calculate_formation_energy(
    filepath: str,
    output_filepath: Optional[str] = None,
    display: bool = True,
    save_format: str = 'tsv',
    sheet_name: Optional[str] = None
) -> FormationEnergyCalculator:
    """
    Convenience function to calculate formation energies in one step.
    
    Args:
        filepath: Input file path (TSV, CSV, or Excel)
        output_filepath: Optional output file path. If None, uses input name with '_formation' suffix
        display: Whether to display results (default: True)
        save_format: Output format ('tsv', 'csv', 'excel')
        sheet_name: Optional sheet name for Excel files (default: 'BEEF-vdW' or first sheet)
    
    Returns:
        FormationEnergyCalculator instance with calculated energies
    
    Example:
        >>> calc = calculate_formation_energy('data.xlsx', 'output.tsv')
        >>> db = calc.to_db()
    """
    # Initialize calculator
    calc = FormationEnergyCalculator(filepath, sheet_name=sheet_name)
    
    # Calculate formation energies
    calc.calculate_formation_energies()
    
    # Display results
    if display:
        calc.display()
    
    # Save if output path provided
    if output_filepath is None:
        input_path = Path(filepath)
        output_filepath = input_path.parent / f"{input_path.stem}_formation.{save_format}"
    
    calc.save(output_filepath, format=save_format)
    
    return calc


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        
        calc = calculate_formation_energy(input_file, output_file)
    else:
        print("Usage: python formation_energy.py <input_file> [output_file]")
        print("\nExample:")
        print("  python formation_energy.py data.xlsx output.tsv")
