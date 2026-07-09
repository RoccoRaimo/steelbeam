"""
steelbeam - Eng. Rocco Raimo
---
A python package for calculation of resistance and stability of steel beams, based on multiple national codes.
---

Unit conversion and handling for steelbeam package, using pint.
"""

import pint

ureg = pint.UnitRegistry(autoconvert_to_preferred = True)
preferred_units = [
    ureg.mm,
    ureg.kg,
    ureg.s,
    ureg.K,
    ureg.kN,
    ureg.W,
    ureg.MPa
]
imperial_preferred_units = [
    ureg.inch,
    ureg.lbf,
    ureg.s,
    ureg.K,
    ureg.ksi,
    ureg.lbf * ureg.inch,
]
ureg.default_preferred_units = preferred_units

Quantity = pint.Quantity


def get_preferred_units(unit_system: str):
    unit_system = unit_system.upper()
    if unit_system == 'SI':
        return preferred_units
    if unit_system == 'IMPERIAL':
        return imperial_preferred_units
    raise ValueError("unit_system must be either 'SI' or 'IMPERIAL'")



m = ureg.m
mm = ureg.mm
inch = ureg.inch
MPa = ureg.MPa
ksi = ureg.ksi
N = ureg.N
lbf = ureg.lbf

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

def create_quantity_from_input(value, unit_system: str, quantity_type: str) -> Quantity:
    """
    Create a pint Quantity object from user input.
    
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
    Quantity
        Quantity object with proper units
    """
    if isinstance(value, Quantity):
        return value
    
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
        return value
    if unit_str == '':
        return value
    return ureg.Quantity(value, unit_str)


DISPLAY_UNITS = {
    'SI': {
        'length': 'mm',
        'area': 'mm**2',
        'inertia': 'mm**4',
        'section_modulus': 'mm**3',
        'stress': 'MPa',
        'force': 'N',
        'moment': 'N*m',
        'ratio': '',
    },
    'IMPERIAL': {
        'length': 'inch',
        'area': 'inch**2',
        'inertia': 'inch**4',
        'section_modulus': 'inch**3',
        'stress': 'ksi',
        'force': 'lbf',
        'moment': 'lbf*in',
        'ratio': '',
    }
}


def convert_quantity_to_display(value: Quantity, quantity_type: str, units: str) -> float:
    """
    Convert a Quantity object to a display value in the specified unit system.
    
    Parameters
    ----------
    value : Quantity
        The Quantity object (stored in base SI units internally)
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
    
    if not isinstance(value, Quantity):
        return float(value)

    target_unit = DISPLAY_UNITS[units].get(quantity_type)
    if not target_unit:
        return float(value.magnitude)

    if target_unit == '':
        return float(value.magnitude)

    return float(value.to(target_unit).magnitude)


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
        'r': 'length',
    }

    def get_val(attr):
        val = getattr(beam, attr)
        if val is None:
            return None
        if isinstance(val, Quantity):
            quantity_type = attr_to_quantity.get(attr, attr)
            return convert_quantity_to_display(val, quantity_type, units)
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
        'r': get_val('r'),
        'units': units,
        'input_units': INPUT_UNITS[units],
    }
