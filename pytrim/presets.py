"""Material presets for common ion implantation scenarios.

This module provides predefined configurations for common material
combinations used in ion implantation, making it easier to set up
standard simulations.
"""
import json
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
from pathlib import Path


@dataclass
class MaterialPreset:
    """Preset configuration for a material combination."""
    
    name: str
    description: str
    
    # Projectile (ion)
    z1: int
    m1: float
    element1: str
    
    # Target
    z2: int
    m2: float
    element2: str
    density: float  # atoms/Å³
    
    # Default parameters
    energy: float  # eV
    corr_lindhard: float
    
    # Geometry defaults
    zmin: float
    zmax: float
    
    # Optional geometry type and parameters
    geometry_type: str = "planar"
    geometry_params: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MaterialPreset':
        """Create from dictionary."""
        return cls(**data)
    
    def save(self, filepath: Path):
        """Save preset to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, filepath: Path) -> 'MaterialPreset':
        """Load preset from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


# Predefined presets for common scenarios
PRESETS = {
    "B in Si": MaterialPreset(
        name="B in Si",
        description="Boron implantation in Silicon (Standard PMOS)",
        z1=5, m1=11.009, element1="B",
        z2=14, m2=28.086, element2="Si",
        density=0.04994,  # Si: 5.0e22 atoms/cm³
        energy=50000.0,
        corr_lindhard=1.5,
        zmin=0.0,
        zmax=4000.0,
        geometry_type="planar"
    ),
    
    "As in Si": MaterialPreset(
        name="As in Si",
        description="Arsenic implantation in Silicon (NMOS source/drain)",
        z1=33, m1=74.922, element1="As",
        z2=14, m2=28.086, element2="Si",
        density=0.04994,
        energy=80000.0,
        corr_lindhard=1.5,
        zmin=0.0,
        zmax=3000.0,
        geometry_type="planar"
    ),
    
    "P in Si": MaterialPreset(
        name="P in Si",
        description="Phosphorus implantation in Silicon (NMOS)",
        z1=15, m1=30.974, element1="P",
        z2=14, m2=28.086, element2="Si",
        density=0.04994,
        energy=60000.0,
        corr_lindhard=1.5,
        zmin=0.0,
        zmax=3500.0,
        geometry_type="planar"
    ),
    
    "BF2 in Si": MaterialPreset(
        name="BF2 in Si",
        description="BF2 molecular implantation in Silicon (Shallow junctions)",
        z1=5, m1=49.0,  # BF2 molecule
        element1="BF2",
        z2=14, m2=28.086, element2="Si",
        density=0.04994,
        energy=40000.0,
        corr_lindhard=1.5,
        zmin=0.0,
        zmax=2000.0,
        geometry_type="planar"
    ),
    
    "Ga in GaN": MaterialPreset(
        name="Ga in GaN",
        description="Gallium implantation in Gallium Nitride",
        z1=31, m1=69.723, element1="Ga",
        z2=31, m2=69.723, element2="GaN",  # Average for compound
        density=0.08838,  # GaN: 8.838e22 atoms/cm³
        energy=100000.0,
        corr_lindhard=1.5,
        zmin=0.0,
        zmax=2500.0,
        geometry_type="planar"
    ),
    
    "He in W": MaterialPreset(
        name="He in W",
        description="Helium implantation in Tungsten (Plasma-wall interaction)",
        z1=2, m1=4.003, element1="He",
        z2=74, m2=183.84, element2="W",
        density=0.06306,  # W: 6.306e22 atoms/cm³
        energy=20000.0,
        corr_lindhard=1.5,
        zmin=0.0,
        zmax=1500.0,
        geometry_type="planar"
    ),
    
    "Ar in Cu": MaterialPreset(
        name="Ar in Cu",
        description="Argon implantation in Copper (Surface modification)",
        z1=18, m1=39.948, element1="Ar",
        z2=29, m2=63.546, element2="Cu",
        density=0.08491,  # Cu: 8.491e22 atoms/cm³
        energy=50000.0,
        corr_lindhard=1.5,
        zmin=0.0,
        zmax=2000.0,
        geometry_type="planar"
    ),
    
    "N in Ti": MaterialPreset(
        name="N in Ti",
        description="Nitrogen implantation in Titanium (TiN formation)",
        z1=7, m1=14.007, element1="N",
        z2=22, m2=47.867, element2="Ti",
        density=0.05662,  # Ti: 5.662e22 atoms/cm³
        energy=35000.0,
        corr_lindhard=1.5,
        zmin=0.0,
        zmax=2500.0,
        geometry_type="planar"
    ),
}


class PresetManager:
    """Manager for loading, saving, and managing presets."""
    
    def __init__(self, user_preset_dir: Optional[Path] = None):
        """Initialize preset manager.
        
        Parameters:
            user_preset_dir: Directory for user-defined presets
        """
        if user_preset_dir is None:
            user_preset_dir = Path.home() / ".cytrim" / "presets"
        
        self.user_preset_dir = user_preset_dir
        self.user_preset_dir.mkdir(parents=True, exist_ok=True)
        
        # Combined presets (built-in + user)
        self.presets = PRESETS.copy()
        self._load_user_presets()
    
    def _load_user_presets(self):
        """Load all user-defined presets from directory."""
        for preset_file in self.user_preset_dir.glob("*.json"):
            try:
                preset = MaterialPreset.load(preset_file)
                self.presets[preset.name] = preset
            except Exception as e:
                print(f"Warning: Could not load preset {preset_file}: {e}")
    
    def get_preset(self, name: str) -> Optional[MaterialPreset]:
        """Get preset by name."""
        return self.presets.get(name)
    
    def get_all_presets(self) -> Dict[str, MaterialPreset]:
        """Get all available presets."""
        return self.presets.copy()
    
    def save_preset(self, preset: MaterialPreset, overwrite: bool = False):
        """Save a user-defined preset.
        
        Parameters:
            preset: Preset to save
            overwrite: Allow overwriting existing user presets
        """
        filepath = self.user_preset_dir / f"{preset.name}.json"
        
        if filepath.exists() and not overwrite:
            raise FileExistsError(
                f"Preset '{preset.name}' already exists. "
                "Use overwrite=True to replace it."
            )
        
        preset.save(filepath)
        self.presets[preset.name] = preset
    
    def delete_preset(self, name: str):
        """Delete a user-defined preset.
        
        Parameters:
            name: Name of preset to delete
            
        Raises:
            ValueError: If trying to delete built-in preset
        """
        if name in PRESETS:
            raise ValueError(f"Cannot delete built-in preset '{name}'")
        
        filepath = self.user_preset_dir / f"{name}.json"
        if filepath.exists():
            filepath.unlink()
        
        if name in self.presets:
            del self.presets[name]
    
    def get_preset_names(self) -> list:
        """Get list of all preset names."""
        return sorted(self.presets.keys())
    
    def is_builtin(self, name: str) -> bool:
        """Check if preset is built-in (not user-defined)."""
        return name in PRESETS


# Global preset manager instance
_preset_manager = None


def get_preset_manager() -> PresetManager:
    """Get global preset manager instance."""
    global _preset_manager
    if _preset_manager is None:
        _preset_manager = PresetManager()
    return _preset_manager
