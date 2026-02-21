import pandas as pd
import ast
import os
from typing import Optional, List, Union
import numpy as np


class FrequencyData:
    """
    Class for loading and querying frequency data.
    
    Usage:
    ------
    from playground.data import freq
    
    # Load data once
    data = freq.FrequencyData()
    
    # Query examples
    co2_freqs = data.get('CO2')
    ara_co2 = data.get('CO2', reference='Ara')
    gas_species = data.get_gas()
    ads_species = data.get_ads()
    
    # Get frequency list directly
    freqs = data.get_freq('CO2', reference='Ara')
    
    # Search and filter
    all_ara = data.filter(reference='Ara')
    gas_only = data.filter(status='gas')
    """
    
    def __init__(self, filepath='frequencies.csv'):
        """
        Initialize and load frequency data.
        
        Parameters:
        -----------
        filepath : str
            Path to the CSV file (default: 'frequencies.csv')
        """
        self._load_data(filepath)
    
    def _load_data(self, filepath):
        """Load and parse the CSV file."""
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # If filepath is relative, make it relative to this script's directory
        if not os.path.isabs(filepath):
            filepath = os.path.join(script_dir, filepath)
        
        # Load the CSV file
        self.df = pd.read_csv(filepath)
        
        # Convert the frequencies column from string to list
        self.df['frequencies'] = self.df['frequencies'].apply(
            lambda x: ast.literal_eval(x) if pd.notna(x) and x.strip() else []
        )
        
        # Add number of frequencies column for convenience
        self.df['num_freqs'] = self.df['frequencies'].apply(len)
    
    def get(self, species: str, reference: Optional[str] = None, 
            status: Optional[str] = None) -> pd.DataFrame:
        """
        Get frequency data for a specific species.
        
        Parameters:
        -----------
        species : str
            Species name (e.g., 'CO2', 'CH4', 'H2O')
        reference : str, optional
            Reference name (e.g., 'Ara', 'PengRole2020')
        status : str, optional
            Status ('gas' or 'ads')
            
        Returns:
        --------
        pd.DataFrame
            Filtered data
            
        Examples:
        ---------
        data.get('CO2')
        data.get('CO2', reference='Ara')
        data.get('H', status='ads')
        """
        mask = self.df['species_name'] == species
        
        if reference is not None:
            mask &= self.df['reference'] == reference
        
        if status is not None:
            mask &= self.df['status'] == status
        
        return self.df[mask].copy()
    
    def get_freq(self, species: str, reference: Optional[str] = None, 
                 status: Optional[str] = None) -> List[float]:
        """
        Get frequency list directly for a species.
        Returns the first match if multiple entries exist.
        
        Parameters:
        -----------
        species : str
            Species name
        reference : str, optional
            Reference name
        status : str, optional
            Status ('gas' or 'ads')
            
        Returns:
        --------
        list of float
            List of frequencies, or empty list if not found
            
        Examples:
        ---------
        freqs = data.get_freq('CO2', reference='Ara')
        """
        result = self.get(species, reference, status)
        
        if len(result) == 0:
            return []
        
        return result.iloc[0]['frequencies']
    
    def filter(self, reference: Optional[str] = None, 
               status: Optional[str] = None,
               species_list: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Filter data by reference, status, or species list.
        
        Parameters:
        -----------
        reference : str, optional
            Reference name
        status : str, optional
            Status ('gas' or 'ads')
        species_list : list of str, optional
            List of species names to include
            
        Returns:
        --------
        pd.DataFrame
            Filtered data
            
        Examples:
        ---------
        data.filter(reference='Ara')
        data.filter(status='gas')
        data.filter(reference='Ara', status='gas')
        data.filter(species_list=['CO2', 'H2O', 'CH4'])
        """
        mask = pd.Series([True] * len(self.df), index=self.df.index)
        
        if reference is not None:
            mask &= self.df['reference'] == reference
        
        if status is not None:
            mask &= self.df['status'] == status
        
        if species_list is not None:
            mask &= self.df['species_name'].isin(species_list)
        
        return self.df[mask].copy()
    
    def get_gas(self, reference: Optional[str] = None) -> pd.DataFrame:
        """Get all gas phase species."""
        return self.filter(status='gas', reference=reference)
    
    def get_ads(self, reference: Optional[str] = None) -> pd.DataFrame:
        """Get all adsorbed species."""
        return self.filter(status='ads', reference=reference)
    
    def search(self, pattern: str, column: str = 'species_name') -> pd.DataFrame:
        """
        Search for species matching a pattern.
        
        Parameters:
        -----------
        pattern : str
            Search pattern (supports regex)
        column : str
            Column to search in (default: 'species_name')
            
        Returns:
        --------
        pd.DataFrame
            Matching entries
            
        Examples:
        ---------
        data.search('CO')  # Species containing 'CO'
        data.search('^C[0-9]')  # Species starting with C and a number
        """
        mask = self.df[column].str.contains(pattern, case=False, na=False)
        return self.df[mask].copy()
    
    @property
    def species(self) -> List[str]:
        """Get list of all unique species."""
        return sorted(self.df['species_name'].unique().tolist())
    
    @property
    def references(self) -> List[str]:
        """Get list of all unique references."""
        return sorted(self.df['reference'].unique().tolist())
    
    @property
    def gas_species(self) -> List[str]:
        """Get list of all gas phase species."""
        return sorted(self.df[self.df['status'] == 'gas']['species_name'].unique().tolist())
    
    @property
    def ads_species(self) -> List[str]:
        """Get list of all adsorbed species."""
        return sorted(self.df[self.df['status'] == 'ads']['species_name'].unique().tolist())
    
    def summary(self):
        """Print summary statistics."""
        print(f"Total entries: {len(self.df)}")
        print(f"\nReferences: {', '.join(self.references)}")
        print(f"Number of unique species: {self.df['species_name'].nunique()}")
        print(f"  - Gas phase: {len(self.gas_species)}")
        print(f"  - Adsorbed: {len(self.ads_species)}")
        print(f"\nStatus distribution:")
        print(self.df['status'].value_counts().to_string())
        print(f"\nFrequencies per entry:")
        print(self.df['num_freqs'].describe().to_string())
    
    def __repr__(self):
        return f"FrequencyData({len(self.df)} entries, {self.df['species_name'].nunique()} species)"
    
    def __len__(self):
        return len(self.df)


# Convenience function for backward compatibility
def load_frequencies(filepath='frequencies.csv'):
    """
    Load frequency data (returns DataFrame).
    For simpler usage, use FrequencyData class instead.
    """
    data = FrequencyData(filepath)
    return data.df

# Example usage
if __name__ == "__main__":
    # Load the data
    data = FrequencyData()
    
    # Print summary
    print("=" * 70)
    print("Frequency Data Summary")
    print("=" * 70)
    data.summary()
    
    # Example 1: Get CO2 frequencies
    print("\n" + "=" * 70)
    print("Example 1: Get CO2 frequencies")
    print("=" * 70)
    co2_data = data.get('CO2')
    print(co2_data[['reference', 'status', 'frequencies']])
    
    # Example 2: Get frequency list directly
    print("\n" + "=" * 70)
    print("Example 2: Get CO2 frequency list for Ara reference")
    print("=" * 70)
    freqs = data.get_freq('CO2', reference='Ara')
    print(f"Frequencies: {freqs}")
    print(f"Number of frequencies: {len(freqs)}")
    
    # Example 3: Get all gas phase species for Ara reference
    print("\n" + "=" * 70)
    print("Example 3: All gas phase species from Ara reference")
    print("=" * 70)
    ara_gas = data.filter(reference='Ara', status='gas')
    print(ara_gas[['species_name', 'num_freqs']])
    
    # Example 4: Search for species containing 'CO'
    print("\n" + "=" * 70)
    print("Example 4: Search for species containing 'CO'")
    print("=" * 70)
    co_species = data.search('CO')
    print(co_species[['species_name', 'reference', 'status']].drop_duplicates())
    
    # Example 5: Quick access to properties
    print("\n" + "=" * 70)
    print("Example 5: List all gas phase species")
    print("=" * 70)
    print(f"Gas species: {', '.join(data.gas_species)}")
    
    # Example 6: Get multiple species
    print("\n" + "=" * 70)
    print("Example 6: Get data for specific species list")
    print("=" * 70)
    selected = data.filter(species_list=['CO2', 'H2O', 'CH4'], status='gas')
    print(selected[['species_name', 'reference', 'num_freqs']])
