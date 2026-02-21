"""
Data Loader Module

This module provides easy access to energy data from TSV files in the data directory.
It automatically calculates formation energies and provides a simple interface for
importing and using the data throughout the project.

Usage:
    from data.load_data import load_data, get_formation_energy, get_species_data
    
    # Load BEEF-vdW data
    df = load_data('BEEF-vdW')
    
    # Get formation energy for a specific species
    energy = get_formation_energy('BEEF-vdW', 'CH4')
    
    # Get all data for a specific species
    species_data = get_species_data('BEEF-vdW', 'CH4')
    
    # Load and cache multiple datasets
    beef_df = load_data('BEEF-vdW')
    # other_df = load_data('other-functional')
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Union
import sys

# Add parent directory to path to import formation_energy module
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from tools.formation_energy import FormationEnergyCalculator

# Cache for loaded datasets to avoid recalculation
_DATA_CACHE: Dict[str, pd.DataFrame] = {}

# Path to data directory
DATA_DIR = Path(__file__).parent


def load_data(dataset_name: str, force_reload: bool = False) -> pd.DataFrame:
    """
    Load energy data from a TSV file and calculate formation energies.
    
    Args:
        dataset_name: Name of the dataset (e.g., 'BEEF-vdW', 'PBE', etc.)
                     The function will look for '{dataset_name}.tsv' in the data directory
        force_reload: If True, reload data even if cached (default: False)
    
    Returns:
        DataFrame with all energy data including calculated formation energies
    
    Example:
        >>> df = load_data('BEEF-vdW')
        >>> print(df.columns)
        >>> ch4_data = df[df['species_name'] == 'CH4']
    """
    # Check cache first
    if not force_reload and dataset_name in _DATA_CACHE:
        #print(f"Loading {dataset_name} from cache...")
        return _DATA_CACHE[dataset_name].copy()
    
    # Construct file path
    filepath = DATA_DIR / f"{dataset_name}.tsv"
    
    if not filepath.exists():
        raise FileNotFoundError(
            f"Dataset '{dataset_name}' not found. "
            f"Looking for: {filepath}\n"
            f"Available datasets: {list_available_datasets()}"
        )
    
    print(f"Loading {dataset_name} from {filepath}...")
    
    # Load and calculate formation energies
    calc = FormationEnergyCalculator(str(filepath))
    calc.calculate_formation_energies()
    
    # Cache the result
    _DATA_CACHE[dataset_name] = calc.to_db()
    
    print(f"✓ {dataset_name} loaded successfully ({len(_DATA_CACHE[dataset_name])} entries)")
    
    return _DATA_CACHE[dataset_name].copy()


def get_formation_energy(
    dataset_name: str,
    species_name: str,
    surface_name: Optional[str] = None,
    site_name: Optional[str] = None
) -> Optional[float]:
    """
    Get the formation energy for a specific species.
    
    Args:
        dataset_name: Name of the dataset (e.g., 'BEEF-vdW')
        species_name: Name of the species (e.g., 'CH4', 'H2O')
        surface_name: Optional surface name for adsorbates
        site_name: Optional site name for adsorbates
    
    Returns:
        Formation energy in eV, or None if not found
    
    Example:
        >>> energy = get_formation_energy('BEEF-vdW', 'CH4')
        >>> print(f"Formation energy of CH4: {energy:.4f} eV")
    """
    df = load_data(dataset_name)
    
    # Filter by species name
    filtered = df[df['species_name'] == species_name]
    
    # Further filter by surface and site if provided
    if surface_name is not None and 'surface_name' in df.columns:
        filtered = filtered[filtered['surface_name'] == surface_name]
    
    if site_name is not None and 'site_name' in df.columns:
        filtered = filtered[filtered['site_name'] == site_name]
    
    if filtered.empty:
        print(f"Warning: Species '{species_name}' not found in {dataset_name}")
        return None
    
    if len(filtered) > 1:
        print(f"Warning: Multiple entries found for '{species_name}'. Returning first match.")
    
    return filtered.iloc[0]['formation_energy']


def get_species_data(
    dataset_name: str,
    species_name: str,
    surface_name: Optional[str] = None,
    site_name: Optional[str] = None
) -> Optional[pd.Series]:
    """
    Get all data for a specific species.
    
    Args:
        dataset_name: Name of the dataset (e.g., 'BEEF-vdW')
        species_name: Name of the species (e.g., 'CH4', 'H2O')
        surface_name: Optional surface name for adsorbates
        site_name: Optional site name for adsorbates
    
    Returns:
        Series with all data for the species, or None if not found
    
    Example:
        >>> data = get_species_data('BEEF-vdW', 'CH4')
        >>> print(f"Raw energy: {data['raw_energy']:.4f} eV")
        >>> print(f"Formation energy: {data['formation_energy']:.4f} eV")
    """
    df = load_data(dataset_name)
    
    # Filter by species name
    filtered = df[df['species_name'] == species_name]
    
    # Further filter by surface and site if provided
    if surface_name is not None and 'surface_name' in df.columns:
        filtered = filtered[filtered['surface_name'] == surface_name]
    
    if site_name is not None and 'site_name' in df.columns:
        filtered = filtered[filtered['site_name'] == site_name]
    
    if filtered.empty:
        print(f"Warning: Species '{species_name}' not found in {dataset_name}")
        return None
    
    if len(filtered) > 1:
        print(f"Warning: Multiple entries found for '{species_name}'. Returning first match.")
    
    return filtered.iloc[0]


def get_species_list(dataset_name: str, phase_type: Optional[str] = None) -> list:
    """
    Get list of all species in a dataset.
    
    Args:
        dataset_name: Name of the dataset (e.g., 'BEEF-vdW')
        phase_type: Optional filter by type ('gas', 'liquid', 'ads', 'slab')
    
    Returns:
        List of species names
    
    Example:
        >>> gas_species = get_species_list('BEEF-vdW', 'gas')
        >>> print(f"Gas phase species: {', '.join(gas_species)}")
    """
    df = load_data(dataset_name)
    
    if phase_type is not None:
        df = df[df['type'].str.lower() == phase_type.lower()]
    
    return sorted(df['species_name'].unique().tolist())


def list_available_datasets() -> list:
    """
    List all available datasets in the data directory.
    
    Returns:
        List of dataset names (without .tsv extension)
    
    Example:
        >>> datasets = list_available_datasets()
        >>> print(f"Available datasets: {', '.join(datasets)}")
    """
    tsv_files = list(DATA_DIR.glob("*.tsv"))
    return [f.stem for f in tsv_files]


def filter_by_type(dataset_name: str, phase_type: str) -> pd.DataFrame:
    """
    Get all species of a specific type from a dataset.
    
    Args:
        dataset_name: Name of the dataset (e.g., 'BEEF-vdW')
        phase_type: Type to filter by ('gas', 'liquid', 'ads', 'slab')
    
    Returns:
        Filtered DataFrame
    
    Example:
        >>> gas_df = filter_by_type('BEEF-vdW', 'gas')
        >>> print(f"Found {len(gas_df)} gas phase species")
    """
    df = load_data(dataset_name)
    return df[df['type'].str.lower() == phase_type.lower()].copy()


def get_reference_energies(dataset_name: str) -> Dict[str, float]:
    """
    Get the reference energies used for formation energy calculations.
    
    Args:
        dataset_name: Name of the dataset (e.g., 'BEEF-vdW')
    
    Returns:
        Dictionary mapping element symbols to reference energies
    
    Example:
        >>> refs = get_reference_energies('BEEF-vdW')
        >>> print(f"H reference: {refs['H']:.4f} eV")
        >>> print(f"O reference: {refs['O']:.4f} eV")
        >>> print(f"C reference: {refs['C']:.4f} eV")
    """
    # Load data to ensure calculator is initialized
    load_data(dataset_name)
    
    # Create a fresh calculator to get reference energies
    filepath = DATA_DIR / f"{dataset_name}.tsv"
    calc = FormationEnergyCalculator(str(filepath))
    calc.calculate_formation_energies()
    
    return calc.ref_energies.copy()


def clear_cache():
    """
    Clear the data cache to free memory.
    Use this if you've loaded large datasets and want to free up memory.
    
    Example:
        >>> load_data('BEEF-vdW')
        >>> # ... do some work ...
        >>> clear_cache()  # Free memory
    """
    global _DATA_CACHE
    _DATA_CACHE.clear()
    print("Data cache cleared")


# Convenience function for the most common use case
def load_beef_vdw() -> pd.DataFrame:
    """
    Convenience function to load BEEF-vdW data directly.
    
    Returns:
        DataFrame with BEEF-vdW data including formation energies
    
    Example:
        >>> from data.load_data import load_beef_vdw
        >>> df = load_beef_vdw()
    """
    return load_data('BEEF-vdW')


if __name__ == "__main__":
    # Demo usage
    print("=" * 80)
    print("Data Loader Demo")
    print("=" * 80)
    
    # List available datasets
    print("\nAvailable datasets:")
    for dataset in list_available_datasets():
        print(f"  - {dataset}")
    
    # Load BEEF-vdW data
    print("\n" + "=" * 80)
    df = load_data('BEEF-vdW')
    
    # Show some examples
    print("\n" + "=" * 80)
    print("Example: Get formation energy for CH4")
    ch4_energy = get_formation_energy('BEEF-vdW', 'CH4')
    print(f"  Formation energy of CH4: {ch4_energy:.4f} eV")
    
    print("\nExample: Get all data for H2O")
    h2o_data = get_species_data('BEEF-vdW', 'H2O')
    print(f"  Raw energy: {h2o_data['raw_energy']:.4f} eV")
    print(f"  Formation energy: {h2o_data['formation_energy']:.4f} eV")
    print(f"  Type: {h2o_data['type']}")
    
    print("\nExample: List all gas phase species")
    gas_species = get_species_list('BEEF-vdW', 'gas')
    print(f"  Gas phase species ({len(gas_species)}): {', '.join(gas_species[:5])}...")
    
    print("\nExample: Get reference energies")
    refs = get_reference_energies('BEEF-vdW')
    for elem, energy in refs.items():
        print(f"  E_ref({elem}) = {energy:.6f} eV")
    
    print("\n" + "=" * 80)
    print("✓ Demo complete!")
    print("=" * 80)
