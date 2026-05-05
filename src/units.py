"""
steelbeam - Eng. Rocco Raimo
---
A python package for calculation of resistance and stability of steel beams, based on multiple national codes.
---

Unit conversion and handling for steelbeam package, using forallpeople library.
"""

import forallpeople 
forallpeople.environment('structural', top_level=True)
from forallpeople import Physical

# Unit conversion factors from BASE units (m, m², m³, m⁴, Pa) to DISPLAY units
UNIT_FACTORS = {
    'SI': {
        'length': 1000.0,              # m → mm
        'area': 1e6,                   # m² → mm²
        'inertia': 1e12,               # m⁴ → mm⁴
        'section_modulus': 1e9,        # m³ → mm³
        'stress': 1e-6,                # Pa → MPa
        'force': 1.0,                  # N → N
        'moment': 1.0,                 # N*m → N*m
        'ratio': 1.0,                  # dimensionless
    },
    'IMPERIAL': {
        'length': 1.0 / 0.0254,        # m → in
        'area': 1.0 / 0.00064516,      # m² → in²
        'inertia': (1.0 / 0.0254) ** 4, # m⁴ → in⁴
        'section_modulus': (1.0 / 0.0254) ** 3,  # m³ → in³
        'stress': 1e-6 / 6.894757293168361,  # Pa → ksi
        'force': 1.0 / 4.4482216152605,         # N → lbf
        'moment': 8.85074576749058,             # N*m → lbf*in
        'ratio': 1.0,                           # dimensionless
    }
}

# Unit labels for display
UNIT_LABELS = {
    'SI': {
        'length': 'mm',
        'area': 'mm²',
        'inertia': 'mm⁴',
        'section_modulus': 'mm³',
        'stress': 'MPa',
        'force': 'N',
        'moment': 'N·m',
        'ratio': '',
    },
    'IMPERIAL': {
        'length': 'in',
        'area': 'in²',
        'inertia': 'in⁴',
        'section_modulus': 'in³',
        'stress': 'ksi',
        'force': 'lbf',
        'moment': 'lbf·in',
        'ratio': '',
    }
}

# Input units (what user provides)
INPUT_UNITS = {
    'SI': {
        'length': 'm',
        'area': 'mm²',
        'inertia': 'mm⁴',
        'section_modulus': 'mm³',
        'stress': 'MPa',
        'force': 'N',
        'moment': 'N·m',
        'ratio': '',
    },
    'IMPERIAL': {
        'length': 'in',
        'area': 'in²',
        'inertia': 'in⁴',
        'section_modulus': 'in³',
        'stress': 'ksi',
        'force': 'lbf',
        'moment': 'lbf·in',
        'ratio': '',
    }
}

def create_physical_from_input(value, unit_system: str, quantity_type: str) -> Physical:
    """
    Create a Physical object from user input.
    
    Parameters
    ----------
    value : float
        Numeric input value
    unit_system : str
        'SI' or 'IMPERIAL'
    quantity_type : str
        Type of quantity
    
    Returns
    -------
    Physical
        Physical object with proper units
    """
    if isinstance(value, Physical):
        return value
    
    # Map quantity types to forallpeople unit strings
    unit_map = {
        'length': 'm' if unit_system == 'SI' else 'inch',
        'area': 'mm**2' if unit_system == 'SI' else 'inch**2',
        'inertia': 'mm**4' if unit_system == 'SI' else 'inch**4',
        'section_modulus': 'mm**3' if unit_system == 'SI' else 'inch**3',
        'stress': 'MPa' if unit_system == 'SI' else 'ksi',
        'force': 'N' if unit_system == 'SI' else 'lbf',
        'moment': 'N*m' if unit_system == 'SI' else 'lbf*in',
        'ratio': '',
    }

    unit_str = unit_map.get(quantity_type)
    if unit_str is None:
        # Unknown quantity type: keep the numeric value unchanged
        return value
    if unit_str == '':
        return value
    return value * eval(unit_str)


def convert_physical_to_display(value: Physical, quantity_type: str, units: str) -> float:
    """
    Convert a Physical object to a display value in the specified unit system.
    
    Parameters
    ----------
    value : Physical
        The Physical object (stored in base SI units internally)
    quantity_type : str
        Type of quantity ('length', 'area', 'stress', etc.)
    units : str
        Target unit system ('SI' or 'IMPERIAL')
    
    Returns
    -------
    float
        The numeric value in the display unit system
    """
    if value is None:
        return None
    
    units = units.upper()
    if units not in ('SI', 'IMPERIAL'):
        raise ValueError("units must be either 'SI' or 'IMPERIAL'")
    
    if not isinstance(value, Physical):
        # If it's already a number, return as-is (shouldn't happen with proper init)
        return float(value)
    
    base_value = value.value  # Always in base SI units
    factor = UNIT_FACTORS[units].get(quantity_type, 1.0)
    
    return base_value * factor


def get_unit_label(quantity_type: str, units: str) -> str:
    """Get the display label for a quantity type in the specified unit system."""
    units = units.upper()
    if units not in ('SI', 'IMPERIAL'):
        raise ValueError("units must be either 'SI' or 'IMPERIAL'")
    
    return UNIT_LABELS[units].get(quantity_type, '')


def get_input_unit(quantity_type: str, units: str) -> str:
    """Get the expected input unit for a quantity type."""
    units = units.upper()
    if units not in ('SI', 'IMPERIAL'):
        raise ValueError("units must be either 'SI' or 'IMPERIAL'")
    
    return INPUT_UNITS[units].get(quantity_type, '')


def format_value(val: float) -> str:
    """
    Format a numeric value for display without scientific notation.
    
    Parameters
    ----------
    val : float
        The value to format
    
    Returns
    -------
    str
        Formatted string representation
    """
    if val is None:
        return "None"
    
    # Check if effectively an integer
    if isinstance(val, float) and val.is_integer():
        return f"{int(val)}"
    
    # Format with up to 2 decimal places, strip trailing zeros
    formatted = f"{val:.2f}".rstrip('0').rstrip('.')
    return formatted


def get_section_properties(beam, units: str) -> dict:
    """
    Get section properties for a SteelBeam in the specified unit system.
    
    Parameters
    ----------
    beam : SteelBeam
        The steel beam instance
    units : str
        Target unit system ('SI' or 'IMPERIAL')
    
    Returns
    -------
    dict
        Dictionary with all section properties in display units
    """
    units = units.upper()
    if units not in ('SI', 'IMPERIAL'):
        raise ValueError("units must be either 'SI' or 'IMPERIAL'")

    # Mapping from attribute names to quantity types
    attr_to_quantity = {
        'length': 'length',
        'elastic_modulus': 'stress',
        'f_yk': 'stress',
        'section_area': 'area',
        'section_area_shear_y': 'area',
        'section_area_shear_z': 'area',
        'section_inertia_y': 'inertia',
        'section_inertia_z': 'inertia',
        'section_inertia_torsional': 'inertia',
        'section_w_pl_y': 'section_modulus',
        'section_w_pl_z': 'section_modulus',
        'h_w': 'length',
        't_w': 'length',
        'b': 'length',
        't_f': 'length',
    }

    def get_val(attr):
        val = getattr(beam, attr)
        if val is None:
            return None
        if isinstance(val, Physical):
            quantity_type = attr_to_quantity.get(attr, attr)
            return convert_physical_to_display(val, quantity_type, units)
        return val

    return {
        'length': get_val('length'),
        'elastic_modulus': get_val('elastic_modulus'),
        'f_yk': get_val('f_yk'),
        'section_area': get_val('section_area'),
        'section_area_shear_y': get_val('section_area_shear_y'),
        'section_area_shear_z': get_val('section_area_shear_z'),
        'section_inertia_y': get_val('section_inertia_y'),
        'section_inertia_z': get_val('section_inertia_z'),
        'section_inertia_torsional': get_val('section_inertia_torsional'),
        'section_w_pl_y': get_val('section_w_pl_y'),
        'section_w_pl_z': get_val('section_w_pl_z'),
        'h_w': get_val('h_w'),
        't_w': get_val('t_w'),
        'b': get_val('b'),
        't_f': get_val('t_f'),
        'units': units,
        'input_units': INPUT_UNITS[units],
    }
