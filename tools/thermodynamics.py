"""
Thermodynamics module for calculating thermochemical properties from vibrational frequencies.
Can be used with frequency data from playground.data.freq module.

Usage:
------
from playground.data import freq
from playground.tools import thermodynamics as thermo

# Load frequency data
data = freq.FrequencyData()
freqs = data.get_freq('CO2', reference='Ara')

# Calculate thermodynamics
gas = thermo.IdealGas(freqs, species='CO2', symmetrynumber=2, geometry='linear')
props = gas.get_properties(temperature=300, pressure=1e5)
print(props)

# Or use convenience functions
props = thermo.calc_gas_thermo('CO2', freqs, T=300, P=1e5)
props = thermo.calc_ads_thermo(freqs, T=300)
"""

from ase import units
from ase.thermochemistry import HarmonicThermo, IdealGasThermo
import numpy as np
from typing import List, Dict, Optional, Union, Tuple
import warnings

warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

# Try to import catmap for molecule geometry
try:
    import catmap
    HAS_CATMAP = True
except ImportError:
    HAS_CATMAP = False


# Default ideal gas parameters: [symmetrynumber, geometry, spin]
IDEAL_GAS_PARAMS = {
    'H2': [2, 'linear', 0],
    'N2': [2, 'linear', 0],
    'O2': [2, 'linear', 1.0],
    'H2O': [2, 'nonlinear', 0],
    'CO': [1, 'linear', 0],
    'CO2': [2, 'linear', 0],
    'CH4': [12, 'nonlinear', 0],
    'NH3': [3, 'nonlinear', 0],
    'CH3OH': [1, 'nonlinear', 0],
    'CH2O': [2, 'nonlinear', 0],
    'HCOOH': [1, 'nonlinear', 0],
    'HCOO': [1, 'nonlinear', 0],
    'C2H2': [2, 'linear', 0],
    'C2H4': [4, 'nonlinear', 0],
    'C2H6': [6, 'nonlinear', 0],
    'C3H6': [1, 'nonlinear', 0],
    'C3H8': [2, 'nonlinear', 0],
    'CH3CHO': [1, 'nonlinear', 0],
    'CH3COOH': [1, 'nonlinear', 0],
    'CH3CH2OH': [1, 'nonlinear', 0],
    'HCl': [1, 'linear', 0],
    'Cl2': [2, 'linear', 0],
}


def cm_to_eV(freq_cm: float) -> float:
    """Convert wavenumber (cm^-1) to energy (eV)."""
    return freq_cm * 1.2398e-4


def eV_to_cm(energy_eV: float) -> float:
    """Convert energy (eV) to wavenumber (cm^-1)."""
    return energy_eV / 1.2398e-4


def filter_real_frequencies(frequencies: List[float], threshold: float = 1e-6) -> List[float]:
    """
    Filter out imaginary (negative) and near-zero frequencies.
    
    Parameters:
    -----------
    frequencies : list of float
        Vibrational frequencies in eV
    threshold : float
        Minimum frequency to consider (eV)
        
    Returns:
    --------
    list of float
        Real positive frequencies
    """
    return [f for f in frequencies if f > threshold]


class ThermoProperties:
    """Container for thermodynamic properties."""
    
    def __init__(self, **kwargs):
        """Initialize with thermodynamic properties."""
        self.temperature = kwargs.get('temperature', None)
        self.pressure = kwargs.get('pressure', None)
        self.frequencies = kwargs.get('frequencies', None)
        self.ZPE = kwargs.get('ZPE', None)
        self.U = kwargs.get('U', None)
        self.H = kwargs.get('H', None)
        self.S = kwargs.get('S', None)
        self.F = kwargs.get('F', None)
        self.G = kwargs.get('G', None)
        self.Cv = kwargs.get('Cv', None)
        self.Cp = kwargs.get('Cp', None)
        self.status = kwargs.get('status', None)
    
    def __repr__(self):
        lines = [f"ThermoProperties(T={self.temperature}K"]
        if self.pressure:
            lines.append(f", P={self.pressure:.2e}Pa")
        lines.append(f", status={self.status})")
        return "".join(lines)
    
    def __str__(self):
        """Pretty print thermodynamic properties."""
        lines = ["=" * 60]
        lines.append(f"Thermodynamic Properties ({self.status})")
        lines.append("=" * 60)
        lines.append(f"Temperature: {self.temperature:.2f} K")
        if self.pressure:
            lines.append(f"Pressure: {self.pressure} Pa")
        if self.frequencies:
            lines.append(f"Number of frequencies: {len(self.frequencies)}")
        lines.append("")
        lines.append("Energy corrections (eV):")
        lines.append(f"  ZPE (Zero-point energy):      {self.ZPE:.6f}")
        if self.Cp is not None:
            lines.append(f"  Cp (Heat capacity):           {self.Cp:.6f}")
        if self.Cv is not None:
            lines.append(f"  Cv (Heat capacity):           {self.Cv:.6f}")
        lines.append("")
        if self.H is not None:
            lines.append(f"Enthalpy (H):                   {self.H:.6f} eV")
        if self.U is not None:
            lines.append(f"Internal energy (U):            {self.U:.6f} eV")
        lines.append(f"Entropy (S):                    {self.S:.8f} eV/K")
        lines.append(f"TS:                             {self.temperature * self.S:.6f} eV")
        if self.G is not None:
            lines.append(f"Gibbs free energy (G):          {self.G:.6f} eV")
        if self.F is not None:
            lines.append(f"Helmholtz free energy (F):      {self.F:.6f} eV")
        lines.append("=" * 60)
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'temperature': self.temperature,
            'pressure': self.pressure,
            'frequencies': self.frequencies,
            'ZPE': self.ZPE,
            'U': self.U,
            'H': self.H,
            'S': self.S,
            'F': self.F,
            'G': self.G,
            'Cv': self.Cv,
            'Cp': self.Cp,
            'status': self.status
        }


class IdealGas:
    """
    Ideal gas thermochemistry calculator.
    
    Usage:
    ------
    gas = IdealGas(frequencies, species='CO2', symmetrynumber=2, geometry='linear')
    props = gas.get_properties(temperature=300, pressure=1e5)
    """
    
    def __init__(self, 
                 frequencies: List[float],
                 species: Optional[str] = None,
                 atoms=None,
                 symmetrynumber: Optional[int] = None,
                 geometry: Optional[str] = None,
                 spin: float = 0):
        """
        Initialize ideal gas thermochemistry.
        
        Parameters:
        -----------
        frequencies : list of float
            Vibrational frequencies in cm^-1
        species : str, optional
            Species name (e.g., 'CO2'). If provided and in IDEAL_GAS_PARAMS,
            symmetrynumber and geometry are auto-filled
        atoms : ase.Atoms, optional
            Atoms object for molecular geometry
        symmetrynumber : int, optional
            Rotational symmetry number (default: 1)
        geometry : str, optional
            'linear', 'nonlinear', or 'monatomic' (default: 'nonlinear')
        spin : float
            Electronic spin (default: 0)
        """
        self.frequencies = frequencies
        self.species = species
        self.spin = spin
        
        # Auto-fill parameters if species is known
        if species and species in IDEAL_GAS_PARAMS:
            params = IDEAL_GAS_PARAMS[species]
            self.symmetrynumber = symmetrynumber if symmetrynumber is not None else params[0]
            self.geometry = geometry or params[1]
            self.spin = params[2] if len(params) > 2 else spin
        else:
            self.symmetrynumber = symmetrynumber if symmetrynumber is not None else 1
            self.geometry = geometry or 'nonlinear'
        
        # Create a dummy atoms object if not provided and needed
        if atoms is None and HAS_CATMAP and species:
            try:
                from catmap import molecule
                self.atoms = molecule(species)
            except Exception:
                # Create a minimal dummy atoms object for ASE thermochemistry
                from ase import Atoms
                # Rough atomic masses for common elements
                mass_map = {'H': 1.008, 'C': 12.011, 'N': 14.007, 'O': 15.999, 'S': 32.06}
                
                # Parse simple formulas (e.g., CO2, H2O, CH4)
                if species:
                    # Simple parser for common molecules
                    import re
                    masses = []
                    for match in re.finditer(r'([A-Z][a-z]?)(\d*)', species):
                        element = match.group(1)
                        count = int(match.group(2)) if match.group(2) else 1
                        if element in mass_map:
                            masses.extend([mass_map[element]] * count)
                    
                    if masses:
                        # Create dummy atoms with approximate positions
                        positions = [[0, 0, i * 1.5] for i in range(len(masses))]
                        self.atoms = Atoms(symbols='H' * len(masses), positions=positions)
                        self.atoms.set_masses(masses)
                    else:
                        self.atoms = None
                else:
                    self.atoms = None
        else:
            self.atoms = atoms
        
        # Convert frequencies to eV if needed (assume cm^-1 if > 10)
        if frequencies and max(frequencies) > 10:
            self.frequencies_eV = [cm_to_eV(f) for f in frequencies]
        else:
            self.frequencies_eV = frequencies
        
        # Filter real frequencies
        self.vib_energies = filter_real_frequencies(self.frequencies_eV)
        
        if not self.vib_energies:
            raise ValueError("No real positive frequencies for thermochemistry")
    
    def get_properties(self, temperature: float = 298.15, pressure: float = 101325) -> ThermoProperties:
        """
        Calculate thermodynamic properties at given T and P.
        
        Parameters:
        -----------
        temperature : float
            Temperature in Kelvin (default: 298.15)
        pressure : float
            Pressure in Pascal (default: 101325 = 1 atm)
            
        Returns:
        --------
        ThermoProperties
            Object containing all thermodynamic properties
        """
        thermo = IdealGasThermo(
            self.vib_energies,
            self.geometry,
            atoms=self.atoms,
            symmetrynumber=self.symmetrynumber,
            spin=self.spin
        )
        
        ZPE = thermo.get_ZPE_correction()
        H = thermo.get_enthalpy(temperature, verbose=False)
        S = thermo.get_entropy(temperature, pressure, verbose=False)
        G = H - temperature * S
        Cp = H - ZPE
        
        return ThermoProperties(
            temperature=temperature,
            pressure=pressure,
            frequencies=self.frequencies,
            ZPE=ZPE,
            H=H,
            S=S,
            G=G,
            Cp=Cp,
            status='gas'
        )
    
    def get_free_energy(self, temperature: float = 298.15, pressure: float = 101325) -> float:
        """Get Gibbs free energy correction (ZPE + Cp - TS) in eV."""
        props = self.get_properties(temperature, pressure)
        return props.G
    
    def get_enthalpy(self, temperature: float = 298.15) -> float:
        """Get enthalpy correction (ZPE + Cp) in eV."""
        props = self.get_properties(temperature)
        return props.H
    
    def get_entropy(self, temperature: float = 298.15, pressure: float = 101325) -> float:
        """Get entropy in eV/K."""
        props = self.get_properties(temperature, pressure)
        return props.S


class Adsorbate:
    """
    Adsorbate thermochemistry calculator using harmonic approximation.
    
    Usage:
    ------
    ads = Adsorbate(frequencies)
    props = ads.get_properties(temperature=300)
    """
    
    def __init__(self, frequencies: List[float]):
        """
        Initialize adsorbate thermochemistry.
        
        Parameters:
        -----------
        frequencies : list of float
            Vibrational frequencies in cm^-1 or eV
        """
        self.frequencies = frequencies
        
        # Convert frequencies to eV if needed (assume cm^-1 if > 10)
        if frequencies and max(frequencies) > 10:
            self.frequencies_eV = [cm_to_eV(f) for f in frequencies]
        else:
            self.frequencies_eV = frequencies
        
        # Filter real frequencies
        self.vib_energies = filter_real_frequencies(self.frequencies_eV)
        
        if not self.vib_energies:
            raise ValueError("No real positive frequencies for thermochemistry")
    
    def get_properties(self, temperature: float = 298.15) -> ThermoProperties:
        """
        Calculate thermodynamic properties at given T.
        
        Parameters:
        -----------
        temperature : float
            Temperature in Kelvin (default: 298.15)
            
        Returns:
        --------
        ThermoProperties
            Object containing all thermodynamic properties
        """
        thermo = HarmonicThermo(self.vib_energies)
        
        ZPE = thermo.get_ZPE_correction()
        U = thermo.get_internal_energy(temperature, verbose=False)
        S = thermo.get_entropy(temperature, verbose=False)
        F = thermo.get_helmholtz_energy(temperature, verbose=False)
        Cv = U - ZPE
        
        return ThermoProperties(
            temperature=temperature,
            frequencies=self.frequencies,
            ZPE=ZPE,
            U=U,
            S=S,
            F=F,
            Cv=Cv,
            status='ads'
        )
    
    def get_free_energy(self, temperature: float = 298.15) -> float:
        """Get Helmholtz free energy correction (ZPE + Cv - TS) in eV."""
        props = self.get_properties(temperature)
        return props.F
    
    def get_internal_energy(self, temperature: float = 298.15) -> float:
        """Get internal energy correction (ZPE + Cv) in eV."""
        props = self.get_properties(temperature)
        return props.U
    
    def get_entropy(self, temperature: float = 298.15) -> float:
        """Get entropy in eV/K."""
        props = self.get_properties(temperature)
        return props.S


# Convenience functions

def calc_gas_thermo(species: str, 
                   frequencies: List[float],
                   T: float = 298.15,
                   P: float = 101325,
                   **kwargs) -> ThermoProperties:
    """
    Calculate gas phase thermochemistry.
    
    Parameters:
    -----------
    species : str
        Species name (e.g., 'CO2', 'H2O')
    frequencies : list of float
        Vibrational frequencies in cm^-1
    T : float
        Temperature in K (default: 298.15)
    P : float
        Pressure in Pa (default: 101325 = 1 atm)
    **kwargs : 
        Additional parameters for IdealGas (symmetrynumber, geometry, etc.)
        
    Returns:
    --------
    ThermoProperties
        Thermodynamic properties
        
    Example:
    --------
    from playground.data import freq
    from playground.tools import thermodynamics as thermo
    
    data = freq.FrequencyData()
    freqs = data.get_freq('CO2', reference='Ara')
    props = thermo.calc_gas_thermo('CO2', freqs, T=298.15, P=101325)
    """
    gas = IdealGas(frequencies, species=species, **kwargs)
    return gas.get_properties(T, P)


def calc_ads_thermo(frequencies: List[float],
                   T: float = 298.15) -> ThermoProperties:
    """
    Calculate adsorbate thermochemistry.
    
    Parameters:
    -----------
    frequencies : list of float
        Vibrational frequencies in cm^-1
    T : float
        Temperature in K (default: 298.15)
        
    Returns:
    --------
    ThermoProperties
        Thermodynamic properties
        
    Example:
    --------
    from playground.data import freq
    from playground.tools import thermodynamics as thermo
    
    data = freq.FrequencyData()
    freqs = data.get_freq('CO', reference='PengRole2020', status='ads')
    props = thermo.calc_ads_thermo(freqs, T=298.15)
    """
    ads = Adsorbate(frequencies)
    return ads.get_properties(T)


def calc_equilibrium_potential(deltaG: float, n_electrons: int = 1) -> float:
    """
    Calculate equilibrium potential from reaction free energy.
    
    Parameters:
    -----------
    deltaG : float
        Reaction free energy in eV
    n_electrons : int
        Number of electrons transferred (default: 1)
        
    Returns:
    --------
    float
        Equilibrium potential in V vs. reference
        
    Example:
    --------
    # CO2 + 2H+ + 2e- -> CO + H2O
    U_eq = thermo.calc_equilibrium_potential(deltaG, n_electrons=2)
    """
    return -deltaG / n_electrons


def calc_reaction_free_energy(species_thermo: Dict[str, ThermoProperties],
                              stoichiometry: Dict[str, float],
                              E_electronic: Dict[str, float]) -> float:
    """
    Calculate reaction free energy from species thermochemistry.
    
    Parameters:
    -----------
    species_thermo : dict
        Dictionary of species name -> ThermoProperties
    stoichiometry : dict
        Dictionary of species name -> stoichiometric coefficient
        (positive for products, negative for reactants)
    E_electronic : dict
        Dictionary of species name -> electronic energy (eV)
        
    Returns:
    --------
    float
        Reaction free energy in eV
        
    Example:
    --------
    # CO2 -> CO + O*
    species_thermo = {
        'CO2': co2_props,
        'CO': co_props,
        'O': o_props
    }
    stoichiometry = {'CO2': -1, 'CO': 1, 'O': 1}
    E_electronic = {'CO2': -22.5, 'CO': -14.3, 'O': -1.8}
    deltaG = thermo.calc_reaction_free_energy(species_thermo, stoichiometry, E_electronic)
    """
    deltaG = 0.0
    
    for species, coeff in stoichiometry.items():
        if species not in species_thermo or species not in E_electronic:
            raise KeyError(f"Species {species} not found in input dictionaries")
        
        props = species_thermo[species]
        E_elec = E_electronic[species]
        
        # G = E_electronic + ZPE + thermal corrections
        if props.G is not None:
            G_total = E_elec + props.G
        elif props.F is not None:
            G_total = E_elec + props.F
        else:
            raise ValueError(f"No free energy data for species {species}")
        
        deltaG += coeff * G_total
    
    return deltaG


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("Thermodynamics Module Examples")
    print("=" * 70)
    print()
    
    # Example 1: CO2 gas phase
    print("Example 1: CO2 gas phase thermochemistry")
    print("-" * 70)
    co2_freqs = [649.6, 651.3, 1339.3, 2365.1]  # cm^-1
    co2_gas = IdealGas(co2_freqs, species='CO2')
    co2_props = co2_gas.get_properties(T=298.15, P=101325)
    print(co2_props)
    print()
    
    # Example 2: H adsorbate
    print("Example 2: H adsorbate thermochemistry")
    print("-" * 70)
    h_freqs = [459.5, 563.0, 995.3]  # cm^-1
    h_ads = Adsorbate(h_freqs)
    h_props = h_ads.get_properties(T=298.15)
    print(h_props)
    print()
    
    # Example 3: Using convenience functions
    print("Example 3: Using convenience functions")
    print("-" * 70)
    props = calc_gas_thermo('H2O', [1614.4, 3736.9, 3847.9])  # Uses default T=298.15K, P=101325Pa
    print(f"H2O Gibbs free energy correction: {props.G:.4f} eV")
    print(f"H2O Entropy: {props.S:.6f} eV/K")
    print()
    
    # Example 4: Species not in IDEAL_GAS_PARAMS (uses defaults)
    print("Example 4: Unknown species (uses default symmetry=1, geometry='nonlinear')")
    print("-" * 70)
    unknown_freqs = [500, 1000, 1500, 2000]  # cm^-1
    props = calc_gas_thermo('UnknownMolecule', unknown_freqs, symmetrynumber=1, geometry='linear')
    print(f"Free energy correction: {props.G:.4f} eV")
    print()
    
    # Example 5: Equilibrium potential
    print("Example 5: Calculate equilibrium potential")
    print("-" * 70)
    deltaG_reaction = -0.5  # eV
    U_eq = calc_equilibrium_potential(deltaG_reaction, n_electrons=2)
    print(f"Reaction free energy: {deltaG_reaction:.3f} eV")
    print(f"Equilibrium potential: {U_eq:.3f} V")
    print()
