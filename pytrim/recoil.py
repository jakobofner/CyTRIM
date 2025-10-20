"""Recoil cascade simulation module.

This module extends the basic TRIM simulation to include secondary
collisions (recoil cascades) and damage calculation.
"""
import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Optional


@dataclass
class RecoilEvent:
    """Represents a single recoil event."""
    
    # Position where recoil occurred
    x: float
    y: float
    z: float
    
    # Recoil atom properties
    energy: float  # Kinetic energy of recoiled atom (eV)
    direction: Tuple[float, float, float]  # Direction vector
    
    # Collision partner info
    primary_energy: float  # Energy of primary before collision
    generation: int = 0  # Cascade generation (0=primary, 1=first recoil, etc.)


@dataclass
class DamageProfile:
    """Damage profile from ion implantation."""
    
    # Vacancy positions (displaced target atoms)
    vacancies: List[Tuple[float, float, float]] = field(default_factory=list)
    
    # Interstitial positions (recoiled atoms that stop)
    interstitials: List[Tuple[float, float, float]] = field(default_factory=list)
    
    # Replacement collisions (atom returns to near-original site)
    replacements: int = 0
    
    # Total deposited energy per depth bin
    deposited_energy: List[float] = field(default_factory=list)
    depth_bins: List[float] = field(default_factory=list)
    
    def get_total_damage(self) -> int:
        """Get total number of damage events (Frenkel pairs)."""
        return len(self.vacancies)
    
    def get_dpa_profile(self, target_atoms_per_angstrom3: float, 
                        zmin: float, zmax: float, nbins: int = 50) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate displacements per atom (DPA) vs depth.
        
        Parameters:
            target_atoms_per_angstrom3: Atomic density of target
            zmin, zmax: Depth range
            nbins: Number of bins
            
        Returns:
            (depth_centers, dpa_values)
        """
        if not self.vacancies:
            depth_centers = np.linspace(zmin, zmax, nbins)
            return depth_centers, np.zeros(nbins)
        
        # Extract z-coordinates of vacancies
        vacancy_depths = np.array([z for x, y, z in self.vacancies])
        
        # Create histogram
        bin_edges = np.linspace(zmin, zmax, nbins + 1)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        bin_width = bin_edges[1] - bin_edges[0]
        
        # Count vacancies per bin
        vacancy_counts, _ = np.histogram(vacancy_depths, bins=bin_edges)
        
        # Calculate volume per bin (assuming unit cross-section area)
        # Volume = area (1 Ų) * depth (bin_width)
        volume_per_bin = bin_width  # in Ų
        
        # Number of atoms per bin
        atoms_per_bin = target_atoms_per_angstrom3 * volume_per_bin
        
        # DPA = displacements / atoms
        dpa = vacancy_counts / atoms_per_bin
        
        return bin_centers, dpa


class RecoilCascadeSimulator:
    """Simulator for recoil cascades and damage calculation."""
    
    def __init__(self, 
                 displacement_energy: float = 25.0,  # Ed in eV
                 max_cascade_depth: int = 5,
                 min_recoil_energy: float = 10.0):  # Minimum energy to track
        """Initialize cascade simulator.
        
        Parameters:
            displacement_energy: Threshold energy to displace target atom (eV)
            max_cascade_depth: Maximum cascade generation to simulate
            min_recoil_energy: Minimum recoil energy to track (eV)
        """
        self.Ed = displacement_energy
        self.max_cascade_depth = max_cascade_depth
        self.E_min = min_recoil_energy
        
        self.damage_profile = DamageProfile()
        self.recoil_events = []
    
    def reset(self):
        """Reset damage counters."""
        self.damage_profile = DamageProfile()
        self.recoil_events = []
    
    def calculate_recoil_energy(self, e_primary: float, m1: float, m2: float,
                                 cos_theta: float) -> float:
        """Calculate energy transferred to target atom in collision.
        
        Uses binary collision approximation.
        
        Parameters:
            e_primary: Energy of incoming particle (eV)
            m1: Mass of projectile (amu)
            m2: Mass of target (amu)
            cos_theta: Cosine of scattering angle in CM frame
            
        Returns:
            Recoil energy (eV)
        """
        # Maximum energy transfer (head-on collision)
        gamma = 4 * m1 * m2 / (m1 + m2)**2
        
        # Energy transfer for given scattering angle
        # T = gamma * E * (1 - cos_theta) / 2
        # For small angle scattering, use exact formula
        T_recoil = gamma * e_primary * (1 - cos_theta) / 2
        
        return T_recoil
    
    def is_displacement(self, e_recoil: float) -> bool:
        """Check if recoil energy is sufficient to displace atom.
        
        Parameters:
            e_recoil: Recoil energy (eV)
            
        Returns:
            True if atom is displaced (E_recoil > E_d)
        """
        return e_recoil > self.Ed
    
    def is_trackable(self, e_recoil: float) -> bool:
        """Check if recoil should be tracked further.
        
        Parameters:
            e_recoil: Recoil energy (eV)
            
        Returns:
            True if recoil has enough energy to track
        """
        return e_recoil > self.E_min
    
    def register_collision(self, x: float, y: float, z: float,
                          e_primary: float, e_recoil: float,
                          recoil_direction: Tuple[float, float, float],
                          m1: float, m2: float,
                          generation: int = 0) -> Optional[RecoilEvent]:
        """Register a collision event and determine damage.
        
        Parameters:
            x, y, z: Position of collision
            e_primary: Energy of incoming particle before collision
            e_recoil: Energy transferred to target atom
            recoil_direction: Direction of recoiled atom
            m1: Mass of projectile
            m2: Mass of target
            generation: Cascade generation
            
        Returns:
            RecoilEvent if trackable, None otherwise
        """
        # Check if displacement occurred
        if self.is_displacement(e_recoil):
            # Create vacancy at original position
            self.damage_profile.vacancies.append((x, y, z))
            
            # If recoil energy is high enough, track it
            if self.is_trackable(e_recoil) and generation < self.max_cascade_depth:
                event = RecoilEvent(
                    x=x, y=y, z=z,
                    energy=e_recoil,
                    direction=recoil_direction,
                    primary_energy=e_primary,
                    generation=generation
                )
                self.recoil_events.append(event)
                return event
        
        return None
    
    def register_recoil_stop(self, x: float, y: float, z: float):
        """Register where a recoiled atom comes to rest (interstitial).
        
        Parameters:
            x, y, z: Final position of recoiled atom
        """
        self.damage_profile.interstitials.append((x, y, z))
    
    def register_energy_deposition(self, z: float, energy: float):
        """Register energy deposited at depth (for heating/amorphization).
        
        Parameters:
            z: Depth
            energy: Deposited energy (eV)
        """
        # Simple binning for now
        # In full implementation, this would be more sophisticated
        pass
    
    def get_cascade_statistics(self) -> dict:
        """Get statistics about cascade.
        
        Returns:
            Dictionary with cascade statistics
        """
        n_vacancies = len(self.damage_profile.vacancies)
        n_interstitials = len(self.damage_profile.interstitials)
        n_recoils = len(self.recoil_events)
        
        # Generation distribution
        if self.recoil_events:
            generations = [event.generation for event in self.recoil_events]
            max_gen = max(generations)
            gen_counts = [generations.count(g) for g in range(max_gen + 1)]
        else:
            max_gen = 0
            gen_counts = []
        
        return {
            'total_vacancies': n_vacancies,
            'total_interstitials': n_interstitials,
            'total_recoil_events': n_recoils,
            'max_generation': max_gen,
            'generation_counts': gen_counts,
            'frenkel_pairs': min(n_vacancies, n_interstitials),
        }


def estimate_sputtering_yield(ion_energy: float, m1: float, m2: float,
                               surface_binding_energy: float = 4.0) -> float:
    """Estimate sputtering yield using Sigmund formula.
    
    Parameters:
        ion_energy: Ion energy (eV)
        m1: Ion mass (amu)
        m2: Target mass (amu)
        surface_binding_energy: Surface binding energy (eV)
        
    Returns:
        Estimated number of sputtered atoms per ion
    """
    # Simplified Sigmund formula
    # Y ≈ 0.042 * (m1/m2) * (E / U_s) for m1 << m2
    # More accurate for similar masses:
    
    if ion_energy < surface_binding_energy:
        return 0.0
    
    # Energy factor
    lambda_factor = m1 / (m1 + m2)
    
    # Sigmund's nuclear stopping cross-section factor (simplified)
    # Full formula requires reduced energy and Thomas-Fermi screening
    # This is a rough approximation
    alpha = 0.3 * (m2 / m1)**0.67
    
    Y = alpha * lambda_factor * (ion_energy / surface_binding_energy)
    
    return max(0.0, Y)


# Displacement energy thresholds for common materials (eV)
DISPLACEMENT_ENERGIES = {
    'Si': 15.0,
    'GaAs': 10.0,
    'SiO2': 20.0,
    'W': 90.0,
    'Cu': 30.0,
    'Fe': 40.0,
    'Al': 25.0,
    'Ni': 40.0,
    'Ti': 30.0,
    'C': 28.0,  # Diamond
}


# Surface binding energies for sputtering (eV)
SURFACE_BINDING_ENERGIES = {
    'Si': 4.7,
    'W': 8.8,
    'Cu': 3.5,
    'Fe': 4.3,
    'Al': 3.4,
    'Ti': 4.9,
    'C': 7.4,
}
